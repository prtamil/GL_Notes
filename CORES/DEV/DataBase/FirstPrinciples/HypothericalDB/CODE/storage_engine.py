"""
Storage Engine
==============
The storage engine manages the LIFECYCLE of row versions across time.

It sits between:
  Below: Buffer Manager (memory) + Physical Storage (page layout)
  Above: Transaction Manager (concurrency) + Query Processor (access)

Its core responsibility: given a transaction ID, correctly INSERT / UPDATE /
DELETE tuples while maintaining the version chains that MVCC depends on.

Why version chains?
  An UPDATE doesn't overwrite the old row. It creates a NEW tuple and links
  the old one to it via ctid. Both coexist temporarily.

  old tuple:  xmin=1, xmax=5, ctid=(page=1, slot=2)   ← "replaced by tx 5"
                                          ↓
  new tuple:  xmin=5, xmax=0, ctid=None                ← current version

  A transaction whose snapshot is before tx5 committed still reads the OLD
  tuple. A transaction after tx5 committed reads the NEW one. Same query,
  different answers — both correct relative to their snapshot.

Heap = unordered collection of pages.
  "Heap" because tuples are appended wherever there's space, not sorted.
  Indexes are separate structures that point INTO the heap.
"""

from collections.abc import Iterator
from typing import Any

from physical_storage import Page, Tuple, TupleHeader
from buffer_manager import BufferManager

# A heap location is the stable address of a tuple: (page_id, slot_number)
type HeapLocation = tuple[int, int]


class HeapRelation:
    """
    One table's worth of heap pages.
    Exposes INSERT / UPDATE / DELETE / SEQ_SCAN / VACUUM operations.
    Does NOT enforce visibility — that's the Transaction Manager's job.
    """

    def __init__(self, name: str, buffer_manager: BufferManager):
        self.name     = name
        self._buf_mgr = buffer_manager
        self._page_ids: list[int] = []
        self._next_page_id = 0

    # ── Page management ───────────────────────────────────────────────────────

    def _allocate_page(self) -> Page:
        """
        Create a new page, register it with this relation, and return it PINNED.
        The caller is responsible for calling unpin() when done.
        """
        page_id = self._next_page_id
        self._next_page_id += 1
        self._page_ids.append(page_id)
        frame = self._buf_mgr.pin(page_id)   # pin_count = 1; caller will unpin
        return frame.page

    def _get_page(self, page_id: int) -> Page:
        """Pin a page and return it. Caller MUST call unpin() when done."""
        return self._buf_mgr.pin(page_id).page

    def _page_with_free_space(self) -> Page:
        """Return the last page if it has room, otherwise allocate a new one."""
        if self._page_ids:
            page = self._get_page(self._page_ids[-1])
            if page.header.free_space >= 64:
                return page
            self._buf_mgr.unpin(self._page_ids[-1])
        return self._allocate_page()

    # ── INSERT ────────────────────────────────────────────────────────────────

    def insert(self, data: dict[str, Any], xid: int) -> HeapLocation:
        """
        Append a new tuple to the heap.

        Sets xmin = xid  (this transaction created it)
             xmax = 0    (not deleted yet)
             ctid = None (no newer version)

        Returns the (page_id, slot_num) address of the new tuple.
        """
        header   = TupleHeader(xmin=xid, xmax=0, ctid=None)
        tup      = Tuple(header=header, data=data)
        page     = self._page_with_free_space()
        slot_num = page.insert_tuple(tup)
        page_id  = page.header.page_id
        self._buf_mgr.unpin(page_id, dirty=True)
        return (page_id, slot_num)

    # ── DELETE ────────────────────────────────────────────────────────────────

    def delete(self, location: HeapLocation, xid: int) -> None:
        """
        Logical deletion: stamp xmax = xid on the tuple at `location`.

        The tuple stays physically present so older transactions can still
        see it. VACUUM removes it once no snapshot can reach it.
        """
        page_id, slot_num = location
        page = self._get_page(page_id)
        page.delete_tuple(slot_num, xmax=xid)
        self._buf_mgr.unpin(page_id, dirty=True)

    # ── UPDATE ────────────────────────────────────────────────────────────────

    def update(self, location: HeapLocation,
               new_data: dict[str, Any], xid: int) -> HeapLocation:
        """
        An UPDATE is: INSERT new version + stamp old version as replaced.

        Step 1: Insert the new tuple (xmin = xid, xmax = 0)
        Step 2: Stamp old tuple with xmax = xid  (marks it deleted by this tx)
        Step 3: Set old tuple's ctid = new location  (version chain link)

        Why two steps?  MVCC requires both versions to coexist until all
        concurrent readers that might see the old version are done.
        """
        # Step 1: new version
        new_location = self.insert(new_data, xid)

        # Steps 2 & 3: mark old version as replaced, link to new version
        page_id, slot_num = location
        page = self._get_page(page_id)
        old_tup = page.get_tuple(slot_num)
        if old_tup:
            old_tup.header.xmax = xid
            old_tup.header.ctid = new_location   # ← version chain link
        self._buf_mgr.unpin(page_id, dirty=True)

        return new_location

    # ── SEQUENTIAL SCAN ───────────────────────────────────────────────────────

    def seq_scan(self) -> Iterator[tuple[HeapLocation, Tuple]]:
        """
        Read every page, every slot, yield (location, tuple) for each.

        Includes logically deleted tuples — the caller (transaction manager)
        decides what's visible. The storage engine just delivers all versions.

        This is efficient for small tables or queries touching most rows.
        For selective queries on large tables, an index scan is better.
        """
        for page_id in self._page_ids:
            page = self._get_page(page_id)
            for slot_num, tup in page.all_tuples():
                yield (page_id, slot_num), tup
            self._buf_mgr.unpin(page_id)

    # ── VACUUM ────────────────────────────────────────────────────────────────

    def vacuum(self, oldest_active_xid: int) -> int:
        """
        Physically remove dead tuples that no active transaction can see.

        Safe-to-remove criterion:
          xmax != 0  (logically deleted)
          AND xmax < oldest_active_xid  (even the oldest running tx won't see it)

        Returns number of pages compacted.
        """
        pages_cleaned = 0
        for page_id in self._page_ids:
            page = self._get_page(page_id)
            page.compact(oldest_active_xid)
            self._buf_mgr.unpin(page_id, dirty=True)
            pages_cleaned += 1
        return pages_cleaned

    def __repr__(self) -> str:
        return f"HeapRelation(name={self.name!r}, pages={len(self._page_ids)})"

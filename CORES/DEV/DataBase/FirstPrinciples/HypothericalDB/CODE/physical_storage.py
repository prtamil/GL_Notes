"""
Physical Storage Layer
======================
The foundation of the database. Everything lives in PAGES.

A page is a fixed-size block (8KB). The disk only knows how to read/write
full pages. Random access to any page:  offset = page_id * PAGE_SIZE

Inside a page, two regions grow toward each other:
  [PageHeader][Slot0][Slot1]...[SlotN]  <-- free space -->  [TupleN]...[Tuple0]
   header + slot directory grows →                        ← tuple data grows

Key insight: SLOTS are the indirection layer.
  A tuple's stable address is (page_id, slot_number).
  The slot records WHERE in the page the tuple lives.
  When tuples are compacted/moved, only the slot's offset changes —
  the (page_id, slot_number) address stays the same forever.
"""

from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

PAGE_SIZE = 8192   # 8KB — same default as PostgreSQL


# ─── Tuple Header ─────────────────────────────────────────────────────────────
#
# Every tuple (row version) carries this header. The xmin/xmax fields are what
# make MVCC possible — they record the transaction history of this row version.
#
#   xmin: "I was created by transaction xmin"
#   xmax: "I was deleted/replaced by transaction xmax" (0 means still alive)
#   ctid: if this tuple was UPDATEd, ctid points to the newer version
#
# These three fields let any transaction answer: "should I see this row?"

@dataclass
class TupleHeader:
    xmin: int                              # TID of the INSERT transaction
    xmax: int = 0                          # TID of DELETE/UPDATE (0 = alive)
    ctid: tuple[int, int] | None = None  # (page_id, slot_num) of next version


# ─── Tuple ────────────────────────────────────────────────────────────────────
#
# A tuple = header metadata + actual column values.
# In a real database the column values would be serialized bytes.
# We use a dict here so the concepts aren't buried in serialization code.

@dataclass
class Tuple:
    header: TupleHeader
    data:   dict[str, Any]   # { "column_name": value, ... }

    def is_deleted(self) -> bool:
        """xmax != 0 means some transaction marked this tuple as removed."""
        return self.header.xmax != 0

    def has_newer_version(self) -> bool:
        """ctid points to the replacement tuple created by an UPDATE."""
        return self.header.ctid is not None


# ─── Slot ─────────────────────────────────────────────────────────────────────
#
# A slot is a tiny pointer entry in the page's slot directory.
# It records: where in the page does a tuple live, and how big is it.
#
# LIVE  = slot points to a tuple (may be logically deleted, but physically present)
# EMPTY = slot was freed; can be reused for the next INSERT

class SlotStatus(Enum):
    LIVE  = auto()
    EMPTY = auto()

@dataclass
class Slot:
    offset: int                       # byte offset of the tuple within the page
    length: int                       # byte length of the tuple
    status: SlotStatus = SlotStatus.LIVE


# ─── Page Header ──────────────────────────────────────────────────────────────

@dataclass
class PageHeader:
    page_id:    int
    slot_count: int = 0              # total allocated slots (including empty ones)
    free_space: int = PAGE_SIZE - 32 # bytes available for new tuples (simplified)


# ─── Page ─────────────────────────────────────────────────────────────────────
#
# A page is the atomic unit of disk I/O. The buffer manager always loads and
# writes full pages — never partial reads.
#
# This implementation stores tuples as Python objects (no raw bytes) so we
# can focus on the structural concepts rather than serialization.

class Page:

    def __init__(self, page_id: int):
        self.header = PageHeader(page_id)
        self.slots:  list[Slot]        = []
        self.tuples: list[Tuple | None] = []  # index i matches slots[i]

    # ── INSERT ────────────────────────────────────────────────────────────────

    def insert_tuple(self, tup: Tuple) -> int:
        """
        Add a tuple to this page. Returns the slot number.

        Slot reuse: before growing the slot directory, check if any existing
        slot is EMPTY (freed by a previous deletion + vacuum). Reusing slots
        keeps the directory compact.
        """
        # First, try to reuse an existing EMPTY slot
        for slot_num, slot in enumerate(self.slots):
            if slot.status == SlotStatus.EMPTY:
                self.slots[slot_num]  = Slot(offset=slot_num * 64, length=64)
                self.tuples[slot_num] = tup
                return slot_num

        # No empty slot available — append a new one
        slot_num = len(self.slots)
        self.slots.append(Slot(offset=slot_num * 64, length=64))
        self.tuples.append(tup)
        self.header.slot_count += 1
        self.header.free_space -= 64   # simplified fixed-size accounting
        return slot_num

    # ── READ ──────────────────────────────────────────────────────────────────

    def get_tuple(self, slot_num: int) -> Tuple | None:
        """Fetch a tuple by slot number. Returns None if slot is empty/invalid."""
        if slot_num >= len(self.slots):
            return None
        if self.slots[slot_num].status == SlotStatus.EMPTY:
            return None
        return self.tuples[slot_num]

    # ── DELETE (logical) ──────────────────────────────────────────────────────

    def delete_tuple(self, slot_num: int, xmax: int) -> None:
        """
        LOGICAL deletion: stamp xmax on the tuple header. Do NOT remove it.

        Why keep the tuple? Because older transactions might still be reading
        it. The tuple stays until VACUUM determines no snapshot can see it.
        Physical removal happens later in compact().
        """
        tup = self.get_tuple(slot_num)
        if tup:
            tup.header.xmax = xmax

    # ── COMPACT (vacuum) ──────────────────────────────────────────────────────

    def compact(self, oldest_active_xid: int) -> None:
        """
        VACUUM: physically remove dead tuples that are safe to discard.

        A tuple is safe to remove when:
          - It has been logically deleted (xmax != 0)
          - AND xmax < oldest_active_xid  (no running transaction can see it)

        Slot numbers are PRESERVED — we just mark the slot EMPTY so it can
        be reused. External references like index entries remain valid
        (they'll find an EMPTY slot, which means the row no longer exists).
        """
        for slot_num, tup in enumerate(self.tuples):
            if tup is None:
                continue
            dead_and_invisible = (
                tup.header.xmax != 0 and
                tup.header.xmax < oldest_active_xid
            )
            if dead_and_invisible:
                self.tuples[slot_num]       = None
                self.slots[slot_num].status = SlotStatus.EMPTY
                self.header.free_space     += 64  # reclaim space

    # ── SCAN ──────────────────────────────────────────────────────────────────

    def all_tuples(self) -> Iterator[tuple[int, Tuple]]:
        """
        Yield (slot_num, tuple) for every non-empty slot.
        Includes logically deleted tuples — visibility is checked elsewhere.
        """
        for slot_num, tup in enumerate(self.tuples):
            if tup is not None and self.slots[slot_num].status == SlotStatus.LIVE:
                yield slot_num, tup

    def __repr__(self) -> str:
        live  = sum(1 for t in self.tuples if t and not t.is_deleted())
        dead  = sum(1 for t in self.tuples if t and t.is_deleted())
        empty = sum(1 for s in self.slots  if s.status == SlotStatus.EMPTY)
        return (f"Page(id={self.header.page_id}, "
                f"live={live}, dead={dead}, empty_slots={empty}, "
                f"free={self.header.free_space}B)")

"""
Buffer Manager
==============
Disk I/O is the bottleneck. The buffer manager keeps a pool of pages in
memory so the database avoids hitting the disk on every access.

Think of it as a cache — but with database-aware semantics the OS cache
doesn't have:
  - It understands page structure (not just raw bytes)
  - It tracks which pages are "in use" (pinned) so they can't be evicted
  - It defers writes (dirty pages) and controls write-back order (WAL rule)
  - It participates in MVCC and transaction safety

Lifecycle of a page in the buffer pool:
  disk → [load into frame] → pin (in use) → unpin → [LRU eviction] → disk

LRU eviction policy:
  When the pool is full and we need space, evict the page that was used
  LEAST RECENTLY — that page is probably not needed soon.
  A pinned page cannot be evicted (it's actively being read/written).
"""

from collections import OrderedDict
from dataclasses import dataclass

from physical_storage import Page


# ─── Buffer Frame ─────────────────────────────────────────────────────────────
#
# A frame is one slot in the buffer pool. It wraps a page with the metadata
# the buffer manager needs to manage it:
#   pin_count  — how many callers are actively using this page right now
#   is_dirty   — has this page been modified since it was loaded from disk?

@dataclass
class BufferFrame:
    page:      Page
    page_id:   int
    pin_count: int  = 0
    is_dirty:  bool = False

    def is_pinned(self) -> bool:
        return self.pin_count > 0


# ─── Simulated Disk ───────────────────────────────────────────────────────────
#
# In a real database this reads/writes 8KB blocks from a file at offset
#   offset = page_id * PAGE_SIZE
# We simulate it with an in-memory dict to keep focus on buffer concepts.

class SimulatedDisk:

    def __init__(self):
        self._storage:    dict[int, Page] = {}
        self._read_count  = 0
        self._write_count = 0

    def read_page(self, page_id: int) -> Page:
        """Load a page. Creates a blank page if this page_id is new."""
        self._read_count += 1
        if page_id not in self._storage:
            self._storage[page_id] = Page(page_id)
        return self._storage[page_id]

    def write_page(self, page: Page) -> None:
        """Flush a modified page back to disk."""
        self._write_count += 1
        self._storage[page.header.page_id] = page

    @property
    def stats(self) -> dict[str, int]:
        return {"disk_reads": self._read_count, "disk_writes": self._write_count}


# ─── Buffer Manager ───────────────────────────────────────────────────────────

class BufferManager:

    def __init__(self, pool_size: int = 8, disk: SimulatedDisk | None = None):
        self.pool_size = pool_size
        self.disk      = disk or SimulatedDisk()

        # OrderedDict preserves insertion order.
        # We move a page to the END when it's used (most recent = end).
        # Eviction candidate is always at the FRONT (least recent).
        self._pool: OrderedDict[int, BufferFrame]  = OrderedDict()

    # ── Pin ───────────────────────────────────────────────────────────────────

    def pin(self, page_id: int) -> BufferFrame:
        """
        Bring a page into memory and mark it as in-use (pin it).

        If the page is already in the pool: just increment the pin count.
        If not in pool: load from disk, evicting an unpinned page if needed.

        IMPORTANT: Every caller that pins must eventually unpin.
        Forgetting to unpin leaks pins → pool eventually exhausted.
        """
        if page_id in self._pool:
            self._pool.move_to_end(page_id)   # mark as recently used
            frame = self._pool[page_id]
        else:
            self._ensure_space()
            page  = self.disk.read_page(page_id)
            frame = BufferFrame(page=page, page_id=page_id)
            self._pool[page_id] = frame

        frame.pin_count += 1
        return frame

    # ── Unpin ─────────────────────────────────────────────────────────────────

    def unpin(self, page_id: int, dirty: bool = False) -> None:
        """
        Release a pin on a page.
        If dirty=True: the caller modified the page — mark it for write-back.

        The page stays in the pool after unpinning.
        It will be written to disk and evicted only when the pool needs space.
        """
        if page_id not in self._pool:
            raise RuntimeError(f"Cannot unpin page {page_id}: not in pool")
        frame = self._pool[page_id]
        if frame.pin_count <= 0:
            raise RuntimeError(f"Page {page_id} pin_count already 0")
        frame.pin_count -= 1
        if dirty:
            frame.is_dirty = True

    # ── Flush ─────────────────────────────────────────────────────────────────

    def flush(self, page_id: int) -> None:
        """Explicitly write one dirty page to disk (e.g., at checkpoint)."""
        if page_id in self._pool:
            frame = self._pool[page_id]
            if frame.is_dirty:
                self.disk.write_page(frame.page)
                frame.is_dirty = False

    def flush_all(self) -> None:
        """Write all dirty pages to disk. Called at checkpoint time."""
        for page_id in list(self._pool.keys()):
            self.flush(page_id)

    # ── LRU Eviction ──────────────────────────────────────────────────────────

    def _ensure_space(self) -> None:
        """
        If the pool is full, evict the least-recently-used UNPINNED page.

        Before evicting a dirty page: write it to disk first.
        (Simplified WAL rule — in reality, the WAL log is written before the page.)

        If ALL pages are pinned: the pool is exhausted → crash.
        This should never happen with correct pin/unpin discipline.
        """
        if len(self._pool) < self.pool_size:
            return   # pool has room, nothing to evict

        for page_id, frame in self._pool.items():   # front = least recently used
            if not frame.is_pinned():
                if frame.is_dirty:
                    self.disk.write_page(frame.page)
                del self._pool[page_id]
                return

        raise RuntimeError(
            f"Buffer pool exhausted ({self.pool_size} frames, all pinned). "
            "A caller forgot to unpin."
        )

    # ── Diagnostics ───────────────────────────────────────────────────────────

    def status(self) -> str:
        lines = [f"Buffer pool  [{len(self._pool)}/{self.pool_size} frames in use]"]
        lines.append(f"  {'page_id':>7}  {'pins':>4}  {'dirty':>5}  page state")
        lines.append(f"  {'-'*7}  {'-'*4}  {'-'*5}  {'-'*40}")
        for pid, f in self._pool.items():
            lines.append(
                f"  {pid:>7}  {f.pin_count:>4}  {str(f.is_dirty):>5}  {f.page}"
            )
        return "\n".join(lines)

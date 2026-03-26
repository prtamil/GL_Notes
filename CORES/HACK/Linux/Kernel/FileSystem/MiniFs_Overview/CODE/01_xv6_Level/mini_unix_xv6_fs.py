"""
=============================================================================
  Mini-UNIX-FS  xv6  —  Complete xv6-Faithful Filesystem Simulator
=============================================================================

  This is the xv6 edition.  Every layer, every data structure, every
  algorithm is modelled directly on xv6 (MIT's teaching OS, git.kernel.org
  or github.com/mit-pdos/xv6-riscv).  The code is pure Python — no OS
  calls, no real disk — but the design is exact.

  WHAT IS xv6?
    xv6 is a small UNIX-like operating system written by MIT for teaching.
    It is based on UNIX Sixth Edition (V6) but rewritten for modern hardware.
    Its filesystem is small (~900 lines of C) yet complete enough to run real
    programs.  It is the canonical reference for understanding UNIX internals.

  LAYERS  (top → bottom, matching xv6 source files exactly):

    ┌──────────────────────────────────────────────────────────────┐
    │  Shell / User API                   (this file: shell + demo)│
    ├──────────────────────────────────────────────────────────────┤
    │  File Descriptor Table (struct file / ftable)  SECTION 8    │ kernel/file.c
    ├──────────────────────────────────────────────────────────────┤
    │  Filesystem Operations (namei, create, unlink) SECTION 7    │ kernel/fs.c
    ├──────────────────────────────────────────────────────────────┤
    │  Path Lookup  (namei / nameiparent)            SECTION 6    │ kernel/fs.c
    ├──────────────────────────────────────────────────────────────┤
    │  Directory Layer  (dirlookup / dirlink)        SECTION 5    │ kernel/fs.c
    ├──────────────────────────────────────────────────────────────┤
    │  Inode Layer  (iget/iput/ialloc/iupdate)       SECTION 4    │ kernel/fs.c
    ├──────────────────────────────────────────────────────────────┤
    │  Block Allocator  (balloc/bfree + bitmap)      SECTION 3B   │ kernel/fs.c
    ├──────────────────────────────────────────────────────────────┤
    │  Superblock on Disk  (readsb)                  SECTION 3    │ kernel/fs.c
    ├──────────────────────────────────────────────────────────────┤
    │  Log Layer  (begin_op/end_op/log_write/commit) SECTION 2C   │ kernel/log.c
    ├──────────────────────────────────────────────────────────────┤
    │  Buffer Cache  (bread/bwrite/brelse)           SECTION 2B   │ kernel/bio.c
    ├──────────────────────────────────────────────────────────────┤
    │  Disk Driver  (raw read/write via controller)  SECTION 2    │ kernel/virtio_disk.c
    ├──────────────────────────────────────────────────────────────┤
    │  Disk Controller  (LBA → CHS)                  SECTION 0C   │ hardware
    ├──────────────────────────────────────────────────────────────┤
    │  Physical Platter  (cylinder/head/sector)      SECTION 0A   │ hardware
    └──────────────────────────────────────────────────────────────┘

  DISK LAYOUT  (matches xv6 mkfs layout exactly in spirit):

    Block 0        : Boot block      (unused, reserved)
    Block 1        : Superblock      (magic, total blocks, inode count, etc.)
    Block 2        : Log header      (xv6 log.lh — commit count + block list)
    Block 3–6      : Log data blocks (LOGSIZE=4 blocks)
    Block 7–8      : Inode table     (NINODES=32, IPB=4 inodes per block = 8 blocks)
    Block 9        : Block bitmap    (1 bit per data block, packed into one block)
    Block 10–255   : Data blocks     (246 usable data blocks)

  xv6 FEATURES IMPLEMENTED:
    ✓ Superblock on disk  (magic number, geometry, read on mount)
    ✓ Write-ahead log     (begin_op / log_write / end_op / commit)
    ✓ Buffer cache        (bread / bwrite / brelse with ref counts)
    ✓ Block bitmap        (balloc / bfree — bit-level block allocation)
    ✓ Inode table on disk (multiple inodes per block, IPB packing)
    ✓ Indirect blocks     (single indirect — supports files > 4 blocks)
    ✓ Directories         (dirlookup / dirlink / inode type T_DIR)
    ✓ Path resolution     (namei / nameiparent — full multi-component)
    ✓ File descriptor table (struct file / ftable / open / read / write)
    ✓ Hard links + unlink contract (link_count + deferred free)
    ✓ Physical disk       (CHS geometry, LBA translation, I/O log)

=============================================================================
"""

import struct
import contextlib


# =============================================================================
# SECTION 0A — PHYSICAL PLATTER
# =============================================================================

SECTOR_SIZE        = 64    # bytes per sector (small for printability)
NUM_CYLINDERS      = 8
HEADS_PER_CYLINDER = 4
SECTORS_PER_TRACK  = 8
TOTAL_SECTORS      = NUM_CYLINDERS * HEADS_PER_CYLINDER * SECTORS_PER_TRACK  # 256


class PhysicalPlatter:
    """Simulates raw magnetic storage — (cylinder, head, sector) → bytes."""

    def __init__(self):
        self._storage    = {}
        self.read_count  = 0
        self.write_count = 0

    def read_sector(self, c, h, s):
        self._check(c, h, s)
        self.read_count += 1
        return bytearray(self._storage.get((c, h, s), bytearray(SECTOR_SIZE)))

    def write_sector(self, c, h, s, data):
        self._check(c, h, s)
        assert len(data) <= SECTOR_SIZE
        self.write_count += 1
        buf = bytearray(SECTOR_SIZE)
        buf[:len(data)] = data
        self._storage[(c, h, s)] = buf

    def _check(self, c, h, s):
        assert 0 <= c < NUM_CYLINDERS,      f"Bad cylinder {c}"
        assert 0 <= h < HEADS_PER_CYLINDER, f"Bad head {h}"
        assert 0 <= s < SECTORS_PER_TRACK,  f"Bad sector {s}"

    def dump_geometry(self):
        print(f"\n[platter]  {NUM_CYLINDERS}cyl × {HEADS_PER_CYLINDER}heads × "
              f"{SECTORS_PER_TRACK}sec = {TOTAL_SECTORS} sectors × {SECTOR_SIZE}B "
              f"= {TOTAL_SECTORS * SECTOR_SIZE}B")
        print(f"  Physical reads={self.read_count}  writes={self.write_count}\n")


# =============================================================================
# SECTION 0B — DISK GEOMETRY (LBA ↔ CHS)
# =============================================================================

def lba_to_chs(lba):
    c = lba // (HEADS_PER_CYLINDER * SECTORS_PER_TRACK)
    h = (lba // SECTORS_PER_TRACK) % HEADS_PER_CYLINDER
    s = lba % SECTORS_PER_TRACK
    return c, h, s

def chs_to_lba(c, h, s):
    return (c * HEADS_PER_CYLINDER + h) * SECTORS_PER_TRACK + s


# =============================================================================
# SECTION 0C — DISK CONTROLLER
# =============================================================================

IO_TRACE = False

class DiskController:
    """LBA → CHS bridge.  virtio_disk.c in xv6."""

    def __init__(self, platter):
        self.platter = platter
        self.io_log  = []

    def read(self, lba):
        c, h, s = lba_to_chs(lba)
        if IO_TRACE:
            print(f"  [CTRL READ ] LBA={lba:>3} → C={c} H={h} S={s}")
        self.io_log.append(("READ ", lba, c, h, s))
        return self.platter.read_sector(c, h, s)

    def write(self, lba, data):
        c, h, s = lba_to_chs(lba)
        if IO_TRACE:
            print(f"  [CTRL WRITE] LBA={lba:>3} → C={c} H={h} S={s}  "
                  f"{bytes(data[:8]).hex()}...")
        self.io_log.append(("WRITE", lba, c, h, s))
        self.platter.write_sector(c, h, s, data)

    def dump_io_log(self, n=20):
        print(f"\n[iolog]  Last {min(n,len(self.io_log))} I/O operations:")
        print(f"  {'OP':<6} {'LBA':>4} {'CYL':>3} {'HEAD':>4} {'SEC':>3}  BYTE_OFF")
        for op, lba, c, h, s in self.io_log[-n:]:
            print(f"  {op:<6} {lba:>4} {c:>3} {h:>4} {s:>3}  {lba*SECTOR_SIZE}")
        print()

    def dump_disk_map(self):
        print("\n[diskmap]  Physical Disk  (role or . )")
        hdr = "  CYL  |"
        for h in range(HEADS_PER_CYLINDER):
            for s in range(SECTORS_PER_TRACK):
                hdr += f"H{h}S{s} "
        print(hdr)
        print("  -----+" + "-----" * HEADS_PER_CYLINDER * SECTORS_PER_TRACK)
        for c in range(NUM_CYLINDERS):
            row = f"  C{c:>3}  |"
            for h in range(HEADS_PER_CYLINDER):
                for s in range(SECTORS_PER_TRACK):
                    lba = chs_to_lba(c, h, s)
                    if (c, h, s) in self.platter._storage:
                        row += f" L{lba:<2} "
                    else:
                        row += "  .  "
            print(row)
        print()


# =============================================================================
# SECTION 0D — I/O TRACE
# =============================================================================

@contextlib.contextmanager
def trace_io(label=""):
    global IO_TRACE
    old, IO_TRACE = IO_TRACE, True
    print(f"\n  ┌─ TRACE: {label}")
    try:
        yield
    finally:
        IO_TRACE = old
        print(f"  └─ TRACE END: {label}\n")


# =============================================================================
# SECTION 1 — DISK LAYOUT CONSTANTS
# =============================================================================
#
#  xv6 reference: kernel/fs.h
#
#  Our disk is 256 blocks of 64 bytes each.
#  Layout mirrors xv6's mkfs output:
#
#  Block 0   : boot
#  Block 1   : superblock
#  Block 2   : log header  (struct logheader)
#  Block 3–6 : log data    (LOGSIZE = 4 blocks)
#  Block 7–8 : inode table (IPB=4 inodes/block, NINODES=32 → 8 blocks)
#  Block 9   : bitmap      (1 bit per data block)
#  Block 10–255: data blocks
#

BLOCK_SIZE    = SECTOR_SIZE   # 64 bytes
TOTAL_BLOCKS  = TOTAL_SECTORS # 256
FSMAGIC       = 0x10203040    # magic number identifying our filesystem

# Log
LOGSTART      = 2             # block where log header lives
LOGSIZE       = 8             # number of log data blocks (blocks 3–10)
MAXOPBLOCKS   = 8             # max blocks one transaction may write

# Inode table
INODE_START   = 7             # first inode block
NINODES       = 32            # total number of inodes
IPB           = 4             # inodes per block (BLOCK_SIZE / sizeof dinode = 64/16)
                              # dinode: mode(2)+nlink(2)+size(4)+direct[6](24)+indirect(4) = 36→pad to 16? 
                              # We use a 16-byte dinode so IPB=4 fits neatly

# Block bitmap
BMAP_START    = INODE_START + (NINODES // IPB)   # = 7 + 8 = block 15
                                                   # Wait — let's recalculate for clarity

# Recompute carefully so nothing overlaps:
# Log header:  block 2      (1 block)
# Log data:    blocks 3–6   (LOGSIZE=4 blocks)
# Inode table: blocks 7–14  (NINODES/IPB = 32/4 = 8 blocks)
# Bitmap:      block 15     (1 block, covers 256 blocks with 256 bits = 32 bytes → fits in 64B)
# Data:        blocks 16–255 (240 data blocks)

LOGSTART      = 2
LOGSIZE       = 8
INODE_START   = LOGSTART + 1 + LOGSIZE   # = 2+1+4 = 7
INODE_BLOCKS  = NINODES // IPB            # = 32/4 = 8 blocks
BMAP_START    = INODE_START + INODE_BLOCKS  # = 7+8 = 15
DATA_START    = BMAP_START + 1              # = 16

# Inode types — mirrors xv6 T_FILE, T_DIR, T_DEVICE
T_UNUSED = 0
T_FILE   = 1
T_DIR    = 2

# Reserved inode numbers
INUM_UNUSED = 0
INUM_ROOT   = 1

# On-disk inode (dinode) — 16 bytes so IPB = BLOCK_SIZE/DINODE_SIZE = 64/16 = 4
#
# Our dinode layout (matches xv6 struct dinode in spirit, scaled down):
#   type      : H (2 bytes) — T_UNUSED / T_FILE / T_DIR
#   nlink     : H (2 bytes) — hard link count
#   size      : I (4 bytes) — file size in bytes
#   addr      : I (4 bytes) — the ONE direct block pointer (NDIRECT=1)
#   indirect  : I (4 bytes) — indirect block pointer (0 = unused)
#   Total     : 2+2+4+4+4 = 16 bytes  ← IPB = 64/16 = 4 ✓
#
# An indirect block holds BLOCK_SIZE/4 = 16 block addresses,
# so max file size = (1 + 16) × 64 = 1088 bytes.
#
NDIRECT       = 1             # one direct block pointer per dinode
NINDIRECT     = BLOCK_SIZE // 4   # pointers per indirect block = 16
MAXFILE       = NDIRECT + NINDIRECT   # max blocks per file = 17

DINODE_FMT    = "HHIII"       # type(2) nlink(2) size(4) addr(4) indirect(4) = 16B
DINODE_SIZE   = struct.calcsize(DINODE_FMT)  # = 16

assert DINODE_SIZE == 16, f"DINODE_SIZE={DINODE_SIZE}, expected 16"
assert BLOCK_SIZE % DINODE_SIZE == 0
IPB = BLOCK_SIZE // DINODE_SIZE   # 64 // 16 = 4

# Directory entry — xv6 struct dirent: ushort inum(2) + char name[DIRSIZ=14] = 16 bytes
DIRSIZ        = 14
DIRENT_FMT    = f"H{DIRSIZ}s"
DIRENT_SIZE   = struct.calcsize(DIRENT_FMT)  # 2+14 = 16 bytes
assert DIRENT_SIZE == 16
DIRENTS_PER_BLOCK = BLOCK_SIZE // DIRENT_SIZE  # 64//16 = 4

# Superblock on-disk format — xv6 struct superblock
# magic(4) size(4) nblocks(4) ninodes(4) nlog(4) logstart(4) inodestart(4) bmapstart(4) = 32 bytes
SB_FMT  = "8I"
SB_SIZE = struct.calcsize(SB_FMT)  # 32 bytes


# =============================================================================
# SECTION 2 — RAW DISK I/O
# =============================================================================

_platter    = PhysicalPlatter()
_controller = DiskController(_platter)


def _raw_read(blockno):
    """Direct disk read — bypasses all caches.  Only bcache may call this."""
    return _controller.read(blockno)


def _raw_write(blockno, data):
    """Direct disk write — bypasses all caches.  Only log/bcache may call this."""
    buf = bytearray(BLOCK_SIZE)
    buf[:len(data)] = data
    _controller.write(blockno, buf)


# =============================================================================
# SECTION 2B — BUFFER CACHE  (kernel/bio.c)
# =============================================================================
#
#  xv6 bcache:  a doubly-linked list of struct buf, each holding one block.
#  Our bcache:  a Python dict with the same semantics.
#
#  Key xv6 functions mirrored:
#    bread(dev, blockno)        → bcache.bread(blockno)
#    bwrite(buf)                → bcache.bwrite(blockno, data)
#    brelse(buf)                → bcache.brelse(blockno)   [dec ref count]
#    bpin(buf) / bunpin(buf)    → bcache.pin / unpin
#
#  Ref count (b.refcnt in xv6):
#    Each cache entry has a ref_count.  A block with ref > 0 is "in use"
#    and cannot be evicted.  brelse decrements it.
#

NBUF = 30   # xv6 NBUF — max cached blocks


class BufEntry:
    """One slot in the buffer cache.  Mirrors xv6 struct buf."""
    __slots__ = ('data', 'dirty', 'refcnt', 'valid')
    def __init__(self, data):
        self.data   = bytearray(data)
        self.dirty  = False
        self.refcnt = 1       # starts at 1 because caller is using it
        self.valid  = True

class BufferCache:
    """
    xv6-style buffer cache.

    bread  : get a locked buffer containing block data (reads from disk on miss)
    bwrite : mark buffer dirty (schedule write to disk via log or direct)
    brelse : release hold on buffer (decrement refcnt)
    bpin   : prevent buffer eviction (xv6 bpin)
    bunpin : allow eviction again
    """

    def __init__(self):
        self._cache  = {}   # blockno → BufEntry
        self.hits    = 0
        self.misses  = 0
        self.flushes = 0

    def bread(self, blockno):
        """
        Return a buffer for blockno.  Reads from disk on cache miss.
        Caller must call brelse(blockno) when done.
        Returns bytearray (copy).
        """
        if blockno in self._cache:
            e = self._cache[blockno]
            e.refcnt += 1
            self.hits += 1
            if IO_TRACE: print(f"  [BCACHE HIT ] blk={blockno} ref={e.refcnt}")
            return bytearray(e.data)

        self.misses += 1
        raw = _raw_read(blockno)
        e   = BufEntry(raw)
        self._cache[blockno] = e
        if IO_TRACE: print(f"  [BCACHE MISS] blk={blockno} loaded from disk")
        return bytearray(e.data)

    def bwrite(self, blockno, data):
        """
        Write data into cache, mark dirty.
        In xv6 this is only called from the log layer (log_write ultimately
        calls bwrite to persist to log).  We expose it directly for clarity.
        """
        buf = bytearray(BLOCK_SIZE)
        buf[:len(data)] = data
        if blockno in self._cache:
            self._cache[blockno].data  = buf
            self._cache[blockno].dirty = True
        else:
            e = BufEntry(buf)
            e.dirty = True
            self._cache[blockno] = e
        if IO_TRACE: print(f"  [BCACHE DIRTY] blk={blockno}")

    def brelse(self, blockno):
        """Release hold on a buffer.  Decrements refcnt.  Mirrors xv6 brelse."""
        if blockno in self._cache:
            self._cache[blockno].refcnt -= 1

    def bpin(self, blockno):
        """Pin a buffer so it won't be evicted.  Mirrors xv6 bpin."""
        if blockno in self._cache:
            self._cache[blockno].refcnt += 1

    def bunpin(self, blockno):
        """Unpin a buffer.  Mirrors xv6 bunpin."""
        if blockno in self._cache:
            self._cache[blockno].refcnt -= 1

    def bflush(self, blockno):
        """Flush one dirty block to disk and clear dirty flag."""
        e = self._cache.get(blockno)
        if e and e.dirty:
            _raw_write(blockno, e.data)
            e.dirty = False
            self.flushes += 1
            if IO_TRACE: print(f"  [BCACHE FLUSH] blk={blockno}")

    def bsync(self):
        """Flush all dirty blocks to disk.  Mirrors Linux writeback."""
        n = 0
        for blockno, e in self._cache.items():
            if e.dirty:
                _raw_write(blockno, e.data)
                e.dirty = False
                n += 1
        self.flushes += n
        if n: print(f"[bsync]  Flushed {n} dirty block(s)")

    def invalidate(self, blockno):
        """Evict a block from cache (used after bfree)."""
        self._cache.pop(blockno, None)

    def dump(self):
        dirty = sum(1 for e in self._cache.values() if e.dirty)
        print(f"\n[bcache]  {len(self._cache)} entries  "
              f"hits={self.hits} misses={self.misses} "
              f"dirty={dirty} flushes={self.flushes}")
        print(f"  {'BLK':>5}  {'REF':>4}  {'DIRTY':>5}  HEX[0:16]")
        for blk in sorted(self._cache):
            e = self._cache[blk]
            print(f"  {blk:>5}  {e.refcnt:>4}  {'YES' if e.dirty else 'no':>5}  "
                  f"{e.data[:16].hex()}")
        print()


bcache = BufferCache()


# Thin wrappers so filesystem code uses these names (matching v3 API)
def disk_read(blockno):
    return bcache.bread(blockno)

def disk_write(blockno, data):
    bcache.bwrite(blockno, data)


# =============================================================================
# SECTION 2C — LOG LAYER  (kernel/log.c)
# =============================================================================
#
#  The log layer provides crash safety via write-ahead logging (WAL).
#
#  How it works (mirrors xv6 log.c exactly):
#
#  1. begin_op()
#     Mark the start of a filesystem transaction.
#     Increments outstanding operation count.
#
#  2. log_write(blockno)
#     Record that block blockno will be modified.
#     Instead of writing directly to its home location, the log notes it.
#     The block's current cached data is what will be committed.
#
#  3. end_op()
#     Decrement outstanding count.
#     When count reaches 0: commit the transaction.
#     Commit writes:
#       a) Each logged block's data to a log data block on disk
#       b) The log header (with block numbers + count) to disk
#       c) Then copies each log data block to its home location
#       d) Clears the log header (count=0) — transaction complete
#
#  Why it matters:
#    If power fails between (b) and (d), on reboot the kernel replays the
#    log (sees header count > 0 → copies log blocks to their homes again).
#    If power fails before (b) is complete, the partial log is ignored.
#    In both cases the on-disk filesystem remains consistent.
#
#  Log disk layout:
#    Block LOGSTART (2)    : log header { n_committed, block_nos[LOGSIZE] }
#    Block LOGSTART+1 (3)  : log data 0
#    Block LOGSTART+2 (4)  : log data 1
#    Block LOGSTART+3 (5)  : log data 2
#    Block LOGSTART+4 (6)  : log data 3
#
#  Log header on-disk format (xv6 struct logheader):
#    n     : int  — number of committed blocks
#    block : int[LOGSIZE]  — home block numbers
#

LOG_HDR_FMT  = f"I{LOGSIZE}I"     # n + LOGSIZE block numbers
LOG_HDR_SIZE = struct.calcsize(LOG_HDR_FMT)   # 4 + 4*4 = 20 bytes, fits in block 2


class Log:
    """
    Write-ahead log.  Mirrors xv6 struct log and kernel/log.c.

    begin_op()    → start a transaction
    log_write(b)  → record block b as modified in this transaction
    end_op()      → commit when all ops complete
    recover()     → replay on startup if unclean shutdown
    """

    def __init__(self):
        self.outstanding   = 0         # active begin_op() calls not yet ended
        self.committing    = False     # True while commit is in progress
        self.pending_writes = []       # blocks logged this transaction (list of blockno)
        self.log_count     = 0        # total transactions committed (for stats)

    # ----------------------------------------------------------------
    # begin_op  — xv6 begin_op()
    # ----------------------------------------------------------------
    def begin_op(self):
        """
        Start a filesystem operation (transaction).
        In xv6 this acquires the log lock and waits if the log is full
        or if another commit is in progress.
        """
        self.outstanding += 1

    # ----------------------------------------------------------------
    # log_write  — xv6 log_write()
    # ----------------------------------------------------------------
    def log_write(self, blockno):
        """
        Tell the log that blockno has been (or will be) modified.
        The block must already be in the buffer cache with its new data.

        In xv6, log_write() also pins the buffer (bpin) so it won't be
        evicted from the cache before commit.  We mirror this.
        """
        if blockno not in self.pending_writes:
            if len(self.pending_writes) >= LOGSIZE:
                raise OSError(f"Log full!  Max {LOGSIZE} blocks per transaction.")
            self.pending_writes.append(blockno)
            bcache.bpin(blockno)   # pin so it stays in cache until commit

    # ----------------------------------------------------------------
    # end_op  — xv6 end_op()
    # ----------------------------------------------------------------
    def end_op(self):
        """
        End one filesystem operation.
        When the last outstanding op ends, commit the transaction.
        """
        self.outstanding -= 1
        if self.outstanding == 0 and self.pending_writes:
            self._commit()

    # ----------------------------------------------------------------
    # _commit  — xv6 commit()
    # ----------------------------------------------------------------
    def _commit(self):
        """
        Write the transaction to disk in crash-safe order:
          1. Write each modified block to a log data block
          2. Write the log header (makes the transaction durable)
          3. Install: copy each log data block to its home location
          4. Clear the log header (transaction complete, log reusable)
        """
        self.committing = True
        blocks = list(self.pending_writes)

        if IO_TRACE:
            print(f"  [LOG COMMIT] writing {len(blocks)} blocks: {blocks}")

        # Step 1: write modified blocks into log data area
        for i, blockno in enumerate(blocks):
            log_block = LOGSTART + 1 + i   # log data block i
            data = bcache.bread(blockno)   # get current (modified) data
            bcache.brelse(blockno)
            _raw_write(log_block, data)    # write to log area on disk

        # Step 2: write log header — this is the "commit point"
        self._write_log_header(blocks)

        # Step 3: install — copy log blocks to their home locations
        self._install_trans(blocks)

        # Step 4: clear log header
        self._write_log_header([])

        # Unpin all buffers
        for blockno in blocks:
            bcache.bunpin(blockno)

        self.pending_writes.clear()
        self.log_count += 1
        self.committing = False

    def _write_log_header(self, blocks):
        """Write log header block.  This is the atomic commit point."""
        n = len(blocks)
        # Pad block list to LOGSIZE entries
        padded = list(blocks) + [0] * (LOGSIZE - len(blocks))
        raw = struct.pack(LOG_HDR_FMT, n, *padded)
        buf = bytearray(BLOCK_SIZE)
        buf[:len(raw)] = raw
        _raw_write(LOGSTART, buf)

    def _install_trans(self, blocks):
        """Copy each log data block to its home disk location."""
        for i, blockno in enumerate(blocks):
            log_block = LOGSTART + 1 + i
            data = _raw_read(log_block)
            _raw_write(blockno, data)      # home location write
            # Also update cache so in-memory view is current
            bcache.bwrite(blockno, data)
            bcache.bflush(blockno)

    # ----------------------------------------------------------------
    # recover  — xv6 recover_from_log() called at mount
    # ----------------------------------------------------------------
    def recover(self):
        """
        On mount: read log header.  If n > 0, replay the log.
        This recovers from a crash that happened after the commit point
        but before install completed.
        """
        raw = _raw_read(LOGSTART)
        n, *block_nos = struct.unpack(LOG_HDR_FMT, raw[:LOG_HDR_SIZE])
        blocks = block_nos[:n]
        if blocks:
            print(f"[log] recovering {n} uncommitted block(s): {blocks}")
            self._install_trans(blocks)
            self._write_log_header([])
        else:
            if IO_TRACE: print(f"  [LOG] clean — no recovery needed")

    def dump(self):
        raw = _raw_read(LOGSTART)
        n, *block_nos = struct.unpack(LOG_HDR_FMT, raw[:LOG_HDR_SIZE])
        print(f"\n[log]  outstanding={self.outstanding}  "
              f"pending={self.pending_writes}  "
              f"committed_transactions={self.log_count}")
        print(f"  On-disk log header: n={n}  blocks={list(block_nos[:n])}\n")


log = Log()


# =============================================================================
# SECTION 3 — SUPERBLOCK ON DISK  (kernel/fs.c: readsb)
# =============================================================================
#
#  xv6 struct superblock lives at block 1.
#  Fields: magic, size (total blocks), nblocks (data blocks),
#          ninodes, nlog, logstart, inodestart, bmapstart.
#
#  On mount, readsb() reads block 1 and populates the in-memory superblock.
#  We do the same: mkfs() writes it, mount() reads it.
#

class Superblock:
    """
    Filesystem superblock — lives at disk block 1.
    Mirrors xv6 struct superblock (kernel/fs.h).
    """
    MAGIC = FSMAGIC

    def __init__(self):
        self.magic      = self.MAGIC
        self.size       = TOTAL_BLOCKS
        self.nblocks    = TOTAL_BLOCKS - DATA_START
        self.ninodes    = NINODES
        self.nlog       = LOGSIZE
        self.logstart   = LOGSTART
        self.inodestart = INODE_START
        self.bmapstart  = BMAP_START

    def write_to_disk(self):
        """Serialise and write superblock to block 1."""
        raw = struct.pack(SB_FMT,
                          self.magic, self.size, self.nblocks, self.ninodes,
                          self.nlog, self.logstart, self.inodestart, self.bmapstart)
        buf = bytearray(BLOCK_SIZE)
        buf[:len(raw)] = raw
        _raw_write(1, buf)

    @classmethod
    def read_from_disk(cls):
        """Deserialise superblock from block 1.  Mirrors xv6 readsb()."""
        raw  = _raw_read(1)
        vals = struct.unpack(SB_FMT, raw[:SB_SIZE])
        sb   = cls.__new__(cls)
        (sb.magic, sb.size, sb.nblocks, sb.ninodes,
         sb.nlog, sb.logstart, sb.inodestart, sb.bmapstart) = vals
        if sb.magic != cls.MAGIC:
            raise OSError(f"Bad superblock magic: {sb.magic:#x} (expected {cls.MAGIC:#x})")
        return sb

    def dump(self):
        print(f"\n[superblock]  (disk block 1)")
        print(f"  magic      = {self.magic:#010x}")
        print(f"  size       = {self.size} blocks")
        print(f"  nblocks    = {self.nblocks} data blocks")
        print(f"  ninodes    = {self.ninodes}")
        print(f"  nlog       = {self.nlog}  logstart={self.logstart}")
        print(f"  inodestart = {self.inodestart}")
        print(f"  bmapstart  = {self.bmapstart}")
        print(f"  datastart  = {DATA_START}")
        print()


# Global in-memory superblock (loaded at mount)
_sb: Superblock = None  # type: ignore


# =============================================================================
# SECTION 3B — BLOCK BITMAP ALLOCATOR  (kernel/fs.c: balloc / bfree)
# =============================================================================
#
#  xv6 uses a bitmap block to track which data blocks are free.
#  Each bit corresponds to one block: 0=free, 1=allocated.
#
#  Block BMAP_START holds the bitmap.
#  With 64-byte blocks × 8 bits = 512 bits — enough for 512 blocks.
#  We have 256 total blocks, so the whole bitmap fits comfortably.
#
#  The bitmap covers ALL blocks (0..255), but only data blocks (16..255)
#  are ever allocated by balloc.  Blocks 0..15 are permanently "in use"
#  (they are part of the fixed filesystem metadata regions).
#

def _bitmap_alloc():
    """
    Find and allocate a free data block.  Mirrors xv6 balloc().
    Returns block number of the allocated block.
    Sets the corresponding bitmap bit to 1.
    Calls log_write on the bitmap block.
    """
    bitmap = bytearray(disk_read(BMAP_START))

    for b in range(DATA_START, TOTAL_BLOCKS):
        byte_idx = b // 8
        bit_idx  = b % 8
        if not (bitmap[byte_idx] & (1 << bit_idx)):
            # Found a free block
            bitmap[byte_idx] |= (1 << bit_idx)
            disk_write(BMAP_START, bitmap)
            log.log_write(BMAP_START)
            # Zero out the newly allocated block
            disk_write(b, bytearray(BLOCK_SIZE))
            log.log_write(b)
            bcache.bflush(b)
            if IO_TRACE: print(f"  [BALLOC] allocated block {b}")
            return b

    raise OSError("No free data blocks — filesystem full!")


def _bitmap_free(b):
    """
    Free data block b.  Mirrors xv6 bfree().
    Clears the corresponding bitmap bit to 0.
    """
    assert b >= DATA_START, f"Cannot free metadata block {b}"
    bitmap = bytearray(disk_read(BMAP_START))
    byte_idx = b // 8
    bit_idx  = b % 8
    assert (bitmap[byte_idx] & (1 << bit_idx)), f"Block {b} was not allocated!"
    bitmap[byte_idx] &= ~(1 << bit_idx)
    disk_write(BMAP_START, bitmap)
    log.log_write(BMAP_START)
    bcache.invalidate(b)
    if IO_TRACE: print(f"  [BFREE] freed block {b}")


def _free_block_count():
    """Count free data blocks from bitmap (for df)."""
    bitmap = bytearray(disk_read(BMAP_START))
    free = 0
    for b in range(DATA_START, TOTAL_BLOCKS):
        byte_idx = b // 8
        bit_idx  = b % 8
        if not (bitmap[byte_idx] & (1 << bit_idx)):
            free += 1
    return free


# =============================================================================
# SECTION 4 — INODE LAYER  (kernel/fs.c)
# =============================================================================
#
#  xv6 on-disk inode layout (struct dinode, kernel/fs.h):
#    short type (2)         — T_UNUSED / T_FILE / T_DIR
#    short nlink (2)        — hard link count
#    uint  size (4)         — file size in bytes
#    uint  addrs[NDIRECT+1] — direct block addrs + one indirect block addr
#
#  In our version: NDIRECT=2, so dinode = type(2)+nlink(2)+size(4)+addr0(4)+addr1(4)+indirect(4) = 20 bytes
#  But we defined DINODE_SIZE=16 above with DINODE_FMT="HHI2I".
#  Let's reconcile: "HHI2I" = H(2)+H(2)+I(4)+2×I(8) = 16 bytes. Good.
#  So NDIRECT=2 (two direct slots: addr0 and addr1), plus one indirect pointer.
#
#  The inode table spans blocks INODE_START to INODE_START+INODE_BLOCKS-1.
#  Within each block, IPB=4 inodes are packed.
#
#  inode inum → block: INODE_START + (inum-1) // IPB
#  inode inum → offset within block: ((inum-1) % IPB) * DINODE_SIZE
#
#  xv6 functions mirrored:
#    ialloc(type)   → alloc an inode of given type
#    iupdate(ip)    → write in-memory inode back to disk (log_write)
#    iget(inum)     → get/cache an inode
#    iput(ip)       → release inode; free if nlink==0 and ref==0
#    bmap(ip, bn)   → map logical block number to disk block (alloc if needed)
#    itrunc(ip)     → free all data blocks of an inode
#    readi(ip, ...)  → read from inode
#    writei(ip, ...) → write to inode
#

class Inode:
    """
    In-memory inode.  Mirrors xv6 struct inode (kernel/file.h).

    Fields match the on-disk dinode plus runtime fields:
      ref  : reference count (how many get_inode calls haven't been iput'd)
      dirty: True if in-memory differs from disk
    """
    def __init__(self, inum):
        self.inum  = inum
        self.type  = T_UNUSED
        self.nlink = 0
        self.size  = 0
        self.addrs = [0] * NDIRECT   # direct block pointers
        self.indirect = 0            # indirect block pointer
        self.ref   = 0
        self.dirty = False

    def is_file(self): return self.type == T_FILE
    def is_dir(self):  return self.type == T_DIR
    def is_free(self): return self.type == T_UNUSED

    def __repr__(self):
        t = {T_UNUSED:"UNUSED", T_FILE:"FILE", T_DIR:"DIR"}.get(self.type, "?")
        return (f"Inode(inum={self.inum}, {t}, nlink={self.nlink}, "
                f"size={self.size}, addrs={self.addrs}, indirect={self.indirect})")


# In-memory inode cache — inum → Inode
_icache: dict = {}


def _inode_block(inum):
    """Block number containing inode inum.  xv6: IBLOCK(i,sb)."""
    return INODE_START + (inum - 1) // IPB

def _inode_offset(inum):
    """Byte offset of inode inum within its block."""
    return ((inum - 1) % IPB) * DINODE_SIZE


def _pack_dinode(inode):
    """Serialise in-memory inode to DINODE_SIZE bytes.  xv6 iupdate."""
    return struct.pack(DINODE_FMT,
                       inode.type, inode.nlink, inode.size,
                       inode.addrs[0],      # the single direct block
                       inode.indirect)


def _unpack_dinode(inum, block_data, offset):
    """Deserialise DINODE_SIZE bytes from block_data at offset.  xv6 iget."""
    raw = block_data[offset: offset + DINODE_SIZE]
    t, nlink, size, a0, indirect = struct.unpack(DINODE_FMT, raw)
    ip = Inode(inum)
    ip.type = t; ip.nlink = nlink; ip.size = size
    ip.addrs = [a0]          # NDIRECT=1 direct block
    ip.indirect = indirect
    return ip


def iget(inum):
    """
    Return an in-memory inode for inum, loading from disk if needed.
    Increments ref count.  Mirrors xv6 iget().
    Caller must call iput() when done.
    """
    if inum in _icache:
        ip = _icache[inum]
        ip.ref += 1
        if IO_TRACE: print(f"  [IGET hit ] inum={inum} ref={ip.ref}")
        return ip

    # Load from disk
    blk    = _inode_block(inum)
    off    = _inode_offset(inum)
    raw    = disk_read(blk)
    bcache.brelse(blk)
    ip     = _unpack_dinode(inum, raw, off)
    ip.ref = 1
    _icache[inum] = ip
    if IO_TRACE: print(f"  [IGET miss] inum={inum} from blk={blk} off={off}")
    return ip


def iput(ip):
    """
    Release a reference to inode ip.  Mirrors xv6 iput().
    If ref reaches 0 and nlink==0 → truncate and free the inode.
    """
    ip.ref -= 1
    if ip.ref == 0 and ip.nlink == 0:
        # No directory entries and no open fds → free the inode
        _itrunc(ip)
        ip.type = T_UNUSED
        _iupdate(ip)
        _icache.pop(ip.inum, None)


def _iupdate(ip):
    """
    Write in-memory inode back to its disk block.  Mirrors xv6 iupdate().
    Marks the block dirty in the buffer cache and logs the write.
    """
    blk  = _inode_block(ip.inum)
    off  = _inode_offset(ip.inum)
    raw  = bytearray(disk_read(blk))
    bcache.brelse(blk)
    raw[off: off + DINODE_SIZE] = _pack_dinode(ip)
    disk_write(blk, raw)
    log.log_write(blk)
    ip.dirty = False


def ialloc(itype):
    """
    Allocate a new inode of given type.  Mirrors xv6 ialloc().
    Scans the inode table for a T_UNUSED slot, initialises it, and returns it.
    """
    for inum in range(1, NINODES + 1):
        blk = _inode_block(inum)
        off = _inode_offset(inum)
        raw = bytearray(disk_read(blk))
        bcache.brelse(blk)
        t, = struct.unpack_from("H", raw, off)
        if t == T_UNUSED:
            # Found a free slot — zero it out and set type
            raw[off: off + DINODE_SIZE] = bytes(DINODE_SIZE)
            struct.pack_into("H", raw, off, itype)
            disk_write(blk, raw)
            log.log_write(blk)
            # Return via iget so it goes into icache
            ip = iget(inum)
            ip.type  = itype
            ip.nlink = 0
            ip.size  = 0
            ip.addrs = [0] * NDIRECT
            ip.indirect = 0
            return ip
    raise OSError("No free inodes — inode table exhausted!")


def _bmap(ip, bn):
    """
    Return the disk block for logical block number bn of inode ip.
    Allocates a block if it doesn't exist yet.
    Mirrors xv6 bmap().

    bn=0..NDIRECT-1  → direct blocks (ip.addrs[bn])
    bn=NDIRECT..     → indirect block (ip.indirect points to a block of addresses)
    """
    if bn < NDIRECT:
        if ip.addrs[bn] == 0:
            b = _bitmap_alloc()
            ip.addrs[bn] = b
            _iupdate(ip)
        return ip.addrs[bn]

    # Indirect
    bn -= NDIRECT
    if bn >= NINDIRECT:
        raise OSError(f"File too large: block {bn + NDIRECT} exceeds MAXFILE={MAXFILE}")

    # Allocate indirect block if needed
    if ip.indirect == 0:
        ib = _bitmap_alloc()
        ip.indirect = ib
        _iupdate(ip)

    # Read indirect block, find the address
    ind_data = bytearray(disk_read(ip.indirect))
    bcache.brelse(ip.indirect)
    addr = struct.unpack_from("I", ind_data, bn * 4)[0]
    if addr == 0:
        b = _bitmap_alloc()
        struct.pack_into("I", ind_data, bn * 4, b)
        disk_write(ip.indirect, ind_data)
        log.log_write(ip.indirect)
        addr = b
    return addr


def _itrunc(ip):
    """
    Free all data blocks of inode ip.  Mirrors xv6 itrunc().
    Called when nlink reaches 0.
    """
    # Free direct blocks
    for i in range(NDIRECT):
        if ip.addrs[i]:
            _bitmap_free(ip.addrs[i])
            ip.addrs[i] = 0

    # Free indirect block contents then the indirect block itself
    if ip.indirect:
        ind_data = bytearray(disk_read(ip.indirect))
        bcache.brelse(ip.indirect)
        for i in range(NINDIRECT):
            addr = struct.unpack_from("I", ind_data, i * 4)[0]
            if addr:
                _bitmap_free(addr)
        _bitmap_free(ip.indirect)
        ip.indirect = 0

    ip.size = 0
    _iupdate(ip)


def readi(ip, offset, n):
    """
    Read n bytes from inode ip starting at offset.  Mirrors xv6 readi().
    Returns bytes.
    """
    if offset > ip.size:
        return b""
    if offset + n > ip.size:
        n = ip.size - offset

    result = bytearray()
    tot = 0
    while tot < n:
        # Which logical block?
        logical_bn = (offset + tot) // BLOCK_SIZE
        disk_bn    = _bmap(ip, logical_bn)
        blk_data   = bytearray(disk_read(disk_bn))
        bcache.brelse(disk_bn)
        # Offset within this block
        blk_off = (offset + tot) % BLOCK_SIZE
        to_read = min(n - tot, BLOCK_SIZE - blk_off)
        result += blk_data[blk_off: blk_off + to_read]
        tot += to_read

    return bytes(result)


def writei(ip, offset, data):
    """
    Write data to inode ip starting at offset.  Mirrors xv6 writei().
    Extends file if writing past current end.
    Returns number of bytes written.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")

    if offset + len(data) > MAXFILE * BLOCK_SIZE:
        raise OSError(f"Write would exceed MAXFILE limit ({MAXFILE * BLOCK_SIZE}B)")

    tot = 0
    while tot < len(data):
        logical_bn = (offset + tot) // BLOCK_SIZE
        disk_bn    = _bmap(ip, logical_bn)
        blk_data   = bytearray(disk_read(disk_bn))
        bcache.brelse(disk_bn)
        blk_off  = (offset + tot) % BLOCK_SIZE
        to_write = min(len(data) - tot, BLOCK_SIZE - blk_off)
        blk_data[blk_off: blk_off + to_write] = data[tot: tot + to_write]
        disk_write(disk_bn, blk_data)
        log.log_write(disk_bn)
        tot += to_write

    if offset + len(data) > ip.size:
        ip.size = offset + len(data)
        _iupdate(ip)

    return len(data)


# =============================================================================
# SECTION 5 — DIRECTORY LAYER  (kernel/fs.c: dirlookup / dirlink)
# =============================================================================
#
#  xv6 directory entry (struct dirent, kernel/fs.h):
#    ushort inum (2 bytes)
#    char   name[DIRSIZ=14] (14 bytes)
#    Total: 16 bytes = DIRENT_SIZE
#
#  dirlookup(dp, name, poff)  → find name in dir inode dp, return inode
#  dirlink(dp, name, inum)    → add (name, inum) entry to dir inode dp
#

def dirlookup(dp, name):
    """
    Search directory inode dp for an entry named 'name'.
    Returns (inode, byte_offset_in_dir) or (None, 0).
    Mirrors xv6 dirlookup().
    """
    assert dp.is_dir(), f"inode {dp.inum} is not a directory"

    for off in range(0, dp.size, DIRENT_SIZE):
        raw = readi(dp, off, DIRENT_SIZE)
        if len(raw) < DIRENT_SIZE:
            break
        inum, name_bytes = struct.unpack(DIRENT_FMT, raw)
        if inum == 0:
            continue
        entry_name = name_bytes.rstrip(b"\x00").decode("ascii", errors="replace")
        if entry_name == name:
            return iget(inum), off

    return None, 0


def dirlink(dp, name, inum):
    """
    Add a new directory entry (name, inum) to directory dp.
    Reuses deleted slots (inum==0).
    Mirrors xv6 dirlink().
    """
    # Check name doesn't already exist
    existing, _ = dirlookup(dp, name)
    if existing is not None:
        iput(existing)
        raise FileExistsError(f"'{name}' already exists in directory")

    # Find a free slot or append
    off = 0
    for off in range(0, dp.size, DIRENT_SIZE):
        raw = readi(dp, off, DIRENT_SIZE)
        if len(raw) < DIRENT_SIZE:
            break
        inum_slot, _ = struct.unpack(DIRENT_FMT, raw)
        if inum_slot == 0:
            break   # reuse this empty slot
    else:
        off = dp.size  # append at end

    # Write the new entry
    name_enc = name.encode("ascii")[:DIRSIZ]
    raw = struct.pack(DIRENT_FMT, inum, name_enc)
    writei(dp, off, raw)
    log.log_write(_bmap(dp, off // BLOCK_SIZE))   # ensure data block is logged


# =============================================================================
# SECTION 6 — PATH LOOKUP  (kernel/fs.c: namei / nameiparent)
# =============================================================================
#
#  xv6 implements two path resolution functions:
#    namei(path)          → return inode for path (or error)
#    nameiparent(path, name) → return parent dir inode; put leaf name in 'name'
#
#  Both walk the path component by component using skipelem().
#

def _skipelem(path):
    """
    Like xv6 skipelem(): split next component from rest of path.
    Returns (component, rest) or ("", "") when done.
    """
    path = path.lstrip("/")
    if not path:
        return "", ""
    slash = path.find("/")
    if slash < 0:
        return path, ""
    return path[:slash], path[slash:]


def namei(path):
    """
    Resolve path to its inode.  Returns inode (ref'd) or raises.
    Mirrors xv6 namei().
    Caller must iput() the returned inode.
    """
    ip, _ = _namex(path, parent=False)
    return ip


def nameiparent(path):
    """
    Resolve path to its parent directory inode and return (parent_inode, leaf_name).
    Mirrors xv6 nameiparent().
    Caller must iput() the returned inode.
    """
    ip, name = _namex(path, parent=True)
    return ip, name


def _namex(path, parent):
    """
    Core path resolution.  Mirrors xv6 namex().
    If parent=False: return (inode_of_path, "")
    If parent=True:  return (inode_of_parent_dir, leaf_name)
    """
    if path.startswith("/"):
        ip = iget(INUM_ROOT)
    else:
        raise ValueError("Relative paths not supported — use absolute paths")

    while True:
        name, rest = _skipelem(path.lstrip("/") if path else "")
        if not name:
            # No more components
            if parent:
                iput(ip)
                raise ValueError(f"nameiparent called on root")
            return ip, ""

        # If parent=True and there are no more components after name → return now
        next_name, _ = _skipelem(rest)
        if parent and not next_name:
            return ip, name

        # Look up name in current directory
        if not ip.is_dir():
            iput(ip)
            raise NotADirectoryError(f"'{name}' is not a directory")

        next_ip, _ = dirlookup(ip, name)
        iput(ip)

        if next_ip is None:
            raise FileNotFoundError(f"'{name}' not found")

        ip   = next_ip
        path = rest


# =============================================================================
# SECTION 7 — FILESYSTEM OPERATIONS  (kernel/fs.c + kernel/sysfile.c)
# =============================================================================
#
#  High-level filesystem operations exposed to users.
#  Each one wraps its work in begin_op() / end_op() so it is logged.
#
#  Functions mirror xv6 sys_* in kernel/sysfile.c:
#    sys_mkdir  → fs_mkdir
#    sys_open   → fs_create / fd_open
#    sys_link   → fs_link
#    sys_unlink → fs_unlink
#

class FileSystem:
    """
    High-level filesystem operations.
    All mutation functions wrap their work in begin_op / end_op.
    """

    # ------------------------------------------------------------------
    # mkfs — format the disk
    # ------------------------------------------------------------------
    def mkfs(self):
        """
        Format the disk.  Mirrors xv6 mkfs.c.
        Writes: superblock, blank inode table, blank bitmap, root directory.
        """
        _icache.clear()

        # Write superblock
        sb = Superblock()
        sb.write_to_disk()

        # Clear log header
        log._write_log_header([])

        # Blank out inode blocks
        blank = bytearray(BLOCK_SIZE)
        for blk in range(INODE_START, INODE_START + INODE_BLOCKS):
            _raw_write(blk, blank)

        # Blank bitmap — mark metadata blocks (0..DATA_START-1) as allocated
        bitmap = bytearray(BLOCK_SIZE)
        for b in range(DATA_START):   # blocks 0..15 are "in use"
            bitmap[b // 8] |= (1 << (b % 8))
        _raw_write(BMAP_START, bitmap)

        # Populate buffer cache with what we just wrote
        for blk in range(0, DATA_START):
            bcache.bwrite(blk, _raw_read(blk))

        # Create root directory inode 1
        log.begin_op()
        root = ialloc(T_DIR)
        assert root.inum == INUM_ROOT, f"Root inode must be 1, got {root.inum}"
        root.nlink = 1
        _iupdate(root)
        # Add . and .. entries
        dirlink(root, ".", INUM_ROOT)
        dirlink(root, "..", INUM_ROOT)
        iput(root)
        log.end_op()

        print(f"[mkfs]  Formatted {TOTAL_BLOCKS}-block filesystem")
        print(f"  Superblock at block 1  (magic {FSMAGIC:#010x})")
        print(f"  Log        at blocks {LOGSTART}–{LOGSTART+LOGSIZE}")
        print(f"  Inodes     at blocks {INODE_START}–{INODE_START+INODE_BLOCKS-1}"
              f"  ({NINODES} inodes, {IPB} per block)")
        print(f"  Bitmap     at block  {BMAP_START}")
        print(f"  Data       at blocks {DATA_START}–{TOTAL_BLOCKS-1}"
              f"  ({TOTAL_BLOCKS-DATA_START} blocks)\n")

    # ------------------------------------------------------------------
    # mount — read superblock, recover log
    # ------------------------------------------------------------------
    def mount(self):
        global _sb
        _sb = Superblock.read_from_disk()
        log.recover()

    # ------------------------------------------------------------------
    # mkdir
    # ------------------------------------------------------------------
    def mkdir(self, path):
        """Create directory at path.  Mirrors xv6 sys_mkdir."""
        log.begin_op()
        try:
            dp, name = nameiparent(path)
            ip = ialloc(T_DIR)
            ip.nlink = 1
            _iupdate(ip)
            dirlink(ip, ".",  ip.inum)
            dirlink(ip, "..", dp.inum)
            dirlink(dp, name, ip.inum)
            dp.nlink += 1
            _iupdate(dp)
            iput(ip)
            iput(dp)
        except Exception:
            log.end_op()
            raise
        log.end_op()
        print(f"[mkdir]  {path}")

    # ------------------------------------------------------------------
    # create (file or dir) — internal helper
    # ------------------------------------------------------------------
    def _create(self, path, itype):
        """
        Allocate a new inode for path.  Mirrors xv6 create() in sysfile.c.
        Returns the new inode (ref'd).  Caller must iput().
        """
        dp, name = nameiparent(path)

        # Does it already exist?
        existing, _ = dirlookup(dp, name)
        if existing is not None:
            iput(dp)
            iput(existing)
            raise FileExistsError(f"{path} already exists")

        ip = ialloc(itype)
        ip.nlink = 1
        _iupdate(ip)

        if itype == T_DIR:
            dp.nlink += 1
            _iupdate(dp)
            dirlink(ip, ".",  ip.inum)
            dirlink(ip, "..", dp.inum)

        dirlink(dp, name, ip.inum)
        iput(dp)
        return ip   # caller must iput

    # ------------------------------------------------------------------
    # touch
    # ------------------------------------------------------------------
    def touch(self, path):
        """Create an empty file."""
        log.begin_op()
        try:
            ip = self._create(path, T_FILE)
            inum = ip.inum
            iput(ip)
        except Exception:
            log.end_op()
            raise
        log.end_op()
        print(f"[touch]  {path}  (inum={inum}, iblk={_inode_block(inum)})")
        return inum

    # ------------------------------------------------------------------
    # write_file — write bytes to a path
    # ------------------------------------------------------------------
    def write_file(self, path, data):
        """Overwrite file at path with data.  Uses writei."""
        if isinstance(data, str):
            data = data.encode("utf-8")

        log.begin_op()
        try:
            ip = namei(path)
            if not ip.is_file():
                iput(ip)
                raise IsADirectoryError(f"{path} is a directory")
            _itrunc(ip)          # free existing blocks
            writei(ip, 0, data)
            iput(ip)
        except Exception:
            log.end_op()
            raise
        log.end_op()
        print(f"[write]  {path}  ({len(data)}B)")

    # ------------------------------------------------------------------
    # read_file — read all bytes from a path
    # ------------------------------------------------------------------
    def read_file(self, path):
        """Read full contents of file at path."""
        ip = namei(path)
        if not ip.is_file():
            iput(ip)
            raise IsADirectoryError(f"{path} is a directory")
        data = readi(ip, 0, ip.size)
        iput(ip)
        return data.decode("utf-8", errors="replace")

    # ------------------------------------------------------------------
    # link — hard link
    # ------------------------------------------------------------------
    def link(self, old_path, new_path):
        """Create hard link.  Mirrors xv6 sys_link."""
        log.begin_op()
        try:
            ip = namei(old_path)
            if ip.is_dir():
                iput(ip)
                log.end_op()
                raise IsADirectoryError("Cannot hard-link a directory")
            ip.nlink += 1
            _iupdate(ip)

            dp, name = nameiparent(new_path)
            dirlink(dp, name, ip.inum)
            iput(dp)
            iput(ip)
        except Exception:
            log.end_op()
            raise
        log.end_op()
        print(f"[link]   {old_path} → {new_path}")

    # ------------------------------------------------------------------
    # unlink — remove a name
    # ------------------------------------------------------------------
    def unlink(self, path):
        """
        Unlink a name.  Mirrors xv6 sys_unlink.
        Frees inode only when nlink==0 AND ref==0 (no open fds).
        """
        log.begin_op()
        try:
            dp, name = nameiparent(path)
            if name in (".", ".."):
                iput(dp)
                log.end_op()
                raise ValueError("Cannot unlink . or ..")

            ip, off = dirlookup(dp, name)
            if ip is None:
                iput(dp)
                log.end_op()
                raise FileNotFoundError(f"{path} not found")

            if ip.is_dir():
                # Only allow rmdir of empty directories
                if ip.size > 2 * DIRENT_SIZE:  # more than just . and ..
                    iput(ip); iput(dp)
                    log.end_op()
                    raise OSError(f"{path}: directory not empty")
                dp.nlink -= 1
                _iupdate(dp)

            # Zero out the directory entry
            empty_entry = struct.pack(DIRENT_FMT, 0, b"\x00" * DIRSIZ)
            writei(dp, off, empty_entry)
            log.log_write(_bmap(dp, off // BLOCK_SIZE))

            ip.nlink -= 1
            _iupdate(ip)

            # iput handles freeing when ref+nlink both reach 0
            iput(ip)
            iput(dp)
        except Exception:
            log.end_op()
            raise
        log.end_op()
        print(f"[unlink] {path}")

    # ------------------------------------------------------------------
    # ls
    # ------------------------------------------------------------------
    def ls(self, path="/"):
        """List directory contents."""
        ip = namei(path)
        if not ip.is_dir():
            iput(ip)
            raise NotADirectoryError(f"{path} is not a directory")

        entries = []
        for off in range(0, ip.size, DIRENT_SIZE):
            raw = readi(ip, off, DIRENT_SIZE)
            if len(raw) < DIRENT_SIZE:
                break
            inum_e, name_b = struct.unpack(DIRENT_FMT, raw)
            if inum_e == 0:
                continue
            name = name_b.rstrip(b"\x00").decode("ascii", errors="replace")
            ei   = iget(inum_e)
            t    = {T_FILE:"FILE", T_DIR:"DIR "}.get(ei.type, "????")
            fds  = sum(1 for f in _fd_table._table.values() if f['inum'] == inum_e)
            entries.append((inum_e, t, ei.size, fds, name))
            iput(ei)

        iput(ip)
        blk = _inode_block(ip.inum)
        print(f"\n[ls]  {path}  (inum={ip.inum}, iblk={blk}):")
        print(f"  {'INUM':>4}  {'TYPE':<5}  {'SIZE':>6}  {'FDS':>3}  NAME")
        print(f"  {'----':>4}  {'-----':<5}  {'------':>6}  {'---':>3}  ----")
        for inum_e, t, size, fds, name in sorted(entries, key=lambda e: e[4]):
            print(f"  {inum_e:>4}  {t:<5}  {size:>6}  {fds:>3}  {name}")
        print()

    # ------------------------------------------------------------------
    # stat
    # ------------------------------------------------------------------
    def stat(self, path):
        """Print full inode information."""
        ip = namei(path)
        t  = {T_FILE:"Regular File", T_DIR:"Directory"}.get(ip.type, "?")
        open_fds = [fd for fd, f in _fd_table._table.items() if f['inum'] == ip.inum]
        blk = _inode_block(ip.inum)
        off = _inode_offset(ip.inum)

        print(f"\n[stat]  {path}")
        print(f"  inum        = {ip.inum}  (disk block {blk}, offset {off})")
        print(f"  type        = {t}")
        print(f"  nlink       = {ip.nlink}")
        print(f"  size        = {ip.size} bytes")
        print(f"  open fds    = {open_fds if open_fds else 'none'}")
        print(f"  direct blks = {ip.addrs}")
        print(f"  indirect    = {ip.indirect}")
        for i, a in enumerate(ip.addrs):
            if a:
                c, h, s = lba_to_chs(a)
                print(f"    direct[{i}]  LBA={a} → C={c} H={h} S={s} "
                      f"(byte {a*SECTOR_SIZE})")
        if ip.indirect:
            c, h, s = lba_to_chs(ip.indirect)
            print(f"    indirect   LBA={ip.indirect} → C={c} H={h} S={s}")
        print()
        iput(ip)

    # ------------------------------------------------------------------
    # df
    # ------------------------------------------------------------------
    def df(self):
        free_b = _free_block_count()
        free_i = sum(1 for inum in range(1, NINODES + 1)
                     if inum not in _icache or _icache[inum].type == T_UNUSED)
        print(f"\n[df]  Filesystem statistics:")
        print(f"  Total blocks   : {TOTAL_BLOCKS}  (data: {TOTAL_BLOCKS-DATA_START})")
        print(f"  Free data blks : {free_b}")
        print(f"  Used data blks : {TOTAL_BLOCKS-DATA_START-free_b}")
        print(f"  Buffer cache   : hits={bcache.hits} misses={bcache.misses} "
              f"dirty={sum(1 for e in bcache._cache.values() if e.dirty)}")
        print(f"  Phys I/O       : reads={_platter.read_count} "
              f"writes={_platter.write_count}")
        print(f"  Log commits    : {log.log_count}")
        print(f"  Open fds       : {len(_fd_table._table)}\n")

    # ------------------------------------------------------------------
    # dump_inodes
    # ------------------------------------------------------------------
    def dump_inodes(self):
        print(f"\n[inodes]  Inode table (disk blocks {INODE_START}–"
              f"{INODE_START+INODE_BLOCKS-1}, {IPB} inodes/block):")
        print(f"  {'INUM':>4}  {'BLK':>4}  {'OFF':>4}  {'TYPE':<5}  "
              f"{'NLINK':>5}  {'SIZE':>6}  ADDRS")
        print(f"  {'----':>4}  {'----':>4}  {'----':>4}  {'-----':<5}  "
              f"{'-----':>5}  {'------':>6}  -----")
        for inum in range(1, NINODES + 1):
            blk = _inode_block(inum)
            off = _inode_offset(inum)
            raw = disk_read(blk)
            bcache.brelse(blk)
            t_val, = struct.unpack_from("H", raw, off)
            if t_val != T_UNUSED:
                ip = iget(inum)
                t  = {T_FILE:"FILE", T_DIR:"DIR "}.get(ip.type,"?")
                print(f"  {inum:>4}  {blk:>4}  {off:>4}  {t:<5}  "
                      f"{ip.nlink:>5}  {ip.size:>6}  "
                      f"{ip.addrs}+ind={ip.indirect}")
                iput(ip)
        print()

    def geometry(self): _platter.dump_geometry()
    def diskmap(self):  _controller.dump_disk_map()
    def iolog(self, n=20): _controller.dump_io_log(n)
    def cache(self):    bcache.dump()
    def logdump(self):  log.dump()
    def sbdump(self):   Superblock.read_from_disk().dump()

    def explain_block(self, blockno):
        c, h, s  = lba_to_chs(blockno)
        in_cache = blockno in bcache._cache
        dirty    = in_cache and bcache._cache[blockno].dirty
        on_disk  = (c, h, s) in _platter._storage

        # Determine filesystem role
        if blockno == 0:    role = "boot block"
        elif blockno == 1:  role = "superblock"
        elif blockno == LOGSTART: role = "log header"
        elif LOGSTART < blockno <= LOGSTART + LOGSIZE: role = f"log data {blockno-LOGSTART}"
        elif INODE_START <= blockno < INODE_START+INODE_BLOCKS:
            first_inum = (blockno - INODE_START) * IPB + 1
            role = f"inode block (inums {first_inum}–{first_inum+IPB-1})"
        elif blockno == BMAP_START: role = "block bitmap"
        elif blockno >= DATA_START: role = "data block"
        else: role = "unknown"

        print(f"\n[explain]  Block {blockno}:")
        print(f"  Role        : {role}")
        print(f"  LBA → CHS   : {blockno} → C={c} H={h} S={s}")
        print(f"  Byte offset : {blockno * SECTOR_SIZE}")
        print(f"  In bcache   : {'YES' + (' (DIRTY)' if dirty else '') if in_cache else 'no'}")
        print(f"  On platter  : {'yes' if on_disk else 'not yet (zeros)'}")
        if on_disk:
            data = disk_read(blockno)
            bcache.brelse(blockno)
            printable = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data)
            print(f"  Hex[0:32]   : {data[:32].hex()}")
            print(f"  ASCII[0:32] : {printable[:32]}")
        print()


# =============================================================================
# SECTION 8 — FILE DESCRIPTOR TABLE  (kernel/file.c)
# =============================================================================
#
#  xv6 struct file (kernel/file.h):
#    int   type  (FD_NONE / FD_PIPE / FD_INODE / FD_DEVICE)
#    int   ref   (reference count — for dup())
#    char  readable, writable
#    struct inode *ip
#    uint  off   (byte offset)
#
#  xv6 ftable: a global array of NFILE=100 struct file.
#
#  Our implementation:
#    _fd_table maps int fd → { inum, offset, readable, writable }
#    open()  → allocate fd, iget inode
#    read()  → readi at offset
#    write() → writei at offset
#    close() → iput; if nlink==0 and ref==0 → inode freed (deferred free)
#    dup()   → duplicate fd (independent offset)
#

NFILE = 20   # max open files (xv6 uses 100)

class FDTable:
    """
    Open file descriptor table.
    Mirrors xv6 ftable + per-process ofile[] array.
    """
    def __init__(self):
        self._table   = {}   # fd → {inum, offset, readable, writable, ref}
        self._next_fd = 3    # 0=stdin,1=stdout,2=stderr

    def open(self, path, flags="r"):
        """
        Open a file.  flags: "r"=read, "w"=write/create, "rw"=both.
        Mirrors xv6 sys_open().
        Returns integer file descriptor.
        """
        readable = "r" in flags
        writable = "w" in flags

        log.begin_op()
        try:
            try:
                ip = namei(path)
            except FileNotFoundError:
                if not writable:
                    log.end_op()
                    raise
                # O_CREATE path
                dp, name = nameiparent(path)
                ip = ialloc(T_FILE)
                ip.nlink = 1
                _iupdate(ip)
                dirlink(dp, name, ip.inum)
                iput(dp)

            if ip.is_dir() and writable:
                iput(ip)
                log.end_op()
                raise IsADirectoryError(f"{path} is a directory")
        except Exception:
            log.end_op()
            raise
        log.end_op()

        if len(self._table) >= NFILE:
            iput(ip)
            raise OSError("Too many open files")

        fd = self._next_fd
        self._next_fd += 1
        self._table[fd] = {
            'inum': ip.inum, 'offset': 0,
            'readable': readable, 'writable': writable,
            'ref': 1
        }
        # Keep inode ref alive (don't iput until close)
        # ip.ref is already 1 from iget inside namei/ialloc

        print(f"[open]   fd={fd}  {path}  inum={ip.inum}  flags={flags}")
        return fd

    def read(self, fd, n=None):
        """Read n bytes from fd.  Mirrors xv6 fileread()."""
        entry = self._table.get(fd)
        if not entry: raise OSError(f"fd {fd} not open")
        if not entry['readable']: raise PermissionError(f"fd {fd} not readable")

        ip = iget(entry['inum'])
        if n is None: n = ip.size - entry['offset']
        data = readi(ip, entry['offset'], n)
        entry['offset'] += len(data)
        iput(ip)

        print(f"[read]   fd={fd}  {len(data)}B  "
              f"offset {entry['offset']-len(data)}→{entry['offset']}")
        return data.decode("utf-8", errors="replace")

    def write(self, fd, data):
        """Write data to fd at current offset.  Mirrors xv6 filewrite()."""
        if isinstance(data, str): data = data.encode("utf-8")
        entry = self._table.get(fd)
        if not entry: raise OSError(f"fd {fd} not open")
        if not entry['writable']: raise PermissionError(f"fd {fd} not writable")

        ip = iget(entry['inum'])
        log.begin_op()
        try:
            n = writei(ip, entry['offset'], data)
        except Exception:
            log.end_op()
            iput(ip)
            raise
        log.end_op()
        entry['offset'] += n
        iput(ip)
        print(f"[write]  fd={fd}  {n}B  offset→{entry['offset']}")

    def seek(self, fd, offset, whence=0):
        """
        Reposition fd offset.  whence: 0=SEEK_SET, 1=SEEK_CUR, 2=SEEK_END.
        Mirrors lseek(2).
        """
        entry = self._table.get(fd)
        if not entry: raise OSError(f"fd {fd} not open")
        ip = iget(entry['inum'])
        if   whence == 0: new_off = offset
        elif whence == 1: new_off = entry['offset'] + offset
        elif whence == 2: new_off = ip.size + offset
        else: raise ValueError("whence must be 0, 1, or 2")
        iput(ip)
        if new_off < 0: raise OSError("Seek before start of file")
        entry['offset'] = new_off
        print(f"[seek]   fd={fd}  offset→{new_off}")

    def dup(self, fd):
        """
        Duplicate a file descriptor.  Mirrors xv6 sys_dup().
        Returns a new fd pointing to same inode, independent offset.
        """
        entry = self._table.get(fd)
        if not entry: raise OSError(f"fd {fd} not open")
        new_fd = self._next_fd
        self._next_fd += 1
        # Share inode — new fd holds its own ref (iget without iput).
        # open() already holds one ref; dup() adds another one for the new fd.
        ip = iget(entry['inum'])   # bumps ref — kept alive for new_fd
        self._table[new_fd] = dict(entry)
        self._table[new_fd]['offset'] = 0   # independent offset
        print(f"[dup]    fd={fd} → new fd={new_fd}  inum={ip.inum}  ref={ip.ref}")
        return new_fd

    def close(self, fd):
        """
        Close fd.  Mirrors xv6 fileclose().
        Calls iput() on the inode — if nlink==0 and ref drops to 0,
        iput() frees the inode and its blocks (deferred-free path).
        """
        entry = self._table.pop(fd, None)
        if not entry: raise OSError(f"fd {fd} not open")

        inum = entry['inum']
        # The fd holds exactly one inode ref (from open/dup's iget).
        # Release it.  If nlink==0 and ref drops to 0, iput frees the inode.
        if inum in _icache:
            ip = _icache[inum]
            iput(ip)   # release the fd's held reference
            print(f"[close]  fd={fd}  inum={inum}  "
                  f"nlink={ip.nlink}  ref_after={ip.ref}")
        else:
            # Inode was already evicted (shouldn't normally happen with ref>0)
            print(f"[close]  fd={fd}  inum={inum}  (inode not in cache)")

    def dump(self):
        print(f"\n[fds]  Open file table ({len(self._table)}/{NFILE}):")
        if not self._table:
            print("  (none)")
        else:
            print(f"  {'FD':>4}  {'INUM':>4}  {'FLAGS':>8}  {'OFFSET':>7}")
            for fd, e in sorted(self._table.items()):
                flags = ("r" if e['readable'] else "-") + ("w" if e['writable'] else "-")
                print(f"  {fd:>4}  {e['inum']:>4}  {flags:>8}  {e['offset']:>7}")
        print()


_fd_table = FDTable()


# =============================================================================
# SECTION 9 — DEMO
# =============================================================================

def run_demo():
    global _sb
    print("=" * 70)
    print("  Mini-UNIX-FS  xv6  —  Complete xv6-Faithful Filesystem")
    print("=" * 70)

    fs = FileSystem()
    fs.mkfs()
    fs.mount()

    print("\n--- Phase 0: Superblock and disk layout ---")
    fs.sbdump()

    print("--- Phase 1: Create directories ---")
    fs.mkdir("/home")
    fs.mkdir("/home/alice")
    fs.ls("/")

    print("--- Phase 2: Create and write files ---")
    fs.touch("/home/alice/notes.txt")
    fs.write_file("/home/alice/notes.txt",
                  "Hello from xv6 Mini-FS!\nThis uses the log layer.\n")
    fs.ls("/home/alice")

    print("--- Phase 3: stat — full inode info with physical location ---")
    fs.stat("/home/alice/notes.txt")

    print("--- Phase 4: Inode table on disk ---")
    fs.dump_inodes()

    print("--- Phase 5: Buffer cache and log ---")
    fs.cache()
    fs.logdump()

    print("--- Phase 6: File descriptor operations ---")
    fd1 = _fd_table.open("/home/alice/notes.txt", "r")
    chunk = _fd_table.read(fd1, 12)
    print(f"  Read 12B: {repr(chunk)}")
    _fd_table.seek(fd1, 0)
    full = _fd_table.read(fd1)
    print(f"  Full read: {repr(full)}")
    _fd_table.close(fd1)

    print("--- Phase 7: write via fd (writei path) ---")
    fd2 = _fd_table.open("/home/alice/notes.txt", "rw")
    _fd_table.write(fd2, "OVERWRITTEN via fd\n")
    _fd_table.seek(fd2, 0)
    updated = _fd_table.read(fd2)
    print(f"  Content after write: {repr(updated)}")
    _fd_table.close(fd2)

    print("--- Phase 8: Hard links ---")
    fs.link("/home/alice/notes.txt", "/home/alice/notes.bak")
    fs.stat("/home/alice/notes.txt")    # nlink should be 2

    print("--- Phase 9: Unlink while open (deferred-free) ---")
    fd3 = _fd_table.open("/home/alice/notes.txt", "r")
    fs.unlink("/home/alice/notes.txt")  # nlink → 1 (backup still exists)
    fs.unlink("/home/alice/notes.bak")  # nlink → 0 but fd3 still open
    data = _fd_table.read(fd3)
    print(f"  Still readable after both unlinks: {repr(data)}")
    _fd_table.close(fd3)               # now truly freed

    print("--- Phase 10: Indirect block test (large file) ---")
    fs.touch("/bigfile.txt")
    big_data = "ABCDEFGH" * 20         # 160 bytes > NDIRECT*BLOCK_SIZE=128B
    fs.write_file("/bigfile.txt", big_data)
    fs.stat("/bigfile.txt")            # should show indirect block
    content = fs.read_file("/bigfile.txt")
    print(f"  Read back {len(content)} chars, matches: {content == big_data}")
    fs.unlink("/bigfile.txt")

    print("--- Phase 11: Log replay simulation ---")
    print("  Simulating crash: dirty blocks in cache, log has committed data")
    fs.touch("/crash_test.txt")
    fs.write_file("/crash_test.txt", "Written before crash\n")
    log.begin_op()
    ip = namei("/crash_test.txt")
    writei(ip, 0, b"Partially written")
    log.log_write(ip.addrs[0])
    # Don't call end_op — simulate crash mid-transaction
    iput(ip)
    # The log header on disk still has the previous committed state
    print("  Replaying log (as kernel does on reboot)...")
    log.recover()
    recovered = fs.read_file("/crash_test.txt")
    print(f"  Recovered content: {repr(recovered)}")

    print("\n--- Phase 12: Final state ---")
    fs.df()
    fs.dump_inodes()
    fs.diskmap()


# =============================================================================
# SECTION 10 — INTERACTIVE SHELL
# =============================================================================

def interactive_shell(fs):
    print("\n" + "=" * 70)
    print("  Mini-UNIX-FS xv6  Interactive Shell")
    print("  Type 'help' for commands, 'exit' to quit")
    print("=" * 70 + "\n")

    cwd = "/"

    HELP = """
  Filesystem  (xv6-layer operations — all logged):
    ls   [path]            List directory
    mkdir  <path>          Create directory
    touch  <path>          Create empty file
    write  <path> <text>   Write text to file  (overwrites)
    cat    <path>          Read file
    stat   <path>          Full inode info + physical location
    link   <old> <new>     Hard link
    unlink <path>          Remove name (may defer inode free)
    df                     Filesystem statistics
    inodes                 Dump inode table with disk locations
    pwd / cd <path>        Navigate
    sb                     Show superblock

  File Descriptors  (xv6 fileread/filewrite path):
    open  <path> [r|w|rw]  Open file, print fd number
    read  <fd> [N]         Read N bytes from fd
    fwrite <fd> <text>     Write text to fd at current position
    seek  <fd> <off> [w]   Seek fd (whence: 0=SET 1=CUR 2=END)
    dup   <fd>             Duplicate fd
    close <fd>             Close fd
    fds                    Show open file table

  Storage layers:
    cache                  Buffer cache state
    sync                   Flush dirty blocks to disk
    log                    Log state and on-disk header
    lba  <N>               Decode block N: LBA → CHS + role
    explain <N>            Full block decode: cache + platter + hex
    diskmap                Physical disk map
    iolog [N]              Last N I/O operations
    geometry               Physical disk geometry

  help / exit
"""
    print(HELP)

    while True:
        try:
            line = input(f"xv6fs:{cwd}$ ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        if not line:
            continue

        parts = line.split(maxsplit=1)
        cmd   = parts[0].lower()
        args  = parts[1].strip() if len(parts) > 1 else ""

        def resolve(p):
            if not p: return cwd
            if p.startswith("/"): return p
            return ("/" + p) if cwd == "/" else (cwd + "/" + p)

        try:
            # Filesystem commands
            if cmd == "exit":
                print("Bye!"); break
            elif cmd == "help":
                print(HELP)
            elif cmd == "pwd":
                print(cwd)
            elif cmd == "cd":
                t = resolve(args) if args else "/"
                ip = namei(t)
                if not ip.is_dir():
                    iput(ip); print(f"  Not a directory: {t}")
                else:
                    cwd = t; iput(ip)
            elif cmd == "ls":
                fs.ls(resolve(args) if args else cwd)
            elif cmd == "mkdir":
                if not args: print("  Usage: mkdir <path>"); continue
                fs.mkdir(resolve(args))
            elif cmd == "touch":
                if not args: print("  Usage: touch <path>"); continue
                fs.touch(resolve(args))
            elif cmd == "write":
                p2 = args.split(maxsplit=1)
                if len(p2) < 2: print("  Usage: write <path> <text>"); continue
                fs.write_file(resolve(p2[0]), p2[1] + "\n")
            elif cmd == "cat":
                if not args: print("  Usage: cat <path>"); continue
                print(fs.read_file(resolve(args)), end="")
            elif cmd == "stat":
                if not args: print("  Usage: stat <path>"); continue
                fs.stat(resolve(args))
            elif cmd == "link":
                p2 = args.split()
                if len(p2) < 2: print("  Usage: link <old> <new>"); continue
                fs.link(resolve(p2[0]), resolve(p2[1]))
            elif cmd == "unlink":
                if not args: print("  Usage: unlink <path>"); continue
                fs.unlink(resolve(args))
            elif cmd == "df":
                fs.df()
            elif cmd == "inodes":
                fs.dump_inodes()
            elif cmd == "sb":
                fs.sbdump()

            # File descriptor commands
            elif cmd == "open":
                p2 = args.split()
                if not p2: print("  Usage: open <path> [r|w|rw]"); continue
                flags = p2[1] if len(p2) > 1 else "r"
                fd = _fd_table.open(resolve(p2[0]), flags)
                print(f"  → fd={fd}")
            elif cmd == "read":
                p2 = args.split()
                if not p2 or not p2[0].isdigit():
                    print("  Usage: read <fd> [N]"); continue
                n   = int(p2[1]) if len(p2) > 1 and p2[1].isdigit() else None
                txt = _fd_table.read(int(p2[0]), n)
                print(repr(txt))
            elif cmd == "fwrite":
                p2 = args.split(maxsplit=1)
                if len(p2) < 2 or not p2[0].isdigit():
                    print("  Usage: fwrite <fd> <text>"); continue
                _fd_table.write(int(p2[0]), p2[1] + "\n")
            elif cmd == "seek":
                p2 = args.split()
                if len(p2) < 2: print("  Usage: seek <fd> <off> [whence]"); continue
                whence = int(p2[2]) if len(p2) > 2 else 0
                _fd_table.seek(int(p2[0]), int(p2[1]), whence)
            elif cmd == "dup":
                if not args.isdigit(): print("  Usage: dup <fd>"); continue
                new_fd = _fd_table.dup(int(args))
                print(f"  → new fd={new_fd}")
            elif cmd == "close":
                if not args.isdigit(): print("  Usage: close <fd>"); continue
                _fd_table.close(int(args))
            elif cmd == "fds":
                _fd_table.dump()

            # Storage layer commands
            elif cmd == "cache":
                bcache.dump()
            elif cmd == "sync":
                bcache.bsync()
            elif cmd == "log":
                log.dump()
            elif cmd == "diskmap":
                fs.diskmap()
            elif cmd == "iolog":
                n = int(args) if args.isdigit() else 20
                fs.iolog(n)
            elif cmd == "geometry":
                fs.geometry()
            elif cmd == "explain":
                if not args.isdigit(): print("  Usage: explain <N>"); continue
                fs.explain_block(int(args))
            elif cmd == "lba":
                if not args.isdigit(): print("  Usage: lba <N>"); continue
                lba = int(args)
                c, h, s = lba_to_chs(lba)
                if   lba == 0:                                  role = "boot"
                elif lba == 1:                                  role = "superblock"
                elif lba == LOGSTART:                           role = "log header"
                elif LOGSTART < lba <= LOGSTART+LOGSIZE:        role = f"log data {lba-LOGSTART}"
                elif INODE_START <= lba < INODE_START+INODE_BLOCKS:
                    first = (lba-INODE_START)*IPB+1
                    role  = f"inodes {first}–{first+IPB-1}"
                elif lba == BMAP_START:                         role = "block bitmap"
                elif lba >= DATA_START:                         role = "data block"
                else:                                           role = "unknown"
                print(f"\n  LBA {lba} → C={c} H={h} S={s}  "
                      f"byte={lba*SECTOR_SIZE}  role={role}\n")
            else:
                print(f"  Unknown: '{cmd}'  (type 'help')")

        except (FileNotFoundError, FileExistsError, NotADirectoryError,
                IsADirectoryError, PermissionError, OSError, ValueError) as e:
            print(f"  Error: {e}")
        except Exception as e:
            import traceback
            print(f"  Unexpected error: {e}")
            traceback.print_exc()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import sys

    fs = FileSystem()
    fs.mkfs()
    fs.mount()

    if "--shell" in sys.argv:
        interactive_shell(fs)
    else:
        run_demo()
        print("\n" + "=" * 70)
        print("  Demo complete.  Launching interactive shell...")
        print("  Prompt: xv6fs:/$ ")
        print("  Try: mkdir /test  touch /test/a.txt  write /test/a.txt hello")
        print("       open /test/a.txt r  read <fd>  close <fd>")
        print("       explain 1  lba 7  log  cache  diskmap")
        print("=" * 70)
        interactive_shell(fs)

"""
=============================================================================
  Mini-UNIX-FS  v2  —  UNIX Filesystem + Physical Disk Abstraction
=============================================================================

  NEW in v2:
    SECTION 0A — Physical Platter (the actual spinning magnetic disk)
    SECTION 0B — Disk Geometry (CHS: Cylinders, Heads, Sectors)
    SECTION 0C — Disk Controller (translates LBA block numbers to CHS)
    SECTION 0D — Disk I/O Log (every read/write is traced end-to-end)

  Everything that existed before (SECTION 1–9) is unchanged.
  The only change: disk_read() / disk_write() now go THROUGH the controller,
  so you can see the full journey from:

      filesystem  →  block number  →  CHS address  →  physical platter bytes

  How a real hard disk works (simplified):

      Platter  = spinning magnetic disk.  Multiple platters on one spindle.
      Track    = one circular ring on a platter surface.
      Cylinder = all tracks at the same radius across all platter surfaces.
      Head     = read/write arm.  One head per platter surface.
      Sector   = smallest addressable unit on a track (= our BLOCK_SIZE).

  CHS addressing:
      Every sector on the disk has a unique address:  (Cylinder, Head, Sector)
      The disk controller uses this to physically position the arm.

  LBA (Logical Block Addressing):
      The OS uses a simpler flat address: block 0, 1, 2, ... N
      The disk controller translates LBA → CHS internally.
      Formula:
          cylinder = LBA  //  (HEADS_PER_CYLINDER × SECTORS_PER_TRACK)
          head     = (LBA //  SECTORS_PER_TRACK) % HEADS_PER_CYLINDER
          sector   = LBA  %   SECTORS_PER_TRACK

  This file simulates ALL of these layers so you can trace a write like:
      write_file("/notes.txt", "hello")
        → filesystem allocates block 42
        → disk_write(block_no=42, data)
        → controller: LBA 42 → Cylinder 2, Head 1, Sector 2
        → platter: platter[2][1][2] = bytearray("hello...")

=============================================================================
"""

import struct


# =============================================================================
# SECTION 0A — PHYSICAL PLATTER
# =============================================================================
#
#  A real hard disk platter is a spinning aluminium disk coated with a
#  magnetic material.  Data is stored as tiny magnetised regions.
#
#  We model the platter's storage as a 3-dimensional array:
#
#      platter_storage[cylinder][head][sector] = bytearray(SECTOR_SIZE)
#
#  Think of it like:
#      cylinder  = which "ring" from the outside edge inward   (like a tree ring)
#      head      = which surface of which platter (top/bottom of each disk)
#      sector    = which slice of that ring (like slices of a pie)
#
#  A real disk might have:
#      ~50,000 cylinders
#      2–8 heads (1 per platter surface)
#      ~1000 sectors per track
#
#  Ours is tiny for visibility:
#      8 cylinders
#      4 heads
#      8 sectors per track
#      Total sectors = 8 × 4 × 8 = 256  ← matches TOTAL_BLOCKS exactly
#

SECTOR_SIZE        = 64    # bytes per sector (= BLOCK_SIZE, must match)
NUM_CYLINDERS      = 8     # how many cylinder rings on the platter
HEADS_PER_CYLINDER = 4     # how many read/write heads (platter surfaces)
SECTORS_PER_TRACK  = 8     # how many sectors per track (per head per cylinder)

TOTAL_SECTORS = NUM_CYLINDERS * HEADS_PER_CYLINDER * SECTORS_PER_TRACK
# = 8 × 4 × 8 = 256  ← must equal TOTAL_BLOCKS below


class PhysicalPlatter:
    """
    Simulates the raw magnetic storage of a hard disk platter.

    Real platter: magnetic regions on spinning aluminium disks.
    Our platter:  a 3D Python dict indexed by (cylinder, head, sector).

    The platter knows NOTHING about filesystems, inodes, or blocks.
    It only knows: "store these bytes at this physical location."
    """

    def __init__(self):
        # 3D storage: [cylinder][head][sector] → bytearray(SECTOR_SIZE)
        # Stored as a flat dict of (c,h,s) tuples for simplicity.
        # Unwritten sectors read as zeros (like a freshly degaussed disk).
        self._storage = {}

        # Track how many physical reads/writes have happened
        self.read_count  = 0
        self.write_count = 0

    def read_sector(self, cylinder, head, sector):
        """
        Physically read one sector from the platter.

        On a real disk this means:
          1. Seek the arm to the correct cylinder  (mechanical movement)
          2. Wait for the platter to rotate to the right sector  (rotational latency)
          3. Read the magnetic signal as the sector passes under the head

        Here: just look up the dict.
        """
        self._validate_address(cylinder, head, sector)
        self.read_count += 1
        key = (cylinder, head, sector)
        if key not in self._storage:
            return bytearray(SECTOR_SIZE)   # unwritten sector = all zeros
        return bytearray(self._storage[key])  # return a copy

    def write_sector(self, cylinder, head, sector, data):
        """
        Physically write one sector to the platter.

        On a real disk this means:
          1. Seek the arm to the correct cylinder
          2. Wait for the correct sector to rotate under the head
          3. Flip the magnetic polarity of the surface to encode the data

        Here: just store in the dict.
        """
        self._validate_address(cylinder, head, sector)
        assert len(data) <= SECTOR_SIZE, "Data exceeds sector size!"
        self.write_count += 1
        buf = bytearray(SECTOR_SIZE)
        buf[:len(data)] = data
        self._storage[(cylinder, head, sector)] = buf

    def _validate_address(self, cylinder, head, sector):
        """Guard against out-of-range addresses."""
        if not (0 <= cylinder < NUM_CYLINDERS):
            raise ValueError(f"Cylinder {cylinder} out of range (0..{NUM_CYLINDERS-1})")
        if not (0 <= head < HEADS_PER_CYLINDER):
            raise ValueError(f"Head {head} out of range (0..{HEADS_PER_CYLINDER-1})")
        if not (0 <= sector < SECTORS_PER_TRACK):
            raise ValueError(f"Sector {sector} out of range (0..{SECTORS_PER_TRACK-1})")

    def dump_geometry(self):
        """Print the physical disk geometry — educational overview."""
        print("\n[platter]  Physical Disk Geometry:")
        print(f"  Cylinders        : {NUM_CYLINDERS}")
        print(f"  Heads/cylinder   : {HEADS_PER_CYLINDER}")
        print(f"  Sectors/track    : {SECTORS_PER_TRACK}")
        print(f"  Sector size      : {SECTOR_SIZE} bytes")
        print(f"  Total sectors    : {TOTAL_SECTORS}")
        print(f"  Total capacity   : {TOTAL_SECTORS * SECTOR_SIZE} bytes  "
              f"({TOTAL_SECTORS * SECTOR_SIZE // 1024} KB)")
        print(f"  Physical reads   : {self.read_count}")
        print(f"  Physical writes  : {self.write_count}")
        print()


# =============================================================================
# SECTION 0B — DISK GEOMETRY (CHS ↔ LBA TRANSLATION)
# =============================================================================
#
#  The filesystem thinks in "block numbers" (LBA = Logical Block Address).
#  Block 0, block 1, block 2 ... block 255.
#
#  The physical platter thinks in (Cylinder, Head, Sector) tuples.
#
#  The disk controller translates between these two views.
#
#  LBA → CHS formula:
#
#      cylinder = LBA  //  (HEADS_PER_CYLINDER × SECTORS_PER_TRACK)
#      head     = (LBA //  SECTORS_PER_TRACK)  %  HEADS_PER_CYLINDER
#      sector   = LBA  %   SECTORS_PER_TRACK
#
#  CHS → LBA formula (inverse):
#
#      LBA = (cylinder × HEADS_PER_CYLINDER + head) × SECTORS_PER_TRACK + sector
#
#  Example with our geometry (4 heads, 8 sectors/track):
#
#      LBA 0   →  C=0, H=0, S=0   (very first sector)
#      LBA 7   →  C=0, H=0, S=7   (last sector of track 0)
#      LBA 8   →  C=0, H=1, S=0   (first sector of head 1)
#      LBA 31  →  C=0, H=3, S=7   (last sector of cylinder 0)
#      LBA 32  →  C=1, H=0, S=0   (first sector of cylinder 1)
#      LBA 255 →  C=7, H=3, S=7   (very last sector)
#

def lba_to_chs(lba):
    """
    Convert a Logical Block Address (LBA) to a physical (Cylinder, Head, Sector).

    This is the core translation the disk controller performs on every I/O.
    The filesystem only ever sees LBA (=block numbers).
    The platter only ever sees CHS.
    This function is the bridge.
    """
    cylinder = lba // (HEADS_PER_CYLINDER * SECTORS_PER_TRACK)
    head     = (lba // SECTORS_PER_TRACK) % HEADS_PER_CYLINDER
    sector   = lba % SECTORS_PER_TRACK
    return cylinder, head, sector


def chs_to_lba(cylinder, head, sector):
    """Inverse of lba_to_chs.  Useful for diagnostics."""
    return (cylinder * HEADS_PER_CYLINDER + head) * SECTORS_PER_TRACK + sector


def explain_lba(lba):
    """Print a human-readable breakdown of an LBA address. Educational helper."""
    c, h, s = lba_to_chs(lba)
    print(f"  LBA {lba:>3}  →  Cylinder {c}, Head {h}, Sector {s}  "
          f"(byte offset on disk: {lba * SECTOR_SIZE})")


# =============================================================================
# SECTION 0C — DISK CONTROLLER
# =============================================================================
#
#  The disk controller is the hardware chip that sits between the OS and the
#  physical platters.  In a real disk (SATA/NVMe), it:
#
#    1. Receives a command from the OS:  READ block 42
#    2. Translates LBA 42 → CHS using the geometry
#    3. Positions the read/write arm (seek)
#    4. Waits for the correct sector to rotate under the head
#    5. Reads or writes the magnetic data
#    6. Returns data (or confirmation) to the OS
#
#  Our controller does the same thing in software:
#    - Translates LBA → CHS
#    - Calls PhysicalPlatter.read_sector() or write_sector()
#    - Optionally logs the operation so you can see the full trace
#

# I/O logging toggle: set to True to see every physical I/O
IO_TRACE = False   # flip to True for full trace output


class DiskController:
    """
    Simulates the disk controller (ATA/SATA controller in real hardware).

    Responsibilities:
      - Translate LBA (block number) to physical CHS address
      - Issue read/write commands to the physical platter
      - Log I/O operations for educational tracing

    The filesystem layer calls controller.read(block_no) and
    controller.write(block_no, data).  It never talks to the platter directly.
    """

    def __init__(self, platter):
        self.platter   = platter       # the physical storage underneath
        self.io_log    = []            # list of (op, lba, cylinder, head, sector)

    def read(self, lba):
        """
        Read one block (sector) by LBA number.

        Translates LBA → CHS, then reads the physical sector.
        This is what the kernel's block device driver calls.
        """
        c, h, s = lba_to_chs(lba)

        if IO_TRACE:
            print(f"  [CTRL READ ] LBA={lba:>3} → C={c} H={h} S={s}")

        self.io_log.append(("READ ", lba, c, h, s))
        return self.platter.read_sector(c, h, s)

    def write(self, lba, data):
        """
        Write one block (sector) by LBA number.

        Translates LBA → CHS, then writes to the physical sector.
        """
        c, h, s = lba_to_chs(lba)

        if IO_TRACE:
            preview = bytes(data[:8]).hex()
            print(f"  [CTRL WRITE] LBA={lba:>3} → C={c} H={h} S={s}  data={preview}...")

        self.io_log.append(("WRITE", lba, c, h, s))
        self.platter.write_sector(c, h, s, data)

    def dump_io_log(self, last_n=20):
        """Print the recent I/O operation log. Shows LBA → CHS translations."""
        print(f"\n[io_log]  Last {min(last_n, len(self.io_log))} disk I/O operations:")
        print(f"  {'OP':<6}  {'LBA':>4}  {'CYL':>4}  {'HEAD':>4}  {'SEC':>4}  BYTE_OFFSET")
        print(f"  {'------':<6}  {'----':>4}  {'----':>4}  {'----':>4}  {'----':>4}  -----------")
        entries = self.io_log[-last_n:]
        for op, lba, c, h, s in entries:
            byte_off = lba * SECTOR_SIZE
            print(f"  {op:<6}  {lba:>4}  {c:>4}  {h:>4}  {s:>4}  {byte_off}")
        print()

    def dump_disk_map(self):
        """
        Print a visual map of the disk showing which LBA blocks are written.
        Rows = cylinders, columns = heads × sectors.
        """
        print("\n[diskmap]  Physical Disk Layout  (W=written, .=empty)")
        print(f"  Rows=Cylinders(0..{NUM_CYLINDERS-1}), "
              f"Cols=Head×Sector (H0S0..H{HEADS_PER_CYLINDER-1}S{SECTORS_PER_TRACK-1})")

        # Header row
        header = "  CYL  |"
        for h in range(HEADS_PER_CYLINDER):
            for s in range(SECTORS_PER_TRACK):
                header += f"H{h}S{s} "
        print(header)
        print("  -----+" + "-----" * HEADS_PER_CYLINDER * SECTORS_PER_TRACK)

        for c in range(NUM_CYLINDERS):
            row = f"  C{c:>3}  |"
            for h in range(HEADS_PER_CYLINDER):
                for s in range(SECTORS_PER_TRACK):
                    lba = chs_to_lba(c, h, s)
                    key = (c, h, s)
                    written = key in self.platter._storage
                    row += f" L{lba:<2} " if written else "  .  "
            print(row)
        print()


# =============================================================================
# SECTION 0D — I/O LOG HELPER
# =============================================================================
#
#  A context manager that temporarily enables IO_TRACE so you can watch
#  exactly which physical sectors a single filesystem operation touches.
#
#  Usage:
#      with trace_io("write_file"):
#          fs.write_file("/notes.txt", "hello")
#

import contextlib

@contextlib.contextmanager
def trace_io(label=""):
    """Context manager: enables IO_TRACE for the duration of the block."""
    global IO_TRACE
    old = IO_TRACE
    IO_TRACE = True
    print(f"\n  ┌─ IO TRACE START: {label}")
    try:
        yield
    finally:
        IO_TRACE = old
        print(f"  └─ IO TRACE END:   {label}\n")


# =============================================================================
# SECTION 1 — CONSTANTS  (disk geometry for the filesystem layer)
# =============================================================================
#
#  IMPORTANT: BLOCK_SIZE must equal SECTOR_SIZE defined above.
#  The filesystem calls blocks what the hardware calls sectors.
#  They are the same physical unit — just named differently at each layer.
#

BLOCK_SIZE        = SECTOR_SIZE   # filesystem "block" = hardware "sector" = 64 bytes
TOTAL_BLOCKS      = TOTAL_SECTORS # must match physical disk capacity = 256

INODE_TABLE_START = 2             # block where inode table begins
INODE_TABLE_SIZE  = 32            # how many inodes we support (blocks 2..33)
DATA_START_BLOCK  = 34            # first data block available for file content

MAX_DIRECT_BLOCKS = 4             # direct block pointers per inode
MAX_FILENAME_LEN  = 12            # max chars in a filename
DIRENT_PER_BLOCK  = 4             # dirents per block: 64 / (4+12) = 4

# Inode type constants
INODE_FREE = 0
INODE_FILE = 1
INODE_DIR  = 2

# Reserved inode numbers
INODE_UNUSED = 0   # 0 = "no inode" / empty dirent slot
INODE_ROOT   = 1   # 1 = root directory, always


# =============================================================================
# SECTION 2 — DISK  (now routes through DiskController → PhysicalPlatter)
# =============================================================================
#
#  Previously:  disk_read/write talked directly to a Python dict.
#  Now:         disk_read/write talk to the DiskController,
#               which translates LBA → CHS and talks to the PhysicalPlatter.
#
#  The rest of the code (sections 3–9) is UNCHANGED.
#  Only disk_read() and disk_write() changed — everything above them is new.
#
#  Full call chain for a single block read:
#
#  filesystem layer
#      ↓  disk_read(block_no=42)
#  SECTION 2  (this section)
#      ↓  controller.read(lba=42)
#  SECTION 0C  DiskController
#      ↓  lba_to_chs(42) → (C=1, H=1, S=2)
#  SECTION 0B  Geometry translation
#      ↓  platter.read_sector(cylinder=1, head=1, sector=2)
#  SECTION 0A  PhysicalPlatter
#      ↓  returns bytearray from _storage[(1,1,2)]
#  back up the chain → filesystem gets its bytes
#

# Instantiate the hardware stack (done once at module load)
_platter    = PhysicalPlatter()
_controller = DiskController(_platter)


def disk_read(block_no):
    """
    Read one filesystem block by block number (LBA).

    Internally calls the disk controller, which translates to CHS
    and reads the physical platter sector.
    """
    return _controller.read(block_no)


def disk_write(block_no, data):
    """
    Write one filesystem block by block number (LBA).

    Internally calls the disk controller, which translates to CHS
    and writes to the physical platter sector.
    """
    assert len(data) <= BLOCK_SIZE, "Data larger than block size!"
    buf = bytearray(BLOCK_SIZE)
    buf[:len(data)] = data
    _controller.write(block_no, buf)


# =============================================================================
# SECTION 3 — SUPERBLOCK
# =============================================================================
#
#  The superblock is the "control panel" of the filesystem.
#  Kernel reads it first when mounting the filesystem.
#
#  It tracks:
#    - total number of blocks and inodes
#    - which blocks are free  (free_blocks list = simple stack)
#    - which inodes are free  (free_inodes list = simple stack)
#

class Superblock:
    def __init__(self):
        self.total_blocks  = TOTAL_BLOCKS
        self.total_inodes  = INODE_TABLE_SIZE
        self.free_blocks   = list(range(DATA_START_BLOCK, TOTAL_BLOCKS))
        self.free_inodes   = list(range(2, INODE_TABLE_SIZE + 1))

    @property
    def free_block_count(self):
        return len(self.free_blocks)

    @property
    def free_inode_count(self):
        return len(self.free_inodes)

    def alloc_block(self):
        """
        Pop one free block number.
        Zeros the sector on the platter before returning it (security).
        """
        if not self.free_blocks:
            raise OSError("No free blocks — disk is full!")
        block_no = self.free_blocks.pop()
        disk_write(block_no, bytearray(BLOCK_SIZE))
        return block_no

    def free_block(self, block_no):
        """Return block to the free list."""
        assert block_no not in self.free_blocks, "Double-free of block!"
        self.free_blocks.append(block_no)

    def alloc_inode(self):
        """Pop one free inode number."""
        if not self.free_inodes:
            raise OSError("No free inodes — inode table is full!")
        return self.free_inodes.pop()

    def free_inode(self, ino):
        """Return inode to the free list."""
        assert ino not in self.free_inodes, "Double-free of inode!"
        self.free_inodes.append(ino)

    def __repr__(self):
        return (f"Superblock(total_blocks={self.total_blocks}, "
                f"total_inodes={self.total_inodes}, "
                f"free_blocks={self.free_block_count}, "
                f"free_inodes={self.free_inode_count})")


# =============================================================================
# SECTION 4 — INODE TABLE
# =============================================================================
#
#  Each inode describes exactly ONE file (or directory).
#  The inode does NOT store the filename — that lives in the directory.
#
#  inode contains:
#    mode       : INODE_FREE / INODE_FILE / INODE_DIR
#    link_count : number of directory entries pointing to this inode
#    size       : file size in bytes
#    direct[]   : up to MAX_DIRECT_BLOCKS direct block pointers  (=LBA numbers)
#    indirect   : block number of an "indirect block"
#

class Inode:
    def __init__(self, ino):
        self.ino        = ino
        self.mode       = INODE_FREE
        self.link_count = 0
        self.size       = 0
        self.direct     = [0] * MAX_DIRECT_BLOCKS
        self.indirect   = 0

    def is_file(self):  return self.mode == INODE_FILE
    def is_dir(self):   return self.mode == INODE_DIR
    def is_free(self):  return self.mode == INODE_FREE

    def __repr__(self):
        t = {INODE_FREE:"FREE", INODE_FILE:"FILE", INODE_DIR:"DIR"}.get(self.mode,"?")
        return (f"Inode(ino={self.ino}, type={t}, links={self.link_count}, "
                f"size={self.size}, direct={self.direct}, indirect={self.indirect})")


# Global inode table: ino → Inode object
inode_table = {i: Inode(i) for i in range(INODE_TABLE_SIZE + 1)}

def get_inode(ino):
    """Fetch inode by number. Like kernel's iget()."""
    if ino < 1 or ino > INODE_TABLE_SIZE:
        raise ValueError(f"Invalid inode number: {ino}")
    return inode_table[ino]


# =============================================================================
# SECTION 5 — DIRECTORY FORMAT
# =============================================================================
#
#  A directory is a special file whose data blocks contain a flat list of
#  (inode_number, filename) pairs called directory entries (dirents).
#
#  dirent structure:
#    inode  : 4 bytes  → which inode this name points to (0 = empty slot)
#    name   : 12 bytes → the filename, null-padded
#
#  Total: 16 bytes per dirent.  4 dirents fit in one 64-byte block.
#

DIRENT_FORMAT = "I12s"
DIRENT_SIZE   = struct.calcsize(DIRENT_FORMAT)   # = 16 bytes


def pack_dirent(ino, name):
    """Serialise (ino, name) into 16 raw bytes."""
    return struct.pack(DIRENT_FORMAT, ino, name.encode("ascii")[:MAX_FILENAME_LEN])


def unpack_dirent(raw):
    """Deserialise 16 raw bytes into (ino, name)."""
    ino, name_bytes = struct.unpack(DIRENT_FORMAT, raw)
    return ino, name_bytes.rstrip(b"\x00").decode("ascii")


def dir_read_entries(dir_inode):
    """Read all valid (ino, name) entries from a directory's data blocks."""
    entries = []
    for blk_ptr in dir_inode.direct:
        if blk_ptr == 0:
            continue
        block_data = disk_read(blk_ptr)
        for i in range(DIRENT_PER_BLOCK):
            offset = i * DIRENT_SIZE
            raw = block_data[offset: offset + DIRENT_SIZE]
            if len(raw) < DIRENT_SIZE:
                break
            ino, name = unpack_dirent(raw)
            if ino != 0:
                entries.append((ino, name))
    return entries


def dir_lookup(dir_inode, name):
    """Search directory for a name. Returns inode number or None."""
    for ino, entry_name in dir_read_entries(dir_inode):
        if entry_name == name:
            return ino
    return None


def dir_add_entry(dir_inode, name, ino, sb):
    """Add a (name → ino) entry to a directory. Reuses empty slots first."""
    for blk_ptr in dir_inode.direct:
        if blk_ptr == 0:
            continue
        block_data = disk_read(blk_ptr)
        for i in range(DIRENT_PER_BLOCK):
            offset = i * DIRENT_SIZE
            slot_ino, _ = unpack_dirent(block_data[offset: offset + DIRENT_SIZE])
            if slot_ino == 0:
                block_data[offset: offset + DIRENT_SIZE] = pack_dirent(ino, name)
                disk_write(blk_ptr, block_data)
                dir_inode.size += DIRENT_SIZE
                return
    for idx in range(MAX_DIRECT_BLOCKS):
        if dir_inode.direct[idx] == 0:
            new_block = sb.alloc_block()
            dir_inode.direct[idx] = new_block
            block_data = bytearray(BLOCK_SIZE)
            block_data[0: DIRENT_SIZE] = pack_dirent(ino, name)
            disk_write(new_block, block_data)
            dir_inode.size += DIRENT_SIZE
            return
    raise OSError("Directory is full!")


def dir_remove_entry(dir_inode, name):
    """Remove named entry from directory. Returns removed inode number or None."""
    for blk_ptr in dir_inode.direct:
        if blk_ptr == 0:
            continue
        block_data = disk_read(blk_ptr)
        for i in range(DIRENT_PER_BLOCK):
            offset = i * DIRENT_SIZE
            slot_ino, entry_name = unpack_dirent(block_data[offset: offset + DIRENT_SIZE])
            if entry_name == name and slot_ino != 0:
                removed_ino = slot_ino
                block_data[offset: offset + DIRENT_SIZE] = pack_dirent(0, "")
                disk_write(blk_ptr, block_data)
                dir_inode.size -= DIRENT_SIZE
                return removed_ino
    return None


# =============================================================================
# SECTION 6 — PATH LOOKUP
# =============================================================================
#
#  Resolves "/home/alice/notes.txt" → inode number.
#  Walks component by component, starting at the root inode.
#

def path_lookup(path, sb=None):
    """Resolve a path string to an inode number."""
    if path == "/":
        return INODE_ROOT
    parts = [p for p in path.strip("/").split("/") if p]
    current_ino = INODE_ROOT
    for component in parts:
        current_inode = get_inode(current_ino)
        if not current_inode.is_dir():
            raise NotADirectoryError(f"'{component}' not a directory in '{path}'")
        found_ino = dir_lookup(current_inode, component)
        if found_ino is None:
            raise FileNotFoundError(f"'{component}' not found in '{path}'")
        current_ino = found_ino
    return current_ino


def path_split(path):
    """Split path into (parent_path, filename)."""
    parts = path.rstrip("/").split("/")
    filename = parts[-1]
    parent   = "/".join(parts[:-1]) or "/"
    return parent, filename


# =============================================================================
# SECTION 7 — FILESYSTEM API
# =============================================================================

class MiniFS:
    """
    Mini UNIX Filesystem.
    All operations flow down through:
        MiniFS → disk_read/write → DiskController → PhysicalPlatter
    """

    def __init__(self):
        self.sb = Superblock()
        self._format()

    def _format(self):
        """mkfs: reset all inodes, create root directory at inode 1."""
        for ino in inode_table:
            inode_table[ino].__init__(ino)
        root = get_inode(INODE_ROOT)
        root.mode       = INODE_DIR
        root.link_count = 2
        root.size       = 0
        dir_add_entry(root, ".",  INODE_ROOT, self.sb)
        dir_add_entry(root, "..", INODE_ROOT, self.sb)

    # ------------------------------------------------------------------
    # mkdir
    # ------------------------------------------------------------------
    def mkdir(self, path):
        """Create a directory."""
        parent_path, dirname = path_split(path)
        parent_ino   = path_lookup(parent_path)
        parent_inode = get_inode(parent_ino)
        if not parent_inode.is_dir():
            raise NotADirectoryError(f"{parent_path} is not a directory")
        if dir_lookup(parent_inode, dirname) is not None:
            raise FileExistsError(f"{path} already exists")
        new_ino   = self.sb.alloc_inode()
        new_inode = get_inode(new_ino)
        new_inode.mode       = INODE_DIR
        new_inode.link_count = 2
        new_inode.size       = 0
        dir_add_entry(new_inode, ".",  new_ino,    self.sb)
        dir_add_entry(new_inode, "..", parent_ino, self.sb)
        dir_add_entry(parent_inode, dirname, new_ino, self.sb)
        parent_inode.link_count += 1
        print(f"[mkdir]  {path}  (inode {new_ino})")

    # ------------------------------------------------------------------
    # touch
    # ------------------------------------------------------------------
    def touch(self, path):
        """Create an empty file."""
        parent_path, filename = path_split(path)
        parent_ino   = path_lookup(parent_path)
        parent_inode = get_inode(parent_ino)
        if not parent_inode.is_dir():
            raise NotADirectoryError(f"{parent_path} is not a directory")
        if dir_lookup(parent_inode, filename) is not None:
            raise FileExistsError(f"{path} already exists")
        new_ino   = self.sb.alloc_inode()
        new_inode = get_inode(new_ino)
        new_inode.mode       = INODE_FILE
        new_inode.link_count = 1
        new_inode.size       = 0
        dir_add_entry(parent_inode, filename, new_ino, self.sb)
        print(f"[touch]  {path}  (inode {new_ino})")
        return new_ino

    # ------------------------------------------------------------------
    # write_file
    # ------------------------------------------------------------------
    def write_file(self, path, data):
        """Write data to a file. Each block goes to a physical sector via controller."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        ino   = path_lookup(path)
        inode = get_inode(ino)
        if not inode.is_file():
            raise IsADirectoryError(f"{path} is a directory")
        # Free old blocks
        for i, blk_ptr in enumerate(inode.direct):
            if blk_ptr != 0:
                self.sb.free_block(blk_ptr)
                inode.direct[i] = 0
        # Write new blocks
        remaining = data
        block_idx = 0
        while remaining and block_idx < MAX_DIRECT_BLOCKS:
            chunk     = remaining[:BLOCK_SIZE]
            remaining = remaining[BLOCK_SIZE:]
            new_block = self.sb.alloc_block()
            disk_write(new_block, chunk)
            inode.direct[block_idx] = new_block
            block_idx += 1
        if remaining:
            raise OSError(f"File too large! Max {MAX_DIRECT_BLOCKS * BLOCK_SIZE} bytes.")
        inode.size = len(data)
        # Show which physical sectors were used
        used_blocks = [b for b in inode.direct if b != 0]
        chs_list = [lba_to_chs(b) for b in used_blocks]
        print(f"[write]  {path}  ({len(data)} bytes, "
              f"LBA blocks {used_blocks}, physical CHS {chs_list})")

    # ------------------------------------------------------------------
    # read_file
    # ------------------------------------------------------------------
    def read_file(self, path):
        """Read file contents. Each block is fetched from a physical sector."""
        ino   = path_lookup(path)
        inode = get_inode(ino)
        if not inode.is_file():
            raise IsADirectoryError(f"{path} is a directory")
        buf = bytearray()
        for blk_ptr in inode.direct:
            if blk_ptr == 0:
                break
            buf += disk_read(blk_ptr)
        result = bytes(buf[:inode.size])
        c, h, s = lba_to_chs(inode.direct[0]) if inode.direct[0] else (0,0,0)
        print(f"[read]   {path}  ({len(result)} bytes, "
              f"first block LBA={inode.direct[0]}  C={c} H={h} S={s})")
        return result.decode("utf-8", errors="replace")

    # ------------------------------------------------------------------
    # ls
    # ------------------------------------------------------------------
    def ls(self, path="/"):
        """List directory contents."""
        ino   = path_lookup(path)
        inode = get_inode(ino)
        if not inode.is_dir():
            raise NotADirectoryError(f"{path} is not a directory")
        entries = dir_read_entries(inode)
        print(f"\n[ls]  {path}  (inode {ino}):")
        print(f"  {'INO':>4}  {'TYPE':<5}  {'SIZE':>6}  NAME")
        print(f"  {'----':>4}  {'-----':<5}  {'------':>6}  ----")
        for entry_ino, name in sorted(entries, key=lambda e: e[1]):
            ei = get_inode(entry_ino)
            t  = {INODE_FILE:"FILE", INODE_DIR:"DIR "}.get(ei.mode, "FREE")
            print(f"  {entry_ino:>4}  {t:<5}  {ei.size:>6}  {name}")
        print()

    # ------------------------------------------------------------------
    # stat
    # ------------------------------------------------------------------
    def stat(self, path):
        """Show inode metadata and physical block locations."""
        ino   = path_lookup(path)
        inode = get_inode(ino)
        t = {INODE_FILE:"Regular File", INODE_DIR:"Directory"}.get(inode.mode,"?")
        print(f"\n[stat]  {path}")
        print(f"  Inode number : {inode.ino}")
        print(f"  Type         : {t}")
        print(f"  Size         : {inode.size} bytes")
        print(f"  Link count   : {inode.link_count}")
        used = [b for b in inode.direct if b != 0]
        print(f"  LBA blocks   : {used}")
        # Show physical location for each block
        for lba in used:
            c, h, s = lba_to_chs(lba)
            print(f"    LBA {lba:>3} → Cylinder {c}, Head {h}, Sector {s}  "
                  f"(byte {lba * SECTOR_SIZE} on disk)")
        print()

    # ------------------------------------------------------------------
    # ln  (hard link)
    # ------------------------------------------------------------------
    def ln(self, existing_path, new_path):
        """Create a hard link."""
        target_ino   = path_lookup(existing_path)
        target_inode = get_inode(target_ino)
        if target_inode.is_dir():
            raise IsADirectoryError("Cannot hard-link a directory")
        parent_path, link_name = path_split(new_path)
        parent_inode = get_inode(path_lookup(parent_path))
        if dir_lookup(parent_inode, link_name) is not None:
            raise FileExistsError(f"{new_path} already exists")
        dir_add_entry(parent_inode, link_name, target_ino, self.sb)
        target_inode.link_count += 1
        print(f"[ln]     {new_path} → inode {target_ino}  "
              f"(link_count={target_inode.link_count})")

    # ------------------------------------------------------------------
    # rm
    # ------------------------------------------------------------------
    def rm(self, path):
        """Remove a directory entry. Free inode+blocks when link_count reaches 0."""
        parent_path, name = path_split(path)
        parent_inode = get_inode(path_lookup(parent_path))
        removed_ino  = dir_remove_entry(parent_inode, name)
        if removed_ino is None:
            raise FileNotFoundError(f"{path} not found")
        target_inode = get_inode(removed_ino)
        target_inode.link_count -= 1
        print(f"[rm]     '{name}' removed  (inode {removed_ino}, "
              f"link_count now {target_inode.link_count})")
        if target_inode.link_count == 0:
            for i, blk_ptr in enumerate(target_inode.direct):
                if blk_ptr != 0:
                    self.sb.free_block(blk_ptr)
                    target_inode.direct[i] = 0
            if target_inode.indirect:
                self.sb.free_block(target_inode.indirect)
                target_inode.indirect = 0
            target_inode.mode       = INODE_FREE
            target_inode.size       = 0
            target_inode.link_count = 0
            self.sb.free_inode(removed_ino)
            print(f"         → link_count=0: freed inode {removed_ino} and blocks")

    # ------------------------------------------------------------------
    # df
    # ------------------------------------------------------------------
    def df(self):
        """Filesystem + physical disk usage."""
        used_blocks = TOTAL_BLOCKS - DATA_START_BLOCK - self.sb.free_block_count
        used_inodes = INODE_TABLE_SIZE - self.sb.free_inode_count
        print(f"\n[df]  Filesystem + Disk Usage:")
        print(f"  Total sectors  : {TOTAL_SECTORS}  "
              f"({NUM_CYLINDERS}cyl × {HEADS_PER_CYLINDER}head × {SECTORS_PER_TRACK}sec)")
        print(f"  FS data blocks : {TOTAL_BLOCKS - DATA_START_BLOCK}")
        print(f"  Used blocks    : {used_blocks}")
        print(f"  Free blocks    : {self.sb.free_block_count}")
        print(f"  Used inodes    : {used_inodes} / {INODE_TABLE_SIZE}")
        print(f"  Phys reads     : {_platter.read_count}")
        print(f"  Phys writes    : {_platter.write_count}")
        print()

    # ------------------------------------------------------------------
    # dump_inodes
    # ------------------------------------------------------------------
    def dump_inodes(self):
        """Print all non-free inodes with LBA and CHS locations."""
        print(f"\n[inodes]  Active Inode Table:")
        print(f"  {'INO':>4}  {'TYPE':<5}  {'LINKS':>5}  {'SIZE':>6}  LBA BLOCKS → CHS")
        print(f"  {'----':>4}  {'-----':<5}  {'-----':>5}  {'------':>6}  ----------------")
        for ino in range(1, INODE_TABLE_SIZE + 1):
            inode = inode_table[ino]
            if inode.mode != INODE_FREE:
                t = {INODE_FILE:"FILE", INODE_DIR:"DIR "}.get(inode.mode, "?")
                blocks = [b for b in inode.direct if b != 0]
                chs    = [lba_to_chs(b) for b in blocks]
                print(f"  {ino:>4}  {t:<5}  {inode.link_count:>5}  {inode.size:>6}  "
                      f"{blocks} → {chs}")
        print()

    # ------------------------------------------------------------------
    # geometry  — new command to show disk hardware info
    # ------------------------------------------------------------------
    def geometry(self):
        """Show physical disk geometry and I/O statistics."""
        _platter.dump_geometry()

    # ------------------------------------------------------------------
    # diskmap  — visual layout of what's written on the platter
    # ------------------------------------------------------------------
    def diskmap(self):
        """Show visual map of which physical sectors are written."""
        _controller.dump_disk_map()

    # ------------------------------------------------------------------
    # iolog  — show recent physical I/O operations with CHS translation
    # ------------------------------------------------------------------
    def iolog(self, n=20):
        """Show the last N disk I/O operations (LBA → CHS translation log)."""
        _controller.dump_io_log(last_n=n)

    # ------------------------------------------------------------------
    # explain_block  — decode one block number into everything
    # ------------------------------------------------------------------
    def explain_block(self, block_no):
        """
        Fully decode a block number — show all layers from LBA to physical bytes.
        Great for understanding the translation chain.
        """
        c, h, s = lba_to_chs(block_no)
        byte_offset = block_no * SECTOR_SIZE
        data = disk_read(block_no)
        written = (c, h, s) in _platter._storage

        print(f"\n[explain]  Block {block_no}:")
        print(f"  Filesystem view  : block number (LBA) = {block_no}")
        print(f"  Controller view  : LBA {block_no} → Cylinder {c}, Head {h}, Sector {s}")
        print(f"  Platter view     : byte offset {byte_offset} on disk surface")
        print(f"  Written          : {'yes' if written else 'no (reads as zeros)'}")
        if written:
            printable = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data)
            print(f"  Raw hex (first 32): {data[:32].hex()}")
            print(f"  ASCII preview     : {printable[:32]}")
        print()


# =============================================================================
# SECTION 8 — DEMO
# =============================================================================

def run_demo():
    print("=" * 70)
    print("  Mini-UNIX-FS v2  —  With Physical Disk Layer")
    print("=" * 70)

    fs = MiniFS()

    print("\n--- Phase 0: Physical disk geometry ---")
    fs.geometry()

    print("--- Phase 1: Show LBA → CHS for key blocks ---")
    print("  Filesystem block layout translated to physical addresses:")
    for lba in [0, 1, 2, 33, 34, 127, 255]:
        c, h, s = lba_to_chs(lba)
        role = {0:"boot", 1:"superblock", 2:"inode_table_start",
                33:"inode_table_end", 34:"first_data_block",
                127:"mid_disk", 255:"last_block"}.get(lba, "")
        print(f"  LBA {lba:>3} ({role:<20}) → C={c} H={h} S={s}")
    print()

    print("--- Phase 2: Create directories ---")
    fs.mkdir("/home")
    fs.mkdir("/home/alice")

    print("\n--- Phase 3: Create and write a file (watch the CHS output) ---")
    fs.touch("/home/alice/notes.txt")
    with trace_io("write_file notes.txt"):
        fs.write_file("/home/alice/notes.txt", "Hello from the physical disk layer!")

    print("--- Phase 4: Read the file back (watch the CHS output) ---")
    with trace_io("read_file notes.txt"):
        content = fs.read_file("/home/alice/notes.txt")
    print(f"  Content: {repr(content)}\n")

    print("--- Phase 5: stat shows LBA + CHS for every block ---")
    fs.stat("/home/alice/notes.txt")

    print("--- Phase 6: Hard link + verify same physical blocks ---")
    fs.ln("/home/alice/notes.txt", "/home/alice/notes.bak")
    fs.stat("/home/alice/notes.txt")   # same physical blocks as backup

    print("--- Phase 7: Inode table with physical addresses ---")
    fs.dump_inodes()

    print("--- Phase 8: Disk map — visual physical layout ---")
    fs.diskmap()

    print("--- Phase 9: I/O log — every LBA→CHS translation ---")
    fs.iolog(n=15)

    print("--- Phase 10: Explain a specific block in full ---")
    # Allocations start from end of disk; search backwards
    for b in range(TOTAL_BLOCKS - 1, DATA_START_BLOCK - 1, -1):
        c, h, s = lba_to_chs(b)
        if (c, h, s) in _platter._storage:
            fs.explain_block(b)
            break

    print("--- Phase 11: Final df with physical I/O counts ---")
    fs.df()


# =============================================================================
# SECTION 9 — INTERACTIVE SHELL
# =============================================================================

def interactive_shell(fs):
    print("\n" + "=" * 70)
    print("  Mini-UNIX-FS v2 Interactive Shell")
    print("  New commands: geometry, diskmap, iolog, explain <N>, lba <N>")
    print("  Type 'help' for all commands, 'exit' to quit")
    print("=" * 70 + "\n")

    cwd = "/"

    HELP = """
  Filesystem commands:
    ls   [path]               List directory contents
    mkdir <path>              Create a directory
    touch <path>              Create an empty file
    write <path> <text>       Write text to a file
    cat   <path>              Read a file
    stat  <path>              Show inode + physical block locations
    ln    <src> <dst>         Create a hard link
    rm    <path>              Remove a file/directory entry
    df                        Show filesystem + physical I/O usage
    inodes                    Dump inode table with CHS addresses
    pwd / cd <path>           Navigate

  Physical disk commands  (NEW in v2):
    geometry                  Show disk geometry (cylinders/heads/sectors)
    diskmap                   Visual map of physical platter — what's written where
    iolog [N]                 Show last N disk I/O ops with LBA→CHS translation
    lba <N>                   Translate block number N to CHS address
    explain <N>               Fully decode block N: LBA, CHS, bytes, ASCII

  help / exit
"""
    print(HELP)

    while True:
        try:
            line = input(f"minifs:{cwd}$ ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not line:
            continue

        parts = line.split(maxsplit=1)
        cmd   = parts[0]
        args  = parts[1].strip() if len(parts) > 1 else ""

        def resolve(p):
            if p.startswith("/"):
                return p
            return ("/" if cwd == "/" else cwd) + ("" if cwd == "/" else "/") + p

        try:
            if cmd == "exit":
                print("Bye!"); break

            elif cmd == "help":
                print(HELP)

            elif cmd == "pwd":
                print(cwd)

            elif cmd == "cd":
                target = resolve(args) if args else "/"
                ino = path_lookup(target)
                if not get_inode(ino).is_dir():
                    print(f"  Not a directory: {target}")
                else:
                    cwd = target

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
                print(fs.read_file(resolve(args)))

            elif cmd == "stat":
                if not args: print("  Usage: stat <path>"); continue
                fs.stat(resolve(args))

            elif cmd == "ln":
                p2 = args.split()
                if len(p2) < 2: print("  Usage: ln <src> <dst>"); continue
                fs.ln(resolve(p2[0]), resolve(p2[1]))

            elif cmd == "rm":
                if not args: print("  Usage: rm <path>"); continue
                fs.rm(resolve(args))

            elif cmd == "df":
                fs.df()

            elif cmd == "inodes":
                fs.dump_inodes()

            # ---- NEW physical disk commands ----

            elif cmd == "geometry":
                fs.geometry()

            elif cmd == "diskmap":
                fs.diskmap()

            elif cmd == "iolog":
                n = int(args) if args.isdigit() else 20
                fs.iolog(n)

            elif cmd == "lba":
                if not args.isdigit():
                    print("  Usage: lba <block_number>"); continue
                lba = int(args)
                c, h, s = lba_to_chs(lba)
                print(f"\n  LBA {lba}  →  Cylinder={c}, Head={h}, Sector={s}")
                print(f"  Byte offset on disk: {lba * SECTOR_SIZE}")
                role = {0:"boot block", 1:"superblock",
                        **{i:"inode table" for i in range(2, DATA_START_BLOCK)},
                        **{i:"data block" for i in range(DATA_START_BLOCK, TOTAL_BLOCKS)}
                       }.get(lba, "unknown")
                print(f"  Filesystem role: {role}\n")

            elif cmd == "explain":
                if not args.isdigit():
                    print("  Usage: explain <block_number>"); continue
                fs.explain_block(int(args))

            else:
                print(f"  Unknown command: {cmd}  (type 'help')")

        except Exception as e:
            print(f"  Error: {e}")


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import sys

    if "--shell" in sys.argv:
        fs = MiniFS()
        interactive_shell(fs)
    else:
        run_demo()
        print("\n" + "=" * 70)
        print("  Demo complete.  Launching interactive shell...")
        print("  Try:  geometry | diskmap | iolog | lba 42 | explain 34")
        print("=" * 70)
        fs = MiniFS()
        interactive_shell(fs)

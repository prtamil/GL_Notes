# Understanding a UNIX-Style Filesystem from First Principles

### A Deep Technical Essay on `mini_unix_fs_v2.py`

---

> _"The filesystem is one of the most beautiful data structures ever invented. It is simple enough to understand completely, yet powerful enough to organise every file on every computer on the planet."_

---

## Table of Contents

1. [Why Study a Filesystem from Scratch?](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#1-why-study-a-filesystem-from-scratch)
2. [The Complete Stack: From User Command to Magnetic Platter](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#2-the-complete-stack-from-user-command-to-magnetic-platter)
3. [Section 0A — The Physical Platter: What a Disk Actually Is](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#3-section-0a--the-physical-platter-what-a-disk-actually-is)
4. [Section 0B — Disk Geometry: CHS Addressing](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#4-section-0b--disk-geometry-chs-addressing)
5. [Section 0C — The Disk Controller: Bridging LBA and CHS](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#5-section-0c--the-disk-controller-bridging-lba-and-chs)
6. [Section 0D — The I/O Trace: Watching Every Physical Operation](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#6-section-0d--the-io-trace-watching-every-physical-operation)
7. [Section 1 — Constants: Where Geometry Becomes Agreement](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#7-section-1--constants-where-geometry-becomes-agreement)
8. [Section 2 — disk_read and disk_write: The Rewired Interface](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#8-section-2--disk_read-and-disk_write-the-rewired-interface)
9. [Section 3 — The Superblock: The Filesystem's Control Panel](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#9-section-3--the-superblock-the-filesystems-control-panel)
10. [Section 4 — The Inode: The Soul of a File](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#10-section-4--the-inode-the-soul-of-a-file)
11. [Section 5 — The Directory: Names Are Just Labels](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#11-section-5--the-directory-names-are-just-labels)
12. [Section 6 — Path Lookup: Walking the Tree](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#12-section-6--path-lookup-walking-the-tree)
13. [Section 7 — The MiniFS API: Tying It All Together](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#13-section-7--the-minifs-api-tying-it-all-together)
14. [Hard Links: The Deepest Insight](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#14-hard-links-the-deepest-insight)
15. [Deletion: rm Is Actually Unlink](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#15-deletion-rm-is-actually-unlink)
16. [The Complete Layered Architecture](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#16-the-complete-layered-architecture)
17. [Tracing a Single Write End-to-End](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#17-tracing-a-single-write-end-to-end)
18. [What This Simulator Deliberately Leaves Out](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#18-what-this-simulator-deliberately-leaves-out)
19. [How This Maps to Real Linux](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#19-how-this-maps-to-real-linux)
20. [Closing Thoughts](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#20-closing-thoughts)

---

## 1. Why Study a Filesystem from Scratch?

Every time you type `ls`, `cat`, `cp`, or `rm` in a terminal, you trigger a chain of operations that descends from the comfortable world of userspace commands all the way down into the kernel's filesystem layer — and then further still, through a disk controller, to magnetic regions on a spinning platter or cells in a flash chip. Most programmers use filesystems every day of their careers without understanding any of this.

That gap matters more than it might seem. The same mental model governs:

- **Database storage engines** — PostgreSQL's page layout, SQLite's B-tree pages
- **Container overlayfs** — how Docker layers are stacked and merged
- **FUSE filesystems** — building custom filesystems in userspace
- **Linux VFS** — the kernel's unified interface across dozens of filesystem types
- **Log-structured stores** — LevelDB, RocksDB, Cassandra's SSTables
- **NVMe and SSD internals** — flash translation layers, wear levelling

`mini_unix_fs_v2.py` makes the entire stack visible in one file. Version 1 showed everything from the superblock upward. Version 2 adds the hardware layers underneath: the physical platter, CHS geometry, and the disk controller that translates between the OS's flat block numbers and the drive's physical coordinates. The simulator now spans the complete journey from a user typing `write /notes.txt hello` down to bytes being stored at a specific cylinder, head, and sector on a spinning disk.

---

## 2. The Complete Stack: From User Command to Magnetic Platter

Before diving into individual sections, it helps to see the entire call chain at once. When you call `fs.write_file("/home/alice/notes.txt", "hello")`, here is everything that happens, in order:

```
  User calls:  fs.write_file("/home/alice/notes.txt", "hello")
       │
       ▼
  SECTION 7  MiniFS.write_file()
    Resolves path → inode number
    Allocates a free block number (e.g., 252)
    Calls disk_write(block_no=252, data=b"hello...")
       │
       ▼
  SECTION 2  disk_write()
    Packages data into a full BLOCK_SIZE buffer
    Calls _controller.write(lba=252, data)
       │
       ▼
  SECTION 0C  DiskController.write()
    Translates: lba_to_chs(252)  →  Cylinder=7, Head=3, Sector=4
    Logs the operation to io_log
    Calls _platter.write_sector(cylinder=7, head=3, sector=4, data)
       │
       ▼
  SECTION 0B  lba_to_chs()
    cylinder = 252 // (4 × 8) = 7
    head     = (252 // 8) % 4  = 3
    sector   = 252 % 8         = 4
       │
       ▼
  SECTION 0A  PhysicalPlatter.write_sector()
    Validates address bounds
    Increments write_count
    Stores: _storage[(7, 3, 4)] = bytearray(b"hello...")
```

Every layer has a single, clean responsibility. The filesystem layer knows nothing about cylinders. The controller knows nothing about inodes. The platter knows nothing about filenames. This is not just good software design — it is how real hardware and operating systems are actually structured.

---

## 3. Section 0A — The Physical Platter: What a Disk Actually Is

```python
class PhysicalPlatter:
    def __init__(self):
        self._storage  = {}   # (cylinder, head, sector) → bytearray
        self.read_count  = 0
        self.write_count = 0

    def read_sector(self, cylinder, head, sector):
        self._validate_address(cylinder, head, sector)
        self.read_count += 1
        key = (cylinder, head, sector)
        if key not in self._storage:
            return bytearray(SECTOR_SIZE)
        return bytearray(self._storage[key])

    def write_sector(self, cylinder, head, sector, data):
        self._validate_address(cylinder, head, sector)
        self.write_count += 1
        buf = bytearray(SECTOR_SIZE)
        buf[:len(data)] = data
        self._storage[(cylinder, head, sector)] = buf
```

A hard disk is, at its physical core, one or more **platters** — circular disks coated in a magnetic material, spinning at 5,400–15,000 RPM. Data is stored by magnetising tiny regions of the surface in one of two polarities, representing 0 and 1. A read/write head, mounted on a mechanical arm, hovers nanometres above the surface as it spins past.

### The Three Physical Dimensions

Understanding a hard disk requires understanding three spatial dimensions that together form every byte's address.

**Tracks** are concentric circular rings on the platter surface. When the arm moves inward or outward, it moves from one track to another. This movement is called a **seek** and is the most expensive operation a spinning disk performs — it takes 3–15 milliseconds on a real drive, an eternity compared to nanoseconds of RAM access.

**Cylinders** are all tracks at the same radial distance, across all platter surfaces and all physical disks on the spindle. If you have two platters (four surfaces), all four tracks at radius R form one cylinder. The name comes from the shape: if you could see through the platters, the set of tracks at the same radius would form a hollow cylinder through the stack. Data is stored cylinder-by-cylinder rather than platter-by-platter because moving between cylinders requires a physical seek, while switching between heads at the same cylinder is instantaneous — you just activate a different head electrically.

**Sectors** are fixed-size arcs of a track — the pie slices of a circular ring. Each sector stores one unit of data. On real hard disks, a sector is traditionally 512 bytes; modern drives and SSDs use 4,096-byte sectors. In our simulator, a sector is 64 bytes so its contents are printable.

### Our Simulated Geometry

```python
NUM_CYLINDERS      = 8    # rings on the platter
HEADS_PER_CYLINDER = 4    # surfaces (2 platters, top and bottom of each)
SECTORS_PER_TRACK  = 8    # sectors per ring per surface
SECTOR_SIZE        = 64   # bytes per sector
# Total: 8 × 4 × 8 = 256 sectors
```

This is tiny but geometrically faithful. Every relationship and formula works identically to a 1 TB drive with millions of cylinders. The `geometry` command shows these numbers at runtime along with live read/write counts:

```
[platter]  Physical Disk Geometry:
  Cylinders        : 8
  Heads/cylinder   : 4
  Sectors/track    : 8
  Sector size      : 64 bytes
  Total sectors    : 256
  Total capacity   : 16384 bytes  (16 KB)
  Physical reads   : 32
  Physical writes  : 15
```

### The 3D Storage Address

Every byte of data on the disk has a physical address of the form `(cylinder, head, sector)`. The `PhysicalPlatter` enforces this coordinate system. The `_storage` dict — indexed by `(c, h, s)` tuples — is the simplest possible model of what the magnetic surface holds.

On a real disk, `read_sector` would involve sending a seek command to the arm actuator, waiting for the correct sector to rotate under the head, and decoding the raw magnetic flux signal through error correction into clean bytes. In our simulation, all of that is replaced by a dict lookup. The point is to simulate the _interface_ — the fact that every read and write must name a specific physical coordinate — not the underlying physics.

---

## 4. Section 0B — Disk Geometry: CHS Addressing

```python
def lba_to_chs(lba):
    cylinder = lba // (HEADS_PER_CYLINDER * SECTORS_PER_TRACK)
    head     = (lba // SECTORS_PER_TRACK) % HEADS_PER_CYLINDER
    sector   = lba % SECTORS_PER_TRACK
    return cylinder, head, sector

def chs_to_lba(cylinder, head, sector):
    return (cylinder * HEADS_PER_CYLINDER + head) * SECTORS_PER_TRACK + sector
```

The operating system does not want to think about cylinders, heads, and sectors when it writes a file. It wants a flat, numbered sequence of blocks: block 0, block 1, block 2 ... block N. This is called **LBA — Logical Block Addressing**. The OS uses LBA exclusively; the drive hardware uses CHS physically. The translation between them is the `lba_to_chs` function.

### The Translation Formula in Detail

With our geometry (4 heads, 8 sectors per track), each cylinder holds `4 × 8 = 32` sectors. Working through the formula:

```
cylinder  = LBA ÷ 32          (integer division — which ring?)
head      = (LBA ÷ 8) mod 4   (which surface of that ring?)
sector    = LBA mod 8          (which slice of that ring+surface?)
```

The sectors fill up head-by-head within each cylinder before advancing to the next. This ordering is physically optimal: reading an entire cylinder requires no arm movement at all, because all heads can activate sequentially without seeking.

Mapping the filesystem's fixed regions to physical locations:

|LBA|Cylinder|Head|Sector|Filesystem Role|
|---|---|---|---|---|
|0|0|0|0|Boot block|
|1|0|0|1|Superblock|
|2|0|0|2|First inode table block|
|33|1|0|1|Last inode table block|
|34|1|0|2|First data block|
|127|3|3|7|Middle of disk|
|255|7|3|7|Last sector on disk|

You can verify any of these from the interactive shell with `lba N`:

```
minifs:/$ lba 34
  LBA 34  →  Cylinder=1, Head=0, Sector=2
  Byte offset on disk: 2176
  Filesystem role: data block
```

### Why LBA Exists

Before LBA, the BIOS and operating systems had to know the exact CHS geometry of every drive model. As drives got larger and geometries more complex — varying numbers of sectors per track, zone bit recording, hidden spare sectors — this became unmanageable. LBA was introduced in the early 1990s: the OS provides a flat block number and the drive firmware handles translation internally. Modern NVMe SSDs have no cylinders or heads at all, but they still accept LBA numbers — the SSD controller maps them to flash pages using entirely different algorithms, completely invisible to the OS.

Our `lba_to_chs()` function is the exact same translation that HDD firmware performs, made visible in Python.

---

## 5. Section 0C — The Disk Controller: Bridging LBA and CHS

```python
class DiskController:
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
            preview = bytes(data[:8]).hex()
            print(f"  [CTRL WRITE] LBA={lba:>3} → C={c} H={h} S={s}  data={preview}...")
        self.io_log.append(("WRITE", lba, c, h, s))
        self.platter.write_sector(c, h, s, data)
```

The disk controller is the hardware chip that sits between the computer's memory bus and the physical platters. In real ATA/SATA drives it handles command queuing, error correction, bad sector remapping, write caching, and, most relevantly here, LBA-to-CHS translation.

Our `DiskController` does one thing per call: translate the LBA, log the operation, and forward to `PhysicalPlatter`. This is intentionally minimal — the goal is to make the translation step explicit and observable, not to simulate real controller firmware.

### The I/O Log

```python
self.io_log.append(("READ ", lba, c, h, s))
```

Every single read or write is recorded with its LBA and CHS translation. The `iolog` command in the shell prints this log:

```
[io_log]  Last 15 disk I/O operations:
  OP       LBA   CYL  HEAD   SEC  BYTE_OFFSET
  ------  ----  ----  ----  ----  -----------
  WRITE    252     7     3     4  16128   ← file data lands here
  READ     253     7     3     5  16192
  READ     254     7     3     6  16256
  READ     255     7     3     7  16320
```

This is the most powerful educational feature in the simulator. It makes completely visible something that is entirely hidden in real systems: every filesystem operation — creating a directory, resolving a path, writing a file — translates to a sequence of physical sector reads and writes at specific CHS addresses. In a real Linux system, the equivalent tool is `blktrace`.

### The IO_TRACE Flag and trace_io Context Manager

```python
IO_TRACE = False

with trace_io("write_file"):
    fs.write_file("/home/alice/notes.txt", "Hello!")
```

Wrapping an operation in `trace_io` enables real-time printing of every I/O as it is dispatched:

```
  ┌─ IO TRACE START: write_file
  [CTRL READ ] LBA=255 → C=7 H=3 S=7   ← reading root dir block
  [CTRL READ ] LBA=254 → C=7 H=3 S=6   ← reading /home dir block
  [CTRL WRITE] LBA=252 → C=7 H=3 S=4  data=48656c6c6f2100...
  └─ IO TRACE END:   write_file
```

The reads before the write are the filesystem scanning directory blocks to find the file's entry. The write is the file data reaching the physical sector.

---

## 6. Section 0D — The I/O Trace: Watching Every Physical Operation

```python
@contextlib.contextmanager
def trace_io(label=""):
    global IO_TRACE
    old = IO_TRACE
    IO_TRACE = True
    print(f"\n  ┌─ IO TRACE START: {label}")
    try:
        yield
    finally:
        IO_TRACE = old
        print(f"  └─ IO TRACE END:   {label}\n")
```

This is a Python **context manager** — the `with trace_io("label"):` syntax activates it. During the `with` block, `IO_TRACE` is `True`, causing the controller to print every physical I/O. When the block exits, `IO_TRACE` is restored. The `try/finally` ensures restoration even if an exception occurs inside.

The `contextlib.contextmanager` decorator turns a generator with a single `yield` into a context manager. Everything before `yield` runs on enter; everything after runs on exit. This is standard Python, but the pattern it implements — temporarily enabling diagnostics around a specific operation — is the same principle behind real kernel tracing tools: `strace` intercepts syscalls, `blktrace` traces block layer I/O, `ftrace` traces kernel functions. Our `trace_io` is a miniature version of all of them.

---

## 7. Section 1 — Constants: Where Geometry Becomes Agreement

In v2, the constants section contains a critical new relationship:

```python
BLOCK_SIZE   = SECTOR_SIZE    # filesystem "block" = hardware "sector" = 64 bytes
TOTAL_BLOCKS = TOTAL_SECTORS  # must match: 8 × 4 × 8 = 256
```

These two lines declare an **alignment** between the logical and physical worlds. The filesystem speaks in "blocks." The hardware speaks in "sectors." They are the same physical unit — 64 bytes — seen from two different perspectives. The assignment `BLOCK_SIZE = SECTOR_SIZE` is not just a code convenience; it is the fundamental agreement that makes the whole stack work.

```
Filesystem layer:  Block  0,  Block  1,  Block  2  ...  Block 255
                     │          │          │                │
                  (identity: block number = LBA)
                     │          │          │                │
Controller sees:   LBA  0,   LBA  1,   LBA  2  ...   LBA 255
                     │          │          │                │
Platter sees:    C0,H0,S0  C0,H0,S1  C0,H0,S2  ...  C7,H3,S7
```

Every filesystem region now has a physical home:

```
LBA  0       (C=0, H=0, S=0)  → Boot block
LBA  1       (C=0, H=0, S=1)  → Superblock
LBA  2..33   (C=0,H=0,S=2 to C=1,H=0,S=1) → Inode table
LBA  34..255 (C=1,H=0,S=2 to C=7,H=3,S=7) → Data blocks
```

---

## 8. Section 2 — disk_read and disk_write: The Rewired Interface

In v1, `disk_read` and `disk_write` talked directly to a Python dict. In v2, those same two functions route through the full hardware stack:

```python
# v1 — direct dict access (simple)
disk = {}
def disk_read(block_no):
    return bytearray(disk.get(block_no, bytearray(BLOCK_SIZE)))

# v2 — routes through controller → platter (complete stack)
_platter    = PhysicalPlatter()
_controller = DiskController(_platter)

def disk_read(block_no):
    return _controller.read(block_no)

def disk_write(block_no, data):
    buf = bytearray(BLOCK_SIZE)
    buf[:len(data)] = data
    _controller.write(block_no, buf)
```

Everything above these two functions — sections 3 through 9, covering the superblock, inode table, directory code, path lookup, and the entire MiniFS API — is completely unchanged between v1 and v2. They call `disk_read` and `disk_write` exactly as before.

This is **interface stability** in action. By keeping `disk_read(block_no)` and `disk_write(block_no, data)` as the fixed contract, the entire physical hardware simulation was inserted beneath the filesystem without touching a single line of filesystem code. This is exactly how the Linux block device layer works: filesystems call `submit_bio()`, and the block layer routes the request to whatever device — HDD, SSD, RAID, network storage — is underneath.

---

## 9. Section 3 — The Superblock: The Filesystem's Control Panel

The superblock is the first thing the kernel reads when mounting a filesystem partition, and it contains everything needed to begin operating.

```python
class Superblock:
    def __init__(self):
        self.total_blocks  = TOTAL_BLOCKS
        self.total_inodes  = INODE_TABLE_SIZE
        self.free_blocks   = list(range(DATA_START_BLOCK, TOTAL_BLOCKS))
        self.free_inodes   = list(range(2, INODE_TABLE_SIZE + 1))
```

Four essential values: total blocks, total inodes, which blocks are free, which inodes are free. This is enough for the kernel to begin allocating resources and accessing files.

### The Free List as a Stack

```python
def alloc_block(self):
    block_no = self.free_blocks.pop()             # O(1)
    disk_write(block_no, bytearray(BLOCK_SIZE))   # zero the physical sector
    return block_no

def free_block(self, block_no):
    self.free_blocks.append(block_no)             # O(1)
```

Both allocation and freeing are O(1) — a single list operation. No scanning, no searching, no bitmaps. The `disk_write` on allocation zeroes the physical sector before returning it, preventing leftover data from a previously deleted file from being readable in a new one. In v2, this zero-write travels the full path down to `_platter.write_sector()` — visible in the I/O log as a `WRITE` with `data=0000000000000000...` before any actual file data write.

### The Asymmetry of Inode Numbers

The inode free list begins at 2, not 0 or 1. Inode 0 is permanently "null" — used as the zero-value in directory entry slots to mean "empty." Inode 1 is permanently reserved for the root directory. This means the kernel always knows where the root is without any lookup, simply by opening inode 1. Both conventions come directly from UNIX V6.

---

## 10. Section 4 — The Inode: The Soul of a File

If there is one concept that separates those who understand UNIX from those who merely use it, it is the inode.

```python
class Inode:
    def __init__(self, ino):
        self.ino        = ino
        self.mode       = INODE_FREE
        self.link_count = 0
        self.size       = 0
        self.direct     = [0] * MAX_DIRECT_BLOCKS
        self.indirect   = 0
```

The inode is the metadata record for a single file. It answers: what kind of thing is this? How big is it? Where on the physical platter does its data live? How many names does it have? The inode deliberately does **not** answer one question: _what is its name?_ That omission is the most important design decision in the entire filesystem.

### The direct[] Array — Block Numbers Are Physical Addresses

```python
self.direct = [0] * MAX_DIRECT_BLOCKS   # [0, 0, 0, 0]
```

Each non-zero entry is an LBA block number. In v2 the `stat` command decodes each one all the way to its physical address:

```
[stat]  /home/alice/notes.txt
  Inode number : 30
  Type         : Regular File
  Size         : 35 bytes
  Link count   : 1
  LBA blocks   : [252]
    LBA 252 → Cylinder 7, Head 3, Sector 4  (byte 16128 on disk)
```

The block number stored in `direct[0] = 252` is simultaneously a filesystem abstraction (an LBA) and a physical disk address: `Cylinder 7, Head 3, Sector 4`. The `direct[]` array is, at bottom, a list of physical locations on the spinning platter. The connection between the inode and the magnetic surface is made visible here for the first time.

### The indirect Field

```python
self.indirect = 0   # 0 = not used
```

For files larger than `MAX_DIRECT_BLOCKS × BLOCK_SIZE`, the `indirect` field stores the LBA of a block whose _contents_ are more LBA block pointers rather than file data. Each of those pointers is itself an LBA that maps to a CHS address on the platter. The hierarchy of indirection is a hierarchy of physical addresses.

### The Global Inode Table

```python
inode_table = {i: Inode(i) for i in range(INODE_TABLE_SIZE + 1)}

def get_inode(ino):
    return inode_table[ino]
```

O(1) lookup by inode number. In a real filesystem, inodes are stored on disk at LBA 2–33 (physical sectors `C=0,H=0,S=2` through `C=1,H=0,S=1`). When the kernel needs an inode it has not cached, it reads the appropriate LBA through the controller — another CHS translation, another physical sector read.

---

## 11. Section 5 — The Directory: Names Are Just Labels

A directory is a special file whose data blocks contain a flat list of `(inode_number, filename)` pairs called directory entries.

```python
DIRENT_FORMAT = "I12s"    # 4-byte unsigned int + 12-byte ASCII string
DIRENT_SIZE   = 16        # bytes per entry
DIRENT_PER_BLOCK = 4      # 64 bytes / 16 bytes = 4 entries per sector
```

### Binary Serialisation with struct

```python
def pack_dirent(ino, name):
    return struct.pack("I12s", ino, name.encode("ascii")[:12])

def unpack_dirent(raw):
    ino, name_bytes = struct.unpack("I12s", raw)
    return ino, name_bytes.rstrip(b"\x00").decode("ascii")
```

The `struct` module serialises Python objects into the exact byte layout that appears on the disk sector. The round-trip is complete: Python object → `pack` → raw bytes → `disk_write` → controller CHS translation → physical sector → `disk_read` → controller CHS translation → raw bytes → `unpack` → Python object. Every name you look up started its journey as bytes magnetised into a specific CHS address on the platter.

### Directory Layout in a Physical Sector

A single 64-byte sector holds exactly four directory entries:

```
Byte  0–15:  [ inode=1  | name="."    ]
Byte 16–31:  [ inode=1  | name=".."   ]
Byte 32–47:  [ inode=32 | name="home" ]
Byte 48–63:  [ inode=30 | name="tmp"  ]
```

That 64-byte block lives at a specific LBA — say, 255 — which the controller translates to `C=7, H=3, S=7`. When you run `ls /`, the filesystem reads that one physical sector and scans its four 16-byte records.

### The Meaning of `.` and `..`

```python
dir_add_entry(new_inode, ".",  new_ino,    self.sb)
dir_add_entry(new_inode, "..", parent_ino, self.sb)
```

Ordinary directory entries, stored in ordinary sectors. The `.` entry holds the directory's own inode number; `..` holds the parent's. For root, both point to inode 1. Running `cd ..` in a shell reads the physical sector holding the current directory's block, finds the `..` entry, and loads the parent's inode number. No special kernel data structure is involved — just a sector read and a 16-byte record lookup.

### Empty Slots and Deletion

```python
# Mark a slot deleted — zero the inode field only
block_data[offset: offset + DIRENT_SIZE] = pack_dirent(0, "")
```

Deleted entries are not physically removed. The slot is zeroed in place. The bytes remain on the sector's magnetic surface with `ino=0`, which the scanner skips. New entries reuse empty slots before allocating new blocks. The platter is not rewritten to compact the directory.

---

## 12. Section 6 — Path Lookup: Walking the Tree

Path lookup transforms `/home/alice/notes.txt` into an inode number. Every step reads a physical sector through the controller.

```python
def path_lookup(path):
    parts = path.strip("/").split("/")
    current_ino = INODE_ROOT   # always start at inode 1

    for component in parts:
        current_inode = get_inode(current_ino)
        found_ino = dir_lookup(current_inode, component)
        current_ino = found_ino

    return current_ino
```

### Physical Trace of a Path Lookup

With `IO_TRACE = True`, resolving `/home/alice/notes.txt` would print:

```
Component "home":
  CTRL READ  LBA=255 → C=7, H=3, S=7   (root directory sector)
  Found: "home" → inode 32

Component "alice":
  CTRL READ  LBA=254 → C=7, H=3, S=6   (/home/ directory sector)
  Found: "alice" → inode 31

Component "notes.txt":
  CTRL READ  LBA=253 → C=7, H=3, S=5   (/home/alice/ directory sector)
  Found: "notes.txt" → inode 30
```

Three components, three physical sector reads, three CHS translations. A path with depth N costs N physical sector reads on a cold cache. This is why deep directory trees are slower on spinning disks — each level is a potential seek and a platter read.

The tree structure of the filesystem is not stored in any explicit data structure in memory. It is **implicit in the directory entries on the platter**, reconstructed on demand by walking sector by sector from the root inode. The path lookup algorithm has been essentially unchanged since UNIX V6, and it still runs in the Linux kernel today as `link_path_walk()`.

---

## 13. Section 7 — The MiniFS API: Tying It All Together

The `MiniFS` class is the filesystem's public interface — the equivalent of the POSIX system call layer. In v2, every method exposes the physical layer in its output, making the connection from API call to platter coordinate visible.

### `write_file()` — now shows CHS

```python
chs_list = [lba_to_chs(b) for b in used_blocks]
print(f"[write]  {path}  ({len(data)} bytes, "
      f"LBA blocks {used_blocks}, physical CHS {chs_list})")
```

Output:

```
[write]  /home/alice/notes.txt  (35 bytes, LBA blocks [252], physical CHS [(7, 3, 4)])
```

The inode now stores `direct[0] = 252`. That number is simultaneously a filesystem block number, an LBA, and the physical address `Cylinder=7, Head=3, Sector=4` on the platter.

### `stat()` — decodes every block to its physical address

```python
for lba in used:
    c, h, s = lba_to_chs(lba)
    print(f"  LBA {lba:>3} → Cylinder {c}, Head {h}, Sector {s}  "
          f"(byte {lba * SECTOR_SIZE} on disk)")
```

Every block pointer in the inode is decoded to its full physical address, including the byte offset from the beginning of the disk. This is the most direct answer to the question "where exactly is my file?"

### `dump_inodes()` — the whole table with CHS

```
[inodes]  Active Inode Table:
   INO  TYPE   LINKS    SIZE  LBA BLOCKS → CHS
     1  DIR        3      48  [255] → [(7, 3, 7)]
    30  FILE       2      35  [252] → [(7, 3, 4)]
    31  DIR        2      64  [253] → [(7, 3, 5)]
    32  DIR        3      48  [254] → [(7, 3, 6)]
```

The inode table with physical addresses in one view. Every directory and file is shown with its data's exact physical location.

### New Physical Disk Commands

**`geometry`** — full disk specification with live I/O counts from the `PhysicalPlatter` object.

**`diskmap`** — a visual grid of the entire platter, rows being cylinders, columns being head×sector combinations. Written sectors show their LBA number; empty sectors show `.`:

```
  C  7  |  .  .  .  .  .  .  .  .  .  .  .  .  . L252 L253 L254 L255
```

This reveals that our allocator assigns blocks from the end of the disk (high LBAs first, because `free_blocks.pop()` takes the last element). Files cluster in the final cylinder.

**`iolog [N]`** — the last N disk I/O operations with LBA and CHS. The closest thing in the simulator to Linux's `blktrace`.

**`lba N`** — translates one block number to CHS, byte offset, and filesystem role. Try `lba 0` through `lba 35` to see the full filesystem layout.

**`explain N`** — the most comprehensive command. Decodes one block through every layer: LBA, CHS, byte offset, whether it has been written, raw hex, and ASCII preview:

```
[explain]  Block 252:
  Filesystem view  : block number (LBA) = 252
  Controller view  : LBA 252 → Cylinder 7, Head 3, Sector 4
  Platter view     : byte offset 16128 on disk surface
  Written          : yes
  Raw hex (first 32): 48656c6c6f2066726f6d207468652070...
  ASCII preview     : Hello from the p
```

---

## 14. Hard Links: The Deepest Insight

Hard links demonstrate a fundamental truth: a file's data has a fixed physical location on the platter, and multiple names can point to that location through a single inode.

```python
def ln(self, existing_path, new_path):
    target_ino = path_lookup(existing_path)
    dir_add_entry(parent_inode, link_name, target_ino, self.sb)
    target_inode.link_count += 1
```

Creating a hard link allocates no new data blocks. It touches the platter only to write a new 16-byte directory entry. The new name points to the same inode, which holds the same `direct[]` LBA numbers, which map to the same physical CHS addresses.

After `ln /home/alice/notes.txt /home/alice/notes.bak`:

```
"notes.txt"  → inode 30 → direct[0]=252 → C=7,H=3,S=4 → bits on platter
"notes.bak"  → inode 30 → direct[0]=252 → C=7,H=3,S=4 → same bits
                 ↑ same inode              ↑ same physical location
```

Running `stat` on both names produces identical output, including the same Cylinder, Head, and Sector. The inode is the file; the names are labels pointing at it; the LBA is the disk address; the CHS is the physical seat.

This understanding immediately explains several behaviours that confuse new UNIX users: `mv` within the same filesystem is instantaneous because it only rewrites a directory entry — no data moves on the platter. `stat` shows the same inode number for two different filenames because they genuinely share one inode. Hard links to directories are forbidden because circular `..` entries would create infinite loops in path traversal.

---

## 15. Deletion: rm Is Actually Unlink

```python
def rm(self, path):
    removed_ino = dir_remove_entry(parent_inode, name)
    target_inode.link_count -= 1

    if target_inode.link_count == 0:
        for i, blk_ptr in enumerate(target_inode.direct):
            if blk_ptr != 0:
                self.sb.free_block(blk_ptr)   # returns LBA to free list
                target_inode.direct[i] = 0
        target_inode.mode = INODE_FREE
        self.sb.free_inode(removed_ino)
```

Deletion has two phases. Phase 1: zero out the 16-byte directory entry on one physical sector. Phase 2, only when `link_count` reaches 0: return the data block LBAs to the superblock's free list and mark the inode free.

Notice what "freeing a block" means physically. The LBA is appended to `free_blocks`. The physical sector on the platter is **not zeroed or overwritten**. The magnetic bits remain unchanged until that sector is allocated again for a future write. This is why deleted files can sometimes be recovered with forensic tools — `rm` removes the inode's reference to the sector, but the bits on the surface persist. Secure deletion tools like `shred` explicitly overwrite freed sectors with random data before returning them to the free list.

---

## 16. The Complete Layered Architecture

The simulator's sections form a genuine layered architecture spanning raw physics to user-visible operations.

```
┌──────────────────────────────────────────────────────────┐
│  SECTION 9 — Interactive Shell                           │  ← User interface
│  geometry, diskmap, iolog, lba, explain, ls, cat...      │
├──────────────────────────────────────────────────────────┤
│  SECTION 7 — MiniFS API                                  │  ← Filesystem API
│  mkdir, touch, write_file, read_file, ln, rm, stat       │     (syscall layer)
├──────────────────────────────────────────────────────────┤
│  SECTION 6 — Path Lookup                                 │  ← Name resolution
│  path_lookup(), path_split()                             │
├───────────────────────┬──────────────────────────────────┤
│  SECTION 5            │  SECTION 4                       │  ← Metadata layer
│  Directory ops        │  Inode table                     │
│  dir_lookup,          │  get_inode, Inode class          │
│  dir_add_entry,       │  direct[] = LBA pointers         │
│  dir_remove_entry     │                                  │
├───────────────────────┴──────────────────────────────────┤
│  SECTION 3 — Superblock                                  │  ← Allocation layer
│  alloc_block() → returns LBA                             │
│  free_block()  ← recycles LBA                           │
├──────────────────────────────────────────────────────────┤
│  SECTION 2 — disk_read() / disk_write()                  │  ← Stable I/O contract
│  The unchanged interface between FS and storage          │
├──────────────────────────────────────────────────────────┤
│  SECTION 0C — DiskController                             │  ← LBA→CHS bridge
│  .read(lba), .write(lba, data), io_log, IO_TRACE         │
├──────────────────────────────────────────────────────────┤
│  SECTION 0B — Geometry Translation                       │  ← Address math
│  lba_to_chs():  cylinder = LBA ÷ (heads × sectors)      │
│                 head     = (LBA ÷ sectors) mod heads     │
│                 sector   = LBA mod sectors               │
├──────────────────────────────────────────────────────────┤
│  SECTION 0A — PhysicalPlatter                            │  ← Raw storage
│  _storage[(c, h, s)] = bytearray(64)                    │
│  read_sector(c,h,s), write_sector(c,h,s,data)           │
├──────────────────────────────────────────────────────────┤
│  SECTION 1 — Constants                                   │  ← Geometry spec
│  BLOCK_SIZE = SECTOR_SIZE = 64                           │
│  TOTAL_BLOCKS = TOTAL_SECTORS = 8×4×8 = 256             │
└──────────────────────────────────────────────────────────┘
```

Each layer exposes a minimal, stable interface to the layer above. The filesystem never sees a cylinder number. The platter never sees an inode. The path lookup never sees a byte. This disciplined separation is not just good software engineering — it is the architecture of every storage system built in the last fifty years, from the first UNIX disk driver to modern NVMe SSDs.

---

## 17. Tracing a Single Write End-to-End

Let us follow `fs.write_file("/home/alice/notes.txt", "Hello!")` through every layer.

**Step 1: Path resolution (Sections 6 + 5)** `path_lookup` walks three components. Each `dir_lookup` calls `disk_read` on a directory sector. Each `disk_read` routes through `_controller.read(lba)`, which calls `lba_to_chs` and reads from `_platter._storage[(c,h,s)]`.

**Step 2: Inode retrieval (Section 4)** The path lookup returns inode 30. `get_inode(30)` returns the in-memory object immediately — no disk I/O. Inodes are cached in `inode_table`.

**Step 3: Allocate a new block (Sections 3 + 2 + 0C + 0B + 0A)** `sb.alloc_block()` pops LBA 252 from `free_blocks`. It immediately calls `disk_write(252, zeros)` to clear the sector. That call routes:

```
disk_write(252, zeros)
  → _controller.write(252, zeros)
  → lba_to_chs(252) = (7, 3, 4)
  → _platter.write_sector(7, 3, 4, zeros)
  → _storage[(7,3,4)] = bytearray(64)
```

**Step 4: Write file data (Sections 2 + 0C + 0B + 0A)** `disk_write(252, b"Hello!")` routes the same path, this time with actual content:

```
  → _controller.write(252, b"Hello!...")
  → lba_to_chs(252) = (7, 3, 4)
  → _platter.write_sector(7, 3, 4, b"Hello!...")
  → _storage[(7,3,4)] = b"Hello!\x00...\x00"
```

**Step 5: Update inode (Section 4)** `inode.direct[0] = 252` and `inode.size = 6`. In-memory only. A production filesystem would persist the updated inode to its sector at LBA 2–33.

**Step 6: Output**

```
[write]  /home/alice/notes.txt  (6 bytes, LBA blocks [252], physical CHS [(7, 3, 4)])
```

The 6 bytes of "Hello!" now live at `Cylinder 7, Head 3, Sector 4`, starting at byte `252 × 64 = 16128` on the simulated magnetic surface.

---

## 18. What This Simulator Deliberately Leaves Out

### Rotational Latency and Seek Time

Our platter performs all reads and writes in O(1) — a dict lookup. A real spinning disk incurs two sources of mechanical latency: **seek time** (moving the arm to the right cylinder, typically 3–15ms) and **rotational latency** (waiting for the correct sector to spin under the head, on average 2–8ms). These latencies are why disk layout matters enormously on spinning drives — sequential accesses to adjacent sectors cost one rotation, while random accesses scattered across the disk cost a seek plus a rotation each.

### No Buffer Cache

A real kernel maintains the **page cache** — recently accessed disk blocks held in RAM. Most reads hit the cache without touching the platter at all. Our simulator reads the platter dict on every `disk_read` call. The physical read/write counts shown by `geometry` and `df` would be dramatically smaller in a system with caching.

### No Command Queuing

Modern disk controllers and NVMe SSDs support **native command queuing** — they accept dozens of outstanding requests and reorder them to minimise total seek time, serving whichever pending request requires the least arm movement next. Our controller processes one request at a time, in strict order.

### No Error Correction

Real disk sectors include ECC bytes — extra data that allows the controller to detect and correct single-bit errors and detect multi-bit errors. A 512-byte "logical sector" is actually stored in a larger physical unit including parity and ECC fields, invisible to the OS. Our platter stores raw bytes with no redundancy.

### No Bad Sector Remapping

Real drives maintain a small reserve of hidden spare sectors. When a sector develops a surface defect, the controller transparently remaps that LBA to a spare, invisible to the OS. Our platter has no spares.

### No Journaling

If power fails mid-`mkdir` — after allocating an inode but before writing the directory entry — the filesystem is inconsistent. Real filesystems use **journaling** (ext4, XFS, NTFS) or **copy-on-write** (btrfs, ZFS) to ensure the disk is always recoverable. Our simulator has no crash safety.

### No Open File Table

In a real kernel, `open()` creates an entry in the process's open file table. Even if `link_count` reaches 0, the inode is not freed until all open descriptors are closed. Our simulator frees the inode immediately when `link_count == 0`.

---

## 19. How This Maps to Real Linux

Every layer of the simulator corresponds to real structures and tools in Linux.

### Inspecting Physical Disk Geometry

```bash
# Show disk geometry (cylinders, heads, sectors per track)
hdparm -g /dev/sda

# Show model, RPM, sector size
hdparm -I /dev/sda | grep -E "Model|rotation|Sector"

# Live block I/O tracing — equivalent to our iolog command
sudo blktrace -d /dev/sda -o - | blkparse -i -
```

### The ext4 Inode Structure

The `Inode` class corresponds to `struct ext4_inode` in `fs/ext4/ext4.h`:

```c
struct ext4_inode {
    __le16  i_mode;        /* type + permissions (our: mode) */
    __le16  i_links_count; /* hard link count (our: link_count) */
    __le32  i_size_lo;     /* file size in bytes (our: size) */
    __le32  i_block[15];   /* block pointers (our: direct[] + indirect) */
    ...
};
```

The `i_block[15]` array has 12 direct pointers, 1 indirect, 1 double-indirect, 1 triple-indirect — the same hierarchical structure as ours, extended to very large files.

### The ext4 Directory Entry

Corresponds to `struct ext4_dir_entry_2` in the kernel:

```c
struct ext4_dir_entry_2 {
    __le32  inode;              /* inode number (our: ino) */
    __le16  rec_len;            /* entry length */
    __u8    name_len;
    __u8    file_type;
    char    name[EXT4_NAME_LEN]; /* filename (our: name[12]) */
};
```

### Viewing Raw Inode and Block Data

```bash
# Show inode number
ls -i /home/alice/notes.txt

# Full inode metadata
stat /home/alice/notes.txt

# Raw inode dump from ext4 (requires debugfs)
sudo debugfs /dev/sda1 -R "stat /home/alice/notes.txt"

# Which physical blocks a file occupies
sudo debugfs /dev/sda1 -R "blocks /home/alice/notes.txt"

# Dump a raw block in hex (equivalent to our explain command)
sudo dd if=/dev/sda bs=4096 skip=<block_no> count=1 | xxd | head
```

### Verifying Hard Link and Deletion Behaviour

```bash
echo "hello" > original.txt
ln original.txt hardlink.txt
stat original.txt    # Links: 2, Inode: N
stat hardlink.txt    # Links: 2, Inode: N  ← same inode, same physical blocks
rm original.txt      # link_count → 1, platter unchanged
cat hardlink.txt     # still works
rm hardlink.txt      # link_count → 0, LBAs returned to free list
                     # bits remain on platter until sector is reused
```

---

## 20. Closing Thoughts

The v2 simulator now spans the complete journey of data: from a user typing a command in a shell, through the filesystem's inode and block allocation machinery, through the disk controller's LBA-to-CHS address translation, to bits stored at specific physical coordinates on a spinning magnetic platter — or, by analogy, in specific cells of a flash chip.

The key insights, now complete from the top of the stack to the bottom:

**The platter is the ground truth.** Everything above it — block numbers, inodes, directory entries, filenames, paths — is an abstraction. Ultimately, every byte of every file exists as a physical state at a (Cylinder, Head, Sector) coordinate. Every layer exists to make that physical fact usable by humans.

**LBA is the contract between the OS and the drive.** The operating system speaks in flat block numbers. The drive speaks in physical coordinates. The disk controller translates between them at every I/O. This clean interface is why an OS does not need to know whether it is talking to an HDD, an SSD, a RAID array, or network storage — they all accept LBA numbers and handle the physical details internally.

**The inode is the file. The name is a label. The block number is a physical address.** A file's identity is its inode number. Its data lives at the LBA numbers in `direct[]`. Those LBA numbers translate to physical disk addresses via the controller. The filename is a mapping in a directory entry, stored in its own physical sectors, pointing to the inode. None of these are the same thing.

**Interface stability enables independent evolution.** The filesystem was rewritten beneath a stable `disk_read(block_no)` / `disk_write(block_no, data)` interface. This is how the Linux VFS works: filesystems call the block layer through a fixed interface, and the block layer handles everything below — caching, queuing, error correction, device-specific addressing — without the filesystem knowing or caring.

**Deletion does not erase. It deallocates.** `rm` removes a directory entry and decrements a reference count. It does not touch the magnetic surface. The bits persist until the sector is reallocated and overwritten. Reference counting — not erasure — is the natural deletion model when multiple names can point to one object.

Begin at the platter. Follow a write from sector to inode to directory entry to path. Trace a read back in reverse. Run `blktrace` on a real Linux system and recognise, in the stream of LBA reads and writes, the exact same sequence you just watched in Python. The stack is the same — only the materials differ.

---

_Essay based on `mini_unix_fs_v2.py` — a Python simulator covering the complete storage stack from physical magnetic platter to UNIX filesystem API._

_Concepts rooted in: Lions' Commentary on UNIX 6th Edition Source Code, the ATA/SATA disk interface standard, the POSIX filesystem standard, and the Linux ext4 and block-layer implementations._
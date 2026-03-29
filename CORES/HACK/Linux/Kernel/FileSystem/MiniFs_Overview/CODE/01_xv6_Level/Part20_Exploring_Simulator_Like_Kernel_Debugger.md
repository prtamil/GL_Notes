# Part 20 — How to Explore the Simulator Like a Kernel Debugger

---

## The Simulator as an Interactive Kernel

The simulator is not just code to read — it is an interactive kernel you can interrogate. Every internal state that would require `gdb`, `dmesg`, `/proc`, or `debugfs` on a real system is directly accessible.

This part is a reference guide to using the inspection commands, with the actual expected output based on the real code constants.

---

## Starting Up

```python
from mini_unix_xv6_fs import *

fs = FileSystem()
fs.mkfs()   # format: writes superblock, root dir, blank bitmap
fs.mount()  # reads superblock, runs log.recover()
```

`mkfs()` prints the real layout (based on computed constants):
```
[mkfs]  Formatted 256-block filesystem
  Superblock at block 1  (magic 0x10203040)
  Log        at blocks 2–10
  Inodes     at blocks 11–18  (32 inodes, 4 per block)
  Bitmap     at block  19
  Data       at blocks 20–255  (236 blocks)
```

> If the printed output says different block numbers, the constants were changed. Always trust `mkfs()` output over comments in the file.

---

## Disk Inspection Commands

### `fs.geometry()` — Physical Disk Dimensions

```
[platter]  8cyl × 4heads × 8sec = 256 sectors × 64B = 16384B
  Physical reads=14  writes=22
```

Shows total platter I/O counts. Watch these grow as you perform operations. High read count with low write count indicates cache-heavy operation.

### `fs.diskmap()` — Physical Sector Occupancy Grid

```
[diskmap]  Physical Disk  (role or . )
  CYL  | H0S0 H0S1 H0S2 H0S3 H0S4 H0S5 H0S6 H0S7 H1S0 ...
  -----+----------------------------------------------------
  C  0 |  L1   L2   L3   L4   L5   L6   L7   L8  L9  L10  L11 ...
  C  1 |  .    .    .    ...
```

After `mkfs()`, blocks 1–19 (superblock through bitmap) are written. Block 20 onward appear as data is created. Each cell shows the LBA or `.` for unwritten.

### `fs.iolog(n)` — Last n Physical I/O Operations

```
[iolog]  Last 10 I/O operations:
  OP     LBA  CYL  HEAD  SEC  BYTE_OFF
  WRITE    1    0     0    1        64
  WRITE    2    0     0    2       128
  READ    11    0     1    3       704
  WRITE   11    0     1    3       704
  WRITE   19    0     2    3      1216
  WRITE   20    0     2    4      1280
```

Every `_raw_read` and `_raw_write` appears here with LBA, CHS, and byte offset. Use it to verify:
- Which blocks are accessed during a specific operation
- Whether cache is working (reads absent from iolog = cache hits)
- The ordering of writes during a commit (log data → log header → install → clear)

### `fs.explain_block(n)` — Decode Any Block

```python
fs.explain_block(11)
```

```
[explain]  Block 11:
  Role        : inode block (inums 1–4)
  LBA → CHS   : 11 → C=0 H=1 S=3
  Byte offset : 704
  In bcache   : YES
  On platter  : yes
  Hex[0:32]   : 02000100200000001000000000000000...
  ASCII[0:32] : .. . .  . . . . . . . . . . . . .
```

The role is decoded from the computed constants:
- Blocks 3–10 → `log data N`
- Blocks 11–18 → `inode block (inums X–Y)`
- Block 19 → `block bitmap`
- Blocks 20–255 → `data block`

Use `explain_block` to:
- Verify `b"Hello"` bytes in a data block
- Read raw inode fields from an inode block
- See bitmap bits after allocation/free
- Check log header state (block 2) during a transaction

---

## Filesystem State Commands

### `fs.sbdump()` — Superblock Fields

```
[superblock]  (disk block 1)
  magic      = 0x10203040
  size       = 256 blocks
  nblocks    = 236 data blocks
  ninodes    = 32
  nlog       = 8  logstart=2
  inodestart = 11
  bmapstart  = 19
  datastart  = 20
```

### `fs.dump_inodes()` — All Active Inodes

```
[inodes]  Inode table (disk blocks 11–18, 4 inodes/block):
  INUM   BLK   OFF  TYPE   NLINK    SIZE  ADDRS
     1    11     0  DIR        2      32  [20]+ind=0
     2    11    16  FILE       1       5  [22]+ind=0
```

Shows every non-UNUSED inode: disk block, offset within that block, type, nlink, size, and block pointers. Essential for verifying that `touch`, `mkdir`, `link`, and `unlink` update nlink correctly.

### `fs.stat("/path")` — Full Inode Detail with CHS

```
[stat]  /notes.txt
  inum        = 2  (disk block 11, offset 16)
  type        = Regular File
  nlink       = 1
  size        = 5 bytes
  open fds    = none
  direct blks = [22]
  indirect    = 0
    direct[0]  LBA=22 → C=0 H=2 S=6 (byte 1408)
```

Inode 2 is at block 11 offset 16. Its data is at LBA 22 = `(C=0, H=2, S=6)`.

### `fs.ls("/path")` — Directory Listing

```
[ls]  /  (inum=1, iblk=11):
  INUM  TYPE   SIZE  FDS  NAME
     1  DIR       32    0  .
     1  DIR       32    0  ..
     2  FILE       5    0  notes.txt
```

### `fs.df()` — Usage Statistics

```
[df]  Filesystem statistics:
  Total blocks   : 256  (data: 236)
  Free data blks : 234
  Used data blks : 2
  Buffer cache   : hits=45 misses=18 dirty=0
  Phys I/O       : reads=18 writes=22
  Log commits    : 2
  Open fds       : 0
```

---

## Cache and Log Commands

### `fs.cache()` — Buffer Cache State

```
[bcache]  8 entries  hits=45 misses=8 dirty=0 flushes=6
  BLK  REF  DIRTY  HEX[0:16]
    1    0     no  40302010...
    2    0     no  00000000...
   11    0     no  02000100...
   19    0     no  ffff0f00...
   20    0     no  01001400...
```

Dirty blocks have modifications not yet committed. After `log.end_op()` completes, dirty should be 0.

### `fs.logdump()` — Log State

```
[log]  outstanding=0  pending=[]  committed_transactions=2
  On-disk log header: n=0  blocks=[]
```

Shows whether a transaction is in progress (`outstanding > 0`), which blocks are pending commit (`pending=[...]`), and the on-disk log header. Use this to verify transactions start and end correctly.

---

## Live I/O Tracing

```python
with trace_io("writing notes.txt"):
    fs.write_file("/notes.txt", "Hello")
```

Output:
```
  ┌─ TRACE: writing notes.txt
  [BCACHE MISS] blk=11 loaded from disk
  [CTRL READ ] LBA= 11 → C=0 H=1 S=3
  [BALLOC] allocated block 22
  [BCACHE DIRTY] blk=19
  [BCACHE DIRTY] blk=22
  [BCACHE DIRTY] blk=11
  [LOG COMMIT] writing 3 blocks: [11, 19, 22]
  [CTRL WRITE] LBA=  3 → C=0 H=0 S=3  ...
  [CTRL WRITE] LBA=  4 → C=0 H=0 S=4  ...
  [CTRL WRITE] LBA=  5 → C=0 H=0 S=5  48656c6c6f...
  [CTRL WRITE] LBA=  2 → C=0 H=0 S=2  03000000 0b000000 13000000 16000000...
  [CTRL WRITE] LBA= 11 → C=0 H=1 S=3  ...
  [CTRL WRITE] LBA= 19 → C=0 H=2 S=3  ...
  [CTRL WRITE] LBA= 22 → C=0 H=2 S=6  48656c6c6f...
  [CTRL WRITE] LBA=  2 → C=0 H=0 S=2  00000000...
  └─ TRACE END: writing notes.txt
```

`48656c6c6f` = hex encoding of `"Hello"`. The log header write (`LBA=2`) contains `03000000` (n=3) followed by `0b000000 13000000 16000000` (blocks 11, 19, 22 in little-endian).

---

## Interactive Shell

The simulator also has a full interactive shell:

```python
interactive_shell(fs)
```

Gives a prompt `xv6fs:/$ ` with all commands available:

```
xv6fs:/$ mkdir /home
xv6fs:/$ touch /home/readme.txt
xv6fs:/$ write /home/readme.txt Hello World
xv6fs:/$ stat /home/readme.txt
xv6fs:/$ explain 11
xv6fs:/$ diskmap
xv6fs:/$ iolog 5
```

---

## A Debugging Session Template

When something unexpected happens:

```python
# 1. Current state
fs.ls("/")
fs.dump_inodes()
fs.df()

# 2. Check bitmap for allocation state
fs.explain_block(19)   # block 19 = bitmap

# 3. Check the suspicious inode
fs.stat("/suspicious/path")

# 4. Check the suspicious data block
fs.explain_block(n)

# 5. Log state
fs.logdump()

# 6. Recent I/Os
fs.iolog(20)

# 7. Cache dirty state
fs.cache()
```

---

## Connecting Simulator Commands to Linux Tools

| Simulator command | Linux equivalent | What it shows |
|-------------------|-----------------|---------------|
| `fs.diskmap()` | `hdparm --read-sector` | which sectors are written |
| `fs.iolog()` | `blktrace` / `iostat` | physical I/O operations |
| `fs.explain_block(n)` | `debugfs dump_block n` | raw block contents |
| `fs.stat(path)` | `stat` + `debugfs stat` | inode fields + CHS address |
| `fs.dump_inodes()` | `debugfs ls -l` | all active inodes |
| `fs.sbdump()` | `debugfs show_super_stats` | superblock fields |
| `fs.cache()` | `/proc/sys/vm/dirty_*` | buffer cache state |
| `trace_io(...)` | `strace -e read,write` | per-call I/O trace |
| `fs.df()` | `df -i` | block and inode usage |
| `fs.logdump()` | `debugfs logdump` | journal/log state |

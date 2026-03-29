# Part 6 — Superblock (Filesystem Geometry)

---

## What Problem the Superblock Solves

When a kernel mounts a filesystem, it has no built-in knowledge of how that filesystem was laid out. How many blocks total? Where does the inode table start? Where is the bitmap? These values were fixed at format time by `mkfs`, and they can vary between filesystems.

The superblock is the answer: a fixed-size record at a fixed location (block 1) that describes the entire layout. It is the first thing the kernel reads when mounting.

---

## The On-Disk Format

The superblock lives at block 1. Its format mirrors xv6 `struct superblock` in `kernel/fs.h`:

```python
# magic(4) size(4) nblocks(4) ninodes(4) nlog(4) logstart(4) inodestart(4) bmapstart(4)
SB_FMT  = "8I"   # eight unsigned 32-bit integers = 32 bytes
SB_SIZE = struct.calcsize(SB_FMT)  # = 32 bytes
```

Eight fields, each 4 bytes, totaling 32 bytes. The remaining 32 bytes of the 64-byte block are unused.

| Field        | Value        | Meaning                                        |
|--------------|--------------|------------------------------------------------|
| `magic`      | `0x10203040` | Identifies this filesystem type                |
| `size`       | 256          | Total blocks on disk                           |
| `nblocks`    | 236          | Usable data blocks (`TOTAL_BLOCKS - DATA_START = 256 - 20`) |
| `ninodes`    | 32           | Total inode slots                              |
| `nlog`       | 8            | Log size in blocks (`LOGSIZE`)                 |
| `logstart`   | 2            | Block number of log header                     |
| `inodestart` | 11           | First block of inode table (`INODE_START`)     |
| `bmapstart`  | 19           | Block number of block bitmap (`BMAP_START`)    |

---

## The Magic Number

```python
FSMAGIC = 0x10203040
```

The first field in every filesystem superblock is a magic number — a distinctive byte sequence that identifies the filesystem type. If you read block 1 from a disk formatted with a different filesystem, the magic number will be wrong and `mount()` will refuse:

```python
if sb.magic != cls.MAGIC:
    raise OSError(f"Bad superblock magic: {sb.magic:#x} (expected {cls.MAGIC:#x})")
```

Real filesystem magic numbers: ext4 = `0xEF53`, btrfs = `_BHRfS_M` in ASCII.

---

## Writing and Reading the Superblock

**Writing** (called by `mkfs()`):

```python
def write_to_disk(self):
    raw = struct.pack(SB_FMT,
                      self.magic, self.size, self.nblocks, self.ninodes,
                      self.nlog, self.logstart, self.inodestart, self.bmapstart)
    buf = bytearray(BLOCK_SIZE)
    buf[:len(raw)] = raw
    _raw_write(1, buf)
```

`_raw_write` is called directly — bypassing the buffer cache and the log. The superblock is written once at format time and never modified by normal operations. It is not part of a logged transaction.

**Reading** (called by `mount()`):

```python
@classmethod
def read_from_disk(cls):
    raw  = _raw_read(1)
    vals = struct.unpack(SB_FMT, raw[:SB_SIZE])
    sb   = cls.__new__(cls)
    (sb.magic, sb.size, sb.nblocks, sb.ninodes,
     sb.nlog, sb.logstart, sb.inodestart, sb.bmapstart) = vals
    if sb.magic != cls.MAGIC:
        raise OSError(...)
    return sb
```

`cls.__new__(cls)` creates an instance without calling `__init__`, then populates fields directly from disk bytes.

---

## The Mount Sequence

```python
def mount(self):
    global _sb
    _sb = Superblock.read_from_disk()
    log.recover()
```

Mount does exactly two things:

1. Read the superblock into the global `_sb`. After this, any code that needs geometry reads from `_sb` rather than hardcoded constants.

2. Run `log.recover()`. Replay any committed-but-not-installed log entries from a previous crash. This must happen before any filesystem operation touches disk.

---

## The Superblock Is the Bootstrap

The superblock is a contract between `mkfs` and `mount`. `mkfs` decides the layout and writes it to block 1. `mount` reads block 1 and trusts it completely.

The `Superblock` class constructor fills in the actual computed values:

```python
class Superblock:
    def __init__(self):
        self.magic      = self.MAGIC       # 0x10203040
        self.size       = TOTAL_BLOCKS     # 256
        self.nblocks    = TOTAL_BLOCKS - DATA_START  # 256 - 20 = 236
        self.ninodes    = NINODES          # 32
        self.nlog       = LOGSIZE          # 8
        self.logstart   = LOGSTART         # 2
        self.inodestart = INODE_START      # 11
        self.bmapstart  = BMAP_START       # 19
```

Every field maps directly to a constant from Section 1.

---

## Inspecting the Superblock

```python
fs.sbdump()
```

Output after `mkfs()`:
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

Also verify raw bytes:
```python
fs.explain_block(1)
```

The hex dump shows 32 bytes of packed integers: `40302010` (magic in little-endian), `00010000` (256), `ec000000` (236), etc.

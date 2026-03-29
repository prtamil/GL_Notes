# Part 3 — Raw Disk and Controller Abstraction

---

## What Lives Below the Filesystem

Every filesystem textbook starts with inodes. But inodes are stored on something. That something is a physical disk — a spinning aluminium platter coated in magnetic material, with a read/write arm that moves across its surface. The filesystem does not talk to the platter directly. Between them sits a controller.

The simulator makes all three layers visible:

```
filesystem  →  block number  →  DiskController  →  CHS address  →  PhysicalPlatter
```

This is Sections 0A through 0D in `mini_unix_xv6_fs.py`.

---

## Section 0A: The Physical Platter

A real hard disk has multiple platters on a shared spindle. Each platter surface has a read/write head. Data is stored as magnetic polarities in small regions called sectors.

The simulator models platter storage as a 3D dictionary:

```python
self._storage = {}  # key: (cylinder, head, sector), value: bytearray(SECTOR_SIZE)
```

The geometry:

```python
SECTOR_SIZE        = 64    # bytes per sector
NUM_CYLINDERS      = 8     # cylinder rings
HEADS_PER_CYLINDER = 4     # read/write heads (one per platter surface)
SECTORS_PER_TRACK  = 8     # sectors per track
TOTAL_SECTORS      = 8 × 4 × 8 = 256
```

Every sector is identified by three coordinates — `(cylinder, head, sector)`. A cylinder is a "ring" at a fixed radius across all platter surfaces. A head is one surface of one platter. A sector is a pie-slice of one track.

On a real disk, moving between cylinders requires physically moving the arm (seek latency). Switching heads is instantaneous (electronic). Waiting for a specific sector means waiting for the platter to rotate (rotational latency). The simulator ignores all of these costs — but the addressing structure is real.

Reading an unwritten sector returns zeros, just like a freshly degaussed disk:

```python
def read_sector(self, c, h, s):
    key = (c, h, s)
    if key not in self._storage:
        return bytearray(SECTOR_SIZE)   # all zeros
    return bytearray(self._storage[key])
```

Writing stores a padded `bytearray`:

```python
def write_sector(self, c, h, s, data):
    buf = bytearray(SECTOR_SIZE)
    buf[:len(data)] = data
    self._storage[(c, h, s)] = buf
```

The platter validates addresses and rejects out-of-range coordinates. Beyond that, it knows nothing — no filenames, no inodes, no structure at all.

---

## Section 0B: LBA ↔ CHS Translation

Operating systems do not want to reason about disk geometry. Instead they use Logical Block Addressing: a flat sequence of block numbers starting at 0.

The conversion formula between LBA and CHS is fixed and deterministic:

```python
def lba_to_chs(lba):
    c = lba // (HEADS_PER_CYLINDER * SECTORS_PER_TRACK)   # which cylinder ring
    h = (lba // SECTORS_PER_TRACK) % HEADS_PER_CYLINDER   # which head
    s = lba % SECTORS_PER_TRACK                            # which sector
    return c, h, s
```

Working through an example. LBA = 20 (the first data block, `DATA_START=20`):

```
c = 20 // (4 × 8) = 20 // 32 = 0
h = (20 // 8) % 4  = 2 % 4   = 2
s = 20 % 8         =          4
```

So block 20 lives at `(Cylinder=0, Head=2, Sector=4)`.

Another example — LBA = 11 (first inode block, `INODE_START=11`):

```
c = 11 // 32 = 0
h = (11 // 8) % 4 = 1 % 4 = 1
s = 11 % 8 = 3
```

Block 11 lives at `(Cylinder=0, Head=1, Sector=3)`.

The reverse:

```python
def chs_to_lba(c, h, s):
    return (c * HEADS_PER_CYLINDER + h) * SECTORS_PER_TRACK + s
```

These two functions are the entire geometry layer. Everything above uses block numbers. Everything below uses CHS.

---

## Section 0C: The Disk Controller

The controller bridges the filesystem and the platter. It performs translation, logs every operation, and produces the diskmap visualization.

```python
class DiskController:
    def read(self, lba):
        c, h, s = lba_to_chs(lba)
        if IO_TRACE:
            print(f"  [CTRL READ ] LBA={lba:>3} → C={c} H={h} S={s}")
        self.io_log.append(("READ ", lba, c, h, s))
        return self.platter.read_sector(c, h, s)

    def write(self, lba, data):
        c, h, s = lba_to_chs(lba)
        if IO_TRACE:
            print(f"  [CTRL WRITE] LBA={lba:>3} → C={c} H={h} S={s}")
        self.io_log.append(("WRITE", lba, c, h, s))
        self.platter.write_sector(c, h, s, data)
```

Every read and write goes through `lba_to_chs` and lands in `io_log`. This log is what powers `fs.iolog()` — the simulator's equivalent of Linux `blktrace`.

---

## Section 0D: The IO Trace Context Manager

You can enable live tracing for any block of code:

```python
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
```

Usage:

```python
with trace_io("writing notes.txt"):
    fs.write_file("/notes.txt", "Hello, world")
```

During that block, every `disk_read` and `disk_write` prints its LBA and CHS coordinates. After the block, tracing reverts to its previous state. This is the same pattern used by Linux `strace` and `ftrace` — scoped observation without permanent state change.

---

## The Raw I/O Interface

Between the controller and the filesystem, Section 2 defines two thin wrappers:

```python
def _raw_read(blockno):
    """Direct disk read — bypasses all caches. Only bcache may call this."""
    return _controller.read(blockno)

def _raw_write(blockno, data):
    """Direct disk write — bypasses all caches. Only log/bcache may call this."""
    buf = bytearray(BLOCK_SIZE)
    buf[:len(data)] = data
    _controller.write(blockno, buf)
```

The docstrings are important: only `bcache` and the log layer are permitted to call `_raw_read` and `_raw_write`. Everything else must go through the buffer cache. This enforces the layering discipline — the filesystem code never accesses the platter directly.

---

## What This Layer Demonstrates

The three-layer hardware model illustrates a principle that runs through all of systems programming: **stable interfaces absorb complexity**.

The filesystem was originally written to use a simple dict for disk storage (`disk[blockno] = data`). When the physical platter layer was added, only `_raw_read` and `_raw_write` needed to change. Every filesystem function above remained identical.

This is the same reason Linux's VFS layer can support ext4, btrfs, tmpfs, and NFS — all behind the same `read()`/`write()` interface. The interface is the contract. What lies beneath the interface is an implementation detail.

---

## What You Can Observe

```python
fs.geometry()   # print platter dimensions and I/O counts
fs.diskmap()    # grid showing which (C,H,S) cells have been written
fs.iolog(20)    # last 20 disk operations with LBA and CHS
```

After creating a few files, `diskmap()` shows you exactly which physical sectors are occupied. You can correlate each LBA back to a filesystem role using `explain_block()`.

This is the only level in the entire stack where you can see a filename-to-magnetic-surface path rendered completely. No abstraction is hidden.

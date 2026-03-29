# Part 5 — Log Layer (Correctness Contract)

---

## The Problem: Power Can Fail at Any Moment

Consider writing a file. The filesystem must:

1. Allocate a data block (update bitmap at block 19)
2. Write the data to that block
3. Update the inode to point to the data block
4. Update the inode's size field

These are four separate disk writes. Power can fail after any one of them. If it fails after step 1 but before step 3, you have a block marked as allocated but no inode pointing to it — a leaked block. The filesystem is inconsistent.

The log layer prevents this. Its guarantee: **all writes in a transaction are either all applied or all discarded**. There is no intermediate state.

---

## Write-Ahead Logging in Three Sentences

Before writing anything to its final disk location, write it to the log first. Only after the entire transaction is safely in the log, copy it to the final locations. Only after all final writes succeed, clear the log.

If power fails at any point, replay the log on next mount. If the log is not fully committed, ignore it. If it is committed, re-apply it. Either way, the filesystem is consistent.

---

## The Log Disk Layout

The log occupies a fixed region of the disk:

```
Block 2 (LOGSTART)      : Log header
Blocks 3–10             : Log data (LOGSIZE=8 blocks)
```

The log header (`struct logheader` in xv6) stores:
- `n` — how many blocks are committed in this transaction
- `block_nos[LOGSIZE]` — the home addresses of the committed blocks

```python
LOG_HDR_FMT  = f"I{LOGSIZE}I"   # one int (count) + 8 ints (block numbers)
# With LOGSIZE=8: "I8I" = 9 × 4 bytes = 36 bytes — fits in 64-byte block 2
LOG_HDR_SIZE = struct.calcsize(LOG_HDR_FMT)
```

Writing the log header with `n > 0` is the **commit point**.

---

## The Four-Step Commit Protocol

```python
def _commit(self):
    blocks = list(self.pending_writes)

    # Step 1: write modified blocks into log data area (blocks 3..10)
    for i, blockno in enumerate(blocks):
        log_block = LOGSTART + 1 + i   # 3, 4, 5, ...
        data = bcache.bread(blockno)
        bcache.brelse(blockno)
        _raw_write(log_block, data)

    # Step 2: write log header — THIS IS THE COMMIT POINT
    self._write_log_header(blocks)

    # Step 3: install — copy log blocks to home locations
    self._install_trans(blocks)

    # Step 4: clear log header — transaction complete
    self._write_log_header([])

    for blockno in blocks:
        bcache.bunpin(blockno)

    self.pending_writes.clear()
    self.log_count += 1
```

**Step 1**: For each block in the transaction, read its current (modified) data from the buffer cache and write it to a log data block (at `LOGSTART + 1 + i`). After this step the log area holds the new versions of all modified blocks, but the log header still says `n=0`.

**Step 2**: Write the log header with the count and block numbers. This single write is the commit point. It is atomic (one sector write). Either it completes or it doesn't.

**Step 3**: Copy each log data block to its home location. If power fails during this, recovery will redo these copies (log header says `n > 0`).

**Step 4**: Write the log header with `n=0`. The log is reusable.

---

## The Three Failure Scenarios

**Failure before Step 2 (before commit point)**:
Log header has `n=0`. Recovery reads `n=0`, does nothing. The transaction is discarded. Home blocks unchanged — as if the operation never happened.

**Failure during Step 3 (after commit, before install completes)**:
Log header has `n > 0`. Recovery calls `_install_trans()` again, re-copying all log blocks to their home locations. Idempotent — doing it twice has the same effect as once.

**Failure during Step 4 (after install, before log cleared)**:
Log header still has `n > 0`. Recovery replays the install again (harmless, data already written), then clears the header.

In every case: **the filesystem ends up consistent**.

---

## The begin_op / log_write / end_op API

### `begin_op()`

```python
def begin_op(self):
    self.outstanding += 1
```

Marks the start of a filesystem operation. In xv6 this also waits if the log is full or a commit is in progress.

### `log_write(blockno)`

```python
def log_write(self, blockno):
    if blockno not in self.pending_writes:
        if len(self.pending_writes) >= LOGSIZE:
            raise OSError(f"Log full!  Max {LOGSIZE} blocks per transaction.")
        self.pending_writes.append(blockno)
        bcache.bpin(blockno)   # pin so it stays in cache until commit
```

Records that `blockno` has been modified. The block's current data in the buffer cache is what will be committed. Pinning prevents cache eviction before the commit. If `log_write` is called twice for the same block, the second call is a no-op — only one log entry per block per transaction.

### `end_op()`

```python
def end_op(self):
    self.outstanding -= 1
    if self.outstanding == 0 and self.pending_writes:
        self._commit()
```

When `outstanding` reaches zero, all operations have finished and `_commit()` runs.

---

## Recovery on Mount

```python
def recover(self):
    raw = _raw_read(LOGSTART)   # read block 2
    n, *block_nos = struct.unpack(LOG_HDR_FMT, raw[:LOG_HDR_SIZE])
    blocks = block_nos[:n]
    if blocks:
        print(f"[log] recovering {n} uncommitted block(s): {blocks}")
        self._install_trans(blocks)
        self._write_log_header([])
```

Called by `mount()` before any filesystem operations. Reads the log header from block 2. If `n > 0`, calls `_install_trans()` to complete the interrupted install, then clears the header. The same install logic that runs during a normal commit.

---

## Every Mutation Must Call log_write

The pattern every filesystem modification follows:

```python
disk_write(blockno, data)    # update block in buffer cache
log.log_write(blockno)       # register block in current transaction
```

You'll see this exact pair in `_bitmap_alloc`, `_iupdate`, `writei`, `dirlink`, and `_bmap`. If you skip `log_write` for a modification, that block will not be included in the commit and the write may be lost on crash.

---

## Observing the Log

```python
fs.logdump()
```

Output after a fresh filesystem with one file:
```
[log]  outstanding=0  pending=[]  committed_transactions=2
  On-disk log header: n=0  blocks=[]
```

After starting a transaction but before `end_op`:
```
[log]  outstanding=1  pending=[11, 19, 20]  committed_transactions=2
  On-disk log header: n=0  blocks=[]
```

The pending list shows which blocks will be committed. The on-disk header shows what the last committed state was. After `end_op`:
```
[log]  outstanding=0  pending=[]  committed_transactions=3
  On-disk log header: n=0  blocks=[]
```

---

## Connection to Databases

Write-ahead logging is the same technique used by every ACID-compliant database:

| System | Write-ahead area | Commit point | Replay on recovery |
|--------|-----------------|--------------|-------------------|
| xv6 log | blocks 3–10 | log header write | `recover()` |
| PostgreSQL | `pg_wal/` | WAL record flush | recovery on startup |
| SQLite WAL | `.wal` file | WAL frame header | checkpoint |
| RocksDB | WAL file | sync | replay on open |

xv6's log layer is the smallest, clearest implementation of this pattern. Understanding it makes every database WAL immediately recognizable.

# Part 16 — Crash Recovery Replay Model

---

## What Recovery Must Handle

Power can fail at any point during a filesystem operation. After power is restored and the system reboots, the kernel must decide what state the filesystem is in and repair it if necessary.

The log layer's design makes this decision simple: **read the log header. If n > 0, the transaction committed — replay it. If n = 0, nothing committed — the filesystem is clean.**

There is no need to scan the entire filesystem for inconsistencies. No fsck required for normal crash recovery. The log provides a precise record of what was in progress.

---

## The Recovery Function

```python
def recover(self):
    raw = _raw_read(LOGSTART)
    n, *block_nos = struct.unpack(LOG_HDR_FMT, raw[:LOG_HDR_SIZE])
    blocks = block_nos[:n]
    if blocks:
        print(f"[log] recovering {n} uncommitted block(s): {blocks}")
        self._install_trans(blocks)
        self._write_log_header([])
    else:
        if IO_TRACE: print(f"  [LOG] clean — no recovery needed")
```

Called by `mount()` before any other operation. Reads block 2 (the log header), checks `n`. If `n > 0`: call `_install_trans()` to re-apply the committed writes, then clear the header. If `n == 0`: done.

---

## The Three Failure Scenarios in Detail

### Scenario A: Crash Before the Commit Point

The log header on disk still has `n=0`. During recovery, `recover()` reads `n=0` and does nothing.

The home blocks on disk are unchanged — whatever state they were in before the operation started. The operation is completely discarded. The filesystem is as if the operation never happened.

Example: Power fails during Step 1 of commit (writing log data blocks to disk). The log header was not yet written with `n > 0`. Recovery: `n=0` → do nothing. The inode, bitmap, and data blocks are unchanged. The file was not written.

### Scenario B: Crash After the Commit Point, Before Install

Power fails after Step 2 (the log header write) but before Step 3 (installing blocks to home locations) is complete. On disk:
- Log header: `n=3, blocks=[7,15,16]` ← committed
- Log data blocks 3, 4, 5: contain the modified versions of blocks 7, 15, 16
- Home blocks 7, 15, 16: partially updated (some may have been written, some not)

Recovery: `n=3` → call `_install_trans([7, 15, 16])`:

```python
def _install_trans(self, blocks):
    for i, blockno in enumerate(blocks):
        log_block = LOGSTART + 1 + i
        data = _raw_read(log_block)
        _raw_write(blockno, data)
        bcache.bwrite(blockno, data)
        bcache.bflush(blockno)
```

Re-reads each log data block and writes it to its home location. Then clears the log header.

**Idempotent**: if some home blocks were already installed before the crash, writing them again from the log has the same effect. The log data is the authoritative committed version.

### Scenario C: Crash After Install, Before Log Clear

Home blocks are fully installed. The log header still says `n=3` (Step 4 didn't complete). Recovery: re-runs `_install_trans()`, writes all home blocks again (same data, no change), then clears the header. Harmless.

---

## The Commit Point Is Atomic

The entire safety argument rests on one assumption: **writing the log header is atomic**.

This means: either the entire log header is written (with `n > 0` and the correct block list), or it isn't written at all (still `n=0`). There is no "partial write" where `n=3` but only two block numbers are written.

On real disks, a single sector write (512 bytes, or 4096 bytes on newer disks) is typically atomic — the disk firmware guarantees it either completes or is discarded. The log header is 32 bytes, well within one sector.

This is why the log header write is Step 2 rather than Step 1: you must write all the log data first, then write the header. If you wrote the header first and then crashed before writing the log data, you'd have a committed transaction pointing to garbage log blocks.

---

## Why Log Order Matters

The four-step commit has a strict ordering requirement:

```
Step 1 (log data)    must complete before Step 2 (log header)
Step 2 (log header)  must persist before Step 3 (install)
Step 3 (install)     must complete before Step 4 (clear header)
```

Each step has a disk write barrier. In xv6, this is achieved by using blocking disk writes at each step. In modern systems, disk write barriers (flush commands) are explicit. In the simulator, `_raw_write()` is synchronous — it completes before returning, so the ordering is natural.

If Step 1 could be reordered with Step 2 (e.g., by a write-reorder in the disk firmware), the log would be unsafe. This is why real WAL implementations use explicit fsync/fdatasync calls and sometimes O_DIRECT I/O to bypass OS caching and force ordered disk writes.

---

## Simulating a Crash

You can simulate a crash in the simulator by calling the recovery function directly on a filesystem where a transaction was in progress. Or more precisely, you can observe the log state mid-transaction with `fs.logdump()`:

```python
log.begin_op()
# ... make some modifications ...
# DON'T call log.end_op()
fs.logdump()   # shows pending_writes, outstanding=1
```

Output:
```
[log]  outstanding=1  pending=[7, 15, 16]  committed_transactions=3
  On-disk log header: n=0  blocks=[]
```

The in-memory log has pending writes, but `n=0` on disk because `end_op` hasn't been called. A crash here would discard all the changes.

After calling `log.end_op()` and then `fs.logdump()`:
```
[log]  outstanding=0  pending=[]  committed_transactions=4
  On-disk log header: n=0  blocks=[]
```

The transaction committed and the log was cleared.

---

## Connection to Database Recovery

The xv6 log is a minimal write-ahead log. The concepts map directly to database systems:

| xv6 log           | PostgreSQL WAL       | SQLite WAL mode |
|-------------------|----------------------|-----------------|
| `begin_op()`      | `BEGIN`              | Transaction start|
| `log_write(b)`    | WAL record write     | WAL frame write |
| Commit point      | WAL flush (fsync)    | WAL header write|
| `_install_trans`  | Checkpoint           | Checkpoint      |
| `recover()`       | Recovery on startup  | Recovery        |

The fundamental pattern — write to a log first, mark committed, then apply to main storage — is universal. xv6's implementation is the clearest possible version of this pattern.

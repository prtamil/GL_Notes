# Part 1 — What xv6 Filesystem Is Solving

---

## The Problem Every Filesystem Must Solve

A filesystem exists to answer one question: **how do you durably map names to bytes?**

That sounds simple. But it breaks into five distinct sub-problems, and every design decision in a filesystem is a response to one of them.

```
1. Where do the bytes live on disk?
2. How do you find them again from a name?
3. What happens if power fails mid-write?
4. How do multiple processes share access safely?
5. How do you reuse space when files are deleted?
```

xv6's filesystem solves all five. The simulator `mini_unix_xv6_fs.py` implements all five layers in pure Python so you can trace each one in isolation.

---

## Why xv6 Is the Right Study Target

xv6 is a small UNIX reimplementation written by MIT professors for the 6.828 operating systems course. Its filesystem is roughly 900 lines of C across three files:

```
kernel/bio.c      — buffer cache
kernel/log.c      — write-ahead log
kernel/fs.c       — everything else (superblock, bitmap, inodes, directories)
```

It is the **smallest complete UNIX filesystem** that exists. Every production filesystem — ext4, btrfs, ZFS, NTFS, APFS — is a more complex version of the same ideas. Study xv6's filesystem and you have the mental model to navigate all of them.

The simulator maps each source file exactly:

| xv6 source file       | Simulator section | What it handles                        |
|-----------------------|-------------------|----------------------------------------|
| `kernel/virtio_disk.c`| Section 2         | Raw disk I/O (reads/writes blocks)     |
| `kernel/bio.c`        | Section 2B        | Buffer cache — `bread/bwrite/brelse`   |
| `kernel/log.c`        | Section 2C        | Write-ahead log — crash safety         |
| `kernel/fs.c`         | Sections 3–6      | Superblock, bitmap, inodes, dirs, paths|
| `kernel/file.c`       | Section 8         | File descriptor table                  |
| `kernel/sysfile.c`    | Section 7         | Syscall implementations: open/link/unlink |
| `mkfs/mkfs.c`         | `FileSystem.mkfs()`| Disk formatter                        |

---

## The Two Core Contracts

Every filesystem makes two contracts with its users. xv6 makes both explicit.

### Contract 1: Performance (Buffer Cache)

Reading from disk is slow. The buffer cache (`kernel/bio.c`) keeps recently-used blocks in memory. If you read the same inode block ten times during a path traversal, it hits physical disk only once. This is the **performance contract**: the filesystem will not read the same block from disk more than necessary.

### Contract 2: Correctness (Write-Ahead Log)

Writing to disk is dangerous. If power fails after you update the inode but before you update the directory entry, the filesystem is corrupt. The write-ahead log (`kernel/log.c`) prevents this: all writes in one operation are either all applied or all discarded. This is the **correctness contract**: the filesystem will never be left in a half-written, inconsistent state.

Everything else in the filesystem — inodes, directories, path lookup, block allocation — sits on top of these two contracts.

---

## What the Five Layers Actually Are

Reading the simulator's layer diagram from top to bottom tells you what each layer is responsible for:

```
Shell / User API          — human-readable commands: mkdir, write, read, ls
File Descriptor Table     — what open() returns; tracks per-process state
Filesystem Operations     — mkdir, link, unlink, create implementations
Path Lookup               — "/home/alice/notes.txt" → inode number 4
Directory Layer           — inode 4 → block containing 16-byte name entries
Inode Layer               — inode 4 → {size, type, block pointers}
Block Allocator (bitmap)  — which blocks are free
Superblock                — total blocks, where each region starts
Log Layer                 — crash-safe write batching
Buffer Cache              — block-level RAM cache
Raw Disk I/O              — controller.read(lba) / controller.write(lba, data)
Disk Controller           — LBA block number → (cylinder, head, sector)
Physical Platter          — actual bytes stored at (c, h, s)
```

Each layer knows about exactly one abstraction below it and exposes exactly one abstraction above it. The platter knows nothing about filenames. The path lookup layer knows nothing about disk geometry. This separation is not an accident — it is the core design principle of UNIX storage.

---

## What the Simulator Adds Over Raw xv6

The simulator extends xv6 with a physical disk model (Sections 0A–0D) that xv6 abstracts away. In xv6, `virtio_disk.c` talks to virtual hardware — you never see the actual geometry. The simulator exposes:

- A `PhysicalPlatter` with real cylinder/head/sector addresses
- A `DiskController` that logs every LBA↔CHS translation
- A `trace_io()` context manager that prints every disk operation during execution

This means you can trace a single `write("/notes.txt", "Hello")` all the way from filename to the physical byte offset on a simulated magnetic platter.

---

## Reading This Codebase

The simulator is structured as a single file where each section number corresponds exactly to its xv6 source equivalent. When you read a function like `_bmap()` in Section 4, you can look up `bmap()` in `kernel/fs.c` and find the same algorithm in C.

The Python is deliberately explicit. Where xv6 uses pointer arithmetic and bit manipulation without comment, the simulator adds labels and traces. The goal is not to be idiomatic Python — it is to be readable xv6.

Start by running `mkfs()` and watching the output. Then write a file and call `diskmap()`. Every byte has a story.

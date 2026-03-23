Great question. **Block groups are the most important design idea in modern Unix filesystems.** Once you understand them deeply, disk filesystems stop feeling mysterious.

We’ll use ext4 as the reference implementation from the Linux Kernel.

---

# 1. The Problem Early Filesystems Had

Early Unix filesystems stored things like this:

```
[ superblock ]
[ inode table ]
[ data blocks ]
```

When a file grows, the OS may allocate blocks **far away on disk**.

Example:

```
inode → block 100
       → block 4000
       → block 90000
```

On spinning disks this caused **huge seek times**.

Disk heads had to move constantly.

So BSD introduced a brilliant idea:

**Divide the disk into smaller regions.**

These are **block groups**.

---

# 2. What a Block Group Is

A **block group** is a small self-contained chunk of the filesystem.

Each block group contains **everything needed to store files locally**.

Typical structure:

```
Block Group
 ├── Block Bitmap
 ├── Inode Bitmap
 ├── Inode Table
 └── Data Blocks
```

This layout repeats across the disk.

Example disk:

```
Disk
 ├── Block Group 0
 ├── Block Group 1
 ├── Block Group 2
 └── Block Group 3
```

Think of block groups like **mini-filesystems inside the filesystem**.

---

# 3. Real ext4 Disk Layout

Actual layout is roughly:

```
Disk
│
├── Boot Block
├── Superblock
├── Group Descriptor Table
│
├── Block Group 0
│   ├── block bitmap
│   ├── inode bitmap
│   ├── inode table
│   └── data blocks
│
├── Block Group 1
│   ├── block bitmap
│   ├── inode bitmap
│   ├── inode table
│   └── data blocks
│
├── Block Group 2
│
└── ...
```

The **Group Descriptor Table** stores metadata about every block group.

---

# 4. What the Block Group Descriptor Stores

Each block group has a descriptor entry.

Example:

```
struct block_group_descriptor
{
    block_bitmap_location
    inode_bitmap_location
    inode_table_location
    free_blocks_count
    free_inodes_count
}
```

So the kernel can quickly find:

```
where blocks are
where inodes are
how much free space exists
```

---

# 5. Inside One Block Group

Let’s zoom into one block group.

```
Block Group N
+-------------------+
| Block Bitmap      |
+-------------------+
| Inode Bitmap      |
+-------------------+
| Inode Table       |
+-------------------+
| Data Blocks       |
+-------------------+
```

Each part has a specific job.

---

# 6. Block Bitmap

This tracks **which data blocks are free or used**.

Example:

```
Block numbers:  0 1 2 3 4 5 6 7
Bitmap bits:    1 1 0 0 1 0 0 0
```

Meaning:

```
1 = block used
0 = block free
```

When a file needs a new block:

```
filesystem scans bitmap
finds free block
marks it used
```

Fast allocation.

---

# 7. Inode Bitmap

Tracks **free and used inodes**.

Example:

```
inode numbers:  1 2 3 4 5 6
bitmap bits:    1 1 0 0 1 0
```

Meaning:

```
inode 1 used
inode 3 free
inode 4 free
```

So when creating a file:

```
find free inode
mark it used
```

---

# 8. Inode Table

This stores the **actual inode structures**.

Example:

```
inode table
 ├── inode 1
 ├── inode 2
 ├── inode 3
 ├── inode 4
```

Each inode contains:

```
file size
permissions
timestamps
block pointers
```

Example:

```
inode 10
size = 12 KB
blocks = [502,503,504]
```

---

# 9. Data Blocks

This is where **actual file data lives**.

Example:

```
block 502 → first part of file
block 503 → second part
block 504 → third part
```

Directories also use data blocks to store:

```
filename → inode
```

---

# 10. Why Block Groups Are Powerful

They provide **locality**.

When you create a file inside a directory:

The filesystem tries to allocate:

```
directory inode
file inode
file blocks
```

**inside the same block group**.

Example:

```
Block Group 10
 ├── directory inode
 ├── file inode
 └── file data blocks
```

So disk reads stay **close together**.

On HDD this massively reduces seek time.

---

# 11. Allocation Strategy

When you create a file:

```
mkdir /home/user
touch file.txt
```

Filesystem tries:

1️⃣ allocate inode near directory inode  
2️⃣ allocate data blocks near that inode

Example:

```
Block Group 7
 ├── inode 300 (directory)
 ├── inode 301 (file)
 └── blocks 9000-9003 (file data)
```

This makes reading a directory **very fast**.

---

# 12. Block Group Size

Block group size depends on block size.

Example ext4 defaults:

```
block size = 4 KB
blocks per group ≈ 32768
```

So block group size:

```
32768 * 4 KB = 128 MB
```

Meaning each block group manages **~128 MB of disk**.

Large disks therefore contain **many block groups**.

Example:

```
1 TB disk
≈ 8000 block groups
```

---

# 13. Parallelism Benefit

Block groups also improve **parallel allocation**.

Different CPUs can allocate blocks from different groups.

Example:

```
CPU 1 → block group 5
CPU 2 → block group 6
CPU 3 → block group 7
```

Less locking → better performance.

---

# 14. Redundancy

Some block groups contain **backup superblocks**.

Example:

```
Block Group 0 → primary superblock
Block Group 1 → backup
Block Group 5 → backup
```

If the main superblock is corrupted, the filesystem can recover.

---

# 15. Complete Example

Imagine this directory:

```
/home/user/file.txt
```

Disk layout might look like:

```
Block Group 12
 ├── inode 501  (home)
 ├── inode 502  (user)
 ├── inode 503  (file.txt)
 ├── block 9001 (directory entries)
 ├── block 9002 (file data)
 └── block 9003 (file data)
```

Everything stored **near each other**.

---

# The Core Idea to Remember

A **block group is a locality optimization**.

It groups together:

```
metadata
inodes
data blocks
```

so related files stay **physically close on disk**.

This dramatically reduces disk seek time.

---

If you want, the **next deep concept** that builds directly on block groups is:

**“How ext4 extent trees replaced block pointers.”**

That change is one of the biggest performance improvements in modern filesystems and very interesting from a systems design perspective.
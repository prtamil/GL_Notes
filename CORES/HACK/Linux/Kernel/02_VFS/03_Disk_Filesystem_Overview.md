Perfect next step. Once VFS clicks, the natural question is: **what does the filesystem actually look like on disk?**  
Let’s walk through how a typical Linux disk filesystem (like ext4 used by the Linux Kernel) organizes data.

I’ll explain it in layers so the whole structure becomes very clear.

---

# 1. First Principle: A Disk Is Just Blocks

A disk is divided into **fixed-size blocks**.

Typical sizes:

```
512 bytes (old disks)
4 KB (modern default)
```

Example disk:

```
1 GB disk
block size = 4 KB

Total blocks ≈ 262,144
```

Everything in a filesystem is built from **blocks**.

Blocks store:

- metadata
    
- inode tables
    
- directories
    
- file data
    

---

# 2. High-Level Filesystem Layout

A filesystem like ext4 divides the disk into regions.

Simplified layout:

```
+--------------------+
| Boot Block         |
+--------------------+
| Superblock         |
+--------------------+
| Block Group Table  |
+--------------------+
| Block Group 0      |
|  - inode bitmap    |
|  - block bitmap    |
|  - inode table     |
|  - data blocks     |
+--------------------+
| Block Group 1      |
+--------------------+
| Block Group 2      |
+--------------------+
| ...                |
+--------------------+
```

This design is extremely important for **performance and scalability**.

---

# 3. Boot Block

The very first sector.

Purpose:

```
bootloader
```

Example bootloaders:

- GRUB
    

Modern systems often place boot code elsewhere, but historically the first block is reserved.

---

# 4. Superblock (Filesystem Metadata)

The **superblock describes the filesystem itself**.

It contains:

```
total blocks
total inodes
block size
filesystem state
mount time
inode table location
```

Example conceptually:

```
superblock
{
  total_blocks = 262144
  total_inodes = 65536
  block_size = 4096
}
```

If the superblock is corrupted, the filesystem may not mount.

That’s why filesystems store **backup superblocks**.

---

# 5. Block Groups (The Key Design)

Large disks are divided into **block groups**.

This was inspired by BSD's Fast File System.

Example:

```
Disk
 ├── Block Group 0
 ├── Block Group 1
 ├── Block Group 2
 └── Block Group 3
```

Each block group contains:

```
block bitmap
inode bitmap
inode table
data blocks
```

Why?

To keep **related data close together on disk**.

Example:

```
directory + file inode + file data
```

all stored in the same block group → fewer disk seeks.

---

# 6. Block Bitmap

Tracks **free/used data blocks**.

Example bitmap:

```
Block:  0 1 2 3 4 5 6 7
Bitmap: 1 1 0 0 1 0 0 0
```

Meaning:

```
1 = used
0 = free
```

This allows fast allocation of new blocks.

---

# 7. Inode Bitmap

Tracks **which inodes are free or used**.

Example:

```
Inode:  1 2 3 4 5 6
Bitmap: 1 1 0 0 1 0
```

Meaning:

```
inode 1 used
inode 2 used
inode 3 free
```

---

# 8. Inode Table

This is where **all inode structures are stored on disk**.

Example:

```
inode table
 ├── inode 1
 ├── inode 2
 ├── inode 3
 ├── inode 4
```

Each inode contains metadata like:

```
file size
owner
permissions
timestamps
block pointers
```

Example inode:

```
inode 10
size: 8192
blocks: [501, 502]
```

Meaning:

```
data block 501
data block 502
```

contain the file data.

---

# 9. Data Blocks

These store the **actual file contents**.

Example:

```
Block 501 → "Hello world"
Block 502 → rest of file
```

For directories, data blocks store **directory entries**.

---

# 10. Directory Structure

A directory is just a **special file**.

Its data blocks contain mappings:

```
filename → inode
```

Example directory:

```
home/
```

Stored as:

```
file1.txt → inode 10
notes.txt → inode 11
image.png → inode 12
```

So a directory block might look like:

```
[ file1.txt | inode 10 ]
[ notes.txt | inode 11 ]
[ image.png | inode 12 ]
```

This is where the VFS **dentry objects come from**.

---

# 11. File Data Layout

Small file example:

```
inode
 └── block pointer → block 501
```

Large file example:

```
inode
 ├── direct blocks
 ├── indirect block
 ├── double indirect
 └── triple indirect
```

Conceptually:

```
inode
 ├─ block[0]
 ├─ block[1]
 ├─ block[2]
 ├─ indirect pointer
 │      └─ block list
```

This allows files to grow very large.

---

# 12. Example File Lookup

Suppose we read:

```
/home/user/file.txt
```

Step-by-step:

### 1 Root inode

```
inode 2 → /
```

---

### 2 Directory lookup

Find entry:

```
home → inode 50
```

---

### 3 Next directory

```
user → inode 70
```

---

### 4 File entry

```
file.txt → inode 100
```

---

### 5 Read inode

```
inode 100
blocks: [501, 502]
```

---

### 6 Read data blocks

```
block 501
block 502
```

Return data to user.

---

# 13. Full Disk Path Example

```
Disk
 │
 ▼
Superblock
 │
 ▼
Inode Table
 │
 ▼
inode 100
 │
 ▼
data block pointers
 │
 ▼
block 501 → file data
```

---

# 14. Why This Design Works Well

This design provides:

### Efficient allocation

Bitmaps allow fast scanning.

### Locality

Block groups reduce disk seeks.

### Scalability

Supports huge files and large disks.

### Reliability

Backup superblocks + journaling.

---

# 15. Journaling (Modern Filesystems)

Filesystems like ext4 use **journaling**.

Idea:

```
write change to journal
apply change
mark journal complete
```

So if a crash happens:

```
journal replay restores consistency
```

Without journaling, filesystems could become corrupted.

---

# The Complete Mental Model

```
Disk
 │
 ├── Superblock
 │
 ├── Block Groups
 │      ├── block bitmap
 │      ├── inode bitmap
 │      ├── inode table
 │      └── data blocks
 │
 └── File data
```

Directories map:

```
filename → inode
```

Inodes map:

```
inode → data blocks
```

---

💡 Since you enjoy **systems internals**, the next fascinating topics are:

1. **How journaling actually works internally**
    
2. **How ext4 allocates blocks (extent trees)**
    
3. **Why filesystem fragmentation happens**
    
4. **How SSDs changed filesystem design**
    

The **extent tree design in ext4** is particularly elegant and very different from older Unix filesystems.
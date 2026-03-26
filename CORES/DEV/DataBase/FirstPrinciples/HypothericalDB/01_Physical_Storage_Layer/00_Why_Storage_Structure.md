# Database Page Structure — First Principles

A database doesn't store tables. It stores **pages** — fixed-size blocks of bytes (typically 8 KB) laid out sequentially in a file. Because every page is the same size, you can jump to any page instantly:

```
offset = page_number × page_size
```

That single property is why databases scale. No scanning, no guessing.

---

## Inside a Page

Every page is a structured arena with four regions:

```
+------------------+
| HEADER           |  → row_count, free_space_start, free_space_end, flags
+------------------+
| SLOT DIRECTORY   |  → grows downward: offsets pointing to tuples
+------------------+
| FREE SPACE       |  ← gap between slots and tuples
+------------------+
| TUPLE DATA       |  → grows upward: actual stored records
+------------------+
```

Tuples pack from the bottom up. Slots pack from the top down. The gap is free space.

---

## Slots: Stable Addressing

Tuples can't be referenced by raw byte offset — updates may move them. So every tuple gets a stable logical address:

```
(page_number, slot_number)
```

The slot directory is the indirection layer. When a tuple moves, only its slot entry changes. Everything pointing to `(page 42, slot 3)` still finds its tuple. This is what makes indexes and transactions possible.

---

## Tuple = Header + Column Data

A tuple is the **physical stored version of a row**. It is not just column values:

```
tuple
 ├── tuple header  (metadata)
 └── column values (user data)
```

The tuple header fields:

```
xmin   → transaction that created this version
xmax   → transaction that deleted/replaced this version
flags  → committed? deleted? part of update chain?
ctid   → pointer to the newer version of this tuple
```

A **logical row** and a **physical tuple** are different things. One UPDATE on a row creates two tuples temporarily:

```
tuple_v1(age=25, xmax=TxB)  →  tuple_v2(age=30, xmin=TxB)
```

Both coexist until cleanup. The storage engine uses the header fields to decide which is visible to each reader.

---

## Version Chains and Snapshot Isolation

When a transaction reads a row, it doesn't lock it — it finds the version whose header matches its snapshot:

```
function is_visible(tuple, txn):
    if tuple.xmin > txn.snapshot_start:  return NOT_VISIBLE  # created after snapshot
    if tuple.xmax < txn.snapshot_start:  return NOT_VISIBLE  # deleted before snapshot
    return VISIBLE
```

Multiple versions chain together via `ctid`:

```
v1 → v2 → v3
```

Readers walk the chain backward until they find their version. Writers never overwrite — they append. This is why **readers don't block writers and writers don't block readers**. Stale versions are cleaned up later by vacuum, once no active transaction can see them anymore.

---

## CRUD Inside a Page

**Insert** — write tuple at free_space_end, add slot, shrink free space from both ends.

```
function insert_row(page, row):
    if free_space(page) < size(row) + slot_size: return PAGE_FULL
    offset = page.free_space_end - size(row)
    write row at offset
    slot_id = page.row_count
    page.slots[slot_id] = offset
    page.row_count += 1
    page.free_space_end -= size(row)
    page.free_space_start += slot_size
    return slot_id
```

**Read** — look up slot, follow its offset, check visibility.

```
function read_row(page, slot_id, txn):
    offset = page.slots[slot_id]
    if offset == EMPTY: return NOT_FOUND
    tuple = read bytes at offset
    if is_visible(tuple, txn): return tuple.columns
    return NOT_VISIBLE
```

**Update** — mark old tuple xmax, write new tuple (don't overwrite).

```
function update_row(page, slot_id, new_row, txn):
    old_offset = page.slots[slot_id]
    old_tuple = read tuple at old_offset
    old_tuple.xmax = txn.id                     # invalidate old version
    if free_space(page) >= size(new_row):
        new_offset = page.free_space_end - size(new_row)
        write new_row at new_offset             # new version
        old_tuple.ctid = (page_id, new_slot)    # link versions
        return SUCCESS
    return PAGE_FULL                            # caller must move to new page
```

**Delete** — mark slot EMPTY, set xmax. Space reclaimed by vacuum later.

```
function delete_row(page, slot_id, txn):
    offset = page.slots[slot_id]
    if offset == EMPTY: return NOT_FOUND
    tuple = read tuple at offset
    tuple.xmax = txn.id                         # mark deleted
    page.slots[slot_id] = EMPTY
    page.row_count -= 1
    return SUCCESS
```

---

## Row Retrieval Path

Once a page is loaded into memory, retrieval follows one of two paths:

**Sequential scan:**
```
for slot in page.slot_directory:
    tuple = read_tuple(page, slot.offset)
    if is_visible(tuple, txn):
        yield tuple.columns
```

**Index lookup:**
```
index entry: id=10 → (page 42, slot 3)

load page 42 → go to slot 3 → read offset → read tuple → check visibility → return columns
```

An index stores `(page_id, slot_number)`, not the row itself. The slot layer keeps index pointers stable even when tuples move during compaction.

---

## The Stack

```
DATABASE → TABLE → FILE → PAGE → SLOT → TUPLE → COLUMN VALUES
```

| Layer  | Responsibility                          |
|--------|-----------------------------------------|
| File   | Persistence on disk                     |
| Page   | O(1) disk access via fixed-size offset  |
| Slot   | Stable addressing despite tuple movement|
| Tuple  | Versioned record with lifecycle metadata|
| Column | The actual user data                    |

Everything else — indexes, transactions, vacuuming, buffer pool — is built on top of this structure.

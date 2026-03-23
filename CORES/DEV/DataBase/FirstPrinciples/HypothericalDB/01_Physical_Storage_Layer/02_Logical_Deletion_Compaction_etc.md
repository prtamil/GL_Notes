Here is your second **first-principles storage-engine essay** completing the fragmentation + compaction mental model layer. Together with your previous essay on tuple headers, this finishes the **core hypothetical heap-storage engine lifecycle** needed before moving comfortably into PostgreSQL internals.

---

# Logical Deletion, Fragmentation, Slot Reuse, and Page Compaction

## Why Deleting a Row Cannot Immediately Reclaim Physical Storage Space

A relational database stores table data inside fixed-size storage units called pages. Each page contains rows arranged using a structured layout that includes a page header, a slot directory, free space, and tuple storage regions. While this structure allows efficient insertion and lookup of rows, it introduces an important constraint: removing a row cannot immediately reclaim its physical storage space without harming performance and correctness.

To understand why, one must first understand how rows are stored inside pages.

---

# Row Storage Inside Pages Using Slot Directories

Inside a page, rows are not accessed directly by their physical byte positions. Instead, they are accessed through slot directory entries.

Conceptually:

```
slot0 → offset 7900
slot1 → offset 7600
slot2 → offset 7200
```

Each slot acts as a stable reference pointing to a row’s location within the page. External structures such as indexes refer to rows using a logical address:

```
(page_number, slot_number)
```

Because slot numbers remain stable even when row locations change, the storage engine can reorganize data safely without invalidating references.

However, this design also introduces a consequence: removing a row does not automatically create reusable contiguous free space inside the page.

Instead, it creates fragmentation.

---

# Why Row Deletion Creates Internal Fragmentation

Suppose a page contains three rows:

```
[header]
[slot0]
[slot1]
[slot2]

free space

[row2]
[row1]
[row0]
```

If row1 is deleted, the storage engine cannot simply shift row2 downward immediately. Doing so would require rewriting memory and updating slot offsets during every delete operation.

Instead, the deleted row becomes an empty region:

```
[header]
[slot0]
[slot1 = empty]
[slot2]

free space

[row2]
[deleted space]
[row0]
```

This empty region is not contiguous with the main free-space region. Therefore it cannot be reused efficiently until later reorganization occurs.

This condition is called internal fragmentation.

---

# Logical Deletion Versus Physical Deletion

To manage fragmentation safely, storage engines distinguish between logical deletion and physical deletion.

Logical deletion means marking a row as deleted without removing its bytes from the page.

Conceptually:

```
slot still exists
row bytes still exist
row marked invisible
```

Physical deletion means reclaiming the storage occupied by the row and reorganizing the remaining data inside the page.

Conceptually:

```
row bytes removed
neighbor rows shifted
slot directory updated
free space merged
```

Logical deletion happens immediately.

Physical deletion happens later.

This separation allows databases to maintain performance while preserving correctness.

---

# Slot Reuse

Even though deleted rows leave fragmented storage behind, their slot entries remain useful.

Instead of allocating a new slot for every inserted row, the storage engine may reuse an existing empty slot created by a deletion.

For example:

```
slot1 = empty
```

A later insert operation can reuse slot1:

```
slot1 → offset 7000
```

This avoids unnecessary slot directory growth and preserves stable addressing for row references.

Slot reuse is therefore a lightweight form of storage recycling that occurs without reorganizing the entire page.

---

# Why Deleted Row Bytes Are Temporarily Preserved

When a row is deleted, the storage engine does not immediately remove its bytes from memory.

Instead:

```
row marked deleted
slot retained
row bytes preserved
```

This behavior exists for two important reasons.

First, some transactions may still need to read the deleted row because their logical view of the database began earlier. Removing the row immediately would violate snapshot consistency.

Second, shifting rows during every delete operation would require moving large amounts of memory repeatedly, reducing performance significantly.

Thus, logical deletion allows deletion to occur quickly while preserving correctness.

---

# Why Immediate Memory Movement Would Reduce Performance

Consider a page containing many rows.

If each delete operation triggered immediate memory reorganization:

```
shift rows
update slots
merge free space
rewrite offsets
```

Then even small delete operations would become expensive.

In workloads with frequent updates and deletes, this would result in excessive CPU usage and cache disruption.

Instead, storage engines delay reorganization until it becomes necessary.

This approach improves overall throughput by spreading maintenance work across time rather than performing it immediately.

---

# Deferred Cleanup and Background Maintenance

Because logical deletion leaves fragmented space behind, storage engines eventually perform maintenance operations that reorganize pages.

These operations:

```
remove obsolete row versions
merge fragmented regions
shift remaining rows
update slot offsets
restore contiguous free space
```

Maintenance may occur:

```
periodically
during background processing
during explicit maintenance commands
```

Deferred cleanup ensures that the system remains efficient without slowing down normal operations.

---

# Analogy: Removing Books From a Library Shelf

A useful analogy is a library shelf.

Suppose books are arranged on shelves with fixed index numbers:

```
Shelf position 1 → Book A
Shelf position 2 → Book B
Shelf position 3 → Book C
```

If Book B is removed, librarians do not immediately shift every remaining book leftward. Instead:

```
position 2 becomes empty
```

Later, a new book may be placed in that position.

Occasionally, librarians reorganize shelves to make better use of space.

Similarly, databases leave empty storage temporarily and reorganize pages later when appropriate.

---

# Slot Reuse During Insert Operations

When inserting a new row, the storage engine first checks whether any empty slots exist.

If an empty slot is available, it is reused:

```
empty slot → assigned new row offset
```

If no empty slot exists, a new slot entry is created at the end of the slot directory.

This strategy reduces metadata growth while preserving stable addressing.

---

# Page Compaction

Over time, fragmented storage inside a page may accumulate.

When fragmentation becomes significant, the storage engine performs page compaction.

Page compaction reorganizes rows inside the page so that fragmented regions merge into a single contiguous free-space block.

Conceptually:

Before compaction:

```
[row3]
[gap]
[row2]
[gap]
[row1]
```

After compaction:

```
[row3]
[row2]
[row1]

free space
```

During compaction:

```
rows shifted
slot offsets updated
free space merged
```

Importantly, slot numbers remain unchanged. Only their offsets are modified.

Thus, external references to rows remain valid.

---

# Logical Delete Algorithm

Logical deletion marks a row as removed without reclaiming storage immediately.

```
function delete_row(page, slot_id):

    if slot_id is invalid:
        return ERROR

    tuple = page.slots[slot_id]

    if tuple already deleted:
        return ERROR

    mark tuple as deleted

    mark slot as reusable

    return SUCCESS
```

This operation executes quickly because it avoids memory movement.

---

# Slot Reuse During Insert Algorithm

Insertion prefers reusing empty slots before creating new ones.

```
function insert_row(page, row):

    if free_space(page) < size(row):
        return PAGE_FULL

    slot_id = find_reusable_slot(page)

    if slot_id exists:

        offset = allocate_space(page, row)

        write row at offset

        page.slots[slot_id] = offset

        return slot_id

    else:

        slot_id = allocate_new_slot(page)

        offset = allocate_space(page, row)

        write row at offset

        page.slots[slot_id] = offset

        return slot_id
```

This approach balances efficiency with structural stability.

---

# Page Compaction Algorithm

Page compaction restores contiguous free space by relocating rows.

```
function compact_page(page):

    new_offset = page.end_of_page

    for each slot in slot_directory:

        if slot contains live row:

            row = read row

            new_offset -= size(row)

            move row to new_offset

            update slot offset

    update free_space_boundaries(page)

    return SUCCESS
```

Compaction reorganizes storage without changing slot identities.

---

# Fragmentation Management Enables Scalable Storage Systems

Fragmentation is a natural consequence of efficient deletion strategies. Instead of removing rows immediately, storage engines separate deletion into logical and physical phases.

Logical deletion preserves correctness and performance during normal operation.

Slot reuse allows efficient recycling of metadata structures.

Page compaction restores storage efficiency when fragmentation becomes significant.

Together, these techniques allow databases to manage large volumes of changing data without sacrificing speed or correctness.

By controlling fragmentation carefully, storage engines transform fixed-size pages into flexible containers capable of supporting dynamic workloads at scale.
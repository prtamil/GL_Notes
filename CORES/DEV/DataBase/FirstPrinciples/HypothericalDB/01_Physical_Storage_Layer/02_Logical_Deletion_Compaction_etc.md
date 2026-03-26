# Logical Deletion, Fragmentation, and Page Compaction

---

## The Problem: Why You Can't Just Erase a Row

Imagine two transactions running at the same time:

```
T1 (started at time 100): SELECT * FROM orders WHERE id = 5
T2 (started at time 101): DELETE FROM orders WHERE id = 5
```

T2 commits first. If the engine physically erased that row immediately, T1 would lose the data it's supposed to be reading — violating its snapshot. T1 started before the delete; from its perspective, the row still exists.

This is the core reason: **a deleted row may still be visible to other active transactions**. You cannot reclaim its space until you're certain no one needs it anymore.

There's a second reason too — performance. Physically removing a row means shifting every neighbor tuple to close the gap, then updating all their slot offsets. On a busy page with frequent deletes, this is constant expensive memory movement.

The solution: separate deletion into two phases.

---

## What Logical Deletion Actually Does (Backend Mechanics)

A delete is just a **write to the tuple header**. Nothing moves.

```
DELETE FROM orders WHERE id = 5
```

Backend steps:
1. Locate the tuple via its slot: `page.slots[slot_id] → offset`
2. Read the tuple header at that offset
3. Set `xmax = current_transaction_id` — this stamps "deleted by TxN"
4. Mark the slot as reusable in the slot directory
5. Done. The bytes stay exactly where they are.

```
Before DELETE:                    After DELETE:

tuple header:                     tuple header:
  xmin = 50   (created by Tx50)     xmin = 50
  xmax = 0    (not deleted)   →→→   xmax = 101   ← stamped
  flags = live                      flags = dead
  columns: id=5, amount=200         columns: id=5, amount=200  ← still there
```

The tuple is now a **dead tuple** — bytes intact, marked invisible. Any transaction with `snapshot_start >= 101` will skip it. Any transaction with `snapshot_start < 101` (like T1 above) will still see it as live.

```
function delete_row(page, slot_id, txn):
    if slot_id invalid or already deleted: return ERROR
    tuple = read tuple at page.slots[slot_id]
    tuple.xmax = txn.id          # stamp deletion time
    tuple.flags |= DEAD          # mark invisible to new readers
    page.slots[slot_id].reusable = true
    return SUCCESS
```

This is O(1). No memory movement. The page doesn't change shape.

---

## What Fragmentation Looks Like

After several deletes, live tuples have gaps between them:

```
After deleting row1 and row3:

SLOT DIRECTORY:              TUPLE AREA:
[slot0] → offset 900         offset 900: [row0 — live]
[slot1] = reusable           offset 840: [row1 — dead, xmax=101]
[slot2] → offset 780         offset 780: [row2 — live]
[slot3] = reusable           offset 720: [row3 — dead, xmax=98]
                             offset 660: [row4 — live]
```

The dead tuples sit between live ones. That space isn't contiguous with the main free-space region at the top of the page — so a new insert **can't use it** until compaction runs. The page appears fuller than it actually is.

---

## When Is a Dead Tuple Safe to Remove?

The engine can't just delete dead tuples whenever — some transaction might still be reading them. A dead tuple is safe to physically remove only when:

```
xmax < oldest_active_transaction_snapshot
```

In other words: every transaction that started before this tuple was deleted has either committed or aborted. No one alive can see this version anymore.

The component that tracks this is called the **transaction horizon** (in PostgreSQL: `OldestXmin`). Vacuum uses this boundary to decide what to clean.

---

## Slot Reuse

Empty slots don't go to waste. Before growing the slot directory, the engine scans for a reusable slot:

```
function insert_row(page, row):
    if free_space(page) < size(row): return PAGE_FULL

    slot_id = find_reusable_slot(page)     # scan for slot.reusable == true
    if not found:
        slot_id = allocate_new_slot(page)  # grow directory

    offset = page.free_space_end - size(row)
    write row at offset
    page.slots[slot_id] = offset
    page.slots[slot_id].reusable = false
    page.free_space_end -= size(row)
    return slot_id
```

The slot number is reused but gets a new offset — indexes referencing the old `(page, slot)` will read the new tuple. This is safe because indexes always go through the tuple header visibility check.

---

## Page Compaction (Vacuum)

When dead tuples accumulate past a threshold, vacuum runs compaction on the page. It physically removes all dead tuples and packs live ones together:

```
Before compaction:           After compaction:

[row4 — live ]               [row4]
[row3 — dead ]               [row2]
[row2 — live ]     →→→       [row0]
[row1 — dead ]
[row0 — live ]               [    free space    ]
```

```
function compact_page(page):
    new_offset = page.end_of_page
    for each slot in slot_directory:
        if slot has live tuple:
            row = read row at slot.offset
            new_offset -= size(row)
            move row to new_offset
            slot.offset = new_offset      # slot number unchanged, only offset moves
    clear all dead tuple regions
    update page.free_space_boundaries
```

Slot numbers never change. Only their offsets update. All external references (`(page, slot)` in indexes) remain valid.

---

## The Full Lifecycle

```
INSERT  →  write tuple (xmin=TxN, xmax=0), assign slot

DELETE  →  set tuple.xmax=TxN, mark slot reusable          ← logical, instant, O(1)
           tuple bytes stay in place

READ    →  check xmin/xmax against snapshot, skip dead tuples

VACUUM  →  find dead tuples where xmax < oldest_snapshot   ← physical, deferred
           remove them, compact page, restore free space
```

**Why this split works:**
- Logical deletion is instant and non-blocking — writers stamp a header, readers skip dead tuples, no one waits.
- Physical cleanup is deferred until the transaction horizon advances far enough — correctness is preserved automatically.
- The page always knows its own state through the header's `free_space_start/end` — inserts never need to scan for space.

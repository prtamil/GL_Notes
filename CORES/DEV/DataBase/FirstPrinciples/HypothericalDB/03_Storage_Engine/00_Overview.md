Below is your requested **first-principles structured essay** on the **storage engine** in a hypothetical database architecture. This essay connects directly to the mental model you’ve already built around **pages, slots, tuple headers, fragmentation, and the buffer manager**, and now explains how rows behave _over time_, not just _in space_. 🌱

---

# The Storage Engine: How Rows Behave Across Time Inside a Database

## Introduction

A database system begins with physical storage structures such as disk pages, slot directories, and tuple layouts. These structures define how rows are stored as bytes on persistent storage. A buffer manager then improves performance by caching pages in memory and coordinating reads and writes between disk and memory.

However, these components alone cannot support safe concurrent access by multiple users modifying the same data at the same time. They describe _where rows live_ and _how pages move_, but not _how rows evolve across time_.

The subsystem responsible for managing the lifecycle of rows across concurrent transactions is called the **storage engine**.

The storage engine transforms static page structures into a dynamic multi-version data system capable of supporting safe concurrent reads and writes.

---

# Physical Storage Structures vs Memory Page Caching vs Row Lifecycle Management

It is important to distinguish three separate responsibilities inside a database architecture.

Physical storage structures define:

```
how rows are arranged inside disk pages
how slot directories locate tuples
how free space exists inside pages
```

Memory page caching defines:

```
how disk pages move into memory
how cached pages are reused
how dirty pages are written back later
```

Row lifecycle management defines:

```
how rows change over time
how updates create versions
how deletions behave logically
how transactions observe consistent snapshots
```

The storage engine is responsible for the third category.

Thus:

```
page layout → where rows live
buffer manager → how pages move
storage engine → how rows evolve
```

---

# Why Rows Cannot Be Safely Overwritten During Concurrent Execution

If a database overwrote rows directly during updates, concurrent transactions would interfere with each other.

Example:

```
Transaction A reads row
Transaction B updates same row
Transaction A reads again
```

If overwriting occurred immediately:

Transaction A might observe inconsistent state.

Similarly:

```
Transaction A updates row
Transaction B updates same row
```

One update might silently destroy another.

Therefore, overwriting rows directly is unsafe in multi-user systems.

Instead, the storage engine introduces **row versioning**.

---

# Row Versioning and Multiple Tuple Versions

Row versioning allows multiple versions of the same logical row to exist simultaneously.

Example:

```
original row version
updated row version
later updated row version
```

Each version represents the row at a different moment in time.

Transactions observe only the versions that are valid within their snapshot.

This allows:

```
non-blocking reads
safe concurrent updates
snapshot isolation
```

Row versioning is one of the central responsibilities of the storage engine.

---

# Heap Organization and Append-Based Storage

Most relational databases organize table storage as a heap.

A heap is an unordered collection of pages containing tuples.

When inserting new rows:

```
database selects page with free space
tuple appended into page
slot directory updated
```

Importantly:

existing rows are not rewritten during insertion.

This append-oriented design improves performance and simplifies concurrency.

---

# Tuple Version Creation During Updates

Instead of modifying rows directly, updates create new versions.

Conceptually:

```
old version remains
new version inserted elsewhere
version chain updated
```

Example:

```
row version 1 → row version 2 → row version 3
```

Each version represents a valid state at some moment in time.

This design allows concurrent readers to continue observing earlier versions safely.

---

# Logical Deletion vs Physical Deletion

Deletion inside a storage engine is usually logical first.

Logical deletion means:

```
row marked invisible
bytes remain unchanged temporarily
```

Physical deletion means:

```
row bytes removed later
space reclaimed later
```

Logical deletion allows:

```
transaction rollback safety
snapshot correctness
non-blocking readers
```

Physical deletion happens later through cleanup processes.

---

# Version Chains Preserve Row Identity

When updates create new versions, they are connected through version chains.

Conceptually:

```
slot pointer
    ↓
version 1 → version 2 → version 3
```

This allows:

```
old versions remain reachable
new versions become visible later
indexes remain valid
```

Version chains preserve logical row identity even when physical storage changes.

---

# Visibility Rules Across Transactions

Different transactions observe different versions of the same logical row.

Example:

```
Transaction A sees version 1
Transaction B sees version 2
```

Both are correct relative to their snapshot time.

Visibility rules ensure:

```
consistent reads
repeatable queries
isolation guarantees
```

These rules interpret metadata stored inside tuple headers.

---

# Why Indexes Store References Instead of Row Data

Indexes do not store full row contents.

Instead they store references:

```
(index key → heap tuple location)
```

Reasons include:

```
avoid data duplication
reduce index size
support row versioning safely
maintain flexibility
```

If indexes stored row data directly:

updates would require rewriting entire index contents.

Instead indexes remain stable while heap versions evolve.

---

# How Indexes Remain Valid Across Updates

When updates create new row versions:

```
index still points to original tuple location
version chain followed if necessary
latest visible version selected
```

Thus:

```
index pointer remains stable
row versions evolve independently
```

This separation improves performance and correctness.

---

# Analogy: Document Revision History System

A document revision system illustrates storage engine behavior clearly.

Example:

```
Document Version 1
Document Version 2
Document Version 3
```

Readers accessing older revisions still see earlier versions.

Editors creating new revisions do not overwrite history.

Similarly:

```
logical row identity preserved
versions evolve independently
references remain stable
```

The storage engine behaves like a revision-controlled archive rather than a simple file editor.

---

# Free Space Tracking Inside Heap Storage

When inserting new versions, the storage engine must select pages with available space.

Free space tracking maintains information such as:

```
which pages have space
how much space exists
where new tuples should be inserted
```

Without free space tracking:

insert performance would degrade significantly.

Efficient insertion depends on locating candidate pages quickly.

---

# Why Page Compaction Cannot Occur Immediately

Immediate compaction after every update or deletion would require:

```
moving rows
updating slot directories
rewriting offsets
adjusting references
```

This would slow down normal operations.

Instead:

```
fragmentation tolerated temporarily
cleanup deferred
compaction performed later
```

Deferred maintenance improves performance while preserving correctness.

---

# Pseudocode: Insert Tuple Into Heap Page

```
function insert_tuple(relation, tuple):

    page = find_page_with_free_space(relation)

    slot = allocate_slot(page)

    offset = allocate_space(page, tuple.size)

    write_tuple(page, offset, tuple)

    update_slot(slot, offset)

    return slot_pointer
```

---

# Pseudocode: Create New Version During Update

```
function update_tuple(old_tuple, new_values):

    new_tuple = build_tuple(new_values)

    new_location = insert_tuple(relation, new_tuple)

    link_versions(old_tuple, new_location)

    mark_old_tuple_replaced(old_tuple)

    return new_location
```

---

# Pseudocode: Logical Deletion

```
function delete_tuple(tuple):

    mark_tuple_deleted(tuple)

    return success
```

---

# Pseudocode: Visibility Check

```
function is_visible(tuple, snapshot):

    if tuple.created_after(snapshot):
        return false

    if tuple.deleted_before(snapshot):
        return false

    return true
```

---

# Pseudocode: Locate Tuple Through Index Pointer

```
function fetch_visible_tuple(index_pointer, snapshot):

    tuple = read_heap_tuple(index_pointer)

    while tuple exists:

        if is_visible(tuple, snapshot):
            return tuple

        tuple = follow_version_chain(tuple)

    return null
```

---

# Heap Scans Without Indexes

When indexes are unavailable, the storage engine performs sequential scans.

Example:

```
read page 1
scan tuples
read page 2
scan tuples
```

Sequential scanning is efficient because:

```
disk access becomes predictable
prefetching possible
buffer reuse efficient
```

Thus sequential scans remain useful for large queries.

---

# Conclusion: From Static Pages to Dynamic Versioned Storage

Disk pages alone provide only static storage structure.

Buffer managers provide memory caching.

However, only the storage engine provides:

```
row versioning
visibility rules
logical deletion
free space tracking
index coordination
snapshot-safe reads
```

Together these capabilities transform static disk pages into a dynamic multi-version transactional structure.

The storage engine therefore enables safe concurrent access to evolving data while preserving correctness, performance, and isolation across multiple simultaneous users.
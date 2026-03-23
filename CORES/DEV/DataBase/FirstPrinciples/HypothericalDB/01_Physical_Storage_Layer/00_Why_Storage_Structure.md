Here is a **structured essay from first principles**, written the way storage-engine developers reason about databases internally. I’ve kept the explanations in essay format and placed **CRUD algorithms in pseudocode blocks** so you can reuse this as a learning reference while building your own database.

---

# First Principles of Database Storage

## Pages, Slots, Rows, Free Space, and CRUD Algorithms

A database appears, from the outside, to be a system that stores tables made of rows and columns. However, internally a database does not store tables directly. Instead, it stores structured blocks of bytes arranged carefully so that data can be accessed efficiently even when the database grows from kilobytes to terabytes.

To understand how databases scale, one must begin not with SQL or indexes, but with storage primitives. These primitives are the foundation upon which systems such as PostgreSQL are built.

At its core, a database storage engine answers one fundamental question:

> How can we store and retrieve records efficiently from disk?

The answer begins with the concept of the **page**.

---

# The Page: The Atomic Unit of Storage

A database does not read or write individual rows from disk. Instead, it reads and writes fixed-size blocks called pages.

A page is a fixed-size region of bytes, typically:

```
4 KB
8 KB
16 KB
```

Most relational databases use 8 KB pages because this aligns well with operating system disk block sizes and provides predictable performance characteristics.

Each table in a database is stored as a sequence of pages inside a table file:

```
users.table

page0
page1
page2
page3
```

Because every page has the same size, the database can directly compute where a page is located in the file:

```
offset = page_number × page_size
```

This allows the database to jump directly to a page without scanning the entire file. This property makes large-scale storage practical.

---

# Internal Structure of a Page

A page is not simply raw memory. It is a structured container designed to support efficient insertion, deletion, and lookup of rows.

Each page is divided into four logical regions:

```
+------------------+
| PAGE HEADER      |
+------------------+
| SLOT DIRECTORY   |
+------------------+
| FREE SPACE       |
+------------------+
| ROW DATA         |
+------------------+
```

Each region has a specific responsibility.

The page header stores metadata about the page. The slot directory tracks where rows are stored inside the page. The free space region holds unused bytes available for future inserts. The row data region stores the actual records inserted by users.

Together, these components form the fundamental storage structure used by relational databases.

---

# Rows: The Representation of User Data

Rows represent the actual data inserted by users into a table.

For example:

```
(id = 1, name = "ram")
```

Internally, rows are stored as binary sequences of bytes. A simple representation might look like:

```
[id][length][name_bytes]
```

Rows are stored at the bottom of the page and grow upward as new rows are inserted. This placement allows flexible handling of variable-length data such as strings and JSON objects.

Rows are never referenced directly by their physical location inside the page. Instead, they are accessed indirectly through slots.

---

# Slot Directory: The Navigation Layer Inside Pages

The slot directory contains entries that point to the location of rows inside the page.

For example:

```
slot0 → offset 120
slot1 → offset 104
slot2 → offset 88
```

Slots are stored near the top of the page and grow downward as rows are inserted.

The space between slots and rows forms the free space region.

Slots exist because rows may move during updates. Without slots, moving a row would invalidate every reference pointing to that row. With slots, only the slot entry needs to change.

Thus, a row is identified not by its byte offset, but by a pair:

```
(page_number, slot_number)
```

This provides stable addressing for rows even when the underlying storage layout changes.

---

# Page Header: Metadata That Controls Page Behavior

The page header stores information necessary for managing the contents of the page.

Typical fields include:

```
row_count
free_space_start
free_space_end
page_flags
```

These fields allow the database to determine where slots end, where rows begin, and whether enough free space exists to insert a new record.

Without the page header, the database would not be able to safely modify the page structure.

---

# Free Space: The Region That Enables Efficient Growth

Free space exists between the slot directory and the row data area.

When inserting a row, the database allocates memory from the free space region. When deleting rows, space is not immediately reclaimed. Instead, cleanup occurs later during a maintenance process often called vacuuming.

This design improves performance by avoiding unnecessary memory movement during frequent updates and deletes.

---

# Stable Row Identity Using Page and Slot Numbers

Rows are never referenced by byte offsets directly. Instead, they are referenced using a logical address:

```
(page_number, slot_number)
```

For example:

```
(7, 2)
```

This means:

```
page 7
slot 2
```

Using this addressing scheme ensures that rows remain accessible even if their internal position within the page changes.

This abstraction is essential for implementing indexes and transactions.

---

# CRUD Algorithms Inside a Page

The following algorithms describe how rows are inserted, read, updated, and deleted inside a page.

These algorithms operate entirely within the page structure described earlier.

---

# Insert Algorithm

Insertion adds a row into the free space region and creates a slot entry pointing to it.

```
function insert_row(page, row):

    if free_space(page) < size(row) + slot_size:
        return PAGE_FULL

    offset = page.free_space_end - size(row)

    write row at offset

    slot_id = page.row_count

    page.slots[slot_id] = offset

    page.row_count += 1

    page.free_space_end -= size(row)

    page.free_space_start += slot_size

    return slot_id
```

This operation runs in constant time because the page header tracks free space boundaries.

---

# Read Algorithm

Reading a row requires locating the correct slot entry and following its pointer.

```
function read_row(page, slot_id):

    offset = page.slots[slot_id]

    if offset == EMPTY:
        return ROW_NOT_FOUND

    row = read bytes at offset

    return row
```

This operation is efficient because slot lookup occurs in memory after the page is loaded.

---

# Update Algorithm

Updating a row depends on whether the new row fits in the existing location.

```
function update_row(page, slot_id, new_row):

    offset = page.slots[slot_id]

    old_row = read row at offset

    if size(new_row) <= size(old_row):

        overwrite old_row with new_row

        return SUCCESS

    else if free_space(page) >= size(new_row):

        new_offset = page.free_space_end - size(new_row)

        write new_row at new_offset

        page.slots[slot_id] = new_offset

        page.free_space_end -= size(new_row)

        return SUCCESS

    else:

        return PAGE_FULL
```

Slots allow rows to move safely when their size changes.

---

# Delete Algorithm

Deleting a row marks the slot as empty without immediately reclaiming space.

```
function delete_row(page, slot_id):

    offset = page.slots[slot_id]

    if offset == EMPTY:
        return ROW_NOT_FOUND

    page.slots[slot_id] = EMPTY

    page.row_count -= 1

    mark row at offset as deleted

    return SUCCESS
```

Space reclamation occurs later during maintenance.

---

# Why Fixed-Size Pages Enable Scalability

Because pages are fixed in size, their location inside a file can be computed instantly:

```
offset = page_number × page_size
```

This allows the database to access any page directly in constant time regardless of file size.

As a result, databases can scale from small datasets to massive storage systems without changing their storage architecture.

---

# The Layered Mental Model of Database Storage

Database storage is built as a hierarchy of abstractions:

```
DATABASE
  TABLE
    FILE
      PAGE
        SLOT
          ROW
```

Each layer solves a different problem.

The file provides persistence. The page provides efficient disk access. The slot provides stable addressing. The row stores user data.

Together, these primitives form the foundation of relational database storage engines.

Understanding this structure transforms the way one thinks about databases. Instead of viewing them as collections of tables, they become structured systems for managing pages of memory on disk efficiently and reliably.
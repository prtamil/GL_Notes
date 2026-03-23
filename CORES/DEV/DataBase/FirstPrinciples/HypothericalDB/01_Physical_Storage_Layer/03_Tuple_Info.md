Here’s a **one-page mental model** that cleanly connects **page → slot → tuple → row** and explains **how a database retrieves a row once a page is loaded**. This is one of the most important structural ideas in storage engines like PostgreSQL, and once it clicks, heap scans and index lookups become intuitive. 🧠

---

# The Page → Slot → Tuple → Row Retrieval Chain

A relational database stores table data inside **pages**. Each page contains multiple **tuples**, and each tuple represents **one physical version of a row**. The database uses a **slot directory** inside the page to locate tuples efficiently.

Conceptually:

```
table
  ↓
page
  ↓
slot
  ↓
tuple
  ↓
column values
```

This is the full path from storage to row retrieval.

---

# Step 1 — What a Page Contains

A **page** is the fundamental storage unit read from disk into memory.

Typical structure:

```
PAGE
 ├── page header
 ├── slot directory
 └── tuple area
```

The database never reads individual rows from disk. It always reads **entire pages**.

So retrieval always starts like:

```
read page → inspect slot directory → locate tuple
```

---

# Step 2 — What the Slot Directory Does

The slot directory acts like a **table of contents for tuples inside the page**.

Example:

```
slot 1 → offset 820
slot 2 → offset 760
slot 3 → offset 690
```

Each slot stores:

```
pointer to tuple location inside page
```

Important:

Slots do NOT store row data.

They store:

```
where tuple lives
```

Why this matters:

If tuples move during compaction:

```
slot stays same
offset updates
```

So references remain stable.

---

# Step 3 — What a Tuple Contains

A tuple is the **physical stored version of a row**.

Structure:

```
tuple
 ├── tuple header (metadata)
 └── column values
```

Example:

```
tuple
 ├── xmin = creator transaction
 ├── xmax = deleting transaction
 ├── flags
 └── id=10, name="Arun", age=30
```

So:

```
tuple = metadata + actual row values
```

---

# Step 4 — Logical Row vs Physical Tuple

Important distinction:

```
logical row = conceptual table record
tuple = physical stored version
```

Example update:

```
age = 25
```

becomes:

```
tuple_v1(age=25)
tuple_v2(age=30)
```

Same logical row:

```
two tuples exist temporarily
```

Storage engine decides which is visible.

---

# Step 5 — How Retrieval Works After Page Is Loaded

Now the key question you asked:

> I got the page. How do I access the row?

Here is the exact sequence.

### Case 1 — Sequential Scan

Database scans page like this:

```
read page
for each slot:
    find tuple offset
    read tuple header
    check visibility
    if visible:
        return column values
```

Conceptual pseudocode:

```
for slot in page.slot_directory:

    offset = slot.offset

    tuple = read_tuple(page, offset)

    if visible(tuple):

        return tuple.columns
```

So:

```
slot → tuple → row values
```

---

# Step 6 — Retrieval Using an Index

Index does NOT store row itself.

Instead index stores:

```
(pointer → page_id, slot_number)
```

Example:

```
index entry:
id=10 → (page 42, slot 3)
```

Retrieval becomes:

```
load page 42
lookup slot 3
read tuple
check visibility
return row
```

Conceptual flow:

```
index
  ↓
page number
  ↓
slot number
  ↓
tuple
  ↓
row values
```

Very efficient.

---

# Step 7 — Why Slot Directory Exists Instead of Direct Tuple Offsets

Without slot directory:

```
tuple moves
references break
index pointers invalid
```

With slot directory:

```
slot stable
offset changes
indexes remain valid
```

So database references:

```
(slot number)
```

not:

```
(raw byte offset)
```

This is critical design.

---

# Step 8 — Putting Everything Together Visually

Example page layout:

```
PAGE 42

slot directory:
slot 1 → offset 900
slot 2 → offset 820
slot 3 → offset 760

tuple area:

offset 900 → tuple A
offset 820 → tuple B
offset 760 → tuple C
```

Index lookup:

```
id=10 → page 42 slot 2
```

Retrieval:

```
load page 42
go to slot 2
read offset 820
read tuple
check visibility
return row values
```

That’s the complete path from disk page to row.

---

# Final Mental Model (Best One to Remember)

When database retrieves a row:

```
index OR scan
    ↓
page
    ↓
slot directory entry
    ↓
tuple header
    ↓
column values
```

So structurally:

```
page contains slots
slot points to tuple
tuple contains metadata + row values
```

This is the exact chain every relational storage engine follows internally—including systems like PostgreSQL—and understanding this puts you right at the storage-engine designer level of clarity.
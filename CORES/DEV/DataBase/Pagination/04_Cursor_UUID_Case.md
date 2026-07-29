Short answer:

> Cursor pagination **does work with UUID**, but **performance depends on the UUID type and ordering strategy**.

Let’s build the correct mental model so you can decide confidently in real systems.

---

# Core Rule

Cursor pagination needs:

```text
a stable ordering column
+
an index on that column
```

It **does NOT require numeric IDs**.

So this works:

```sql
SELECT *
FROM users
WHERE id > :cursor_uuid
ORDER BY id
LIMIT 20;
```

as long as:

```text
id is indexed
```

---

# The Real Issue With UUID Cursor Pagination

Problem is **not correctness**

Problem is **ordering quality + index locality**

There are two major UUID behaviors:

|UUID type|Cursor pagination quality|
|---|---|
|UUIDv4 (random)|works but slower index locality|
|UUIDv1 / v6 / v7 (time-ordered)|works very well|

---

# Why Random UUID (v4) Is Less Ideal

Example UUIDv4:

```text
f47ac10b-58cc-4372-a567-0e02b2c3d479
```

These values are:

```text
random
non-sequential
non-time-ordered
```

So index structure becomes:

```text
scattered inserts
poor cache locality
more page splits
```

Cursor pagination still works:

```sql
WHERE id > cursor_uuid
```

but performance slightly weaker compared to sequential IDs.

Still far better than OFFSET pagination.

---

# Why Time-Ordered UUID Is Excellent

Example (UUIDv7 conceptually):

```text
018f2c3a-7b21-7c92-b42f-0e02b2c3d479
```

These are:

```text
monotonically increasing
timestamp-based
index-friendly
cursor-friendly
```

Database benefits:

```text
append-heavy insert pattern
better index locality
faster cursor seeks
```

Modern backend systems increasingly prefer:

```text
UUIDv7
ULID
KSUID
Snowflake IDs
```

because they combine:

```text
distributed uniqueness
+
time ordering
```

Perfect for cursor pagination.

---

# Example: Cursor Pagination With UUIDv4 (Still Valid)

Works correctly:

```sql
SELECT *
FROM users
WHERE id > 'f47ac10b-58cc-4372-a567-0e02b2c3d479'
ORDER BY id
LIMIT 20;
```

Database performs:

```text
index seek
then forward scan
```

Cursor logic remains valid.

Only drawback:

```text
insert locality weaker
```

---

# Better Strategy If Using UUIDv4

Instead of ordering by UUID:

use timestamp ordering.

Example:

```sql
ORDER BY created_at
```

cursor query:

```sql
WHERE created_at > :cursor_timestamp
ORDER BY created_at
LIMIT 20;
```

Even safer version:

```sql
ORDER BY created_at, id
```

cursor condition:

```sql
WHERE
created_at > :ts
OR (created_at = :ts AND id > :uuid)
```

This is the **production-grade cursor pagination pattern**.

---

# Production Cursor Pattern (Most Common Design)

Table:

```text
id UUID
created_at timestamp
```

Index:

```sql
INDEX(created_at, id)
```

Cursor query:

```sql
SELECT *
FROM users
WHERE
created_at > :cursor_created_at
OR (
    created_at = :cursor_created_at
    AND id > :cursor_id
)
ORDER BY created_at, id
LIMIT 20;
```

Benefits:

```text
stable ordering
deterministic pagination
fast index seek
works with UUID safely
```

Used in:

```text
GitHub
Slack
Discord
Notion
most timeline-style systems
```

---

# When UUID Cursor Pagination Becomes Problematic

Avoid ordering by UUID if:

```text
UUIDv4
+
very high write volume
+
huge dataset (millions+ rows)
```

Because index fragmentation increases.

Instead:

order by:

```text
created_at
or
UUIDv7
or
Snowflake-style ID
```

---

# Engineering Decision Shortcut

If your primary key is:

### INT AUTO_INCREMENT

Best cursor column:

```text
id
```

---

### UUIDv4

Best cursor column:

```text
created_at, id
```

---

### UUIDv7 / ULID / Snowflake

Best cursor column:

```text
id alone
```

---

# Mental Model Summary

UUID does **not break cursor pagination**

Real rule:

```text
cursor pagination needs ordered index
not numeric ID
```

Best practice pattern:

```text
ORDER BY created_at, id
```

This works reliably in almost every production backend you’ll build—including the kinds of scalable feeds and logs you’re likely to design as you move deeper into DevSecOps-grade system architecture.
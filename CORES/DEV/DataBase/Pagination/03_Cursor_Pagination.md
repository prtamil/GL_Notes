Here is your **backend-engineer reference essay on Cursor Pagination**, written in the **same structured revision-friendly format** as the OFFSET essay. This will help you compare methods directly and build a strong mental model for choosing between them in production systems.

---

# Cursor Pagination — Database-First Reference Essay

Cursor pagination navigates a dataset using a **logical position marker derived from actual row values**, instead of a numeric row offset.

Conceptually:

> cursor pagination = ordered dataset + last-seen value + window extraction

Unlike OFFSET:

```text
OFFSET = position by row number
CURSOR = position by row identity
```

This makes cursor pagination scalable and stable for dynamic datasets.

---

# Core Mental Model

Cursor pagination means:

```text
start after last seen record
return next window
```

Example:

```sql
SELECT *
FROM users
WHERE id > 100
ORDER BY id
LIMIT 10;
```

Interpretation:

```text
ordered users
resume after id = 100
return next 10 rows
```

Database jumps directly using index seek.

---

# Cursor Pagination Inputs (Required Parameters)

Cursor pagination always needs:

|Parameter|Purpose|
|---|---|
|dataset|table or result set|
|ORDER BY|navigation order|
|LIMIT|window size|
|cursor value|last-seen row marker|

Example:

```sql
SELECT *
FROM users
WHERE id > 100
ORDER BY id
LIMIT 10;
```

means:

```text
dataset = users
ordering = id
window size = 10
position marker = last_seen_id = 100
```

---

# Cursor Pagination API Mapping

Most APIs expose cursor pagination as:

```text
cursor token + limit
```

Example request:

```text
GET /users?cursor=100&limit=10
```

Translated query:

```sql
WHERE id > 100
LIMIT 10
```

Cursor represents:

```text
last row from previous page
```

---

# Cursor Pagination Query Template

General structure:

```sql
SELECT columns
FROM table
WHERE ordering_column > cursor_value
ORDER BY ordering_column
LIMIT window_size;
```

Descending order example:

```sql
SELECT *
FROM users
WHERE id < 100
ORDER BY id DESC
LIMIT 10;
```

Comparison operator depends on ordering direction.

---

# Why ORDER BY is Mandatory

Cursor pagination depends on deterministic ordering.

Example:

Correct:

```sql
ORDER BY id
```

Incorrect:

```sql
(no ORDER BY)
```

Without ordering:

```text
cursor position meaningless
navigation impossible
```

Because database cannot define “next”.

---

# Cursor Direction Logic

Operator depends on sorting direction:

|ORDER BY|Cursor condition|
|---|---|
|ASC|id > cursor|
|DESC|id < cursor|

Example ascending:

```sql
WHERE id > 100
ORDER BY id ASC
```

Example descending:

```sql
WHERE id < 100
ORDER BY id DESC
```

This defines navigation flow.

---

# Internal Execution Model (Database Perspective)

Suppose table:

```text
1,000,000 rows
```

Query:

```sql
WHERE id > 500000
LIMIT 10
```

Execution steps:

### Step 1

Planner checks:

```text
index exists?
statistics?
cardinality?
```

---

### Step 2

Planner selects:

```text
index seek
```

instead of sequential traversal.

---

### Step 3

Database jumps directly to:

```text
id = 500000
```

Then reads:

```text
next 10 rows
```

Execution complexity minimal.

---

# Cursor Cost Model

Cursor complexity:

```text
O(log n + limit)
```

Explanation:

```text
log n = index seek cost
limit = window read cost
```

Example:

```text
cursor = 500000
limit = 10
```

Database reads:

```text
10 rows only
```

instead of:

```text
500010 rows
```

Huge improvement over OFFSET.

---

# Why Cursor Pagination is Fast

Cursor pagination uses:

```text
index seek
```

instead of:

```text
index traversal
```

Difference:

OFFSET:

```text
visit rows sequentially
discard skipped rows
```

CURSOR:

```text
jump directly to position
read forward
```

This is the key optimization.

---

# Cursor Behavior With and Without Index

Case 1: Index exists

Example:

```sql
INDEX(id)
```

Execution:

```text
direct jump to cursor location
read next rows
```

Best performance scenario.

---

Case 2: No index

Example:

```sql
WHERE created_at > timestamp
```

without:

```sql
INDEX(created_at)
```

Execution:

```text
full table scan
filter rows
return window
```

Performance degrades heavily.

Cursor pagination requires index support.

---

# Cursor Stability Advantage (Dynamic Dataset Benefit)

Cursor pagination handles inserts safely.

Example timeline:

User loads:

```text
page 1
```

Query:

```sql
WHERE id > 0
LIMIT 10
```

Last row:

```text
id = 10
```

New row inserted:

```text
id = 5
```

User loads:

```text
page 2
```

Query:

```sql
WHERE id > 10
LIMIT 10
```

Result:

```text
no duplicates
no missing rows
```

Dataset shift does not affect navigation.

Major advantage over OFFSET.

---

# Cursor and MVCC Snapshot Behavior

Modern databases use:

```text
MVCC snapshot isolation
```

Meaning:

each query sees consistent snapshot.

Cursor pagination works across snapshot boundaries better because:

```text
cursor anchored to row identity
```

instead of:

```text
row position number
```

This improves stability across requests.

---

# Cursor With Composite Ordering Columns

Sometimes ordering column not unique.

Example:

```sql
ORDER BY created_at
```

Multiple rows share same timestamp.

Solution:

use secondary column:

```sql
ORDER BY created_at, id
```

Cursor query becomes:

```sql
WHERE (created_at, id) > (?, ?)
```

Example:

```sql
WHERE
created_at > last_created_at
OR
(created_at = last_created_at AND id > last_id)
```

Ensures deterministic navigation.

---

# Cursor With JOIN Queries

Example:

```sql
SELECT u.id, p.title
FROM users u
JOIN posts p ON u.id = p.user_id
WHERE p.created_at > cursor_timestamp
ORDER BY p.created_at
LIMIT 10;
```

Execution:

database:

```text
seek index
perform join
return window
```

Efficient compared to OFFSET join pagination.

---

# Cursor With Aggregation Queries

Example:

```sql
SELECT category, COUNT(*)
FROM products
GROUP BY category
HAVING COUNT(*) > cursor_value
ORDER BY COUNT(*)
LIMIT 10;
```

Execution:

aggregation still required first.

Cursor applied after grouping.

Performance similar to OFFSET in aggregation-heavy queries.

---

# Cursor Token Encoding Strategy (Production APIs)

Production systems rarely expose raw IDs directly.

Instead:

cursor token encoded:

```text
base64(last_seen_id)
```

Example:

```text
cursor = "MTAw"
```

Decoded internally:

```text
cursor = 100
```

Benefits:

```text
opaque token
secure navigation state
forward compatibility
```

---

# Forward vs Backward Cursor Pagination

Forward navigation:

```sql
WHERE id > cursor
ORDER BY id ASC
```

Backward navigation:

```sql
WHERE id < cursor
ORDER BY id DESC
```

Supports bidirectional paging.

Common requirement for chat apps.

---

# Cursor Pagination Limitations

Cursor pagination cannot support:

```text
jump to page 5
jump to arbitrary position
```

Because:

```text
cursor depends on previous page
```

Navigation becomes sequential only.

Tradeoff for performance.

---

# Cursor Pagination Best Use Cases

Cursor pagination ideal when:

```text
dataset large
real-time inserts frequent
infinite scroll UI
activity feeds
chat systems
event streams
log viewers
```

Typical production scenario:

```text
social feed timeline
```

---

# Cursor Pagination Weak Use Cases

Cursor pagination not ideal when:

```text
page numbers required
random access navigation required
dataset small
report-style UI
```

Example:

```text
admin dashboards
analytics tables
PDF-style viewers
```

OFFSET better choice there.

---

# Cursor Pagination Optimization Strategies

Best practices:

Use indexed ordering column:

```sql
INDEX(created_at)
```

Use deterministic ordering:

```sql
ORDER BY created_at, id
```

Encode cursor tokens:

```text
base64 encoding
```

Limit window size:

```text
10–50 rows typical
```

Support reverse navigation when needed.

---

# Cursor Pagination Decision Rule (Engineering Shortcut)

Cursor pagination recommended when:

```text
dataset > 50K rows
frequent inserts/deletes
infinite scroll UI
stable navigation required
real-time feeds
```

Otherwise:

```text
OFFSET acceptable
```

---

# Cursor Pagination Mental Model Summary

Think:

```text
ordered dataset
+
last seen row identity
+
window extraction
=
cursor pagination
```

Execution behavior:

```text
seek index
resume from cursor
return next rows
```

Cost model:

```text
O(log n + limit)
```

Strength:

```text
fast
stable
scalable
write-safe
```

Weakness:

```text
no page numbers
sequential navigation only
cursor state required
```

Cursor pagination is best understood as:

> position-by-row-identity navigation through an ordered dataset.
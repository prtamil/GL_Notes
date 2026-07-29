Here is your **backend-engineer reference essay on Keyset Pagination**, written in the same structured style as your OFFSET and CURSOR essays so you can revise all three together and compare them cleanly.

Think of this as the **production-grade version of cursor pagination** used in large systems.

---

# Keyset Pagination — Database-First Reference Essay

Keyset pagination navigates a dataset using a **composite index position marker instead of a single cursor value or numeric offset**.

Conceptually:

> keyset pagination = ordered dataset + composite index position + window extraction

Unlike OFFSET:

```text
position = row number
```

Unlike basic CURSOR:

```text
position = single column value
```

Keyset pagination:

```text
position = multi-column index location
```

This makes it the **most stable and scalable SQL pagination method**.

---

# Core Mental Model

Keyset pagination means:

```text
resume from last index position
return next window
```

Example:

```sql
SELECT *
FROM posts
WHERE (created_at, id) > ('2025-01-01', 500)
ORDER BY created_at, id
LIMIT 10;
```

Interpretation:

```text
ordered dataset
resume after composite key
return next rows
```

Database performs index seek efficiently.

---

# Keyset Pagination Inputs (Required Parameters)

Keyset pagination always needs:

|Parameter|Purpose|
|---|---|
|dataset|table or result set|
|ORDER BY|composite ordering|
|LIMIT|window size|
|keyset values|last row index position|

Example:

```sql
SELECT *
FROM posts
WHERE (created_at, id) > (?, ?)
ORDER BY created_at, id
LIMIT 10;
```

means:

```text
dataset = posts
ordering = created_at, id
window size = 10
position marker = last_seen(created_at, id)
```

---

# Why Keyset Pagination Exists

Single-column cursor pagination fails when:

```text
ordering column not unique
```

Example:

```sql
ORDER BY created_at
```

Multiple rows share timestamp.

Cursor becomes ambiguous.

Keyset pagination solves this:

```sql
ORDER BY created_at, id
```

Now ordering becomes:

```text
globally deterministic
```

Essential for reliable pagination.

---

# Keyset Pagination Query Template

General structure:

```sql
SELECT columns
FROM table
WHERE (ordering_columns) > (keyset_values)
ORDER BY ordering_columns
LIMIT window_size;
```

Example:

```sql
SELECT *
FROM users
WHERE (created_at, id) > (?, ?)
ORDER BY created_at, id
LIMIT 20;
```

This resumes scanning exactly after previous page.

---

# Why Composite ORDER BY is Mandatory

Keyset pagination depends on:

```text
strict deterministic ordering
```

Example problem:

```sql
ORDER BY created_at
```

Multiple rows:

```text
same timestamp
```

Pagination becomes unstable.

Correct solution:

```sql
ORDER BY created_at, id
```

Now ordering unique globally.

---

# Internal Execution Model (Database Perspective)

Suppose table:

```text
10,000,000 rows
```

Index:

```sql
INDEX(created_at, id)
```

Query:

```sql
WHERE (created_at, id) > ('2025-01-01', 500)
LIMIT 10
```

Execution steps:

### Step 1

Planner checks:

```text
composite index exists?
statistics valid?
```

---

### Step 2

Planner performs:

```text
composite index seek
```

instead of scan.

---

### Step 3

Database jumps directly to:

```text
(created_at, id) position
```

Then reads:

```text
next 10 rows only
```

Highly efficient execution.

---

# Keyset Pagination Cost Model

Keyset complexity:

```text
O(log n + limit)
```

Same theoretical complexity as cursor pagination.

But more stable in practice.

Example:

```text
resume position = row 5,000,000
limit = 20
```

Database reads:

```text
20 rows only
```

Not millions.

---

# Why Keyset Pagination is Faster Than OFFSET

OFFSET execution:

```text
scan skipped rows
discard skipped rows
return window
```

Keyset execution:

```text
seek index position
return window immediately
```

Difference:

```text
linear scan vs direct seek
```

This is why keyset scales.

---

# Why Keyset Pagination is More Reliable Than Cursor Pagination

Cursor pagination example:

```sql
WHERE created_at > timestamp
```

Problem:

```text
duplicate timestamps exist
```

Keyset pagination example:

```sql
WHERE (created_at, id) > (timestamp, id)
```

Now ordering becomes:

```text
unique and stable
```

Prevents duplicates and gaps.

---

# Keyset Pagination With Ascending Ordering

Example:

```sql
SELECT *
FROM users
WHERE (created_at, id) > (?, ?)
ORDER BY created_at, id
LIMIT 10;
```

Means:

```text
forward navigation
```

---

# Keyset Pagination With Descending Ordering

Example:

```sql
SELECT *
FROM users
WHERE (created_at, id) < (?, ?)
ORDER BY created_at DESC, id DESC
LIMIT 10;
```

Means:

```text
reverse navigation
```

Operator changes with direction.

---

# Keyset Pagination Without Tuple Syntax (Portable Version)

Some databases don’t support:

```sql
(col1, col2) > (?, ?)
```

Alternative version:

```sql
WHERE
created_at > :ts
OR (
    created_at = :ts
    AND id > :id
)
```

Equivalent logic.

Used widely in production APIs.

---

# Keyset Pagination Index Requirements

Keyset pagination requires:

```sql
INDEX(created_at, id)
```

Index order must match:

```sql
ORDER BY created_at, id
```

Otherwise:

```text
index seek impossible
performance degraded
```

Important rule:

> ORDER BY columns must match index prefix

---

# Keyset Pagination Stability Advantage

Example timeline:

User loads:

```text
page 1
```

Last row:

```text
(created_at = T1, id = 100)
```

New rows inserted earlier:

```text
(created_at = T0)
```

Next query:

```sql
WHERE (created_at, id) > (T1, 100)
```

Result:

```text
no duplicates
no missing rows
stable navigation
```

Unlike OFFSET.

---

# Keyset Pagination With UUID Primary Keys

Example table:

```text
id UUID
created_at timestamp
```

Correct ordering:

```sql
ORDER BY created_at, id
```

Cursor condition:

```sql
WHERE
created_at > :ts
OR (
    created_at = :ts
    AND id > :uuid
)
```

Production-standard pattern.

Works perfectly with UUIDv4.

---

# Keyset Pagination With JOIN Queries

Example:

```sql
SELECT u.id, p.title
FROM users u
JOIN posts p ON u.id = p.user_id
WHERE (p.created_at, p.id) > (?, ?)
ORDER BY p.created_at, p.id
LIMIT 10;
```

Execution:

```text
index seek
join
window extraction
```

Efficient compared to OFFSET joins.

---

# Keyset Pagination With Aggregation Queries

Example:

```sql
SELECT category, COUNT(*)
FROM products
GROUP BY category
ORDER BY COUNT(*), category
LIMIT 10;
```

Problem:

aggregation executed first.

Then pagination applied.

Keyset benefit reduced here.

Best suited for:

```text
row-level navigation
not aggregated datasets
```

---

# Forward vs Backward Navigation Support

Forward:

```sql
WHERE (created_at, id) > (?, ?)
```

Backward:

```sql
WHERE (created_at, id) < (?, ?)
```

Allows:

```text
previous page navigation
chat history browsing
timeline scrolling
```

---

# Keyset Pagination Limitations

Keyset pagination cannot support:

```text
jump to page 5
jump to arbitrary row index
page number UI
```

Because navigation depends on:

```text
previous page keyset position
```

Sequential access only.

Tradeoff for speed and stability.

---

# Keyset Pagination Best Use Cases

Ideal when:

```text
dataset very large
real-time inserts frequent
timeline navigation required
chat systems
activity feeds
event streams
log viewers
infinite scroll UI
```

Typical production example:

```text
Twitter timeline
Slack messages
GitHub commits view
```

---

# Keyset Pagination Weak Use Cases

Not ideal when:

```text
page numbers required
random page jumps required
dataset small
report-style UI
```

Example:

```text
admin dashboards
analytics tables
search results with page numbers
```

OFFSET better there.

---

# Keyset Pagination Optimization Strategies

Best practices:

Use deterministic ordering:

```sql
ORDER BY created_at, id
```

Use matching composite index:

```sql
INDEX(created_at, id)
```

Keep window small:

```text
10–50 rows typical
```

Encode cursor tokens:

```text
base64(created_at + id)
```

Common production approach.

---

# Keyset Pagination Decision Rule (Engineering Shortcut)

Use keyset pagination when:

```text
dataset > 100K rows
ordering column not unique
UUID primary key used
timeline-style navigation required
real-time writes frequent
high-performance API required
```

Otherwise:

```text
cursor pagination sufficient
```

---

# Keyset Pagination vs Cursor Pagination (Important Distinction)

Think:

```text
cursor pagination = single-column resume marker
keyset pagination = multi-column index resume marker
```

Keyset is:

```text
cursor pagination generalized for composite ordering
```

Used when:

```text
ordering not unique
```

---

# Keyset Pagination Mental Model Summary

Think:

```text
ordered dataset
+
composite index position marker
+
window extraction
=
keyset pagination
```

Execution behavior:

```text
seek composite index
resume scanning
return next rows
```

Cost model:

```text
O(log n + limit)
```

Strength:

```text
fastest SQL pagination
stable under writes
handles duplicate ordering values
scales to billions of rows
```

Weakness:

```text
no page numbers
sequential navigation only
composite index required
cursor state required
```

Keyset pagination is best understood as:

> position-by-composite-index navigation through an ordered dataset.
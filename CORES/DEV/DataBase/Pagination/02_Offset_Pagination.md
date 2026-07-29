Here is a **backend-engineer–level essay on OFFSET pagination**, written as a structured reference you can reuse while learning the other pagination methods later. It follows the **database-first mental framework** we established earlier and keeps focus on inputs, execution model, cost model, planner behavior, indexing effects, and when to choose or avoid it.

---

# OFFSET Pagination — Database-First Reference Essay

OFFSET pagination is the **simplest and oldest pagination strategy** in SQL systems. It works by skipping a number of rows in an ordered dataset and returning the next window of rows.

Conceptually:

> OFFSET pagination = ordered dataset + numeric position marker + window extraction

It is intuitive for UI navigation but inefficient for large datasets.

---

# Core Mental Model

OFFSET pagination means:

```text
skip N rows
return next K rows
```

Example:

```sql
SELECT *
FROM users
ORDER BY id
LIMIT 10 OFFSET 20;
```

Interpretation:

```text
ordered users
skip first 20 rows
return next 10 rows
```

---

# OFFSET Pagination Inputs (Required Parameters)

OFFSET pagination always needs these database-level inputs:

|Parameter|Purpose|
|---|---|
|dataset|table or result set|
|ORDER BY|navigation order|
|LIMIT|window size|
|OFFSET|number of rows skipped|

Example mapping:

```sql
SELECT *
FROM users
ORDER BY id
LIMIT 10 OFFSET 20;
```

means:

```text
dataset = users
ordering = id
window size = 10
position marker = row number 20
```

---

# OFFSET Pagination API Mapping

Most web applications expose OFFSET pagination as:

```text
page number + page size
```

Formula:

```text
OFFSET = (page − 1) × LIMIT
```

Example:

```text
page = 3
limit = 10
offset = 20
```

Converted query:

```sql
LIMIT 10 OFFSET 20
```

---

# OFFSET Pagination Query Template

General structure:

```sql
SELECT columns
FROM table
ORDER BY ordering_column
LIMIT window_size
OFFSET skip_rows;
```

Example production-style query:

```sql
SELECT id, name, created_at
FROM users
ORDER BY created_at DESC
LIMIT 20 OFFSET 40;
```

---

# Why ORDER BY is Mandatory

OFFSET operates on **ordered position**, not physical storage order.

Wrong:

```sql
SELECT * FROM users LIMIT 10 OFFSET 20;
```

Correct:

```sql
SELECT *
FROM users
ORDER BY id
LIMIT 10 OFFSET 20;
```

Without ORDER BY:

```text
results unstable
pagination meaningless
```

Because databases do not guarantee row storage order.

---

# Internal Execution Model (Database Perspective)

Suppose table:

```text
1,000,000 rows
```

Query:

```sql
LIMIT 10 OFFSET 500000
```

Execution steps:

### Step 1

Check ordering column index

Planner evaluates:

```text
index exists?
statistics?
table size?
```

---

### Step 2

Choose scan strategy

Planner selects:

```text
index scan
or
sequential scan
```

depending on cost estimate.

---

### Step 3

Traverse rows

Database performs:

```text
visit row 1
visit row 2
visit row 3
...
visit row 500000
discard
return next 10 rows
```

Important:

OFFSET never jumps directly.

It walks sequentially.

---

# OFFSET Cost Model

OFFSET complexity:

```text
O(offset + limit)
```

Example:

```text
OFFSET 500000
LIMIT 10
```

Database processes:

```text
500010 rows
```

to return:

```text
10 rows
```

This is the core limitation.

---

# Why OFFSET Cannot Skip Instantly

OFFSET requires verifying ordered position.

Even with index:

```text
database must move forward through ordered entries
```

Example index structure:

```text
1
2
3
4
...
500000
```

Database still traverses:

```text
1 → 2 → 3 → ... → 500000
```

Sequential leaf-node traversal required.

---

# OFFSET Behavior With and Without Index

Case 1: No index

Query:

```sql
ORDER BY created_at
```

Execution:

```text
scan table
sort dataset
skip rows
return window
```

Worst-case scenario.

---

Case 2: Index exists

Index:

```sql
INDEX(created_at)
```

Execution:

```text
index scan
skip rows sequentially
return window
```

Better but still linear cost.

Index improves speed per step — not skip ability.

---

# OFFSET Performance Timeline (Example Table: 1M rows)

|Query|Work done|
|---|---|
|OFFSET 0|visit 10 rows|
|OFFSET 1,000|visit 1,010 rows|
|OFFSET 10,000|visit 10,010 rows|
|OFFSET 500,000|visit 500,010 rows|
|OFFSET 900,000|visit 900,010 rows|

Latency increases linearly.

---

# OFFSET Stability Problem (Dynamic Dataset Issue)

OFFSET assumes:

```text
dataset unchanged
```

Example timeline:

User loads:

```text
page 1
```

Query:

```sql
LIMIT 10 OFFSET 0
```

New row inserted at top.

User loads:

```text
page 2
```

Query:

```sql
LIMIT 10 OFFSET 10
```

Result:

```text
duplicate row appears
```

Because dataset shifted.

OFFSET pagination is unstable when data changes frequently.

---

# OFFSET and MVCC Snapshot Behavior

Modern databases like:

- PostgreSQL
    
- MySQL InnoDB
    

use:

```text
MVCC snapshot isolation
```

Meaning:

each query sees a consistent snapshot

However:

across multiple requests:

```text
snapshot changes
```

So duplicates still possible between pages.

---

# OFFSET With JOIN Queries

Example:

```sql
SELECT u.id, p.title
FROM users u
JOIN posts p ON u.id = p.user_id
ORDER BY p.created_at
LIMIT 10 OFFSET 100;
```

Execution:

database must:

```text
perform join
sort result
apply offset
return window
```

Cost increases significantly.

OFFSET becomes expensive faster with joins.

---

# OFFSET With Aggregation Queries

Example:

```sql
SELECT category, COUNT(*)
FROM products
GROUP BY category
ORDER BY COUNT(*) DESC
LIMIT 10 OFFSET 20;
```

Execution:

database must:

```text
aggregate first
sort results
apply offset
return window
```

OFFSET applied after aggregation.

Still expensive.

---

# OFFSET With Covering Index Optimization

Example:

Query:

```sql
SELECT id, created_at
FROM posts
ORDER BY created_at
LIMIT 10 OFFSET 20;
```

Index:

```sql
INDEX(created_at, id)
```

Database performs:

```text
index-only scan
```

No table lookup required.

Performance improves significantly.

Still:

```text
offset traversal required
```

---

# OFFSET Planner Optimization Behavior

Query planner decides:

```text
index scan vs sequential scan
```

Based on:

```text
table size
offset size
statistics
```

Example:

Small table:

planner chooses:

```text
sequential scan
```

Large table:

planner chooses:

```text
index scan
```

Planner always minimizes estimated cost.

---

# OFFSET Best Use Cases

OFFSET pagination works well when:

```text
dataset small
offset shallow
page numbers required
queries simple
data mostly static
```

Example scenarios:

```text
admin dashboards
report viewers
analytics UI
internal tooling
search results with small depth
```

---

# OFFSET Worst Use Cases

OFFSET performs poorly when:

```text
deep pagination required
large datasets
frequent inserts/deletes
real-time feeds
infinite scrolling interfaces
```

Example:

```text
social media feed
chat history
activity stream
event logs
```

Better handled by cursor/keyset pagination.

---

# OFFSET Advantages

OFFSET provides:

```text
simple implementation
page number support
easy UI integration
stateless navigation
predictable query structure
```

Example API:

```text
GET /users?page=5&limit=20
```

Very intuitive.

---

# OFFSET Limitations

OFFSET suffers from:

```text
linear scan cost
unstable results
duplicate rows possible
missing rows possible
deep pagination slow
poor distributed scalability
```

These limitations motivate cursor pagination.

---

# OFFSET Optimization Strategies

To make OFFSET safer:

Use indexed ordering:

```sql
ORDER BY created_at
```

with:

```sql
INDEX(created_at)
```

Use deterministic ordering:

```sql
ORDER BY created_at, id
```

Limit maximum offset depth:

```text
max offset = 5000
```

Cache shallow pages:

```text
page 1
page 2
page 3
```

Common production strategy.

---

# OFFSET Decision Rule (Engineering Shortcut)

OFFSET is acceptable when:

```text
table size < 50K rows
offset depth small
page numbers required
dataset mostly static
```

Otherwise:

```text
use cursor pagination
```

---

# OFFSET Mental Model Summary

Think:

```text
ordered dataset
+
row counter
+
window extraction
=
OFFSET pagination
```

Execution behavior:

```text
scan rows
discard skipped rows
return window
```

Cost model:

```text
O(offset + limit)
```

Strength:

```text
simple
page-number friendly
```

Weakness:

```text
slow at scale
unstable with writes
```

OFFSET is best understood as:

> position-by-count navigation through an ordered dataset.
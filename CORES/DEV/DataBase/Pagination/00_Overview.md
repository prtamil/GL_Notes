Here’s a **backend-first, database-first mental model essay** on pagination — the kind of conceptual map senior backend engineers carry. The goal is not just to list techniques, but to help you _grok why pagination exists, what the database is doing underneath, and what strategies scale from thousands to billions of rows._

We’ll cover:

1. What pagination really is (from storage-engine perspective)
    
2. Why ordering is the hidden foundation
    
3. The **three core mental models**
    
4. Additional specialized pagination models beyond those three
    
5. How databases reduce effort internally
    
6. A practical mastery roadmap
    

---

# Pagination: A Database-First Mental Model

Pagination is often taught as:

> “split results into pages”

But from a database perspective pagination actually means:

> efficiently navigate an ordered dataset without reading the entire dataset.

This difference matters.

Because databases are not arrays. They are:

```
disk pages
index trees
heap storage
buffer cache
query planners
```

Pagination exists to control **IO cost**, not UI layout.

---

# The Hidden Rule: Pagination Always Requires Ordering

This query:

```
SELECT * FROM users LIMIT 10;
```

is not pagination.

It’s:

```
first 10 arbitrary rows
```

Real pagination:

```
SELECT *
FROM users
ORDER BY id
LIMIT 10;
```

Pagination =

```
ORDER + WINDOW
```

Window = LIMIT

Navigation = OFFSET or CURSOR

---

# Why Pagination Exists (Storage Engine Reality)

Suppose table:

```
1,000,000 rows
```

Returning all rows:

```
network overload
RAM pressure
disk IO explosion
slow response
```

Instead we request:

```
window of rows
```

Example:

```
rows 21–30
```

Pagination = moving window across ordered rows.

---

# The Three Core Pagination Mental Models

These are the fundamental ones every backend engineer should know:

|Model|Idea|Cost|
|---|---|---|
|Offset|skip rows|O(n)|
|Cursor|resume from position|O(log n)|
|Keyset|navigate index keys|O(log n) optimal|

Let’s explore deeply.

---

# Mental Model 1: OFFSET Pagination

Concept:

```
skip N rows
return next K rows
```

Example:

```
SELECT *
FROM users
ORDER BY id
LIMIT 10 OFFSET 20;
```

Database interprets:

```
scan rows
discard first 20
return next 10
```

Important insight:

OFFSET does not jump.

It walks.

Even with index.

Execution cost:

```
OFFSET + LIMIT row visits
```

Example:

```
OFFSET 500000
LIMIT 10
```

Database still processes:

```
500010 rows
```

to return:

```
10 rows
```

This is why OFFSET becomes slow at scale.

---

## OFFSET strengths

Simple mental model:

```
page = 5
```

Easy UI:

```
jump to page 12
```

Works well for:

```
admin dashboards
small tables
reporting tools
```

---

## OFFSET weaknesses

Breaks at scale:

```
deep pages slow
unstable results
insert/delete shifts dataset
```

OFFSET assumes:

```
dataset static
```

Reality:

```
dataset dynamic
```

Mismatch creates duplicates and missing rows.

---

# Mental Model 2: Cursor Pagination

Concept:

```
resume after last seen position
```

Example:

```
SELECT *
FROM users
WHERE id > 20
ORDER BY id
LIMIT 10;
```

Instead of:

```
page number
```

we use:

```
position marker
```

Example API:

```
GET /users?cursor=20
```

Database execution:

```
jump to id 20 in index
return next 10 rows
```

Cost:

```
O(log n + limit)
```

instead of:

```
O(offset)
```

Major improvement.

---

## Cursor pagination strengths

Stable results:

```
insertions don't affect navigation
```

Fast deep navigation:

```
jump directly via index
```

Works well for:

```
feeds
infinite scroll
APIs
mobile apps
```

---

## Cursor pagination weakness

Cannot easily support:

```
jump to page 50
```

Because:

```
page numbers no longer exist
```

Navigation becomes sequential.

---

# Mental Model 3: Keyset Pagination

Keyset pagination is the most optimized form of cursor pagination.

Concept:

```
navigate using index keys directly
```

Example:

```
SELECT *
FROM users
WHERE id > 20
LIMIT 10;
```

Primary key index used.

Database execution:

```
B-tree search → leaf node → sequential read next rows
```

Extremely efficient.

Cost:

```
O(log n)
```

This is optimal pagination.

---

# Production Keyset Pagination (Composite Cursor)

Real systems rarely paginate using only `id`.

Instead:

```
ORDER BY created_at DESC, id DESC
```

Query:

```
SELECT *
FROM posts
WHERE (created_at, id)
< ('2026-01-01', 500)
ORDER BY created_at DESC, id DESC
LIMIT 10;
```

Index:

```
INDEX(created_at, id)
```

Now database performs:

```
single index traversal
fast sequential read
```

This is how large-scale feeds work.

---

# Are There Only Three Pagination Models?

These three are the foundations.

But real systems extend them into additional patterns.

Here are the extended models backend engineers should know.

---

# Model 4: Seek Pagination (another name for Keyset)

Sometimes called:

```
index seek pagination
```

Same idea:

```
WHERE key > cursor
```

Common in:

```
PostgreSQL
MySQL
SQL Server
```

---

# Model 5: Token Pagination (Distributed Systems)

Used when:

```
data lives across machines
```

Example systems:

- Cassandra
    
- DynamoDB
    

Example:

```
exclusiveStartKey
```

Instead of:

```
cursor=id
```

cursor becomes:

```
opaque token
```

Token represents:

```
partition + offset + replica state
```

---

# Model 6: Search-After Pagination (Search Engines)

Used in:

Elasticsearch

Example:

```
search_after = [timestamp, id]
```

Similar to:

```
composite cursor pagination
```

But optimized for distributed inverted indexes.

---

# Model 7: Window Function Pagination

Example:

```
SELECT *
FROM (
  SELECT *,
         ROW_NUMBER() OVER (ORDER BY id) AS rownum
  FROM users
) t
WHERE rownum BETWEEN 21 AND 30;
```

Useful for:

```
analytics queries
reporting systems
complex joins
```

Not ideal for large datasets.

Because:

```
row numbering required first
```

Expensive.

---

# Model 8: Hybrid Pagination (Real Production Pattern)

Example strategy:

```
OFFSET for first few pages
cursor pagination afterward
```

Used by:

```
large ecommerce platforms
content APIs
```

Reason:

```
page numbers needed initially
performance needed later
```

---

# Model 9: Approximate Pagination (Very Large Systems)

Example:

```
Google search
YouTube
large analytics dashboards
```

Instead of exact:

```
page count
```

they show:

```
About 10,000 results
```

Because:

```
COUNT(*) expensive at scale
```

Approximate counts used.

---

# How Databases Reduce Pagination Effort Internally

This is where real performance comes from.

Databases optimize using:

---

## 1. B-tree index navigation

Instead of:

```
scan entire table
```

database does:

```
jump to index position
```

Cost becomes:

```
log(n)
```

instead of:

```
n
```

---

## 2. Covering index optimization

Example:

```
SELECT id, created_at
```

Index:

```
INDEX(created_at, id)
```

Database avoids table lookup:

```
index-only scan
```

Faster.

---

## 3. Sequential leaf-node reads

After finding first row:

```
next row cheap
next row cheap
next row cheap
```

Because:

```
same disk page
```

---

## 4. Query planner decisions

Planner chooses:

```
index scan
bitmap scan
sequential scan
```

based on:

```
statistics
table size
selectivity
```

Planner minimizes cost automatically.

---

## 5. MVCC snapshot consistency

Used in:

- PostgreSQL
    
- MySQL InnoDB
    

Ensures:

```
consistent pagination view
```

Even during concurrent writes.

---

# Backend Engineer Pagination Mental Model Stack

To truly grok pagination from database perspective:

Think layers.

Layer 1:

```
ordering column choice
```

Layer 2:

```
index structure
```

Layer 3:

```
navigation method
offset vs cursor vs keyset
```

Layer 4:

```
query planner behavior
```

Layer 5:

```
disk vs memory IO
```

Layer 6:

```
distributed system constraints
```

---

# Real-World Pagination Strategy Used at Scale

Typical production query:

```
SELECT *
FROM posts
WHERE (created_at, id)
< (?, ?)
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

Index:

```
INDEX(created_at DESC, id DESC)
```

Cursor returned as:

```
base64(timestamp + id)
```

Response:

```
data
next_cursor
has_more
```

Stable.

Fast.

Scalable.

Industry standard.

---

# The Deepest Pagination Insight

Pagination is not about pages.

It is about:

```
efficient traversal of ordered index space
```

OFFSET:

```
linear traversal
```

Cursor:

```
direct navigation
```

Keyset:

```
index-native traversal
```

Once this clicks, pagination becomes a database navigation problem — not an API formatting problem.

---

If you'd like, next we can go **inside a B-tree index step-by-step** and simulate how a cursor pagination query actually moves through index pages on disk. That’s usually the moment everything becomes crystal clear.
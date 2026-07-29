Great — now let’s connect **SQL pagination theory → real backend implementation** using **Express.js + Node.js** like you’d build in production APIs.

This guide shows:

1. GET request inputs
    
2. Express route example
    
3. SQL query
    
4. response structure
    
5. when to use each method
    

Think of this as your **backend pagination implementation handbook** 📘

---

# Example Dataset Assumption

Example table:

```sql
users(
  id UUID PRIMARY KEY,
  name TEXT,
  created_at TIMESTAMP
)
```

Index:

```sql
INDEX(created_at, id)
```

Used for cursor + keyset pagination.

---

# 1️⃣ OFFSET Pagination (Express Example)

Best when:

```text
admin dashboards
reports
page-number UI
small datasets
```

---

# Client Request Example

Frontend sends:

```http
GET /users?page=3&limit=10
```

Inputs:

|parameter|meaning|
|---|---|
|page|page number|
|limit|rows per page|

---

# Express Route Example

```js
app.get("/users", async (req, res) => {

  const page = parseInt(req.query.page) || 1
  const limit = parseInt(req.query.limit) || 10

  const offset = (page - 1) * limit

  const users = await db.query(
    `
    SELECT *
    FROM users
    ORDER BY created_at DESC
    LIMIT $1 OFFSET $2
    `,
    [limit, offset]
  )

  res.json({
    page,
    limit,
    data: users.rows
  })

})
```

---

# SQL Execution Behavior

Database performs:

```text
ORDER rows
SKIP offset rows
RETURN next limit rows
```

Cost:

```text
O(offset + limit)
```

---

# Example Response

```json
{
  "page": 3,
  "limit": 10,
  "data": [...]
}
```

Simple and predictable 👍

---

# 2️⃣ Cursor Pagination (Express Example)

Best when:

```text
infinite scroll
feeds
large datasets
real-time inserts
```

Cursor = last row id from previous request

---

# Client Request Example

First request:

```http
GET /users?limit=10
```

Next request:

```http
GET /users?cursor=2025-01-10T12:30:00Z&limit=10
```

Cursor uses:

```text
created_at timestamp
```

---

# Express Route Example

```js
app.get("/users", async (req, res) => {

  const limit = parseInt(req.query.limit) || 10
  const cursor = req.query.cursor

  let query
  let values

  if (cursor) {

    query = `
      SELECT *
      FROM users
      WHERE created_at < $1
      ORDER BY created_at DESC
      LIMIT $2
    `

    values = [cursor, limit]

  } else {

    query = `
      SELECT *
      FROM users
      ORDER BY created_at DESC
      LIMIT $1
    `

    values = [limit]

  }

  const users = await db.query(query, values)

  const nextCursor =
    users.rows.length > 0
      ? users.rows[users.rows.length - 1].created_at
      : null

  res.json({
    nextCursor,
    data: users.rows
  })

})
```

---

# SQL Execution Behavior

Database performs:

```text
INDEX SEEK created_at
RETURN next limit rows
```

Cost:

```text
O(log n + limit)
```

Fast even with millions of rows ⚡

---

# Example Response

```json
{
  "nextCursor": "2025-01-09T09:10:22Z",
  "data": [...]
}
```

Frontend sends this cursor in next request.

---

# 3️⃣ Keyset Pagination (Production-Grade Example)

Best when:

```text
UUID primary keys
duplicate timestamps possible
very large datasets
timeline feeds
high-scale APIs
```

Uses:

```text
(created_at, id)
```

as cursor pair

---

# Client Request Example

First request:

```http
GET /users?limit=10
```

Next request:

```http
GET /users?created_at=2025-01-10T12:30:00Z&id=a12f...&limit=10
```

Two inputs:

|parameter|meaning|
|---|---|
|created_at|timestamp cursor|
|id|UUID cursor|

Together form keyset position

---

# Express Route Example

```js
app.get("/users", async (req, res) => {

  const limit = parseInt(req.query.limit) || 10

  const cursorCreatedAt = req.query.created_at
  const cursorId = req.query.id

  let query
  let values

  if (cursorCreatedAt && cursorId) {

    query = `
      SELECT *
      FROM users
      WHERE
        created_at < $1
        OR (
          created_at = $1
          AND id < $2
        )
      ORDER BY created_at DESC, id DESC
      LIMIT $3
    `

    values = [cursorCreatedAt, cursorId, limit]

  } else {

    query = `
      SELECT *
      FROM users
      ORDER BY created_at DESC, id DESC
      LIMIT $1
    `

    values = [limit]

  }

  const users = await db.query(query, values)

  const lastRow = users.rows[users.rows.length - 1]

  res.json({
    nextCursor: lastRow
      ? {
          created_at: lastRow.created_at,
          id: lastRow.id
        }
      : null,
    data: users.rows
  })

})
```

---

# SQL Execution Behavior

Database performs:

```text
COMPOSITE INDEX SEEK
(created_at, id)
RETURN next rows
```

Cost:

```text
O(log n + limit)
```

Most scalable SQL pagination method 🚀

---

# Example Response

```json
{
  "nextCursor": {
    "created_at": "2025-01-09T09:10:22Z",
    "id": "a12f98c0..."
  },
  "data": [...]
}
```

Frontend sends both values next request.

---

# API Input Comparison Summary

|method|GET parameters|
|---|---|
|OFFSET|page, limit|
|CURSOR|cursor, limit|
|KEYSET|created_at + id + limit|

---

# Backend Engineer Pagination Decision Rule

Use OFFSET when:

```text
admin dashboard
report tables
small datasets
```

Use CURSOR when:

```text
infinite scroll
feeds
large datasets
```

Use KEYSET when:

```text
UUID primary keys
duplicate timestamps possible
timeline APIs
millions+ rows
```

---

# Production API Best Practice (Important Insight)

Modern APIs often return cursor like this:

```json
{
  "data": [...],
  "nextCursor": "base64EncodedToken"
}
```

Example encoded token:

```text
base64(created_at + id)
```

Why?

Because:

```text
secure
opaque
forward-compatible
clean API design
```

This is how large-scale backend systems expose pagination safely.
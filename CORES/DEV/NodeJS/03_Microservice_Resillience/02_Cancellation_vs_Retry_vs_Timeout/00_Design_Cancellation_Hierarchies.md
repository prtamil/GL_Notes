**How to Stop the Right Work, at the Right Time, for the Right Reason**

---

## 1. Why “Hierarchy” Matters at All

Naive cancellation looks like this:

```js
ac.abort();

```

Real systems are not one task.

They are **trees of work**:

```js
HTTP Request
 ├── DB query
 ├── File read
 ├── Transform pipeline
 │    ├── Parser
 │    └── Compressor
 └── Cache write

```

If the request is cancelled:

- Some things must stop immediately
- Some must finish cleanup
- Some must not be affected at all
    

That’s a **hierarchy problem**, not an API problem.

---

## 2. The Core Principle (Non-Negotiable)

> **Cancellation flows downward, never upward.**

Parents may cancel children.  
Children must never cancel parents.

If you violate this:

- One failed subtask kills unrelated work
- Shared resources become unstable
    

---

## 3. Cancellation ≠ Error ≠ Timeout

Before hierarchy, get the semantics right:

|Concept|Meaning|
|---|---|
|Error|Unexpected failure|
|Timeout|Policy decision|
|Cancel|Loss of relevance|

Cancellation is **intentional invalidation**, not failure.

Your design must reflect that.

---

## 4. Cancellation Domains (Most Important Concept)

A **cancellation domain** is:

> A set of operations that share the same lifetime.

Example domains:

- One HTTP request
- One user session
- One background job
- One stream pipeline
    

Each domain has **exactly one root signal**.

---

## 5. Root, Branch, Leaf (The Mental Model)

Every cancellation hierarchy has:

### Root

- Owned by the top-level operation
- User disconnects
- Job cancelled
- Process shutting down
    

### Branch

- Subsystems
- Pipelines
- Batches
    

### Leaf

- Individual I/O ops
- Timers
- Streams
    

Cancellation flows:

`Root → Branch → Leaf`

Never sideways. Never upward.

---

## 6. Node’s AbortController Is a Root Tool

AbortController is **not hierarchical by default**.

You must **compose it**.

---

## 7. Pattern: Derived AbortControllers

```js
function deriveSignal(parentSignal) {
  const ac = new AbortController();

  if (parentSignal.aborted) {
    ac.abort();
  } else {
    parentSignal.addEventListener(
      'abort',
      () => ac.abort(),
      { once: true }
    );
  }

  return ac;
}

```

This creates **child cancellation domains**.

---

## 8. Real Example: HTTP Request with Subtasks

### Root: Request Lifetime

```js
app.get('/process', (req, res) => {
  const rootAC = new AbortController();

  req.on('close', () => rootAC.abort());

```

---

### Branch: File Processing Pipeline

  ```js
    const fileAC = deriveSignal(rootAC.signal);

  pipeline(
    fs.createReadStream('input'),
    transform,
    fs.createWriteStream('out'),
    { signal: fileAC.signal },
    handleResult
  );

  ```

---

### Branch: DB Query (Independent Timeout)

  ```js
 const dbAC = deriveSignal(rootAC.signal);

  const timeout = setTimeout(() => {
    dbAC.abort();  // cancels DB, not entire request
  }, 2000);

  queryDB({ signal: dbAC.signal })
    .finally(() => clearTimeout(timeout));

  ```

---

### What This Gives You

|Event|Effect|
|---|---|
|Client disconnects|Everything stops|
|DB slow|Only DB stops|
|File fails|Request continues if allowed|

This is **intentional, explicit control**.

---

## 9. Timeout Belongs to a Child Domain

Timeouts should **never** live at the root.

Why?

- Root cancellation = “request irrelevant”
- Timeout = “this subtask isn’t worth waiting for”
    

Timeout → aborts child controller  
Not the root.

---

## 10. Abort Reason Propagation (Advanced but Crucial)

Modern AbortController supports **reasons**:

`ac.abort(new Error('Client disconnected'));`

Children inherit the reason.

Use this to:

- Distinguish timeout vs disconnect
- Log correctly
- Make retry decisions
    

---

## 11. Cleanup Rules (Hard Rules)

### Rule 1: Cleanup is idempotent

Abort may fire multiple times indirectly.

### Rule 2: Cleanup must not throw

Cleanup failures must be logged, not propagated.

### Rule 3: Cleanup is local

Each domain cleans **its own resources only**.

---

## 12. Streams + Cancellation Hierarchy

Best practice:

- One AbortController per pipeline
    
- Parent controller for request
    
- Derived controllers for:
    
    - Parsing
        
    - Compression
        
    - Upload
        
    - Persistence
        

Never share a controller across unrelated pipelines.

---

## 13. Common Design Failures

### ❌ Global AbortController

Kills unrelated work.

---

### ❌ Child aborting parent

Turns recoverable failure into system failure.

---

### ❌ Mixing timeout and cancel

Timeout is policy. Cancel is authority.

---

## 14. Compare to Go’s `context.Context`

They are philosophically identical:

|Go Context|Node|
|---|---|
|context.WithCancel|AbortController|
|context.WithTimeout|Timeout + abort|
|context.WithValue|Metadata (don’t overuse)|

Same tree. Same rules.

---

## 15. Final Mental Model (Burn This In)

> **Cancellation is about relevance, not failure.**

Design cancellation like you design memory ownership:

- One owner
- Clear lifetimes
- Downward propagation
- Local cleanup
    

If you do this right:

- Your servers stay calm
- Your pipelines stop cleanly
- Your bugs become explainable
    

This is the difference between _code that works_ and _systems that survive_.
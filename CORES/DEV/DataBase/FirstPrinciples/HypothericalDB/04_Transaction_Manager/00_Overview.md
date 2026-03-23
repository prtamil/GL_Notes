## Why a Database Still Needs a Transaction Manager

_(Even After Having Pages, Tuple Headers, a Buffer Manager, and a Multi-Version Storage Engine)_

Modern databases are layered systems. Each layer solves a different category of problems:

- **Physical storage structures** decide where bytes live on disk.
    
- **Tuple headers** record version metadata.
    
- **Buffer managers** control how pages move between disk and memory.
    
- **Storage engines with MVCC** allow multiple row versions to exist safely.
    

Yet even after all this machinery exists, the database is still missing something essential: **a way to decide what is logically true at any moment for each user**.

That responsibility belongs to the **transaction manager**.

This essay builds the idea from first principles.

---

# 1. The Core Problem: Concurrent Access to the Same Logical Row

Consider a simple situation:

Two users modify the same row at the same time.

Example:

```
Row: salary = 50,000
```

Transaction A:

```
UPDATE salary = 60,000
```

Transaction B:

```
UPDATE salary = 55,000
```

Now several questions arise:

- Which update wins?
    
- Should both succeed?
    
- Should one fail?
    
- Should readers see either value immediately?
    
- Should readers see neither value until approval?
    
- Should readers see different values depending on when they started?
    

Even with:

- physical pages
    
- tuple headers
    
- multiple row versions
    
- buffer manager caching
    
- storage engine versioning
    

the system **still cannot answer these questions**.

Because these are **logical correctness questions**, not storage questions.

---

# 2. Why a Storage Engine Alone Cannot Decide Visibility

A multi-version storage engine can do this:

```
Tuple version 1: salary = 50,000
Tuple version 2: salary = 60,000
Tuple version 3: salary = 55,000
```

All versions may exist simultaneously.

But now the storage engine must answer:

```
Which version should Transaction X see?
```

This cannot be answered by storage alone.

Because visibility depends on:

- when Transaction X started
    
- which transactions were active at that moment
    
- whether competing transactions committed
    
- whether competing transactions rolled back
    
- what isolation level Transaction X requested
    

These decisions belong to a higher layer:

> the transaction manager

---

# 3. What a Transaction Is

A **transaction** is a logical unit of work that must appear:

- **Atomic** — either fully applied or not applied at all
    
- **Consistent** — database rules remain valid
    
- **Isolated** — concurrent activity does not leak partial results
    
- **Durable** — committed results survive failures
    

Together these properties form the famous:

```
ACID guarantees
```

Without a transaction manager, ACID cannot exist.

---

# 4. Responsibilities of the Transaction Manager

The transaction manager coordinates logical correctness across concurrent users.

Its responsibilities include:

### 1. Beginning transactions

```
BEGIN TRANSACTION
```

### 2. Assigning transaction identifiers

Each transaction receives:

```
TID (Transaction ID)
```

Example:

```
T1
T2
T3
```

---

### 3. Tracking active transactions

Database maintains:

```
Active transaction list
```

Example:

```
Active = {T2, T5, T7}
```

---

### 4. Committing transactions

```
COMMIT
```

Marks changes as permanent.

---

### 5. Rolling back transactions

```
ROLLBACK
```

Cancels logical effects.

---

### 6. Creating consistent snapshots

Each transaction sees:

```
a stable view of the database
```

---

### 7. Resolving write conflicts

Example:

```
two transactions update same row
```

Only one can succeed.

---

### 8. Enforcing isolation guarantees

Prevents:

- dirty reads
    
- lost updates
    
- inconsistent snapshots
    
- phantom observations
    

---

# 5. Tuple Headers: Where Version Metadata Lives

Inside each tuple version stored on heap pages:

```
TupleHeader
{
    xmin
    xmax
    status_flags
}
```

Meaning:

|Field|Purpose|
|---|---|
|xmin|transaction that created version|
|xmax|transaction that invalidated version|
|status_flags|committed / deleted / locked|

Example:

```
salary = 60,000
xmin = T4
xmax = null
```

Meaning:

```
Created by transaction T4
Still valid
```

---

# 6. Why Tuple Headers Alone Are Not Enough

Tuple headers store metadata.

They do **not interpret metadata**.

Example:

```
xmin = T4
```

Question:

```
Is T4 committed?
```

Tuple header cannot answer.

Transaction manager must check:

```
transaction status table
```

Only then visibility can be decided.

---

# 7. Snapshots: Consistent Views of Time

A **snapshot** represents:

```
which transactions were active when I started
```

Example:

```
Snapshot S:

xmin_visible_before = T10
active_transactions = {T11, T12}
```

Meaning:

Transaction sees:

```
everything committed before T10
```

But ignores:

```
changes from T11 and T12
```

Even if those commit later.

This produces consistency.

---

# 8. Why Different Transactions See Different Versions Safely

Example timeline:

```
T1 starts
T2 updates row
T3 starts
T2 commits
```

Now:

```
T1 sees old version
T3 sees new version
```

Same database.

Different realities.

Both correct.

Because each transaction owns its snapshot.

---

# 9. How Commit Makes Versions Visible

Example:

```
salary = 60,000
xmin = T4
```

Before commit:

```
not visible to others
```

After commit:

```
visible to everyone whose snapshot allows it
```

Commit transforms:

```
tentative version
```

into:

```
official version
```

---

# 10. How Rollback Invalidates Versions

Example:

```
salary = 70,000
xmin = T8
```

If T8 rolls back:

```
ignore this tuple version forever
```

Row remains physically present.

But logically invisible.

Later:

```
vacuum removes it
```

---

# 11. Conflict Detection Between Concurrent Writers

Example:

```
T1 updates row
T2 updates same row
```

Both cannot succeed.

Transaction manager checks:

```
is row already modified by active transaction?
```

If yes:

One transaction must:

```
wait
or abort
```

This prevents:

```
lost update anomaly
```

---

# 12. Analogy: Passport Control System

Imagine airport immigration.

Each traveler:

```
enters country
leaves country
```

Passport contains:

```
entry stamp
exit stamp
```

Database tuple header contains:

```
xmin
xmax
```

Immigration authority:

```
central record of valid travelers
```

Transaction manager:

```
central record of valid transactions
```

Traveler becomes official visitor only after:

```
entry approved
```

Tuple version becomes visible only after:

```
transaction committed
```

Same logic.

---

# 13. Snapshot Creation Allows Readers to Avoid Blocking Writers

Without snapshots:

```
reader waits for writer
writer waits for reader
```

System slows dramatically.

With snapshots:

Reader says:

```
I will view database as it existed when I started
```

So reader continues.

Writer continues.

No blocking required.

This is the magic of MVCC + transaction manager together.

---

# 14. Rollback Restores Logical Correctness Without Immediate Deletion

Rollback does:

```
mark versions invalid
```

Not:

```
physically erase versions immediately
```

Because physical deletion is expensive.

Instead:

```
logical invisibility first
cleanup later
```

This preserves performance and correctness.

---

# 15. Isolation Guarantees Prevent Inconsistent Observations

Transaction manager prevents:

### 1. Dirty reads

Reading uncommitted data

### 2. Disappearing rows

Reading row that later vanishes

### 3. Conflicting versions

Seeing two incompatible truths simultaneously

Isolation ensures:

```
database behaves like ordered timeline
```

even when operations overlap.

---

# 16. Pseudocode: Beginning a Transaction

```
function begin_transaction():
    tid = allocate_transaction_id()

    transaction_table[tid] = ACTIVE

    snapshot = create_snapshot()

    return Transaction(tid, snapshot)
```

---

# 17. Pseudocode: Commit Transaction

```
function commit_transaction(tid):

    write_commit_log_record(tid)

    transaction_table[tid] = COMMITTED

    release_locks(tid)
```

After commit:

```
tuple versions created by tid become visible
```

---

# 18. Pseudocode: Rollback Transaction

```
function rollback_transaction(tid):

    mark_versions_invalid(tid)

    transaction_table[tid] = ABORTED

    release_locks(tid)
```

After rollback:

```
versions ignored by all future readers
```

---

# 19. Pseudocode: Creating Snapshot

```
function create_snapshot():

    snapshot.xmin = oldest_active_transaction()

    snapshot.active_set = list_active_transactions()

    snapshot.xmax = next_transaction_id()

    return snapshot
```

Snapshot represents:

```
visible timeline boundary
```

---

# 20. Pseudocode: Tuple Visibility Check

```
function is_visible(tuple, snapshot):

    if tuple.xmin not committed:
        return false

    if tuple.xmin in snapshot.active_set:
        return false

    if tuple.xmin >= snapshot.xmax:
        return false

    if tuple.xmax exists:

        if tuple.xmax committed before snapshot:
            return false

    return true
```

This determines:

```
should transaction see this version?
```

---

# 21. Pseudocode: Detecting Update Conflict

```
function update_row(transaction, row):

    if row.locked_by_other_transaction():

        wait_or_abort(transaction)

    else:

        create_new_version(row, transaction.tid)
```

Prevents:

```
simultaneous conflicting updates
```

---

# 22. Separation from Physical Storage Layer

Tuple headers live inside:

```
heap pages
```

Transaction manager lives inside:

```
logical concurrency subsystem
```

Storage layer:

```
stores versions
```

Transaction manager:

```
decides visibility of versions
```

This separation keeps architecture clean and scalable.

---

# 23. Final Insight: The Transaction Manager Makes MVCC Safe

A storage engine can:

```
store multiple versions
```

But cannot decide:

```
which version is truth for each user
```

Tuple headers can:

```
record version history
```

But cannot interpret:

```
transaction status meaning
```

Snapshots can:

```
capture time boundaries
```

But cannot enforce:

```
correct concurrency behavior alone
```

Only the **transaction manager** combines:

- transaction identifiers
    
- status tracking
    
- snapshots
    
- commit logic
    
- rollback logic
    
- conflict detection
    
- isolation enforcement
    

into one coordinated system.

And that coordination transforms:

```
multi-version storage
```

into:

```
a safe, concurrent, logically consistent database shared by many users at once
```

That transformation is what makes modern databases trustworthy—even under heavy simultaneous activity.
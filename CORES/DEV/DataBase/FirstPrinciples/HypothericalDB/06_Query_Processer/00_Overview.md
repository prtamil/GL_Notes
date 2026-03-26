## Query Processor — From Declarative SQL to Executable Data Access

A modern database system is composed of multiple cooperating subsystems:

- physical storage structures
    
- buffer manager
    
- storage engine
    
- transaction manager
    
- recovery manager (with write-ahead logging)
    

Together, these layers ensure **data is stored safely, accessed correctly, and recovered after failure**. However, even after building all these components, one essential problem remains:

**How does a database understand what a user wants and decide how to retrieve it efficiently?**

This is the responsibility of the **query processor**.

The query processor transforms human-written SQL into executable operations that retrieve tuples from storage safely and efficiently.

---

# Why Users Write Declarative SQL Instead of Page-Level Retrieval Instructions

A database internally stores data as:

- heap pages
    
- tuples
    
- slot arrays
    
- index structures
    
- buffer-cached disk blocks
    

But users never interact with these structures directly.

Instead of writing:

> read heap page 103  
> check slot 5  
> verify visibility  
> follow index pointer

users write:

```sql
SELECT * FROM users WHERE id = 10;
```

This happens because SQL is **declarative**.

Declarative languages describe:

> what data is required

not:

> how to retrieve that data

This separation is essential because:

- users should not depend on storage layout
    
- physical layout changes over time
    
- indexes may appear or disappear
    
- query strategies differ based on data size
    
- concurrency conditions vary
    
- caching state changes constantly
    

Therefore:

**users describe intent, and the database decides execution strategy**

The subsystem responsible for making that decision is the query processor.

---

# What the Query Processor Does

The query processor converts SQL text into:

> a sequence of executable operations over heap pages and index structures

It acts as a coordinator between:

- storage engine
    
- buffer manager
    
- transaction manager
    
- recovery manager
    

Importantly:

the query processor **does not read disk pages directly**

Instead it requests:

- fetch tuple
    
- scan relation
    
- follow index pointer
    
- check tuple visibility
    

from lower layers.

---

# Query Processing Pipeline Overview

The query processor executes queries through a pipeline:

```
SQL text
   ↓
Parser
   ↓
Planner
   ↓
Optimizer
   ↓
Executor
   ↓
Tuple results
```

Each stage has a precise responsibility.

---

# Stage 1 — Parser

The parser converts SQL text into a structured representation called a:

> syntax tree (parse tree)

Example input:

```sql
SELECT * FROM users WHERE id = 10;
```

Parser produces something like:

```
SELECT
 ├── target: *
 ├── table: users
 └── predicate:
        id = 10
```

The parser identifies:

- tables
    
- columns
    
- operators
    
- predicates
    
- requested operations
    

It also checks:

- syntax correctness
    
- SQL grammar validity
    

### Parser pseudocode

```
function parse(sql_text):

    tokens = tokenize(sql_text)

    syntax_tree = build_parse_tree(tokens)

    if syntax_error:
        raise error

    return syntax_tree
```

The parser understands **structure**, but not execution strategy.

---

# Stage 2 — Schema Validation

Before planning execution, the query processor verifies:

- table exists
    
- column exists
    
- user has permission
    
- data types are compatible
    

Example validation:

```
verify_relation("users")
verify_column("users.id")
verify_operator("=")
```

Only after validation can planning begin.

---

# Stage 3 — Planner (Logical Plan Construction)

The planner converts the syntax tree into a **logical execution strategy**.

Logical operators include:

- scan relation
    
- filter tuples
    
- join relations
    
- project columns
    
- aggregate values
    

Example logical plan:

```
Filter(id = 10)
    ↓
Scan(users)
```

Logical plans describe:

> what operations must happen

but not:

> how they are physically executed

---

### Planner pseudocode

```
function build_logical_plan(parse_tree):

    scan_node = LogicalScan(parse_tree.table)

    if parse_tree.predicate exists:
        return LogicalFilter(scan_node, predicate)

    return scan_node
```

---

# Stage 4 — Optimizer (Physical Plan Selection)

A logical plan can be executed in multiple ways.

Example:

```
Scan(users)
```

can be implemented as:

- sequential scan
    
- index scan
    
- bitmap scan
    

The optimizer selects the most efficient strategy.

It evaluates:

- table size
    
- index availability
    
- predicate selectivity
    
- cached pages
    
- estimated disk cost
    
- CPU cost
    

Example decision:

```
if index exists on users.id:
    choose index scan
else:
    choose sequential scan
```

---

### Optimizer pseudocode

```
function choose_access_method(table, predicate):

    if index_exists(table, predicate.column):

        index_cost = estimate_index_scan_cost()

        seq_cost = estimate_seq_scan_cost()

        if index_cost < seq_cost:
            return INDEX_SCAN

    return SEQ_SCAN
```

This converts a logical plan into a **physical execution plan**.

---

# Stage 5 — Executor (Plan Execution)

The executor performs the selected physical plan step by step.

Important principle:

the executor **does not access disk pages directly**

Instead it requests operations from the storage engine.

Example operations:

```
scan relation
fetch tuple
follow index pointer
check tuple visibility
```

The executor processes tuples:

> one at a time

using iterator-style execution.

This avoids loading entire tables into memory.

---

# Iterator Execution Model

Executor nodes behave like iterators:

```
next_tuple()
next_tuple()
next_tuple()
```

Example:

```
FilterNode.next()

    tuple = child.next()

    if predicate(tuple):
        return tuple
```

This creates streaming execution.

---

# Example Query Execution Walkthrough

Query:

```sql
SELECT * FROM users WHERE id = 10;
```

Execution pipeline:

```
Parse SQL
Validate schema
Build logical plan
Choose index scan
Execute plan
```

Final execution steps:

```
index scan
heap tuple fetch
visibility check
return tuple
```

Explanation:

### Step 1

Follow index pointer:

```
index_lookup(users.id = 10)
```

Result:

```
tuple_id = (page 52, slot 3)
```

---

### Step 2

Fetch heap tuple

```
fetch_tuple(page 52, slot 3)
```

Storage engine interacts with buffer manager:

```
buffer_manager.get_page(52)
```

---

### Step 3

Check visibility

Transaction manager verifies:

```
is_visible(tuple)
```

based on snapshot rules.

---

### Step 4

Return tuple

Executor sends result to client.

---

# Cooperation With Lower Subsystems

The executor coordinates with:

### Storage engine

Requests:

```
fetch tuple
scan relation
follow index pointer
```

---

### Buffer manager

Requests:

```
get cached page
load page if missing
pin page during access
```

---

### Transaction manager

Ensures:

```
tuple visibility
snapshot correctness
isolation guarantees
```

---

### Recovery manager

Ensures:

```
changes obey WAL rules
crash consistency maintained
```

Even read queries interact safely with WAL-managed pages.

---

# Sequential Scan Behavior

If no index exists:

```
SELECT * FROM users WHERE id = 10;
```

becomes:

```
sequential scan(users)
```

Executor behavior:

```
for each page in relation:

    for each tuple in page:

        if tuple.id == 10:

            return tuple
```

Sequential scans are efficient when:

- table is small
    
- predicate matches many rows
    
- index absent
    
- table already cached
    

Thus optimizer sometimes prefers sequential scans even when indexes exist.

---

# Index Scan Behavior

If index exists:

```
users(id)
```

execution becomes:

```
lookup index entry
retrieve tuple pointer
fetch heap tuple
check visibility
return tuple
```

This avoids scanning unrelated rows.

---

# Example Executor Pseudocode (Index Scan)

```
function execute_index_scan(index, key):

    tuple_refs = index.lookup(key)

    for ref in tuple_refs:

        tuple = storage_engine.fetch_tuple(ref)

        if transaction_manager.is_visible(tuple):

            return tuple
```

---

# Executor Requesting Tuples From Storage Engine

Important architectural principle:

executor requests tuples

it does not access disk pages directly

Example:

```
tuple = storage_engine.fetch_tuple(tuple_id)
```

Storage engine internally performs:

```
locate page
request buffer manager
read slot
decode tuple
return result
```

This separation keeps architecture modular.

---

# Analogy — Travel Planner

The query processor behaves like a travel planner.

It:

- chooses routes
    
- schedules connections
    
- selects transport method
    

But it does not:

- build roads
    
- manufacture trains
    
- control traffic lights
    

Similarly:

query processor coordinates execution

lower layers perform physical work.

---

# Analogy — Restaurant Order System

Query processor:

```
customer order coordinator
```

Storage engine:

```
kitchen
```

Buffer manager:

```
ingredient storage racks
```

Transaction manager:

```
order correctness supervisor
```

Recovery manager:

```
backup generator during power failure
```

The coordinator ensures correct workflow without producing ingredients itself.

---

# Logical Access vs Physical Storage Separation

Query processor decides:

```
scan table
use index
apply filter
join relations
```

Storage engine decides:

```
which page
which slot
how tuple encoded
how index structured
```

Thus:

logical access decisions remain independent from physical layout.

This allows databases to:

- reorganize tables
    
- rebuild indexes
    
- compress pages
    
- change storage formats
    

without affecting user queries.

---

# Complete Query Processor Flow Pseudocode

### Step 1 — Parsing

```
syntax_tree = parse(sql_text)
```

---

### Step 2 — Logical Plan Construction

```
logical_plan = build_logical_plan(syntax_tree)
```

---

### Step 3 — Optimization

```
physical_plan = optimize(logical_plan)
```

---

### Step 4 — Execution

```
result = executor.run(physical_plan)
```

---

# Why the Query Processor Is Essential

Even after implementing:

- page storage
    
- buffer manager
    
- storage engine
    
- transaction manager
    
- WAL recovery manager
    

a database still lacks:

```
SQL understanding
execution strategy selection
access-path optimization
tuple-level coordination
```

The query processor provides exactly this missing intelligence.

It transforms:

```
declarative SQL intent
```

into:

```
coordinated tuple-level execution
```

across:

- storage engine
    
- buffer manager
    
- transaction manager
    
- recovery manager
    

so that databases can return **correct, consistent, and efficient results** from large collections of disk-resident data.
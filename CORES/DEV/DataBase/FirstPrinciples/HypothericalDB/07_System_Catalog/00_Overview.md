## Why a Database Requires a System Catalog — The Metadata Brain of the Database

A modern database system already contains several foundational subsystems:

- physical storage structures (pages, tuples, slots)
    
- buffer manager (cached page access)
    
- storage engine (tuple-level operations)
    
- transaction manager (isolation and visibility)
    
- recovery manager with write-ahead logging (crash safety)
    
- query processor (SQL parsing, planning, optimization, execution)
    

Together, these components allow the database to **store data safely and retrieve it efficiently**.

However, even with all these pieces in place, the database still cannot interpret a simple query like:

```sql
SELECT * FROM users;
```

until it answers several essential questions:

- Does the table exist?
    
- Where is the table stored?
    
- Which columns belong to the table?
    
- Do indexes exist for this table?
    
- What permissions apply to the user issuing the query?
    

To answer these questions, the database must store **metadata about itself**.

That metadata lives inside the **system catalog**.

---

# Why Metadata Must Exist Before Queries Can Execute

Consider what happens when the parser encounters:

```sql
SELECT * FROM users;
```

The database cannot execute this immediately. It must first determine:

```
relation name → users
```

Then verify:

```
lookup_relation("users")
```

Questions answered during lookup:

```
Does relation exist?
Which schema owns it?
Which file stores its heap pages?
Which columns belong to it?
Which indexes exist?
Who may access it?
```

Without this information, the database cannot even construct a logical plan.

Therefore:

**SQL interpretation depends on metadata**

And metadata must be stored somewhere persistent and queryable.

---

# Why Metadata Cannot Be Hardcoded into the Database Engine

One might imagine storing schema definitions inside the database executable itself.

But that would fail immediately because databases allow runtime changes such as:

```
CREATE TABLE
ALTER TABLE
DROP INDEX
CREATE SCHEMA
GRANT permissions
```

If metadata were hardcoded:

- schema changes would require recompiling the database
    
- user-created tables could not exist dynamically
    
- permissions could not change
    
- indexes could not be created interactively
    

Instead:

**metadata must live inside the database itself**

This requirement leads to the system catalog.

---

# What the System Catalog Is

The **system catalog** is a collection of internal metadata tables describing:

> the structure and behavior of the database itself

It stores information about:

- tables
    
- columns
    
- indexes
    
- schemas
    
- constraints
    
- permissions
    
- transactions (in some engines)
    
- optimizer statistics
    

These catalog tables behave like ordinary relations but contain **structural information instead of user data**.

---

# Responsibilities of the System Catalog

The catalog answers structural questions required during query processing.

Examples include:

### Table metadata

```
relation name
relation identifier
storage location
owner
schema
```

### Column metadata

```
column name
data type
position
nullability
default value
```

### Index metadata

```
index name
indexed columns
index type
storage location
```

### Constraint metadata

```
primary keys
foreign keys
uniqueness rules
check constraints
```

### Permission metadata

```
who can SELECT
who can INSERT
who can UPDATE
who can DELETE
```

### Optimizer statistics

```
row counts
value distributions
selectivity estimates
histograms
```

All of this information guides query execution decisions.

---

# How the Parser Uses the System Catalog

When parsing:

```sql
SELECT id FROM users;
```

the parser validates:

```
lookup_relation("users")
lookup_column("users", "id")
```

Example pseudocode:

```
function resolve_relation(name):

    entry = catalog.lookup_relation(name)

    if entry == NULL:
        error("relation does not exist")

    return entry
```

Column validation:

```
function resolve_column(relation, column):

    entry = catalog.lookup_column(relation, column)

    if entry == NULL:
        error("column does not exist")

    return entry
```

Without catalog lookup:

the parser cannot confirm query correctness.

---

# How the Planner Uses the System Catalog

After parsing succeeds, the planner constructs logical execution steps.

To do this, it must determine:

```
available indexes
column types
relation size
constraint rules
```

Example:

```
lookup_indexes("users")
```

Planner pseudocode:

```
function get_relation_indexes(relation):

    return catalog.lookup_indexes(relation)
```

The planner uses this metadata to decide whether index-based execution is possible.

---

# How the Optimizer Uses Catalog Statistics

Choosing efficient execution strategies requires estimating cost.

Cost depends on:

```
table size
index selectivity
column value distribution
```

Statistics stored in catalog tables enable estimation.

Example pseudocode:

```
function estimate_scan_cost(relation):

    stats = catalog.lookup_statistics(relation)

    return stats.row_count * cpu_tuple_cost
```

Example:

```
SELECT * FROM users WHERE id = 10;
```

Optimizer decision:

```
if selectivity(id) is high:
    use index scan
else:
    use sequential scan
```

This decision depends entirely on catalog statistics.

---

# How the Storage Engine Uses Catalog Metadata

The storage engine retrieves tuples from heap pages.

But first it must locate:

```
which file stores relation data
```

Example lookup:

```
catalog.lookup_relation_storage("users")
```

Pseudocode:

```
function locate_relation_file(name):

    relation_entry = catalog.lookup_relation(name)

    return relation_entry.storage_identifier
```

Without catalog metadata:

the storage engine cannot locate relation pages on disk.

---

# The Schema Is Stored as Rows Inside Catalog Tables

A powerful architectural idea underlies database design:

> the schema itself is stored inside tables

Example conceptual catalog table:

```
relations_catalog
```

Rows:

```
users
orders
products
customers
```

Example column catalog:

```
columns_catalog
```

Rows:

```
users.id
users.name
users.email
```

Thus:

the database describes itself using the same relational model it provides to users.

---

# Recursive Self-Describing Architecture

This design makes the database:

> self-describing

The database uses tables to describe its own tables.

This is similar to:

### Library analogy

A library contains a catalog describing:

```
book titles
authors
locations
subjects
```

The catalog itself is stored inside the library.

---

### City map analogy

A city planning office stores maps describing:

```
roads
districts
utilities
zones
```

inside the same administrative system that manages the city.

---

### Dictionary analogy

A dictionary defines words using other words from the dictionary itself.

Similarly:

a database defines tables using catalog tables stored inside itself.

---

# Catalog Tables Use the Same Storage Format as User Tables

Catalog tables are not special memory structures.

They are stored as:

```
heap pages
tuples
slot arrays
```

just like ordinary tables.

Example:

```
catalog_relation
    page 1
    page 2
    page 3
```

They are accessed through:

- storage engine
    
- buffer manager
    
- transaction manager
    
- WAL recovery
    

exactly like user relations.

This keeps architecture consistent and elegant.

---

# Schema Changes Modify Catalog Entries

When users execute:

```
CREATE TABLE users(...)
```

the database performs:

```
insert into catalog_relations
insert into catalog_columns
insert into catalog_constraints
```

Not:

```
modify database source code
```

Example pseudocode:

```
function create_table(name, columns):

    catalog.insert_relation(name)

    for column in columns:
        catalog.insert_column(name, column)
```

Similarly:

```
ALTER TABLE
DROP INDEX
CREATE SCHEMA
```

all modify catalog rows.

---

# Retrieving Column Definitions from Catalog

Example pseudocode:

```
function get_columns(relation):

    return catalog.lookup_columns(relation)
```

Planner uses this to build projection operators.

---

# Locating Index Metadata

Example:

```
function get_indexes(relation):

    return catalog.lookup_indexes(relation)
```

Optimizer uses this to evaluate access strategies.

---

# Retrieving Optimizer Statistics

Example:

```
function get_statistics(relation):

    return catalog.lookup_statistics(relation)
```

Statistics influence:

```
join order
scan strategy
access path selection
```

---

# Query Processor Depends on Catalog Metadata Before Execution Begins

Execution cannot start until parsing and planning complete.

Parsing requires:

```
relation lookup
column lookup
type lookup
```

Planning requires:

```
index lookup
constraint lookup
schema lookup
```

Optimization requires:

```
statistics lookup
row counts
selectivity estimates
```

Thus:

the query processor depends heavily on catalog metadata.

---

# Transaction Manager Protects Catalog Consistency

Catalog updates must remain correct under concurrency.

Example:

```
CREATE TABLE users
```

while another transaction executes:

```
SELECT * FROM users
```

Transaction manager ensures:

```
atomic schema visibility
consistent metadata snapshot
isolation guarantees
```

Example pseudocode:

```
begin transaction

insert catalog entries

commit transaction
```

Other transactions see either:

```
table exists
```

or

```
table does not exist
```

Never partial metadata.

---

# Write-Ahead Logging Protects Catalog Metadata

Catalog tables are critical system structures.

Therefore:

catalog modifications must obey WAL rules.

Example:

```
log catalog change
flush WAL
modify catalog page
```

This ensures:

```
crash-safe schema updates
consistent metadata recovery
durable table definitions
```

Without WAL protection:

database structure itself could become corrupted after crashes.

---

# How the System Catalog Enables Runtime Schema Interpretation

Because metadata lives inside relational tables:

the database can interpret schema dynamically.

Example:

```
CREATE TABLE analytics_data(...)
```

Immediately becomes available to:

```
parser
planner
optimizer
executor
```

without restarting the database.

Thus:

the database adapts to schema evolution in real time.

---

# Final Insight — The Database Describes Itself Using Its Own Storage Engine

The system catalog transforms the database into a:

> self-describing relational system

Instead of embedding schema knowledge inside executable code:

the database stores schema definitions as rows inside catalog tables.

These catalog tables are:

- stored in heap pages
    
- cached by the buffer manager
    
- protected by the transaction manager
    
- logged by WAL recovery
    
- queried by the query processor
    

This creates a recursive architecture:

the database uses its own relational storage engine to describe its own structure.

Because of this design, databases remain flexible, extensible, crash-safe, concurrent, and dynamically configurable while continuing to support efficient and correct execution of SQL queries.
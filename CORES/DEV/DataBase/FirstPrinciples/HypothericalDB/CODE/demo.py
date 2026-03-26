"""
HypotheticalDB — End-to-End Demo
=================================
This demo wires all six layers together and walks through a complete database
workflow, printing what's happening at each layer as it goes.

Layers exercised (bottom -> top):
  1. Physical Storage  — pages, slots, tuple headers
  2. Buffer Manager    — page caching, pin/unpin, LRU eviction
  3. Storage Engine    — heap INSERT/UPDATE/DELETE, version chains
  4. Transaction Mgr   — begin/commit, snapshots, MVCC visibility
  5. System Catalog    — CREATE TABLE, CREATE INDEX, schema lookup
  6. Query Processor   — SeqScan, Filter, Project, IndexScan, Aggregate

Scenarios:
  A. CREATE TABLE + INSERT rows inside a transaction
  B. SELECT all rows (SeqScan + MVCC visibility)
  C. UPDATE a row — show the version chain
  D. MVCC: two concurrent transactions see DIFFERENT versions of the same row
  E. COMMIT the update — new readers see the new version
  F. SELECT with WHERE (Filter) and column projection (Project)
  G. Aggregate: COUNT and SUM
  H. VACUUM — physically remove dead tuples
  I. CREATE INDEX + IndexScan
  J. Buffer Manager and Disk I/O statistics
"""

from buffer_manager      import BufferManager, SimulatedDisk
from storage_engine      import HeapRelation
from transaction_manager import TransactionManager
from system_catalog      import SystemCatalog, ColumnDef
from query_processor     import (
    SeqScan, IndexScan, Filter, Project, Aggregate, NestedLoopJoin, Executor
)


# -- Formatting helpers --------------------------------------------------------

def section(title: str) -> None:
    print(f"\n{'='*62}")
    print(f"  {title}")
    print(f"{'='*62}")

def step(msg: str) -> None:
    print(f"\n  >>  {msg}")

def show(msg: str) -> None:
    print(f"      {msg}")

def table_print(rows, cols=None) -> None:
    if not rows:
        print("     (no rows)")
        return
    cols = cols or list(rows[0].keys())
    widths = {c: max(len(c), max(len(str(r.get(c, ""))) for r in rows)) for c in cols}
    header = "  ".join(f"{c:<{widths[c]}}" for c in cols)
    divider = "  ".join("-" * widths[c] for c in cols)
    print(f"     {header}")
    print(f"     {divider}")
    for row in rows:
        line = "  ".join(f"{str(row.get(c,'')):<{widths[c]}}" for c in cols)
        print(f"     {line}")


# -- Bootstrap -----------------------------------------------------------------

def main():
    disk    = SimulatedDisk()
    bufmgr  = BufferManager(pool_size=16, disk=disk)
    txmgr   = TransactionManager()
    catalog = SystemCatalog()
    executor = Executor()

    # ══════════════════════════════════════════════════════════════════════════
    section("A.  CREATE TABLE employees")
    # ══════════════════════════════════════════════════════════════════════════

    catalog.create_table("employees", columns=[
        ColumnDef("id",         "int",  nullable=False),
        ColumnDef("name",       "str",  nullable=False),
        ColumnDef("department", "str"),
        ColumnDef("salary",     "int"),
    ])
    employees = HeapRelation("employees", bufmgr)

    step("Schema registered in system catalog")
    show(catalog.describe())

    # ══════════════════════════════════════════════════════════════════════════
    section("B.  INSERT rows  (Transaction 1)")
    # ══════════════════════════════════════════════════════════════════════════

    tx1 = txmgr.begin()
    step(f"BEGIN  TX-{tx1.xid}  (snapshot.xmax={tx1.snapshot.xmax})")

    seed_data = [
        {"id": 1, "name": "Alice",   "department": "Engineering", "salary": 95000},
        {"id": 2, "name": "Bob",     "department": "Marketing",   "salary": 72000},
        {"id": 3, "name": "Carol",   "department": "Engineering", "salary": 88000},
        {"id": 4, "name": "Dave",    "department": "HR",          "salary": 65000},
        {"id": 5, "name": "Eve",     "department": "Marketing",   "salary": 78000},
    ]

    locations = {}      # id -> (page_id, slot_num)
    for row in seed_data:
        loc = employees.insert(row, xid=tx1.xid)
        locations[row["id"]] = loc
        show(f"  INSERT {row['name']:<8} -> heap location {loc}  "
             f"(xmin=TX-{tx1.xid}, xmax=0)")

    txmgr.commit(tx1)
    step(f"COMMIT TX-{tx1.xid}  -> all 5 rows now visible to future snapshots")

    # ══════════════════════════════════════════════════════════════════════════
    section("C.  SELECT * FROM employees  (SeqScan)")
    # ══════════════════════════════════════════════════════════════════════════

    tx2 = txmgr.begin()
    step(f"BEGIN TX-{tx2.xid}  — sequential scan, all visible rows")

    rows = executor.run(SeqScan(employees, tx2, txmgr))
    table_print(rows)

    txmgr.commit(tx2)

    # ══════════════════════════════════════════════════════════════════════════
    section("D.  UPDATE — version chain (MVCC in action)")
    # ══════════════════════════════════════════════════════════════════════════
    #
    # UPDATE creates a NEW tuple version, stamps the old one with xmax,
    # and links them via ctid. Both versions coexist until VACUUM.
    #
    # Old:  xmin=1, xmax=3, ctid=(1,0)  <- "replaced by TX-3"
    #                          ↓
    # New:  xmin=3, xmax=0,   ctid=None  <- current version

    tx3 = txmgr.begin()
    step(f"BEGIN TX-{tx3.xid}  — UPDATE Alice: salary 95000 -> 110000")

    old_loc  = locations[1]
    new_data = {"id": 1, "name": "Alice", "department": "Engineering", "salary": 110000}
    new_loc  = employees.update(old_loc, new_data, xid=tx3.xid)
    locations[1] = new_loc

    # Inspect the version chain directly on the page
    page = bufmgr.pin(old_loc[0]).page
    bufmgr.unpin(old_loc[0])
    old_tup = page.get_tuple(old_loc[1])
    show(f"Old tuple at {old_loc}: "
         f"xmin={old_tup.header.xmin}, xmax={old_tup.header.xmax}, "
         f"ctid={old_tup.header.ctid}   <- points to new version")

    new_page = bufmgr.pin(new_loc[0]).page
    bufmgr.unpin(new_loc[0])
    new_tup = new_page.get_tuple(new_loc[1])
    show(f"New tuple at {new_loc}: "
         f"xmin={new_tup.header.xmin}, xmax={new_tup.header.xmax}, salary=110000")

    # ══════════════════════════════════════════════════════════════════════════
    section("E.  CONCURRENT READ — two transactions see different versions")
    # ══════════════════════════════════════════════════════════════════════════
    #
    # tx3 has NOT committed yet.
    # A reader starting NOW captures a snapshot where tx3 is still ACTIVE.
    # That reader will see Alice's OLD salary.

    tx_reader_before = txmgr.begin()
    step(f"TX-{tx_reader_before.xid} starts BEFORE TX-{tx3.xid} commits")
    show(f"  TX-{tx3.xid} is in snapshot.active_xids -> its changes are invisible")

    rows_before = executor.run(SeqScan(employees, tx_reader_before, txmgr))
    alice_before = next(r for r in rows_before if r["name"] == "Alice")
    show(f"  Alice's salary seen by TX-{tx_reader_before.xid}: {alice_before['salary']}  <- OLD")

    # Now TX-3 commits
    txmgr.commit(tx3)
    step(f"COMMIT TX-{tx3.xid}")

    # A new reader starting AFTER the commit sees the new version
    tx_reader_after = txmgr.begin()
    step(f"TX-{tx_reader_after.xid} starts AFTER TX-{tx3.xid} commits")

    rows_after = executor.run(SeqScan(employees, tx_reader_after, txmgr))
    alice_after = next(r for r in rows_after if r["name"] == "Alice")
    show(f"  Alice's salary seen by TX-{tx_reader_after.xid}: {alice_after['salary']}  <- NEW")

    txmgr.commit(tx_reader_before)
    txmgr.commit(tx_reader_after)

    # ══════════════════════════════════════════════════════════════════════════
    section("F.  SELECT with WHERE + column projection")
    # ══════════════════════════════════════════════════════════════════════════
    #
    # SELECT name, salary FROM employees WHERE department = 'Engineering'
    #
    # Plan tree:
    #   Project(name, salary)
    #       +---- Filter(department == 'Engineering')
    #               +---- SeqScan(employees)

    tx4 = txmgr.begin()
    step("SELECT name, salary FROM employees WHERE department = 'Engineering'")

    plan = Project(
        columns=["name", "salary"],
        child=Filter(
            predicate=lambda row: row["department"] == "Engineering",
            child=SeqScan(employees, tx4, txmgr)
        )
    )
    results = executor.run(plan)
    table_print(results, cols=["name", "salary"])
    txmgr.commit(tx4)

    # ══════════════════════════════════════════════════════════════════════════
    section("G.  Aggregate — COUNT and SUM per department")
    # ══════════════════════════════════════════════════════════════════════════

    tx5 = txmgr.begin()
    step("SELECT COUNT(*) headcount, SUM(salary) total_salary FROM employees")

    plan = Aggregate(
        child=SeqScan(employees, tx5, txmgr),
        aggregations={
            "headcount":    lambda rows: len(rows),
            "total_salary": lambda rows: sum(r["salary"] for r in rows),
            "avg_salary":   lambda rows: sum(r["salary"] for r in rows) // len(rows),
        }
    )
    results = executor.run(plan)
    table_print(results)
    txmgr.commit(tx5)

    # ══════════════════════════════════════════════════════════════════════════
    section("H.  VACUUM — physically remove Alice's old (dead) tuple")
    # ══════════════════════════════════════════════════════════════════════════
    #
    # Alice's old tuple has xmax = TX-3, which is COMMITTED.
    # Once no active transaction has a snapshot before TX-3, it's safe to remove.
    # oldest_active_xid() gives us the safety horizon.

    horizon = txmgr.oldest_active_xid()
    step(f"Oldest active XID = {horizon}  (safety horizon for VACUUM)")

    # Count dead tuples before vacuum
    page0 = bufmgr.pin(0).page
    bufmgr.unpin(0)
    dead_before = sum(1 for t in page0.tuples if t and t.is_deleted())
    show(f"Page 0 before VACUUM: {dead_before} dead tuple(s)")

    employees.vacuum(oldest_active_xid=horizon)

    dead_after = sum(1 for t in page0.tuples if t and t.is_deleted())
    show(f"Page 0 after  VACUUM: {dead_after} dead tuple(s)  (slots freed for reuse)")

    # ══════════════════════════════════════════════════════════════════════════
    section("I.  CREATE INDEX + IndexScan")
    # ══════════════════════════════════════════════════════════════════════════
    #
    # Build a unique index on employees.id.
    # Then use it to look up a single employee by ID directly.

    id_index = catalog.create_index(
        "employees_id_idx", "employees", "id", unique=True
    )

    # Populate the index by scanning the heap once (like CREATE INDEX CONCURRENTLY)
    tx6 = txmgr.begin()
    for location, tup in employees.seq_scan():
        if txmgr.is_visible(tup, tx6):
            id_index.insert(tup.data["id"], location)
    txmgr.commit(tx6)

    step(f"Index built: {len(id_index._data)} entries  {id_index}")

    # INDEX SCAN: find employee id=3
    tx7 = txmgr.begin()
    step("SELECT * FROM employees WHERE id = 3  (index scan)")

    plan = IndexScan(employees, tx7, txmgr, index=id_index, lookup_key=3)
    results = executor.run(plan)
    table_print(results)
    txmgr.commit(tx7)

    # ══════════════════════════════════════════════════════════════════════════
    section("J.  Buffer Manager + Disk I/O stats")
    # ══════════════════════════════════════════════════════════════════════════

    step("Buffer pool state:")
    print(bufmgr.status())

    step("Disk I/O counters:")
    for k, v in disk.stats.items():
        show(f"  {k}: {v}")

    # ══════════════════════════════════════════════════════════════════════════
    section("K.  Transaction status table")
    # ══════════════════════════════════════════════════════════════════════════

    print(txmgr.status_summary())

    section("Done — all 6 layers exercised end-to-end")


if __name__ == "__main__":
    main()

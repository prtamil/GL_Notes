"""
Query Processor
===============
Bridges the gap between what the user asked for (SQL) and how to get it
(physical operations on heap pages and indexes).

─── Pipeline ─────────────────────────────────────────────────────────────────

  SQL text
    → [Parser]    validate grammar, produce AST
    → [Planner]   translate AST into a logical plan (abstract operations)
    → [Optimizer] choose physical strategy (which index? which join method?)
    → [Executor]  run the plan, stream results back to the user

  In this file we focus on Executor + Plan Nodes.
  Parsing is skipped (we build plans in code directly) to keep concepts clear.

─── Iterator Model (Volcano / Pull Model) ────────────────────────────────────

  Every plan node is an ITERATOR with three methods:
    open()      → initialize state, open child iterators
    next_row()  → return the next matching row, or None when done
    close()     → release resources

  The executor calls open() on the ROOT node, then calls next_row() in a loop.
  Each node calls next_row() on its CHILD to get input rows.
  Data "bubbles up" through the tree one row at a time — like pulling water
  through a tube. No intermediate results loaded into memory (except Aggregate).

  Example plan tree for:
    SELECT name, salary FROM employees WHERE dept='Engineering'

       Project(name, salary)
           │
       Filter(dept == 'Engineering')
           │
       SeqScan(employees)

  Execution: Executor pulls from Project → Project pulls from Filter →
             Filter pulls from SeqScan → SeqScan reads heap pages.

─── Plan Nodes implemented here ─────────────────────────────────────────────

  Leaf nodes (data sources):
    SeqScan    — full table scan, every visible tuple
    IndexScan  — jump to specific tuples via an index

  Unary nodes (transform one stream):
    Filter     — WHERE clause: pass rows matching a predicate
    Project    — SELECT columns: strip rows to only requested columns
    Aggregate  — COUNT/SUM/AVG: consume all rows, emit one summary row

  Binary nodes (combine two streams):
    NestedLoopJoin — simple JOIN: for each outer row, scan entire inner
"""

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from typing import Any

from physical_storage import Tuple
from storage_engine import HeapRelation
from transaction_manager import TransactionManager, Transaction
from system_catalog import IndexEntry

# A Row is what the query layer deals with — plain column→value dicts
Row = dict[str, Any]


# ─── Base Plan Node ───────────────────────────────────────────────────────────

class PlanNode(ABC):
    """
    Every node in the plan tree implements this interface.
    Parent nodes pull from children by calling next_row().
    """

    @abstractmethod
    def open(self) -> None:
        """Initialize state. Called once before the first next_row()."""
        ...

    @abstractmethod
    def next_row(self) -> Row | None:
        """Return the next result row, or None when this node is exhausted."""
        ...

    @abstractmethod
    def close(self) -> None:
        """Release any held resources (file handles, pins, etc.)."""
        ...

    def __iter__(self) -> Iterator[Row]:
        """Convenience: use a PlanNode as a Python iterator."""
        self.open()
        try:
            while True:
                row = self.next_row()
                if row is None:
                    break
                yield row
        finally:
            self.close()


# ─── SeqScan ──────────────────────────────────────────────────────────────────
#
# Reads every tuple in the heap, one page at a time.
# Applies MVCC visibility: skips tuples the current transaction can't see.
#
# When to use: no useful index exists, table is small, predicate is broad.

class SeqScan(PlanNode):

    def __init__(self, relation: HeapRelation,
                 tx: Transaction, tx_manager: TransactionManager):
        self.relation   = relation
        self.tx         = tx
        self.tx_manager = tx_manager
        self._iter: Iterator | None = None

    def open(self) -> None:
        self._iter = self.relation.seq_scan()

    def next_row(self) -> Row | None:
        for _location, tup in self._iter:
            if self.tx_manager.is_visible(tup, self.tx):
                return tup.data       # strip header, return plain data dict
        return None

    def close(self) -> None:
        self._iter = None


# ─── IndexScan ────────────────────────────────────────────────────────────────
#
# Uses an index to jump directly to the target tuple(s).
#
# Steps:
#   1. Look up the key in the index → get (page_id, slot_num)
#   2. Pin the page, fetch the tuple from the heap
#   3. Check MVCC visibility (the index entry might point to an old version)
#   4. Return the data if visible
#
# When to use: highly selective predicate (few matching rows), large table.

class IndexScan(PlanNode):

    def __init__(self, relation: HeapRelation,
                 tx: Transaction, tx_manager: TransactionManager,
                 index: IndexEntry, lookup_key: Any):
        self.relation   = relation
        self.tx         = tx
        self.tx_manager = tx_manager
        self.index      = index
        self.lookup_key = lookup_key
        self._rows:  list[Row] = []
        self._pos:   int       = 0

    def open(self) -> None:
        """
        Perform the index lookup once. All matching tuples are fetched here.
        (For a point lookup there is at most one result.)
        """
        location = self.index.lookup(self.lookup_key)
        if not location:
            return  # key not in index

        page_id, slot_num = location
        frame = self.relation._buf_mgr.pin(page_id)
        tup   = frame.page.get_tuple(slot_num)
        self.relation._buf_mgr.unpin(page_id)

        if tup and self.tx_manager.is_visible(tup, self.tx):
            self._rows = [tup.data]

    def next_row(self) -> Optional[Row]:
        if self._pos < len(self._rows):
            row = self._rows[self._pos]
            self._pos += 1
            return row
        return None

    def close(self) -> None:
        self._rows = []
        self._pos  = 0


# ─── Filter ───────────────────────────────────────────────────────────────────
#
# Implements the WHERE clause. Pulls rows from its child node and passes
# through only those where predicate(row) == True.
#
# The predicate is any Python callable: lambda row: row['salary'] > 80000

class Filter(PlanNode):

    def __init__(self, child: PlanNode, predicate: Callable[[Row], bool]):
        self.child     = child
        self.predicate = predicate

    def open(self) -> None:
        self.child.open()

    def next_row(self) -> Optional[Row]:
        while True:
            row = self.child.next_row()
            if row is None:
                return None          # child exhausted
            if self.predicate(row):
                return row           # passes the WHERE test
            # else: skip this row, pull next from child

    def close(self) -> None:
        self.child.close()


# ─── Project ──────────────────────────────────────────────────────────────────
#
# Implements SELECT col1, col2, ...
# Strips each incoming row down to only the requested columns.
# SELECT * is just Project with all column names.

class Project(PlanNode):

    def __init__(self, child: PlanNode, columns: list[str]):
        self.child   = child
        self.columns = columns

    def open(self) -> None:
        self.child.open()

    def next_row(self) -> Optional[Row]:
        row = self.child.next_row()
        if row is None:
            return None
        return {col: row[col] for col in self.columns if col in row}

    def close(self) -> None:
        self.child.close()


# ─── NestedLoopJoin ───────────────────────────────────────────────────────────
#
# The simplest join algorithm:
#   For each row from the OUTER stream:
#     Restart the INNER stream from the beginning
#     For each inner row:
#       If join_predicate(outer_row, inner_row): emit combined row
#
# Cost: O(outer_rows × inner_rows)  — slow for large tables.
# But it's conceptually transparent: you can see every step.

class NestedLoopJoin(PlanNode):

    def __init__(self, outer: PlanNode, inner: PlanNode,
                 join_predicate: Callable[[Row, Row], bool]):
        self.outer          = outer
        self.inner          = inner
        self.join_predicate = join_predicate
        self._outer_row:    Row | None = None

    def open(self) -> None:
        self.outer.open()
        self._outer_row = self.outer.next_row()   # prime the first outer row
        if self._outer_row:
            self.inner.open()

    def next_row(self) -> Optional[Row]:
        while self._outer_row is not None:
            inner_row = self.inner.next_row()

            if inner_row is None:
                # Inner exhausted → advance outer, restart inner
                self.inner.close()
                self._outer_row = self.outer.next_row()
                if self._outer_row:
                    self.inner.open()
                continue

            if self.join_predicate(self._outer_row, inner_row):
                return {**self._outer_row, **inner_row}   # merge the two rows

        return None   # both streams exhausted

    def close(self) -> None:
        self.inner.close()
        self.outer.close()


# ─── Aggregate ────────────────────────────────────────────────────────────────
#
# Implements COUNT, SUM, AVG, MIN, MAX.
# Aggregate is a BLOCKING operator: it must consume ALL rows from its child
# before it can emit even one result. This is why aggregation is expensive.
#
# aggregations = { "output_col_name": fn(all_rows) -> scalar }
#
# The function receives the full list of rows, so it can do anything:
#   "headcount":    lambda rows: len(rows)
#   "total_salary": lambda rows: sum(r["salary"] for r in rows)
#   "avg_salary":   lambda rows: sum(r["salary"] for r in rows) / len(rows)

class Aggregate(PlanNode):

    def __init__(self, child: PlanNode,
                 aggregations: dict[str, Callable[[list[Row]], Any]]):
        self.child        = child
        self.aggregations = aggregations
        self._result:   Row | None = None
        self._returned: bool       = False

    def open(self) -> None:
        """
        Consume ALL rows from the child, then apply each aggregation function.
        After open() we have exactly one summary row ready to return.

        Aggregation is a BLOCKING operation — we need every row before we
        can compute COUNT, SUM, etc. This is unlike Filter/Project which
        stream one row at a time.
        """
        self.child.open()
        all_rows = list(self.child)    # must read everything first

        self._result   = {col: fn(all_rows) for col, fn in self.aggregations.items()}
        self._returned = False

    def next_row(self) -> Optional[Row]:
        if not self._returned:
            self._returned = True
            return self._result
        return None   # aggregation always returns exactly one row

    def close(self) -> None:
        self.child.close()
        self._result = None


# ─── Executor ─────────────────────────────────────────────────────────────────
#
# The executor drives the plan tree. It calls open() on the root, then
# repeatedly calls next_row() until None, then calls close().
# This is the Volcano iterator model: simple, composable, streaming.

class Executor:

    def run(self, plan: PlanNode) -> list[Row]:
        """Execute a plan and return all result rows as a list."""
        return list(plan)   # __iter__ handles open → next_row loop → close

    def run_streaming(self, plan: PlanNode) -> Iterator[Row]:
        """Execute a plan and yield rows one at a time (streaming mode)."""
        yield from plan

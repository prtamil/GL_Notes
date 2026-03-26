"""
System Catalog
==============
The system catalog is the database's self-description.
It is a set of metadata tables that describe everything else in the system:
tables, columns, indexes, constraints, statistics, and permissions.

Why does this exist?
  Schema cannot be hardcoded. Users CREATE, ALTER, and DROP tables at runtime.
  The database must answer "does this column exist?" before executing any query.
  By storing metadata as regular data, schema changes get ACID guarantees free.

Who uses the catalog?
  Parser       → "Does table 'employees' exist? Does column 'salary' exist?"
  Planner      → "What indexes exist on 'employees'?"
  Optimizer    → "How many rows does 'employees' have? What's the salary distribution?"
  Storage Eng. → "Which pages belong to 'employees'?"

The catalog is self-describing:
  The catalog tables themselves live in heap pages, just like user tables.
  In PostgreSQL these are: pg_class, pg_attribute, pg_index, pg_statistic, etc.
  Here we model them as Python dataclasses for clarity.
"""

from dataclasses import dataclass, field
from typing import Any


# ─── Column Definition ────────────────────────────────────────────────────────
#
# Corresponds to one row in PostgreSQL's pg_attribute table.

@dataclass
class ColumnDef:
    name:     str
    col_type: str        # "int", "str", "float", "bool"
    nullable: bool = True

    def __repr__(self) -> str:
        null = "" if self.nullable else " NOT NULL"
        return f"{self.name} {self.col_type.upper()}{null}"


# ─── Table Entry ──────────────────────────────────────────────────────────────
#
# Corresponds to one row in PostgreSQL's pg_class table.
# Describes one relation (table) in the database.

@dataclass
class TableEntry:
    table_name:  str
    columns:     list[ColumnDef]
    first_page:  int = 0    # page_id where this table's heap begins
    num_pages:   int = 0    # how many pages this table uses
    row_count:   int = 0    # optimizer statistic: approximate row count

    def get_column(self, name: str) -> ColumnDef | None:
        for col in self.columns:
            if col.name == name:
                return col
        return None

    def column_names(self) -> list[str]:
        return [c.name for c in self.columns]

    def validate_row(self, data: dict[str, Any]) -> None:
        """Check that a data dict matches this table's schema."""
        for col in self.columns:
            if not col.nullable and col.name not in data:
                raise ValueError(f"Column '{col.name}' is NOT NULL but missing from insert")
        for key in data:
            if self.get_column(key) is None:
                raise ValueError(f"Unknown column '{key}' in table '{self.table_name}'")

    def __repr__(self) -> str:
        cols = ", ".join(repr(c) for c in self.columns)
        return f"Table({self.table_name!r}: [{cols}], ~{self.row_count} rows)"


# ─── Index Entry ──────────────────────────────────────────────────────────────
#
# Corresponds to one row in PostgreSQL's pg_index table.
# In a real system this would store the B-tree root page ID, fill factor, etc.
# Here we simulate the index data structure with a plain dict.

@dataclass
class IndexEntry:
    index_name:  str
    table_name:  str
    column_name: str
    is_unique:   bool = False

    # Simulated B-tree: maps key → (page_id, slot_num)
    # A real B-tree would span multiple pages and support range scans.
    _data: dict[Any, tuple] = field(default_factory=dict, repr=False)

    def lookup(self, key: Any) -> tuple | None:
        """Point lookup: find the heap location for a key."""
        return self._data.get(key)

    def insert(self, key: Any, location: tuple) -> None:
        """Add a key → heap_location entry (called after INSERT into heap)."""
        if self.is_unique and key in self._data:
            raise ValueError(f"Unique constraint violation on index '{self.index_name}': key={key!r}")
        self._data[key] = location

    def delete(self, key: Any) -> None:
        """Remove a key entry (called after DELETE from heap)."""
        self._data.pop(key, None)

    def __repr__(self) -> str:
        unique = " UNIQUE" if self.is_unique else ""
        return (f"Index({self.index_name!r}{unique} ON "
                f"{self.table_name}({self.column_name}), "
                f"{len(self._data)} entries)")


# ─── Column Statistics ────────────────────────────────────────────────────────
#
# Gathered by ANALYZE and used by the optimizer to choose between
# sequential scan vs index scan, and to estimate join sizes.

@dataclass
class ColumnStats:
    table_name:    str
    column_name:   str
    null_fraction: float = 0.0    # fraction of rows where value is NULL
    n_distinct:    int   = 0      # number of distinct values
    most_common:   list  = field(default_factory=list)  # most frequent values


# ─── System Catalog ───────────────────────────────────────────────────────────

class SystemCatalog:
    """
    The central metadata registry.

    In PostgreSQL: pg_class + pg_attribute + pg_index + pg_statistic + ...
    Here: one unified Python object, split into dicts by entity type.

    A real catalog is itself stored as heap pages (self-describing).
    Here we use plain Python dicts so schema lookups are obvious.
    """

    def __init__(self):
        self._tables:  dict[str, TableEntry]  = {}
        self._indexes: dict[str, IndexEntry]  = {}
        self._stats:   dict[str, ColumnStats] = {}

    # ── DDL: Tables ───────────────────────────────────────────────────────────

    def create_table(self, name: str, columns: list[ColumnDef]) -> TableEntry:
        """
        CREATE TABLE — register the schema in the catalog.

        In a real DB this writes a WAL record, allocates the first heap page,
        and does all of this atomically under a transaction.
        """
        if name in self._tables:
            raise ValueError(f"Table '{name}' already exists")
        entry = TableEntry(table_name=name, columns=columns)
        self._tables[name] = entry
        return entry

    def drop_table(self, name: str) -> None:
        """DROP TABLE — remove schema and all indexes. Heap cleanup is separate."""
        if name not in self._tables:
            raise ValueError(f"Table '{name}' not found")
        del self._tables[name]
        # Remove all indexes on this table
        stale = [k for k, v in self._indexes.items() if v.table_name == name]
        for k in stale:
            del self._indexes[k]

    def get_table(self, name: str) -> TableEntry:
        if name not in self._tables:
            raise ValueError(f"Unknown table '{name}'")
        return self._tables[name]

    def list_tables(self) -> list[str]:
        return list(self._tables.keys())

    # ── DDL: Indexes ──────────────────────────────────────────────────────────

    def create_index(self, index_name: str, table_name: str,
                     column_name: str, unique: bool = False) -> IndexEntry:
        """
        CREATE INDEX — register the index in the catalog.
        The caller is responsible for populating _data via index.insert().
        """
        table = self.get_table(table_name)
        if table.get_column(column_name) is None:
            raise ValueError(f"Column '{column_name}' not found in '{table_name}'")
        if index_name in self._indexes:
            raise ValueError(f"Index '{index_name}' already exists")
        entry = IndexEntry(index_name=index_name, table_name=table_name,
                           column_name=column_name, is_unique=unique)
        self._indexes[index_name] = entry
        return entry

    def get_index(self, index_name: str) -> IndexEntry | None:
        return self._indexes.get(index_name)

    def indexes_for_table(self, table_name: str) -> list[IndexEntry]:
        """Return all indexes defined on a given table."""
        return [e for e in self._indexes.values() if e.table_name == table_name]

    # ── Statistics (ANALYZE) ──────────────────────────────────────────────────

    def update_row_count(self, table_name: str, row_count: int) -> None:
        """
        ANALYZE updates approximate row counts for the optimizer.
        The optimizer uses row_count to decide: index scan vs sequential scan.
          - Small table → sequential scan (index overhead not worth it)
          - Large table + selective predicate → index scan
        """
        self.get_table(table_name).row_count = row_count

    # ── Diagnostics ───────────────────────────────────────────────────────────

    def describe(self) -> str:
        lines = ["System Catalog:"]
        for tbl in self._tables.values():
            lines.append(f"  {tbl}")
            for idx in self.indexes_for_table(tbl.table_name):
                lines.append(f"    └─ {idx}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return (f"SystemCatalog(tables={list(self._tables.keys())}, "
                f"indexes={list(self._indexes.keys())})")

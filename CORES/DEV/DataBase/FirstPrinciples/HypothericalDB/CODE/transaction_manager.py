"""
Transaction Manager
===================
Coordinates logical correctness above the storage engine.

Every tuple in the heap carries xmin (who created it) and xmax (who deleted it).
The transaction manager answers the central MVCC question:

    "Given THIS transaction's snapshot, is THIS tuple version visible to me?"

─── How MVCC works ──────────────────────────────────────────────────────────

  1. When a transaction begins, it receives a SNAPSHOT:
       snapshot = { xmin, xmax, active_xids }
     This is a frozen record of what was committed at that moment.

  2. Readers never block writers. Writers never block readers.
     Each transaction sees a consistent point-in-time view of the world.

  3. A tuple version is visible to a snapshot if:
       - Its creator (xmin) was committed BEFORE the snapshot was taken
       - AND it has not been deleted, OR its deleter (xmax) was NOT yet
         committed when the snapshot was taken

─── Snapshot anatomy ────────────────────────────────────────────────────────

  xmin:        lowest XID that was active when this snapshot was taken
  xmax:        next XID to be assigned (all XIDs >= xmax are "in the future")
  active_xids: set of transactions that were running at snapshot time

  XID is invisible to this snapshot if:
    - xid >= xmax          → started AFTER our snapshot (future)
    - xid in active_xids   → was running when we started (uncommitted)

  XID is visible to this snapshot if:
    - xid < xmax AND xid not in active_xids AND status == COMMITTED
"""

from dataclasses import dataclass, field
from enum import Enum, auto

from physical_storage import Tuple


# ─── Transaction Status ───────────────────────────────────────────────────────

class TxStatus(Enum):
    ACTIVE    = auto()   # currently running
    COMMITTED = auto()   # work is durable and visible to future transactions
    ABORTED   = auto()   # work is discarded; tuples with this xmin are invisible


# ─── Snapshot ─────────────────────────────────────────────────────────────────
#
# A snapshot is an immutable record of the committed world at a point in time.
# Every read transaction carries one. It never changes after creation.

@dataclass(frozen=True)
class Snapshot:
    xmin:        int        # smallest XID that was active at snapshot time
    xmax:        int        # upper bound — all XIDs >= xmax are in the future
    active_xids: frozenset  # XIDs that were running when snapshot was taken

    def xid_committed_before_snapshot(self, xid: int,
                                       status_table: dict[int, TxStatus]) -> bool:
        """
        Was transaction `xid` committed before this snapshot was taken?
        This is the core visibility check used for both xmin and xmax.
        """
        if xid >= self.xmax:
            return False   # started after us — invisible

        if xid in self.active_xids:
            return False   # was running when we started — not yet committed to us

        return status_table.get(xid) == TxStatus.COMMITTED


# ─── Transaction ──────────────────────────────────────────────────────────────

@dataclass
class Transaction:
    xid:      int
    status:   TxStatus          = TxStatus.ACTIVE
    snapshot: Snapshot | None = None   # captured at begin()


# ─── Transaction Manager ──────────────────────────────────────────────────────

class TransactionManager:

    def __init__(self):
        self._next_xid:     int                     = 1
        self._transactions: dict[int, Transaction]  = {}
        self._status_table: dict[int, TxStatus]     = {}
        # status_table is separate from transactions dict because VACUUM and
        # the visibility check need to look up status by XID quickly,
        # even for transactions that have long since finished.

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def begin(self) -> Transaction:
        """
        Start a new transaction.

        Assigns an XID and captures a snapshot of the currently active
        transactions. The snapshot determines what data this transaction
        can see — it never changes after this point.
        """
        xid = self._next_xid
        self._next_xid += 1

        # Who is running RIGHT NOW? These will be invisible to our snapshot.
        currently_active = frozenset(
            x for x, tx in self._transactions.items()
            if tx.status == TxStatus.ACTIVE
        )

        snapshot = Snapshot(
            xmin        = min(currently_active | {xid}),
            xmax        = self._next_xid,  # next XID = upper bound of visibility
            active_xids = currently_active,
        )

        tx = Transaction(xid=xid, snapshot=snapshot)
        self._transactions[xid] = tx
        self._status_table[xid] = TxStatus.ACTIVE
        return tx

    def commit(self, tx: Transaction) -> None:
        """
        Mark the transaction as committed.

        From this point forward, any NEW snapshot will be able to see the
        tuples this transaction created (xmin = tx.xid).
        Existing snapshots that were already taken will NOT see them
        (tx.xid is in their active_xids set).
        """
        tx.status                  = TxStatus.COMMITTED
        self._status_table[tx.xid] = TxStatus.COMMITTED

    def rollback(self, tx: Transaction) -> None:
        """
        Mark as aborted. Any tuples with xmin = tx.xid are invisible to all.

        The tuples remain physically in the heap until VACUUM removes them —
        but the status_table records ABORTED, so visibility checks return False.
        """
        tx.status                  = TxStatus.ABORTED
        self._status_table[tx.xid] = TxStatus.ABORTED

    # ── Visibility ────────────────────────────────────────────────────────────

    def is_visible(self, tup: Tuple, tx: Transaction) -> bool:
        """
        The central MVCC question: can transaction `tx` see this tuple version?

        A tuple version is visible when:
          1. Its creator committed before our snapshot  (xmin check)
          2. It has NOT been deleted, OR its deletion is not yet visible (xmax check)

        Reading this function is the clearest way to understand MVCC.
        """
        snap = tx.snapshot

        # ── 1. Was this tuple created by a transaction we can see? ────────────
        creator_committed = snap.xid_committed_before_snapshot(
            tup.header.xmin, self._status_table
        )
        if not creator_committed:
            return False   # created by uncommitted or future transaction

        # ── 2. Has this tuple been deleted/updated? ───────────────────────────
        if tup.header.xmax == 0:
            return True    # xmax = 0 means "still alive" — definitely visible

        # ── 3. Was the deletion committed before our snapshot? ────────────────
        deletion_committed = snap.xid_committed_before_snapshot(
            tup.header.xmax, self._status_table
        )
        # If deletion IS visible to us, the row is gone from our perspective.
        # If deletion is NOT visible, the row is still alive from our perspective.
        return not deletion_committed

    # ── VACUUM support ────────────────────────────────────────────────────────

    def oldest_active_xid(self) -> int:
        """
        The lowest XID of any currently running transaction.

        VACUUM uses this as the safety horizon:
          Any tuple with xmax < oldest_active_xid is invisible to ALL
          current and future transactions — safe to physically remove.
        """
        active = [xid for xid, tx in self._transactions.items()
                  if tx.status == TxStatus.ACTIVE]
        return min(active) if active else self._next_xid

    # ── Diagnostics ───────────────────────────────────────────────────────────

    def status_summary(self) -> str:
        lines = ["Transaction Status Table:"]
        lines.append(f"  {'XID':>5}  {'Status':>10}  {'Snapshot xmax':>13}")
        lines.append(f"  {'-'*5}  {'-'*10}  {'-'*13}")
        for xid, tx in sorted(self._transactions.items()):
            snap_xmax = tx.snapshot.xmax if tx.snapshot else "─"
            lines.append(f"  {xid:>5}  {tx.status.name:>10}  {snap_xmax!s:>13}")
        return "\n".join(lines)

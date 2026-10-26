### Dictionary ordering — simple overview

The simple idea is that a modern Python dictionary has **two structures**:

```text
Hash
 ↓
Index table
 ↓
Entry number
 ↓
Entry
```

For example:

```text
Index table              Entries

slot 0 → 2  ─────────→   entry[2] = C
slot 1 → 0  ─────────→   entry[0] = A
slot 2 → -
slot 3 → 1  ─────────→   entry[1] = B
```

The **index table is for finding entries**. Its slot order can be arbitrary because it depends on hashes and probing.

The **entries are stored in insertion sequence**:

```text
entry[0] → A
entry[1] → B
entry[2] → C
```

So:

```text
Lookup:    hash → slot → entry number → entry
Iteration: entry[0] → entry[1] → entry[2] → ...
```

Therefore, **resizing can rearrange the index table without changing insertion order**.

---

### Dictionary ordering — CPython terminology

Modern CPython's **compact dictionary** separates the **sparse index table (`dk_indices`)** from the **dense entry array (`dk_entries`)**. The index table is used for **hash lookup and probing**, while the dense entries store the actual **hash, key, and value** data.

The important point is that **hash-table slot position is not insertion order**. Entries are added sequentially to the dense entry array, so their sequence naturally represents insertion order:

```text
dk_indices                    dk_entries

slot → entry index             insertion sequence

  1  →    2  ───────────────→   [0] A
  3  →    0  ───────────────→   [1] B
  4  →    3  ───────────────→   [2] C
  7  →    1  ───────────────→   [3] D
```

Lookup uses:

```text
hash → dk_indices → entry index → dk_entries
```

Iteration walks the **dense entry sequence**, rather than hash-table slots:

```text
dk_entries:
A → B → C → D
     ↑
 insertion order
```

Therefore, **resizing can change `dk_indices` and hash-table positions without changing insertion order**, because the entry sequence is what preserves the ordering.

Insertion order became a **Python language guarantee in Python 3.7**.
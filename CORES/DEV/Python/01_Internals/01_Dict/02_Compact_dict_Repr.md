### Compact dictionary representation

Modern CPython separates the **sparse hash-index table** from the **dense entry array**. Instead of each hash-table slot directly containing `(hash, key, value)`, a slot stores a small **entry index** pointing into the dense entries array:

```text
hash → index table slot → entry index → (hash, key, value)
```

This indirection allows the actual entries to remain **densely packed**, reducing memory overhead and improving cache locality. The index table can still contain empty slots for efficient probing; **"compact" refers to dense entry storage, not eliminating the empty space required by the hash table**. Because entries retain their sequence in the dense array, iteration can follow that sequence to provide **insertion order**, independently of the hash-table slot positions.

### Compact dictionary representation — complete mental model
Yes. Let's make it much simpler. The **only new idea** is that the old table stored the full entry directly, while the compact design stores a **small number that points to the entry**.

### Previous / traditional mental model

```text
Hash
 ↓
slot
 ↓
┌───────────────┐
│ hash,key,value│
└───────────────┘
```

Every occupied slot contains the **whole entry**.

---

### Modern CPython mental model

```text
Hash
 ↓
slot
 ↓
entry number
 ↓
┌───────────────┐
│ hash,key,value│
└───────────────┘
```

The slot contains only an **entry number**.

For example:

```text
Index table              Entries

slot 0 → 2  ──────────→  entry[2] = (hash, "C", 30)
slot 1 → 0  ──────────→  entry[0] = (hash, "A", 10)
slot 2 → -              entry[1] = (hash, "B", 20)
slot 3 → 1  ──────────→
```

So the lookup path is simply:

```text
hash
 ↓
slot
 ↓
entry number
 ↓
actual (hash, key, value)
```

### Why?

Because the **entries can be packed together**:

```text
[ A ][ B ][ C ][ D ]
```

while the lookup table can have empty slots:

```text
[ - ][ 2 ][ - ][ 0 ][ 1 ][ - ]
```

That separation gives us the **compact dictionary** design.

And the important distinction is:

> **Index table = fast lookup.  
> Entry array = actual data + insertion sequence.**

That's the whole concept.
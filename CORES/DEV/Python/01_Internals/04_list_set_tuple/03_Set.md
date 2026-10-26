# Python Set Internals — Interview Essay

## 1. How does a Python `set` work?

A CPython `set` is a **hash table** optimized for storing **unique elements**.

Conceptually:

```text
set
 │
 ▼
hash table
 │
 ├── hash(element)
 │
 ├── determine slot
 │
 └── probe for matching entry
```

For:

```python
s = {"apple", "banana", "orange"}
```

CPython computes the hash of each element and uses it to locate a table position.

A set stores **elements**, whereas a dictionary stores **key-value associations**.

---

# 2. How does set lookup work?

For:

```python
"apple" in s
```

the conceptual sequence is:

```text
"apple"
   │
   ▼
hash("apple")
   │
   ▼
initial table position
   │
   ▼
occupied?
   │
 ┌─┴──────────┐
No            Yes
 │             │
found       compare hash/key
               │
          ┌────┴────┐
        match      collision
          │           │
        found      probe next slot
```

CPython uses **open addressing**, so entries are stored directly in the hash table rather than using separate linked-list buckets.

When multiple hashes map to the same slot, CPython uses a **probing strategy** to search for another candidate slot.

---

# 3. Why is set lookup O(1)?

A good hash function distributes elements across the table.

Therefore:

```text
element
   ↓
hash
   ↓
table index
   ↓
small number of probes
   ↓
element found
```

The expected lookup cost is:

```text
average → O(1)
```

It is **not guaranteed O(1)**.

In pathological collision scenarios, lookup can degrade toward:

```text
O(n)
```

So the technically correct interview answer is:

> **Set membership is expected O(1) because hashing provides direct table addressing and open addressing normally requires only a small number of probes; worst-case lookup is O(n).**

---

# 4. How are collisions handled?

Two different objects can produce the same table position:

```text
hash(A) ──┐
          ├── same slot
hash(B) ──┘
```

This is a **collision**.

CPython's set implementation uses **open addressing with probing** rather than separate chaining.

Conceptually:

```text
slot 5 → A

B also maps to slot 5

        ↓ collision

probe another slot
        ↓
slot 7 → B
```

The implementation uses a **perturbation-based probing algorithm** to improve probe distribution.

---

# 5. `dict` vs `set`

Both are fundamentally **hash-table data structures** in CPython and share important implementation concepts.

```text
dict
 │
 ├── hash(key)
 ├── locate slot
 ├── compare key
 └── retrieve value

set
 │
 ├── hash(element)
 ├── locate slot
 └── compare element
```

The conceptual difference:

```text
dict
    key ───────► value

set
    element
```

Example:

```python
d = {"id": 101}
s = {101}
```

Dictionary:

```text
101 → associated value
```

Set:

```text
101 → membership only
```

A set is therefore useful when the primary question is:

```python
x in s
```

rather than:

```python
value = d[x]
```

---

# 6. Why does a set contain only unique values?

Insertion uses both:

```text
hash
+
equality
```

For:

```python
s.add(x)
```

CPython locates the candidate slot using the hash.

If an equivalent element already exists:

```text
hash(x)
   ↓
candidate slot
   ↓
existing element
   ↓
hash/equality comparison
   ↓
already present
   ↓
don't insert duplicate
```

Therefore set uniqueness is based on:

```text
__hash__()
+
__eq__()
```

with the requirement that equal objects have equal hashes.

---

# 7. Why must set elements be hashable?

A set needs the object's hash to determine where to search.

Therefore:

```python
{1, 2, 3}       # valid
```

but:

```python
{[1, 2]}        # TypeError
```

because lists are mutable and unhashable.

The fundamental requirement is:

```text
hashable
   +
stable hash/equality semantics
   ↓
usable as set element
```

This is the same fundamental rule used by dictionary keys.

---

# 8. Complexity

|Operation|Average|Worst case|
|---|--:|--:|
|`x in set`|O(1)|O(n)|
|`set.add(x)`|O(1) amortized|O(n)|
|`set.remove(x)`|O(1)|O(n)|
|`set.discard(x)`|O(1)|O(n)|

Resizing can make an individual insertion expensive, hence **amortized O(1)** for insertion.

---

# 9. Interview mental model

```text
                 SET
                  │
                  ▼
              hash table
                  │
          ┌───────┴────────┐
          ▼                ▼
      hash(x)          equality
          │                │
          ▼                │
     table position        │
          │                │
          ▼                │
       probing ◄───────────┘
          │
          ▼
      membership
```

### One-line interview answer

> **A CPython set is a hash table using open addressing and perturbation-based probing; it stores unique hashable elements rather than key-value pairs, and membership is expected O(1) because hashing provides near-direct table addressing, with O(n) worst-case behavior under pathological collisions.**
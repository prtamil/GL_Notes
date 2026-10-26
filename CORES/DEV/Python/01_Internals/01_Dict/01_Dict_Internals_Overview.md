# Python `dict` / Hash Table — Interview Revision

## The interview chain to memorize

**Hash → Slot → Collision → Open addressing → Probing → Perturbation → Equality → Resize → O(1) → Compact dict → Insertion order**

If you can explain these concepts in this order, you can reconstruct almost the entire Python dictionary internals answer.

---

A Python `dict` is a **hash-table-based associative container**. Its **average lookup, insertion, and deletion are O(1)** because the key's hash is used to quickly locate a candidate slot instead of searching every entry. The worst case can be **O(n)** with severe collisions.

## 1. Hash

Python computes:

```python
hash(key)
```

The hash is used to determine an **initial table position**.

For strings/bytes, CPython uses **hash randomization**, so hashes can differ between processes. This helps defend against deliberately constructed collision attacks.

---

## 2. Collision

Different keys can map to the same position:

```text
"Alice" → slot 5
"Bob"   → slot 5
```

A hash collision does **not** mean the keys are equal.

```text
same hash ≠ same key
```

Python uses **hash first, equality second**.

```text
hash(key)
   ↓
candidate slot
   ↓
key equality check
   ↓
found / continue probing
```

---

## 3. Open addressing

CPython uses **open addressing**.

Instead of putting a linked list of entries in one bucket, entries occupy slots in the table itself.

If the desired slot is occupied, Python searches for another slot.

---

## 4. Probing

The process of finding another slot is **probing**.

Conceptually:

```text
hash → slot 5
          ↓
       occupied
          ↓
        probe
          ↓
       slot 2
          ↓
       occupied
          ↓
        probe
          ↓
       slot 7
```

CPython does not simply use:

```text
5 → 6 → 7 → 8
```

It uses a **hash-dependent probing strategy**.

---

## 5. Perturbation

CPython maintains a **perturbation value derived from the hash**.

The hash provides the initial position, while its other bits influence later probe positions.

Conceptually:

```text
hash
 ↓
initial slot
 ↓ collision
use perturbation
 ↓
next slot
 ↓ collision
shift perturbation
 ↓
next slot
```

A simplified representation is:

```c
index = hash & mask;
perturb = hash;

while (occupied(index)) {
    index = 5 * index + 1 + perturb;
    perturb >>= 5;
    index &= mask;
}
```

The exact implementation is CPython-specific; remember the **concept**, not the formula.

---

## 6. Insertion vs lookup

**Both use the same hash and probing sequence.**

Insertion:

```text
hash → probe → find empty slot → insert
```

Lookup:

```text
hash → probe → find matching key → return value
```

This is essential: if insertion used one path and lookup another, the dictionary could not reliably find stored keys.

---

## 7. Why keys must be hashable

A dictionary key needs a **stable hash/equality relationship**.

Important rule:

```text
a == b  ⇒  hash(a) == hash(b)
```

But:

```text
hash(a) == hash(b)
does NOT imply
a == b
```

Immutable objects such as strings and integers are suitable keys. Mutable objects such as lists are unhashable because their contents can change.

---

## 8. Resizing / load factor

As the table becomes crowded:

```text
more entries
   ↓
more collisions
   ↓
more probes
   ↓
slower lookup
```

So CPython **resizes** the dictionary and redistributes entries.

**Load factor** is roughly:

```text
entries / available slots
```

Higher load means more collisions.

Don't memorize a simplistic "Python resizes at 75%" rule. A better interview answer is:

> CPython maintains spare capacity and grows the table as necessary to keep probing efficient.

---

## 9. Compact dictionary + ordering

Modern CPython uses a **compact dictionary representation**, separating sparse indexing information from densely stored entries.

Benefits:

- **Lower memory usage**
    
- **Better cache locality**
    
- **Insertion-order iteration**
    

Insertion order became a **Python language guarantee in Python 3.7**.

---

# Final mental model

```text
                         Python dict
                              │
                         Hash table
                              │
                         hash(key)
                              │
                              ▼
                     Initial table slot
                              │
                       ┌──────┴──────┐
                       │             │
                    empty         occupied
                       │             │
                    insert       collision
                                     │
                              Open addressing
                                     │
                                  Probing
                                     │
                              Perturbation
                                     │
                                     ▼
                               Next slot
                                     │
                              Key equality
                               /         \
                            match       different
                              │             │
                           found        probe again
                                            │
                                            ▼
                                           ...

                ┌─────────────────────────────┐
                │ Table gets crowded          │
                │             ↓               │
                │           resize            │
                │             ↓               │
                │        redistribute         │
                └─────────────────────────────┘

Result:
Average lookup / insert / delete → O(1)
Worst case → O(n)

Modern CPython:
Compact dict → less memory + cache efficiency
                         ↓
                  insertion order
```
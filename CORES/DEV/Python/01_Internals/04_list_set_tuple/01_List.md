

# Python List Internals — Interview Essay

## 1. What is a Python list internally?

A CPython `list` is a **dynamic array**, not a linked list.

Conceptually:

```text
PyListObject
 ├── ob_item ──────► contiguous array of PyObject*
 ├── ob_size       → number of elements
 └── allocated     → capacity
```

Example:

```text
list = [A, B, C]

ob_item
   │
   ▼
┌─────┬─────┬─────┬─────┬─────┐
│  A  │  B  │  C  │  .  │  .  │
└─────┴─────┴─────┴─────┴─────┘
       size = 3
       capacity > 3
```

The array stores **pointers to Python objects**, not the objects themselves.

---

# 2. Why is `append()` amortized O(1)?

For:

```python
lst.append(x)
```

if spare capacity exists:

```text
ob_item[size] = x
size++
```

This is **O(1)**.

When capacity is exhausted, CPython must allocate a larger pointer array and copy/move the existing pointers:

```text
old array
[A B C D]

      ↓ resize

new array
[A B C D . . .]
```

That particular append is **O(n)**.

But CPython uses **over-allocation**: it grows the array beyond the immediately required size.

Therefore repeated appends have:

```text
individual append → O(1) amortized
occasional resize → O(n)
```

Across `n` appends, the total resizing work is amortized, giving:

```text
n appends → O(n) total
average append → O(1) amortized
```

Important:

> `append()` is **not strictly O(1)**; it is **amortized O(1)**.

---

# 3. How does a list grow?

CPython does not resize by exactly one element each time.

It uses **overallocation** to provide spare capacity.

Conceptually:

```text
size       capacity

3             4
4             4
5             larger capacity
...
```

The exact growth formula is an **implementation detail and has changed across CPython versions**, so don't memorize an old formula for an interview.

The important implementation principle is:

```text
insufficient capacity
        ↓
allocate larger contiguous pointer array
        ↓
copy/move PyObject* pointers
        ↓
update allocated capacity
```

This geometric/sublinear growth strategy prevents every append from requiring a reallocation.

---

# 4. Why is `insert(0, x)` O(n)?

A list is contiguous.

For:

```python
lst.insert(0, x)
```

existing elements must shift right:

```text
Before:

[A B C D]

insert X at index 0

After:

[X A B C D]
```

Conceptually:

```text
D → next position
C → next position
B → next position
A → next position
```

Approximately `n` pointer movements are required.

Therefore:

```text
insert(0, x) → O(n)
```

Similarly:

```python
lst.insert(i, x)
```

is generally:

```text
O(n - i)
```

for the shifting portion, hence **O(n)** worst case.

For frequent front insertion/removal, use:

```python
collections.deque
```

---

# 5. `append()` vs `extend()`

### `append(x)`

Adds **one object** as one list element:

```python
lst.append([1, 2, 3])
```

Result:

```text
[ existing..., [1, 2, 3] ]
```

Conceptually:

```text
append(x)
    ↓
store one PyObject* at the end
```

Average complexity:

```text
O(1) amortized
```

---

### `extend(iterable)`

Consumes an iterable and adds its elements individually:

```python
lst.extend([1, 2, 3])
```

Result:

```text
[ existing..., 1, 2, 3 ]
```

Conceptually:

```text
iterable
   │
   ├── element 1 → list
   ├── element 2 → list
   └── element 3 → list
```

If `k` elements are added:

```text
O(k) amortized
```

There can also be a resize cost.

---

# 6. `+=` vs `extend()`

For lists:

```python
a += b
```

uses the list's **in-place concatenation** behavior and is closely related to extending the existing list.

Conceptually:

```text
a += b
   ↓
mutate existing list
   ↓
add elements from b
```

Whereas:

```python
a = a + b
```

creates a **new list**:

```text
a + b
 │
 ├── allocate new list
 ├── copy pointers from a
 └── copy pointers from b
```

Therefore:

```text
a.extend(b)
    → mutate a

a += b
    → normally mutate a in place

a = a + b
    → create new list
```

For `a` containing `n` elements and `b` containing `m` elements:

```text
a + b       → O(n + m)
a.extend(b) → O(m) amortized, plus any resize/copy cost
a += b      → O(m) amortized, plus any resize/copy cost
```

---

# 7. Critical distinction: list stores references

This is an excellent interview detail.

Given:

```python
a = [obj1, obj2, obj3]
```

the list's contiguous storage contains:

```text
PyObject* → obj1
PyObject* → obj2
PyObject* → obj3
```

It does **not** copy the actual Python objects during normal list resizing.

Resize primarily moves/copies the **pointers/references**.

Therefore list resizing is relatively cheap compared with copying the objects themselves.

---

# 8. Interview mental model

```text
Python list
     │
     ▼
dynamic array
     │
     ├── contiguous PyObject* array
     ├── size
     └── allocated capacity
           │
           ▼
      over-allocation
           │
           ▼
   amortized O(1) append
```

Operations:

```text
append(x)
    → O(1) amortized

extend(iterable)
    → O(k) amortized for k added elements

a += iterable
    → in-place extension, O(k) amortized

insert(0, x)
    → O(n)

a + b
    → new list, O(len(a) + len(b))
```

### One-line interview answer

> **A CPython list is an over-allocated contiguous dynamic array of `PyObject*` references; `append()` is amortized O(1) because capacity is over-allocated, resizing is occasional O(n), front insertion is O(n) because references must be shifted, `extend()` and `+=` grow the existing list, while `+` allocates a new list and copies both operands.**
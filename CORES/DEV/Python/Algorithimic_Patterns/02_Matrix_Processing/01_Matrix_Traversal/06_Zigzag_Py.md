# 6. Zigzag Traversal

## Mental Model

Zigzag traversal **flips direction after every line**. Rather than always moving the same way, the traversal **bounces back and forth**.

The line can be a row, a column, or a diagonal. The most famous version is the **JPEG diagonal zigzag scan**.

In Python the whole thing collapses to one decision per line: **plain, or `[::-1]`?**

---

## Relationship to Cognitive Verb

```text
Alternate
     ↓
Zigzag Traversal
```

Related verbs:

- Alternate direction
    
- Bounce
    
- Reverse every pass
    
- Sweep back and forth
    
- Oscillate
    

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Row zigzag|alternate rows|`enumerate` + `[::-1]`|
|Column zigzag|alternate columns|`zip(*m)` + `[::-1]`|
|Diagonal zigzag|JPEG ordering|bucket by `r + c`, reverse alternates|
|Alternate direction|even/odd test|`i % 2`, or step `(-1) ** i`|
|Flatten result|produce sequence|`itertools.chain.from_iterable`|
|Level zigzag|tree/BFS levels|`collections.deque`|

---

## Common Uses

- JPEG image compression
    
- Matrix serialization
    
- Robot sweep patterns
    
- Raster scanning
    
- Cache-friendly processing
    
- Game AI search
    
- Hardware image sensors
    
- Scientific visualization
    

---

## Hidden Interview Problems

- Print matrix in zigzag order
    
- Alternate every row
    
- Zigzag level traversal
    
- JPEG scan ordering
    
- Reverse alternate rows
    
- Serialize matrix
    
- Snake vs Zigzag comparison
    

---

## Recognition Clues

If you hear...

- "alternate direction..."
    
- "back and forth..."
    
- "reverse every row..."
    
- "bounce..."
    
- "zigzag..."
    

...think **Zigzag Traversal**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Traversal Unit|Row, Column, or Diagonal|
|Direction|Alternating|
|Coordinate Rule|Reverse every other pass|
|Time Complexity|O(rows × cols)|
|Space Complexity|O(1) extra (excluding output)|
|Common Domains|JPEG, graphics, robotics|

---

## Python Recipe Book

```python
# ============================================
# Basic matrix

from collections import defaultdict, deque
from itertools import chain

m = [[1,  2,  3,  4],
     [5,  6,  7,  8],
     [9,  10, 11, 12],
     [13, 14, 15, 16]]

# ============================================
# The one idiom to remember
#
#   row if i % 2 == 0 else row[::-1]
#
# Slicing already knows how to reverse.
# The only state you need is "which line am I on".

[row if i % 2 == 0 else row[::-1] for i, row in enumerate(m)]

# =>
# [[1, 2, 3, 4],
#  [8, 7, 6, 5],
#  [9, 10, 11, 12],
#  [16, 15, 14, 13]]

# ============================================
# The terse version — the STEP does the work
#
#   (-1) ** i   is  1  on even lines
#               and -1 on odd lines

[row[::(-1) ** i] for i, row in enumerate(m)]

# => same result

# ============================================
# Zigzag by rows

[row if i % 2 == 0 else row[::-1] for i, row in enumerate(m)]

# ============================================
# Flatten zigzag traversal

[x for i, row in enumerate(m) for x in (row if i % 2 == 0 else row[::-1])]

# => [1, 2, 3, 4, 8, 7, 6, 5, 9, 10, 11, 12, 16, 15, 14, 13]

list(chain.from_iterable(row[::(-1) ** i] for i, row in enumerate(m)))

# => same

# ============================================
# Zigzag by columns

cols = [list(col) for col in zip(*m)]

[col if i % 2 == 0 else col[::-1] for i, col in enumerate(cols)]

# =>
# [[1, 5, 9, 13],
#  [14, 10, 6, 2],
#  [3, 7, 11, 15],
#  [16, 12, 8, 4]]

# ============================================
# Generic alternating pattern
#
# Nothing here is matrix-specific — it works on
# any sequence of sequences.

def zigzag(lines):
    return [line if i % 2 == 0 else line[::-1] for i, line in enumerate(lines)]

zigzag(m)               # rows
zigzag(cols)            # columns

# ============================================
# Explicit traversal

for i, row in enumerate(m):
    for x in (row if i % 2 == 0 else row[::-1]):
        print(x)

# ============================================
# Diagonal zigzag — the JPEG scan
#
# Same buckets as lesson 4: every anti-diagonal is
# one value of  r + c.  Then reverse alternate buckets.

diags = defaultdict(list)
for r, row in enumerate(m):
    for c, cell in enumerate(row):
        diags[r + c].append(cell)

[diags[s] for s in sorted(diags)]
# => [[1], [2, 5], [3, 6, 9], [4, 7, 10, 13], [8, 11, 14], [12, 15], [16]]

# walk down on odd s, up on even s
[x for s in sorted(diags) for x in (diags[s] if s % 2 else diags[s][::-1])]

# => [1, 2, 5, 9, 6, 3, 4, 7, 10, 13, 14, 11, 8, 12, 15, 16]
#     the classic JPEG ordering

# ============================================
# Same, as a reusable function

def zigzag_diagonal(m):
    diags = defaultdict(list)
    for r, row in enumerate(m):
        for c, cell in enumerate(row):
            diags[r + c].append(cell)
    return [x for s in sorted(diags)
              for x in (diags[s] if s % 2 else diags[s][::-1])]

zigzag_diagonal([[1, 2, 3],
                 [4, 5, 6],
                 [7, 8, 9]])
# => [1, 2, 4, 7, 5, 3, 6, 8, 9]

# ============================================
# Serialize / deserialize
#
# Zigzag is reversible — reversing alternate rows
# is its own inverse.

flat = [x for i, row in enumerate(m) for x in (row[::(-1) ** i])]

def unzigzag(flat, cols):
    rows = [flat[i:i + cols] for i in range(0, len(flat), cols)]
    return [row[::(-1) ** i] for i, row in enumerate(rows)]

unzigzag(flat, 4) == m          # => True

# on 3.12+ the chunking is itertools.batched(flat, cols)

# ============================================
# Zigzag level traversal (BFS levels, alternating)

def zigzag_levels(root, children):
    out, level = [], [root]
    left_to_right = True
    while level:
        values = [n for n in level]
        out.append(values if left_to_right else values[::-1])
        level = [c for n in level for c in children(n)]
        left_to_right = not left_to_right
    return out

tree = {1: [2, 3], 2: [4, 5], 3: [6, 7], 4: [], 5: [], 6: [], 7: []}

zigzag_levels(1, tree.get)
# => [[1], [3, 2], [4, 5, 6, 7]]

# a deque makes the alternation cheap when levels are large
def zigzag_levels_deque(root, children):
    out, level = [], deque([root])
    left_to_right = True
    while level:
        out.append(list(level) if left_to_right else list(reversed(level)))
        level = deque(c for n in level for c in children(n))
        left_to_right = not left_to_right
    return out

# ============================================
# Compare

# Always forward
[x for row in m for x in row]

# Alternate direction
[x for i, row in enumerate(m) for x in (row if i % 2 == 0 else row[::-1])]
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|alternate rows|`row if i % 2 == 0 else row[::-1]`|
|the terse form|`row[::(-1) ** i]`|
|flattened|`chain.from_iterable(...)`|
|alternate columns|`zigzag(zip(*m))`|
|JPEG order|bucket by `r + c`, reverse even buckets|
|undo a zigzag|apply the same zigzag again|
|zigzag levels|flip a `left_to_right` flag per level|

---

## Key Insight

The defining idea of zigzag traversal is **alternating direction**.

```text
→→→→
←←←←
→→→→
←←←←
```

Unlike spiral traversal, which changes **boundaries**, zigzag traversal changes only the **direction of travel** after each pass.

The traversal unit can be:

|Unit|Example|
|---|---|
|Row|Read left→right, then right→left|
|Column|Read top→bottom, then bottom→top|
|Diagonal|JPEG zigzag ordering|

Think of zigzag as the general pattern:

```text
Forward
   ↓
Reverse
   ↓
Forward
   ↓
Reverse
```

> **Mental shift:** Zigzag traversal is not about _where_ you move next; it's about _changing the direction_ of each successive sweep.

**The Python version of that shift:** you never write a direction. You write `[::-1]` and let `enumerate` decide when to apply it. Every zigzag in this lesson — rows, columns, JPEG diagonals, tree levels — is the same two-part recipe:

```text
1. produce the lines   (rows, zip(*m), buckets by r + c, BFS levels)
2. reverse every other one
```

Change step 1 and you change the pattern. Step 2 never changes.

---

### Zigzag vs Snake

Plenty of sources use the two words interchangeably, but it's worth keeping them apart:

|Pattern|Primary Idea|
|---|---|
|**Zigzag**|Alternate the direction of each traversal unit (rows, columns, or diagonals). The concept is general.|
|**Snake**|A specific zigzag where the traversal unit is **rows** (or sometimes columns), producing a continuous snake-like path.|

Here we'll treat **Snake Traversal** as a special case of zigzag, because it turns up so often in graphics, game maps and interview questions.

---

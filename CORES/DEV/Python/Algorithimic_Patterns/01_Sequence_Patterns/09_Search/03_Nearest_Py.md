# Pattern 28 — Nearest Match

## Mental Model

Find the element **closest to a target value** according to some distance or similarity measure.

**First Match** stops at the first valid element and **Search All** returns every match. **Nearest Match** goes looking for the **best** one.

Python spells it **`min(xs, key=lambda x: abs(x - target))`**. The whole pattern is "min over a distance function", and everything else is just a different idea of what distance means.

---

## Relationship to Cognitive Verb

```text
Search
   ↓
Nearest Match
```

Nearest Match is a **Search** pattern that scans the sequence for the element at **minimum distance** from a target.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Nearest Number|closest to 25|`min(xs, key=lambda x: abs(x - 25))`|
|Nearest by Property|closest age|`min(ps, key=lambda p: abs(p["age"] - 26))`|
|Farthest|maximum distance|`max(xs, key=…)`|
|Best Score|maximum similarity|`max(xs, key=itemgetter("score"))`|
|Closest Point|Euclidean|`min(pts, key=lambda p: p[0]**2 + p[1]**2)`|
|Top K Nearest|closest 3|`heapq.nsmallest(3, xs, key=…)`|
|Nearest in Sorted Data|O(log n)|`bisect` + compare the two neighbours|
|Nearest String|fuzzy match|`difflib.get_close_matches`|
|Distance + Threshold|only if close enough|`min(...)` then check the distance|

> **Note:** `min`/`max` return the **first** element on a tie, and both raise `ValueError` on an empty sequence unless you pass `default=`. On sorted numeric data, `bisect` turns this O(n) scan into O(log n).

---

## Common Uses

- Nearest value lookup

- Closest point

- Nearest timestamp

- Best recommendation

- Fuzzy matching

- Nearest sensor reading

- Spatial search

- AI nearest neighbor

---

## Hidden Interview Problems

- Closest number to a target

- K nearest numbers

- K closest points to the origin

- Nearest timestamp

- Closest pair of values

- Nearest neighbor

- Best fuzzy string match

---

## Recognition Clues

If you hear:

- Closest

- Nearest

- Minimum distance

- Best match

- Similarity

- Nearest neighbor

- Closest value

Think:

**→ Nearest Match**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Search|
|Pattern|Nearest Match|
|Stops Early|No — must see everything|
|Returns|the single best element|
|Comparison|distance / similarity|
|Cost|O(n), or O(log n) if sorted|
|Ties|first one wins|
|Empty Input|`ValueError` unless `default=`|
|Primary Use|Approximate search|

---

## Python Recipe Book

```python
# ============================================
# Input

from operator import itemgetter
import heapq, bisect, difflib, math

xs = [10, 15, 22, 30, 42, 55]

# ============================================
# Nearest number to a target — the idiom

min(xs, key=lambda x: abs(x - 25))      # => 22
min(xs, key=lambda x: abs(x - 40))      # => 42

# "min over a distance function". That's the entire pattern.
# key= is called once per element; min compares the KEYS but
# returns the ELEMENT. That indirection is the useful part.

# ============================================
# Farthest — same call, max instead

max(xs, key=lambda x: abs(x - 25))      # => 55

# ============================================
# Empty input and ties

min([], key=abs, default=None)          # => None    no ValueError
min([1, -1], key=abs)                   # => 1       first wins the tie

# to break a tie deliberately, make the key a TUPLE:
min([1, -1], key=lambda x: (abs(x), x)) # => -1      smaller value wins

# ============================================
# Nearest object by a property

people = [
    {"name": "Alice", "age": 24},
    {"name": "Bob",   "age": 31},
    {"name": "Carol", "age": 27},
]

min(people, key=lambda p: abs(p["age"] - 26))
# => {'name': 'Carol', 'age': 27}

# ============================================
# Highest score — similarity instead of distance

scores = [
    {"name": "A", "score": 0.81},
    {"name": "B", "score": 0.95},
    {"name": "C", "score": 0.76},
]

max(scores, key=itemgetter("score"))    # => {'name': 'B', 'score': 0.95}

# distance → min, similarity → max. Same pattern, opposite direction.
# getting this backwards is the most common "nearest" bug.

# ============================================
# Closest point to the origin

points = [(3, 4), (1, 2), (5, 5)]
min(points, key=lambda p: p[0] ** 2 + p[1] ** 2)            # => (1, 2)

# SQUARED distance — no sqrt. It's monotonic, so the ordering is
# identical and you save n square roots. Only take the root if you
# need the actual distance value to report.

math.dist((1, 2), (0, 0))               # => 2.236...    when you DO need it
min(points, key=lambda p: math.dist(p, (0, 0)))             # => (1, 2)

# ============================================
# Nearest timestamp

times = [100, 140, 180, 250]
min(times, key=lambda t: abs(t - 170))  # => 180

# an exact tie resolves by POSITION, not by value:
min(times, key=lambda t: abs(t - 160))  # => 140
# |140-160| == |180-160| == 20, and 140 comes first.
# if "prefer the later one" matters, spell it out in the key:
min(times, key=lambda t: (abs(t - 160), -t))                # => 180

# nearest EARLIER timestamp only (a common real requirement):
min((t for t in times if t <= 160), key=lambda t: 160 - t, default=None)
# => 140

# ============================================
# Top K nearest

heapq.nsmallest(3, xs, key=lambda x: abs(x - 25))           # => [22, 30, 15]
sorted(xs, key=lambda x: abs(x - 25))[:3]                   # same, O(n log n)

# nsmallest is O(n log k). For k == 1 use min(); for k near n, sort.

# k closest points to the origin — the interview classic:
heapq.nsmallest(2, points, key=lambda p: p[0] ** 2 + p[1] ** 2)
# => [(1, 2), (3, 4)]

# ============================================
# Sorted data? bisect makes it O(log n)

def nearest_sorted(s, target):
    """s must be sorted ascending."""
    i = bisect.bisect_left(s, target)
    if i == 0:
        return s[0]
    if i == len(s):
        return s[-1]
    before, after = s[i - 1], s[i]
    return after if (after - target) < (target - before) else before

nearest_sorted(xs, 25)                  # => 22
nearest_sorted(xs, 40)                  # => 42
nearest_sorted(xs, 5)                   # => 10      clamps at the low end
nearest_sorted(xs, 99)                  # => 55      clamps at the high end

# bisect gives the INSERTION POINT; the nearest element is one of the
# two neighbours around it. The edges are where this goes wrong —
# i == 0 and i == len(s) must be handled separately.

# ============================================
# Nearest string — fuzzy matching

words = ["apple", "apply", "ape", "banana"]
difflib.get_close_matches("aple", words, n=3, cutoff=0.6)
# => ['apple', 'apply', 'ape']

difflib.SequenceMatcher(None, "aple", "apple").ratio()      # => 0.888...

# get_close_matches IS nearest-match with a similarity ratio and a
# threshold. `cutoff` is the "close enough" guard.

# ============================================
# Distance plus a threshold — nearest is not always acceptable

def nearest_within(xs, target, tol):
    best = min(xs, key=lambda x: abs(x - target), default=None)
    return best if best is not None and abs(best - target) <= tol else None

nearest_within(xs, 25, tol=5)           # => 22
nearest_within(xs, 25, tol=1)           # => None    nothing is close enough

# min() ALWAYS returns something. "Nearest" on an unrelated dataset
# is still nearest — check the distance before trusting it.

# ============================================
# Get the distance back too — don't compute it twice

best = min(xs, key=lambda x: abs(x - 25))
best, abs(best - 25)                    # => (22, 3)

# or carry it through:
d, best = min((abs(x - 25), x) for x in xs)         # => (3, 22)

# a tuple genexp with min() gives you both, but note this now
# tiebreaks on the VALUE (second element), not on position

# ============================================
# Closest PAIR within a list — sort first

def closest_pair(a):
    s = sorted(a)
    return min(zip(s, s[1:]), key=lambda p: p[1] - p[0])

closest_pair([10, 15, 22, 30, 42, 55])  # => (10, 15)

# the closest two values are always ADJACENT after sorting —
# that turns an O(n²) pairwise scan into O(n log n)

# ============================================
# THE COST — nearest cannot short-circuit

next((x for x in xs if x > 25), None)   # => 30    stops at the first hit
min(xs, key=lambda x: abs(x - 25))      # => 22    must see all six

# "first" can stop; "best" cannot — you never know the next element
# isn't closer. That's why sorting (bisect) is the only real speedup.

# ============================================
# Compare

min(xs, key=f)                  # single best, O(n)       → Nearest
nsmallest(k, xs, key=f)         # k best, O(n log k)      → Nearest
sorted(xs, key=f)               # all, ranked             → Sort
next((x for x in xs if p(x)))   # first acceptable        → First Match
[x for x in xs if f(x) <= tol]  # all within a radius     → Search All
nearest_sorted(xs, t)           # single best, O(log n)   → Nearest + bisect
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|nearest number|`min(xs, key=lambda x: abs(x - t))`|
|nearest by field|`key=lambda p: abs(p["age"] - t)`|
|best score|`max(xs, key=itemgetter("score"))`|
|closest point|`key=lambda p: p[0]**2 + p[1]**2`|
|k nearest|`heapq.nsmallest(k, xs, key=…)`|
|nearest in sorted data|`bisect` + check both neighbours|
|nearest string|`difflib.get_close_matches`|
|the distance as well|`min((f(x), x) for x in xs)`|
|safe on empty input|`default=None`|
|a deliberate tiebreak|make the key a tuple|
|"close enough" only|`min(...)` then test the distance|

---

### Key Insight

**Nearest Match is `min` with a key, and all the substance lives in the distance function.** Absolute difference for numbers, squared distance for points, `1 - ratio` for strings, seconds apart for timestamps. Once you can write the distance, the search is one line. Direction matters more than it looks, too: **distance wants `min`, similarity wants `max`**, and swapping them hands you the *worst* match with nothing to warn you.

**Nearest can't short-circuit, and that's a genuine algorithmic constraint.** First Match stops at the first hit. Nearest has to look at everything, because the next element could always be closer. The only way to speed it up is to remove the need to look at all: **sort once and use `bisect`**, take the insertion point, and compare the two neighbours around it. That's O(log n) per query instead of O(n), and it pays for itself by the second lookup.

One honest limitation: **`min` always returns something.** Ask for the nearest station to a point in the wrong country and you'll get one, confidently. Nearest only means anything with a threshold, so check `abs(best - target)` against a tolerance before you act on it. `difflib` has a `cutoff` parameter for exactly this reason — the authors knew the answer on its own isn't enough.

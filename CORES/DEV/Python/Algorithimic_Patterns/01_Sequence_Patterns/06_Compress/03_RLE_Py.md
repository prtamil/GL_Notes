# Pattern 19 — Run-Length Encoding (RLE)

## Mental Model

Compress a sequence by replacing each **run of consecutive identical elements** with **(value, count)**.

Rather than storing the repeated values, you store **what the value is** and **how many times it repeats**.

The encoder and decoder are each one line in Python, and they mirror each other exactly: **`groupby`** to encode, **`repeat` + `chain`** to decode.

---

## Relationship to Cognitive Verb

```text
Compress
    ↓
Run-Length Encoding
```

Run-Length Encoding is a **Compress** pattern that boils **runs** down to compact `(value, count)` pairs.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Encode Runs|`AAA → ('A', 3)`|`[(k, len(list(g))) for k, g in groupby(xs)]`|
|Count Runs|`3 2 1`|`[len(list(g)) for _, g in groupby(xs)]`|
|Run Values Only|`A B C`|`[k for k, _ in groupby(xs)]`|
|Decode RLE|`('A',3) → AAA`|`chain.from_iterable(repeat(v, n) for v, n in rle)`|
|Compress Characters|`"aaabb"`|`groupby(s)` + `join`|
|Encode by Key|runs of a field|`groupby(xs, key=f)`|
|Run Statistics|value + length|`[{"value": k, "count": …}]`|

> **Note:** RLE only compresses **consecutive** duplicates. It does not remove duplicates separated by other values — that is Distinct, a different pattern with a different (lossy) result.

---

## Common Uses

- Simple lossless compression

- Bitmap/image compression

- DNA sequences

- Log compression

- Sensor data

- Character compression

- Data serialization

- Network protocols

---

## Hidden Interview Problems

- String compression

- Compress repeated characters

- Encode repeated numbers

- Count consecutive values

- Decode compressed data

- Run statistics

---

## Recognition Clues

If you hear:

- Compress repeated values

- Count consecutive items

- String compression

- Encode runs

- Value and frequency

- Consecutive repetitions

Think:

**→ Run-Length Encoding**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Compress|
|Pattern|Run-Length Encoding|
|Compresses|Consecutive duplicates|
|Output|`(value, count)` pairs|
|Preserves Order|Yes|
|Compression Type|Lossless|
|Worst Case|**Doubles** the size (no adjacent repeats)|

---

## Python Recipe Book

```python
# ============================================
# Input

from itertools import groupby, chain, repeat
from operator import itemgetter

xs = [1, 1, 1, 2, 2, 3, 3, 3, 3, 4]

# ============================================
# Partition into runs

[list(g) for _, g in groupby(xs)]
# => [[1,1,1], [2,2], [3,3,3,3], [4]]

# ============================================
# Basic run-length encoding

def encode(xs):
    return [(k, len(list(g))) for k, g in groupby(xs)]

encode(xs)
# => [(1, 3), (2, 2), (3, 4), (4, 1)]

# ============================================
# Compress characters

encode("aaabbccccd")
# => [('a', 3), ('b', 2), ('c', 4), ('d', 1)]

# the classic interview output format
"".join(f"{k}{len(list(g))}" for k, g in groupby("aaabbccccd"))
# => 'a3b2c4d1'

# ============================================
# Keep only run lengths

[len(list(g)) for _, g in groupby(xs)]          # => [3, 2, 4, 1]

# ============================================
# Keep only run values

[k for k, _ in groupby(xs)]                     # => [1, 2, 3, 4]

# that's the Dedupe pattern — RLE minus the counts

# ============================================
# Decode run-length encoding

def decode(rle):
    return list(chain.from_iterable(repeat(v, n) for v, n in rle))

decode([(1, 3), (2, 2), (3, 4), (4, 1)])
# => [1, 1, 1, 2, 2, 3, 3, 3, 3, 4]

# the comprehension form, if you prefer
[v for value, n in [(1, 3), (2, 2)] for v in [value] * n]
# => [1, 1, 1, 2, 2]

# decoding a string
"".join(c * n for c, n in [('a', 3), ('b', 2)])         # => 'aaabb'

# ============================================
# Encode then decode — the round trip must be exact

decode(encode(xs)) == xs                        # => True

# RLE is LOSSLESS. If this assertion ever fails, the encoder ate a run.

# ============================================
# Compression ratio

len(xs), len(encode(xs))                        # => (10, 4)

# ...and the case that embarrasses RLE
bad = [1, 2, 3, 4, 5]
len(bad), len(encode(bad))                      # => (5, 5)
# every "run" is length 1, so each element becomes a PAIR —
# the encoded form is twice the size of the input.

# Real formats guard against this: a flag bit choosing between
# "literal run" and "repeated run" (PackBits, TGA, PCX all do this).

# ============================================
# Run statistics

[{"value": k, "count": len(list(g))} for k, g in groupby(xs)]
# => [{'value':1,'count':3}, {'value':2,'count':2},
#     {'value':3,'count':4}, {'value':4,'count':1}]

# ============================================
# Longest run

max(encode(xs), key=itemgetter(1))              # => (3, 4)

# longest run of a SPECIFIC value
max((n for v, n in encode(xs) if v == 3), default=0)        # => 4

# ============================================
# Encode by a key — runs of a field, not of the whole record

events = [
    {"t": 0, "state": "ok"},
    {"t": 1, "state": "ok"},
    {"t": 2, "state": "fail"},
    {"t": 3, "state": "ok"},
]
[(k, len(list(g))) for k, g in groupby(events, key=itemgetter("state"))]
# => [('ok', 2), ('fail', 1), ('ok', 1)]

# with the time span of each run
[(k, (lambda r: (r[0]["t"], r[-1]["t"]))(list(g)))
 for k, g in groupby(events, key=itemgetter("state"))]
# => [('ok', (0, 1)), ('fail', (2, 2)), ('ok', (3, 3))]

# ============================================
# A streaming encoder — O(1) memory, no groupby

def encode_stream(it):
    it = iter(it)
    try:
        prev = next(it)
    except StopIteration:
        return
    n = 1
    for x in it:
        if x == prev:
            n += 1
        else:
            yield (prev, n)
            prev, n = x, 1
    yield (prev, n)

list(encode_stream(xs))
# => [(1, 3), (2, 2), (3, 4), (4, 1)]

# use this on a file or socket — groupby needs the source in one piece
# only to the extent you materialize each group, but the explicit form
# makes the constant memory obvious.

# ============================================
# Bitmap / scanline compression — the original use

row = [0,0,0,0, 1,1, 0,0,0,0,0,0]
encode(row)                                     # => [(0,4), (1,2), (0,6)]
# 12 pixels → 3 pairs. On real images with flat regions, this is why
# fax machines and early image formats used RLE at all.

# ============================================
# DNA / sequence data

encode("AAAGGGTTTTCC")
# => [('A',3), ('G',3), ('T',4), ('C',2)]

# ============================================
# Log compression — "last message repeated N times"

log = ["conn ok", "conn ok", "conn ok", "timeout"]
[f"{msg} (x{n})" if n > 1 else msg for msg, n in encode(log)]
# => ['conn ok (x3)', 'timeout']

# ============================================
# Compare

encode(xs)                          # (value, count) pairs   → RLE
[k for k, _ in groupby(xs)]         # values only            → Dedupe
list(dict.fromkeys(xs))             # all duplicates gone    → Distinct
Counter(xs)                         # TOTAL counts, not runs → Summarize

# Counter([1,2,1]) => {1:2, 2:1}    — position forgotten, not compressible
# encode([1,2,1])  => [(1,1),(2,1),(1,1)]  — position preserved, reversible
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|encode|`[(k, len(list(g))) for k, g in groupby(xs)]`|
|decode|`chain.from_iterable(repeat(v, n) for v, n in rle)`|
|encode a string|`"".join(f"{k}{len(list(g))}" …)`|
|decode a string|`"".join(c * n for c, n in rle)`|
|run lengths only|`[len(list(g)) for _, g in groupby(xs)]`|
|runs of a field|`groupby(xs, key=itemgetter(f))`|
|longest run|`max(encode(xs), key=itemgetter(1))`|
|constant memory|the explicit `prev`/`n` loop|

---

### Key Insight

**RLE is the only pattern in the Compress family you can reverse.** Distinct and Dedupe throw information away. RLE just moves it into the count, so `decode(encode(xs)) == xs` holds exactly. That round trip *is* the pattern, and it's the first test you should write.

Here's the honest caveat: **RLE can double your data.** Feed it input with no adjacent repeats and every single element becomes a `(value, 1)` pair. It only compresses one shape of input, long flat runs, which is why it shines on scanned images, sensor states and fax pages and does nothing for text or already-compressed bytes. That's why every real RLE format adds an escape for literal runs. If you're implementing one for anything beyond an exercise, that flag is the part that matters.

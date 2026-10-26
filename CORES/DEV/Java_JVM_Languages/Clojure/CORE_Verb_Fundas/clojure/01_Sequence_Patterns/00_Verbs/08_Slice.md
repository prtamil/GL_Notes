# Sequence Processing — Verb 8: Slice

## Introduction

Sometimes we don't need the entire sequence—we only need **a portion of it**.

**Slice** is the act of extracting a contiguous part of a sequence based on position or a stopping condition.

The mental question is:

> **"Which part of the sequence do I need?"**

Unlike **Select**, which keeps elements based on a predicate regardless of position, **Slice** focuses on taking or removing **contiguous regions** of a sequence.

---

# Slice → Clojure

|Thinking Verb|Mental Question|Common Clojure Functions|
|---|---|---|
|**Slice**|Which part of the sequence do I need?|`take`, `drop`, `take-last`, `drop-last`, `take-while`, `drop-while`, `split-at`, `subvec`|

> **Note:** Most slice operations are based on position or contiguous ranges. `subvec` is specific to vectors and provides efficient slicing.

---

# Common Slice Patterns

|Pattern|Clojure|Example Result|
|---|---|---|
|Take first _N_ elements|`take`|`(take 3 [1 2 3 4 5])` → `(1 2 3)`|
|Drop first _N_ elements|`drop`|`(drop 3 [1 2 3 4 5])` → `(4 5)`|
|Take last _N_ elements|`take-last`|`(take-last 2 [1 2 3 4 5])` → `(4 5)`|
|Drop last _N_ elements|`drop-last`|`(drop-last 2 [1 2 3 4 5])` → `(1 2 3)`|
|Take while condition holds|`take-while`|`(take-while pos? [3 2 1 0 -1])` → `(3 2 1)`|
|Drop while condition holds|`drop-while`|`(drop-while pos? [3 2 1 0 -1])` → `(0 -1)`|
|Split at position|`split-at`|`(split-at 3 [1 2 3 4 5])` → `[(1 2 3) (4 5)]`|
|Slice a vector|`subvec`|`(subvec [1 2 3 4 5] 1 4)` → `[2 3 4]`|

---

# The Clojure-specific catches

**Clojure has no negative indices.** Use `take-last` and `drop-last` for operations at the end.

**`take` and `drop` clamp their bounds. `subvec` and `nth` throw.** Select the behavior that matches the input contract.

**`subvec` is O(1), but it retains the source vector.** A small slice can keep a large source vector in memory. Call `vec` to make an independent vector.

**`take` and `drop` are lazy. `subvec` is not.** Use `take` and `drop` for streams and non-indexed sequences.

---

# One Sentence to Remember

> **Slice extracts a contiguous portion of a sequence based on position or a boundary condition.**

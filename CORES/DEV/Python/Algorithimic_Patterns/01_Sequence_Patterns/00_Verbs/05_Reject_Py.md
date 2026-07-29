# Sequence Processing — Verb 5: Reject

## Introduction

Sometimes it is easier to think about **what should be removed** rather than what should be kept.

**Reject** is the act of creating a new sequence by discarding elements that satisfy a rule or condition.

The mental question is:

> **"What should I discard?"**

Although **Reject** is the logical opposite of **Select**, it is an equally important way of thinking because many real-world problems are naturally expressed as removing unwanted data.

---

# Reject → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Reject**|What should I discard?|`[x for x in xs if not p(x)]`, `itertools.filterfalse`, `itertools.dropwhile`, `xs[n:]`, `xs[:-n]`, `list.remove`, `del`|

> **Note:** Python has no `remove`-the-verb for sequences — you write the negated comprehension, or use `filterfalse`, which takes the same arguments as `filter` and keeps the complement.

---

# Common Rejection Patterns

|Pattern|Python|Example Result|
|---|---|---|
|Remove matching elements|comprehension|`[x for x in [1,2,3,4] if x % 2]` → `[1, 3]`|
|Remove matching, lazily|`filterfalse`|`list(filterfalse(lambda x: x % 2 == 0, [1,2,3,4]))` → `[1, 3]`|
|Drop first _N_ elements|slicing|`[1,2,3,4,5][2:]` → `[3, 4, 5]`|
|Drop last _N_ elements|slicing|`[1,2,3,4,5][:-2]` → `[1, 2, 3]`|
|Drop while a condition holds|`dropwhile`|`list(dropwhile(lambda x: x > 0, [3,2,1,0,-1]))` → `[0, -1]`|
|Remove one value in place|`list.remove`|`xs.remove(3)` removes the **first** `3` (raises if absent)|
|Delete by index in place|`del`|`del xs[2]`, `del xs[1:3]`|
|Remove keys from a dict|comprehension|`{k: v for k, v in d.items() if k not in drop}`|

---

# The Python-specific catches

**Never mutate a list while iterating it.** `for x in xs: if p(x): xs.remove(x)` skips elements, because removal shifts the indices under the loop. Build a new list instead — that is why the comprehension is the idiom.

**`dropwhile` discards only the *leading* run.** Once the predicate fails once, everything after it is kept, even elements that match.

**`.remove()` deletes the first occurrence only**, and raises `ValueError` if there isn't one.

---

# One Sentence to Remember

> **Reject creates a new sequence by discarding elements that satisfy a rule — as a new sequence, never by deleting from the one you're iterating.**

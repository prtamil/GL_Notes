# Sequence Processing — Verb 5: Reject

## Introduction

Sometimes it's easier to say **what has to go** than what should stay.

**Reject** builds a new sequence by throwing away the elements that match a rule.

The question you're asking:

> **"What should I discard?"**

Yes, Reject is just Select turned inside out. It still earns its own name, because plenty of real problems arrive phrased as "get rid of the junk" rather than "keep the good stuff".

---

# Reject → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Reject**|What should I discard?|`[x for x in xs if not p(x)]`, `itertools.filterfalse`, `itertools.dropwhile`, `xs[n:]`, `xs[:-n]`, `list.remove`, `del`|

> **Note:** There's no general "remove" verb for sequences in Python. You either write the comprehension with the condition negated, or use `filterfalse`, which takes the same arguments as `filter` and keeps everything `filter` would have dropped.

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

**Never change a list while you're looping over it.** `for x in xs: if p(x): xs.remove(x)` quietly skips elements, because each removal shifts the indices out from under the loop. Build a new list instead. That's exactly why the comprehension is the idiom here.

**`dropwhile` only drops the *leading* run.** The moment the predicate fails once, everything after that is kept, matches included.

**`.remove()` deletes the first occurrence and nothing else**, and raises `ValueError` if there isn't one.

---

# One Sentence to Remember

> **Reject drops the elements that match a rule and gives you a new sequence back. Always a new sequence, never by deleting from the one you're looping over.**

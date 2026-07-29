# Sequence Processing — Verb 19: Classify

## Introduction

Sometimes we don't just want to group elements—we first want to **assign each element to a category**.

**Classify** is the act of assigning every element in a sequence to a class, label, or category based on a rule.

The mental question is:

> **"Which category does this element belong to?"**

Unlike **Group**, which collects elements into buckets, **Classify** focuses on determining the category for each individual element.

---

# Classify → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Classify**|Which category does this element belong to?|a labelling function + `map`, `if/elif`, `match` (3.10+), `bisect`, a dict lookup, `defaultdict(list)`|

> **Note:** The classifier belongs in a **named function**, not inlined in the comprehension. That rename is not cosmetic: a named `size(n)` is testable, reusable, and the obvious place where the next category gets added.

---

# Common Classification Patterns

|Pattern|Python|Example Result|
|---|---|---|
|Classify by predicate|comprehension|`["odd" if n%2 else "even" for n in [1,2,3]]` → `['odd','even','odd']`|
|Classify by multiple rules|`if/elif` in a function|`[age_band(a) for a in [10,30,70]]` → `['child','adult','senior']`|
|Classify with `match`|`match`/`case` (3.10+)|structural rules, one branch each|
|Classify by numeric range|`bisect`|`labels[bisect(cuts, n)]` — O(log k), cut points stay data|
|Classify by a lookup table|`dict.get`|`{"GET": "read"}.get(verb, "other")`|
|Classify and count|`Counter`|`Counter(age_band(a) for a in ages)`|
|Classify and collect|`defaultdict(list)`|`d[age_band(a)].append(a)` → `{'child': [10], ...}`|
|Two categories only|`bool` key|`out[bool(p(x))].append(x)`|

---

# The Python-specific catches

**A predicate gives two categories; anything more needs labels.** The moment you want "small/medium/large" you are no longer writing a predicate, you are writing a classifier — return strings or an `Enum`, not booleans.

**Chained `if/elif` is O(k) per element and hard-codes the cut points.** For numeric bands, `bisect(cuts, n)` into a labels list is O(log k) and keeps the boundaries editable as data.

**Classify and Group are one step apart.** Classify produces the label; Group is what you do with it. `Counter(classify(x) for x in xs)` counts the categories; `d[classify(x)].append(x)` collects them.

---

# One Sentence to Remember

> **Classify assigns each element to a category based on a rule — and the rule deserves a name.**

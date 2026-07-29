# Sequence Processing — Verb 19: Classify

## Introduction

Before you can group things, you often need to **decide what each one is**.

**Classify** puts a label or category on every element, according to some rule.

The question you're asking:

> **"Which category does this element belong to?"**

**Group** gathers elements into buckets. **Classify** is the earlier step: working out which bucket each element belongs in.

---

# Classify → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Classify**|Which category does this element belong to?|a labelling function + `map`, `if/elif`, `match` (3.10+), `bisect`, a dict lookup, `defaultdict(list)`|

> **Note:** Put the classifier in a **named function** rather than inlining it in the comprehension. That's not just tidiness. A named `size(n)` can be tested, reused, and is the obvious place to add the next category when it turns up.

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

**A predicate buys you two categories. More than that needs labels.** As soon as you want "small/medium/large" you've stopped writing a predicate and started writing a classifier, so return strings or an `Enum` instead of booleans.

**A chain of `if/elif` costs O(k) per element and bakes the cut points into the code.** For numeric bands, `bisect(cuts, n)` into a labels list is O(log k) and leaves the boundaries sitting in data where you can edit them.

**Classify and Group are one step apart.** Classify produces the label; Group decides what to do with it. `Counter(classify(x) for x in xs)` counts the categories, `d[classify(x)].append(x)` collects them.

---

# One Sentence to Remember

> **Classify puts each element in a category using a rule, and that rule deserves a name of its own.**

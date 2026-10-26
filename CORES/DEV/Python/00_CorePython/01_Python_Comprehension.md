# Never Be Confused by a Python Comprehension Again

There is **one** mental model in this essay. Not one for lists and another for dicts, not a special case for nesting. One.

Learn it in Part 1, then watch it explain every comprehension you will ever write — filtered, transformed, nested, into a list, a set, a dict, or a lazy stream. Same model every time.

Our data for the whole essay:

```python
xs = [1, 2, 3, 4, 5, 6]
```

```
  item    1     2     3     4     5     6
```

Six numbers. Keep this row in your head.

---

# Part 1 — The mental model: a belt with three stations

Here is a comprehension that looks scrambled the first time you meet it:

```python
[x * x for x in xs if x % 2 == 0]
```

It isn't scrambled. There are exactly **three jobs**, and every comprehension ever written is those same three:

| Piece | Its job | Nickname |
|---|---|---|
| `for x in xs` | Where the items **come from**, one at a time. | **SOURCE** |
| `if x % 2 == 0` | Who is **allowed through**. Pass or fail, nothing else. | **GATE** |
| `x * x` | What you **make** out of the ones that got through. | **SHAPE** |

Picture a conveyor belt with the three stations in that order, and a basket at the end:

```
   SOURCE  ──→  GATE  ──→  SHAPE  ──→  [ basket ]
   one item     pass?      build it     collect it
   at a time
```

And one sentence, which you will say out loud every time:

> ## **"For each item from the SOURCE, if it passes the GATE, drop the SHAPE in the basket."**

Everything about comprehensions is this sentence. Nothing else.

## Read it in the order the work happens

The only genuinely confusing thing about the syntax is that the SHAPE is written **first**, before you even know what `x` is.

There's a reason, and it's a good one. **The brackets are the basket, and the shape is the label on the front of it.** When you read someone else's code, the first thing you want to know is *what comes out*. Python puts that first.

But that's the **write** order, not the **read** order:

> ### **Write order: `[ SHAPE for SOURCE if GATE ]`. Read order: SOURCE → GATE → SHAPE.**
>
> Your eyes jump to the `for` first. Every time.

Say the `for` out loud, then the `if`, then go back to the front. Once you do this a dozen times you'll stop noticing you're doing it.

## Watch it once

```python
[x * x for x in xs if x % 2 == 0]
```

```
  source    1     2     3     4     5     6
  gate      ✗     ✓     ✗     ✓     ✗     ✓
  shape     ·     4     ·    16     ·    36
```

`1` arrives, fails the gate, falls off the belt. `2` arrives, passes, gets shaped into `4`, lands in the basket. And so on.

```python
→ [4, 16, 36]
```

Notice the basket has **3** items from a source of **6**. The gate is the only thing that can change the count.

## The proof that this is all it is

Every comprehension is a `for` loop you already know how to write:

```python
out = []
for x in xs:                 # SOURCE
    if x % 2 == 0:           # GATE
        out.append(x * x)    # SHAPE
```

That loop and the comprehension are the same program. And the conversion is purely mechanical, in both directions:

> ### **Take the loop. Lift the thing inside `append(...)` to the front. Delete the colons and the line breaks.**

| In the loop | In the comprehension |
|---|---|
| `out = []` … `out` | the `[ ]` |
| `for x in xs:` | `for x in xs` — same words, no colon |
| `if cond:` | `if cond` — same words, no colon |
| `out.append(expr)` | `expr`, moved to the front |

Nothing is added. Nothing is hidden. **If a comprehension ever confuses you, write the loop** — the loop is always legal, and it is always the same thing.

## Two things you get for free

**The source is never touched.** A comprehension reads; it does not modify. `xs` is exactly the same afterwards.

**You always get a brand-new basket.** No accumulator to declare, no chance of appending to the wrong list, no leftover contents from last time.

## What can never be in there

A comprehension holds **expressions only**. No statements. That means no `=` assignment (the walrus `:=` is the one exception — see 6.4), no `break`, no `continue`, no `return`, no `try/except`, no `while`.

That's not a limitation to work around. It's the comprehension being honest with you: **if you need those, you need a loop.** Reach for one without embarrassment.

That's the model. Now we just apply it.

---

# Part 2 — Source and shape (the gate comes later)

Leave the `if` off entirely for now. Two stations: things come in, things get made.

```
   SOURCE  ──→  SHAPE  ──→  [ basket ]
```

With no gate, **nothing is ever dropped** — the basket has exactly as many items as the source. Remember that; it's the crux of the biggest trap in Part 3.

## 2.1 `[x for x in xs]` — the shape that does nothing

```python
[x for x in xs]
```

```
  source    1     2     3     4     5     6
  shape     1     2     3     4     5     6
```

```python
→ [1, 2, 3, 4, 5, 6]
```

A copy. Perfectly legal, occasionally useful (it's how you make a list out of any iterable when you don't feel like typing `list(...)`), but if you see this in real code with no gate and no shape, someone wrote `list(xs)` the long way.

## 2.2 `[x * x for x in xs]` — the everyday transform

```python
[x * x for x in xs]
```

```
  source    1     2     3     4     5     6
  shape     1     4     9    16    25    36
```

```python
→ [1, 4, 9, 16, 25, 36]
```

Six in, six out. **The shape can't change the count — only the gate can.**

## 2.3 The shape can ignore the item entirely

```python
['.' for _ in xs]        # → ['.', '.', '.', '.', '.', '.']
[0] * 6                  # → [0, 0, 0, 0, 0, 0]   (simpler, when the value is constant)
[[] for _ in xs]         # → six SEPARATE empty lists
```

`_` is the conventional name for "I need a loop variable but I'm not going to use it." It's an ordinary name, not syntax; it just tells the reader not to look for it in the shape.

That third line matters: `[[] for _ in xs]` gives you six **distinct** lists, while `[[]] * 6` gives you the same list six times. The comprehension runs the shape once per item; `*` copies a reference.

## 2.4 The shape can be any expression at all

```python
[str(x) for x in xs]              # ['1', '2', '3', '4', '5', '6']
[f"#{x}" for x in xs]             # ['#1', '#2', '#3', '#4', '#5', '#6']
[(x, x * x) for x in xs]          # [(1, 1), (2, 4), ...]     tuples need their parens
[x.upper() for x in "abc"]        # ['A', 'B', 'C']
[len(w) for w in ["hi", "there"]] # [2, 5]
```

Function calls, f-strings, tuples, attribute access, another comprehension — anything you could put on the right of an `=` sign.

## 2.5 The source can be any iterable

Not just lists. **Anything you could put after `for … in` in a normal loop.**

```python
[c for c in "abc"]                     # ['a', 'b', 'c']       string
[i for i in range(4)]                  # [0, 1, 2, 3]          range
[x for x in (1, 2, 3)]                 # [1, 2, 3]             tuple
[k for k in {'a': 1, 'b': 2}]          # ['a', 'b']            dict → its KEYS
[v for v in {'a': 1, 'b': 2}.values()] # [1, 2]                dict values
[line.strip() for line in open(path)]  # a file, line by line
```

Iterating a dict gives you keys — same as a `for` loop, no special rule.

## 2.6 Unpacking in the source

If the source hands you pairs, unpack them right there, exactly as a loop would:

```python
d = {'a': 1, 'b': 2}

[f"{k}={v}" for k, v in d.items()]           # ['a=1', 'b=2']
[f"{i}:{x}" for i, x in enumerate("abc")]    # ['0:a', '1:b', '2:c']
[a + b for a, b in zip([1, 2], [10, 20])]    # [11, 22]
```

This is where comprehensions start paying rent. `enumerate` gives you the index without arithmetic, `zip` walks two sources in lockstep.

## 2.7 The source expression runs exactly once

```python
[x for x in expensive_function()]
```

`expensive_function()` is called **one** time, before anything is pulled. The `for` then walks whatever it returned. This is a real guarantee, and it's the same one a normal `for` loop gives you.

(This matters again in 4.3, where an *inner* source is re-evaluated on every outer item — because there, the loop would too.)

---

# Part 3 — The gate

Add the `if` back. The gate has exactly one power: **decide who continues.** It produces nothing, changes nothing, and shapes nothing.

## 3.1 `if` at the end

```python
[x for x in xs if x > 3]
```

```
  source    1     2     3     4     5     6
  gate      ✗     ✗     ✗     ✓     ✓     ✓
  shape     ·     ·     ·     4     5     6
```

```python
→ [4, 5, 6]
```

The gate reads the **raw item**, before shaping. `x` here is `1, 2, 3, …`, not `x * x`.

## 3.2 Gate and shape together

```python
[x * 10 for x in xs if x % 2 == 0]
```

```
  source    1     2     3     4     5     6
  gate      ✗     ✓     ✗     ✓     ✗     ✓
  shape     ·    20     ·    40     ·    60
```

```python
→ [20, 40, 60]
```

Read it in work order: *from `xs`, keep the evens, multiply by ten.*

## 3.3 More than one gate

Stack them. Every `if` must pass — they chain like `and`:

```python
[x for x in xs if x > 2 if x % 2 == 0]     # → [4, 6]
[x for x in xs if x > 2 and x % 2 == 0]    # → [4, 6]   identical
```

Two gates in a row, or one gate with `and` — same belt, same result. Use whichever reads better; `and` is more common, stacked `if`s can read nicely when the conditions are unrelated.

## 3.4 The gate runs *before* the shape — and that protects you

```python
ys = [1, 0, 2, 0, 3]

[10 // y for y in ys if y]        # → [10, 5, 3]      no ZeroDivisionError
```

The zeros never reach the shape station. This ordering is guaranteed, and it's the standard way to make a risky shape safe.

The reverse does **not** work — a gate cannot inspect the shape's output, because the shape hasn't run yet:

```python
[x * x for x in xs if x * x > 10]      # you must repeat the expression...
[y for x in xs if (y := x * x) > 10]   # ...or compute it once with a walrus (see 6.4)
```

## 3.5 The big one: `if/else` does NOT go at the end

This is the single most common comprehension mistake. Both of these are valid Python, and they are **not** the same thing:

```python
[x for x in xs if x % 2 == 0]                  # GATE   — a filter
[x if x % 2 == 0 else 0 for x in xs]           # SHAPE  — a choice
```

Look at where they sit relative to the `for`:

```
  [ SHAPE          for x in xs   if GATE ]
    ↑ before the for              ↑ after the for
    a choice: every item          a filter: some items
    comes out, in one of          never come out at all
    two forms
```

The rule falls straight out of the model. **A gate says pass or fail. It has no way to emit a value, so it has no `else` to give one.** The moment you want *something* out of the rejected items, you're not filtering any more — you're making a decision inside the shape, and every item still makes it to the basket.

Watch the counts:

```python
[x for x in xs if x % 2 == 0]
```
```
  source    1     2     3     4     5     6
  gate      ✗     ✓     ✗     ✓     ✗     ✓
  basket        [ 2,          4,          6 ]        3 items — SHRANK
```

```python
[x if x % 2 == 0 else 0 for x in xs]
```
```
  source    1     2     3     4     5     6
  gate     — no gate; everyone passes —
  shape     0     2     0     4     0     6
  basket  [ 0, 2, 0, 4, 0, 6 ]                        6 items — SAME LENGTH
```

> ### **Filtering shrinks the basket. A ternary shape never does.**
> **`if` after the `for` = who gets in. `if/else` before the `for` = what they turn into.**

And `[x for x in xs if x > 3 else 0]` is a `SyntaxError` — Python won't even let you say it, precisely because it's meaningless.

## 3.6 Both at once

Perfectly legal to have a choosing shape *and* a gate. Read it in work order and it's easy:

```python
["big" if x > 4 else "small" for x in xs if x % 2 == 0]
```

```
  source    1     2     3     4     5     6
  gate      ✗     ✓     ✗     ✓     ✗     ✓
  shape     ·  small    · small    ·   big
```

```python
→ ['small', 'small', 'big']
```

*From `xs`, keep the evens; each one becomes "big" or "small".* Source, gate, shape. Always that order.

## 3.7 When the basket comes back empty

Like slices, a comprehension never complains — if nothing passes the gate, you get `[]` in silence.

```python
[x for x in xs if x > 100]      # → []      nothing passed
[x for x in [] if x > 0]        # → []      nothing arrived
```

Two different causes, one symptom. **When you get an empty basket, check the source first, then the gate** — an empty or already-consumed source (6.3!) is at least as common as an over-tight condition.

---

# Part 4 — More than one source: nesting

Two `for`s means two loops. And there is one rule that makes the order obvious forever:

> ### **The `for`s appear in exactly the order you would nest them as ordinary loops. Left is outer, right is inner.**

## 4.1 The pairing

```python
[(a, b) for a in [1, 2] for b in "xy"]
```

Which is this loop, mechanically converted:

```python
out = []
for a in [1, 2]:          # ← leftmost for = outermost loop
    for b in "xy":        # ← next for = next loop in
        out.append((a, b))
```

```python
→ [(1, 'x'), (1, 'y'), (2, 'x'), (2, 'y')]
```

The **rightmost source spins fastest** — `b` runs all the way through for each single `a`. Exactly like nested loops, because it *is* nested loops.

## 4.2 Flattening — the one you'll use most

```python
m = [[1, 2], [3, 4], [5, 6]]

[x for row in m for x in row]
```

Read it: *for each `row` in `m`, for each `x` in that `row`, take `x`.*

```
  outer     row=[1,2]        row=[3,4]        row=[5,6]
  inner      1    2           3    4           5    6
  basket  [ 1, 2, 3, 4, 5, 6 ]
```

```python
→ [1, 2, 3, 4, 5, 6]
```

Memorise the shape of this line. It is *the* flatten idiom in Python.

## 4.3 The inner source can depend on the outer

```python
[(a, b) for a in range(3) for b in range(a)]
→ [(1, 0), (2, 0), (2, 1)]
```

`b`'s source is rebuilt for every `a` — `range(0)`, then `range(1)`, then `range(2)`. That's not a special comprehension rule; the nested loop does the same. The dependency only works **left to right**: an outer source can never see an inner variable.

## 4.4 Gates can go after any `for`

Each `if` filters at the point where it's written:

```python
[x for row in m if len(row) == 2 for x in row]   # gate on rows, before descending
[x for row in m for x in row if x % 2 == 0]      # gate on items, at the bottom
→ [2, 4, 6]
```

Placing the gate as early as possible does less work and usually reads better — same as in a loop.

## 4.5 Two `for`s vs. a comprehension inside the shape

These two look similar and do completely different things. This is the distinction worth ten minutes of your attention:

```python
m = [[1, 2], [3, 4], [5, 6]]

[x * 10 for row in m for x in row]       # → [10, 20, 30, 40, 50, 60]      FLAT
[[x * 10 for x in row] for row in m]     # → [[10, 20], [30, 40], [50, 60]] NESTED
```

The model tells you why instantly. **Look at what's in the shape station.**

| | The shape is… | So each source item produces… | Result |
|---|---|---|---|
| `[x*10 for row in m for x in row]` | a **number** | one number per innermost item | one flat list |
| `[[x*10 for x in row] for row in m]` | a **whole list** (its own little belt) | one *list* per row | a list of lists |

Second one, said out loud: *for each row in m, build a basket of that row's items times ten, and put that basket in the outer basket.* One source, and the shape happens to be another comprehension.

> **Structure is decided by the SHAPE, never by the number of `for`s.** A list-shaped shape gives you nesting; a scalar shape gives you flat.

Transposing a matrix uses the same trick, with `zip` doing the pairing:

```python
[list(col) for col in zip(*m)]      # → [[1, 3, 5], [2, 4, 6]]
```

## 4.6 The order trap

```python
[x for x in row for row in m]       # NameError: name 'row' is not defined
```

You used `row` in the leftmost (outer) source, but `row` isn't created until the second `for`. Nested loops would fail the same way. **Left to right, outer to inner — nothing can be used before its `for`.**

## 4.7 Know when to stop

Two `for`s is normal. Three is a code review conversation. Four is a loop wearing a disguise.

```python
# don't
[f(a, b, c) for a in A if p(a) for b in B(a) if q(b) for c in C(b) if r(c)]
```

Nobody reads that once and gets it right. Write the loop, or split it into two named comprehensions:

```python
pairs  = [(a, b) for a in A if p(a) for b in B(a) if q(b)]
result = [f(a, b, c) for a, b in pairs for c in C(b) if r(c)]
```

**A comprehension you have to decode is worse than the loop you were avoiding.**

---

# Part 5 — Four baskets, one belt

Everything so far was about the belt. Now change the basket. **The three stations do not change at all** — only what collects the output.

| Basket | Written | You get | Notes |
|---|---|---|---|
| list | `[ … ]` | a `list` | order kept, duplicates kept |
| set | `{ … }` | a `set` | **duplicates dropped, order gone** |
| dict | `{k: v … }` | a `dict` | shape is a **pair** with a colon |
| generator | `( … )` | a lazy stream | **nothing runs yet** |

## 5.1 List — `[ ]`

The default. Everything in Parts 1–4.

```python
[x % 3 for x in xs]        # → [1, 2, 0, 1, 2, 0]
```

## 5.2 Set — `{ }`

Same belt, and the basket refuses duplicates:

```python
{x % 3 for x in xs}        # → {0, 1, 2}
```

Use it when you want the **distinct** results and don't care about order. It's the shortest way to say "unique":

```python
{w.lower() for w in ["Hi", "HI", "hi", "yo"]}      # → {'hi', 'yo'}
```

## 5.3 Dict — `{k: v}`

Same belt; the shape station now builds a **pair**, and the colon is what tells Python this is a dict and not a set:

```python
{x: x * x for x in xs}
→ {1: 1, 2: 4, 3: 9, 4: 16, 5: 25, 6: 36}
```

```python
{k: v for k, v in d.items() if v > 1}       # filter a dict
{v: k for k, v in d.items()}                # invert a dict
{w: len(w) for w in ["hi", "there"]}        # → {'hi': 2, 'there': 5}
```

**Duplicate keys: the last one wins.** Same as ordinary dict assignment, no surprise.

```python
{len(w): w for w in ["aa", "bb", "c"]}      # → {2: 'bb', 1: 'c'}
```

And the empty-braces gotcha, worth knowing once: `{}` is an empty **dict**, never an empty set. For that, `set()`.

## 5.4 Generator — `( )`

Same belt — but **the belt doesn't start moving until someone asks for an item.**

```python
g = (x * x for x in xs)        # nothing has happened yet
next(g)                        # → 1     now one item ran
sum(x * x for x in xs)         # → 91    parens optional inside a single-argument call
```

Use it when you're feeding the results straight into something else and never need the whole list at once:

```python
sum(x * x for x in xs)
max(len(w) for w in words)
any(x > 5 for x in xs)              # stops at the first True — reads no further
"\n".join(str(x) for x in xs)
```

`any` / `all` short-circuiting is the payoff: with a list comprehension, all six items are built before `any` even looks; with a generator, it stops the moment it sees a `True`.

Two things to respect, both covered in 6.3: a generator is **lazy**, and it is **one-shot**.

## 5.5 There is no tuple comprehension

`(x for x in xs)` is a generator, not a tuple — the parens were already taken. If you want a tuple, say so:

```python
tuple(x * x for x in xs)      # → (1, 4, 9, 16, 25, 36)
```

---

# Part 6 — The traps, and why each one is obvious afterwards

## 6.1 `if/else` in the wrong place

Covered in 3.5, and it's the number one mistake, so here it is once more in the smallest possible form:

```python
[A for x in xs if C]           # filter — some items vanish
[A if C else B for x in xs]    # choice — nothing vanishes
[A for x in xs if C else B]    # SyntaxError — a gate has nothing to say about failures
```

## 6.2 The loop variable does not leak

```python
x = 'important'
sq = [x * x for x in xs]
x                              # → 'important'    untouched
```

A comprehension gets its own scope. Your `x` is safe, and the comprehension's `x` does not exist afterwards. (In Python 2 it *did* leak. Any advice you read that warns about this is old.)

The flip side: **you cannot use the loop variable after the comprehension**, and you cannot accumulate into it. There's no back door.

## 6.3 Generators are lazy, and one-shot

**Lazy** — the work happens later, so it sees the world as it is *then*:

```python
ys = [1, 2, 3]
g  = (y * 10 for y in ys)
ys.append(4)
list(g)                        # → [10, 20, 30, 40]     the 4 got in
```

The equivalent list comprehension would have run immediately and returned `[10, 20, 30]`. Neither is wrong; they answer different questions. Just know which one you asked.

**One-shot** — a generator is consumed as you read it, and it does not rewind:

```python
g = (x for x in xs)
list(g)                        # → [1, 2, 3, 4, 5, 6]
list(g)                        # → []                   already spent
```

That silent `[]` on the second read is a genuinely nasty bug, because it looks exactly like a filter that matched nothing. **If you need the results more than once, use a list.**

The same trap bites with `zip`, `map`, `enumerate` and file handles — all one-shot.

## 6.4 The walrus: compute once, use twice

When the gate and the shape need the same expensive value, `:=` lets you name it inline:

```python
[y for x in xs if (y := x * x) > 10]     # → [16, 25, 36]
```

Read it as: *shape it into `y`, gate on `y`, keep `y`.* The parens around the walrus are required. Use it exactly here — for "compute once, test, then reuse". Anywhere else it makes the line harder to read, not easier.

Without it you'd write the expression twice (`[x*x for x in xs if x*x > 10]`), which is fine for cheap expressions and wasteful for costly ones.

## 6.5 Don't build a basket you're throwing away

```python
[print(x) for x in xs]         # prints — and quietly builds [None, None, None, None, None, None]
```

If you don't want the basket, you don't want a comprehension. **A comprehension is for producing a value; a `for` loop is for doing something.** Use the loop:

```python
for x in xs:
    print(x)
```

Same for `[lst.append(x) for x in xs]` and friends. It works, and every reviewer will flag it.

## 6.6 You cannot stop early

There is no `break` in a comprehension. If you need one:

```python
from itertools import takewhile
list(takewhile(lambda x: x < 4, xs))     # → [1, 2, 3]    stops at the first failure
```

Note the difference from a gate — `[x for x in xs if x < 4]` reads **every** item and would also collect anything small that comes after a big one. `takewhile` genuinely stops. Different questions, different tools. And when in doubt, a loop with a `break` is perfectly good Python.

## 6.7 One line does not mean one thought

A comprehension is not automatically better than the loop. It's better when it says *one clear thing*. When the line grows a second gate, a ternary, and a nested source all at once, its virtue is gone.

Two honest escape hatches, and neither is a defeat:

```python
# name the middle step
evens   = [x for x in xs if x % 2 == 0]
labeled = [f"n{x}" for x in evens]

# or split the line across several — this is still one comprehension
labeled = [
    f"n{x}"
    for x in xs
    if x % 2 == 0
]
```

That second form puts each station on its own line, in work order. For anything non-trivial it's the most readable thing you can write.

---

# Part 7 — The whole thing on one page

```python
xs = [1, 2, 3, 4, 5, 6]
m  = [[1, 2], [3, 4], [5, 6]]
d  = {'a': 1, 'b': 2}
```

## Source, gate, shape

| Comprehension | Source | Gate | Shape | Result |
|---|---|---|---|---|
| `[x for x in xs]` | `xs` | — | `x` | `[1, 2, 3, 4, 5, 6]` |
| `[x * x for x in xs]` | `xs` | — | `x*x` | `[1, 4, 9, 16, 25, 36]` |
| `[x for x in xs if x > 3]` | `xs` | `x > 3` | `x` | `[4, 5, 6]` |
| `[x * 10 for x in xs if x % 2 == 0]` | `xs` | even | `x*10` | `[20, 40, 60]` |
| `[x for x in xs if x > 2 if x % 2 == 0]` | `xs` | both | `x` | `[4, 6]` |
| `[x if x % 2 == 0 else 0 for x in xs]` | `xs` | **none** | choice | `[0, 2, 0, 4, 0, 6]` |
| `['big' if x > 4 else 'small' for x in xs if x % 2 == 0]` | `xs` | even | choice | `['small', 'small', 'big']` |
| `['.' for _ in xs]` | `xs` | — | `'.'` | `['.', '.', '.', '.', '.', '.']` |
| `[x for x in xs if x > 100]` | `xs` | nothing passes | `x` | `[]` |
| `[x for x in xs if x > 3 else 0]` | | | | **SyntaxError** |

## Other sources

| Comprehension | Result |
|---|---|
| `[c for c in "abc"]` | `['a', 'b', 'c']` |
| `[i for i in range(4)]` | `[0, 1, 2, 3]` |
| `[k for k in d]` | `['a', 'b']` |
| `[f"{k}={v}" for k, v in d.items()]` | `['a=1', 'b=2']` |
| `[f"{i}:{c}" for i, c in enumerate("abc")]` | `['0:a', '1:b', '2:c']` |
| `[a + b for a, b in zip([1, 2], [10, 20])]` | `[11, 22]` |

## Nesting

| Comprehension | Result |
|---|---|
| `[(a, b) for a in [1, 2] for b in "xy"]` | `[(1,'x'), (1,'y'), (2,'x'), (2,'y')]` |
| `[x for row in m for x in row]` | `[1, 2, 3, 4, 5, 6]` — **flatten** |
| `[x for row in m for x in row if x % 2 == 0]` | `[2, 4, 6]` |
| `[[x * 10 for x in row] for row in m]` | `[[10,20], [30,40], [50,60]]` — **structure kept** |
| `[(a, b) for a in range(3) for b in range(a)]` | `[(1,0), (2,0), (2,1)]` |
| `[list(col) for col in zip(*m)]` | `[[1,3,5], [2,4,6]]` — transpose |
| `[x for x in row for row in m]` | **NameError** — inner name used too early |

## The four baskets

| Comprehension | Result |
|---|---|
| `[x % 3 for x in xs]` | `[1, 2, 0, 1, 2, 0]` |
| `{x % 3 for x in xs}` | `{0, 1, 2}` — deduped, unordered |
| `{x: x * x for x in xs}` | `{1:1, 2:4, 3:9, 4:16, 5:25, 6:36}` |
| `{v: k for k, v in d.items()}` | `{1: 'a', 2: 'b'}` — inverted |
| `(x * x for x in xs)` | a generator — **nothing has run** |
| `sum(x * x for x in xs)` | `91` |
| `tuple(x * x for x in xs)` | `(1, 4, 9, 16, 25, 36)` |

---

# Part 8 — When it surprises you, ask three questions

1. **"What's my source, what's my gate, what's my shape?"** Say it out loud in that order with your real code. Nine times out of ten the mistake shows up mid-sentence.
2. **Got an empty basket?** Check the **source** before the gate — an empty list, or a generator/`zip`/file you already consumed, looks exactly like a condition that matched nothing.
3. **Wrong number of items?** Only the gate can change the count. Too many means your `if` is really an `if/else` in the shape (3.5); too few means the gate is tighter than you thought.

And the universal fallback: **write it as a loop.** The loop is always legal, always says the same thing, and always makes the bug visible.

---

# Part 9 — Real tasks, using all of it

```python
words = ["apple", "Fig", "banana", "kiwi", "Date"]
nums  = [3, -1, 4, -1, 5, 9, -2, 6]
rows  = [{"name": "ann", "age": 31}, {"name": "bo", "age": 17}]

# --- filter ---
[n for n in nums if n > 0]                    # [3, 4, 5, 9, 6]
[w for w in words if len(w) > 3]              # ['apple', 'banana', 'kiwi', 'Date']
[w for w in words if w[0].isupper()]          # ['Fig', 'Date']

# --- transform ---
[w.lower() for w in words]                    # ['apple', 'fig', ...]
[abs(n) for n in nums]                        # [3, 1, 4, 1, 5, 9, 2, 6]
[n if n > 0 else 0 for n in nums]             # clamp: [3, 0, 4, 0, 5, 9, 0, 6]

# --- both ---
[w.upper() for w in words if len(w) > 4]      # ['APPLE', 'BANANA']

# --- pulling fields out of records ---
[r["name"] for r in rows]                     # ['ann', 'bo']
[r["name"] for r in rows if r["age"] >= 18]   # ['ann']
{r["name"]: r["age"] for r in rows}           # {'ann': 31, 'bo': 17}

# --- index and pairing ---
[f"{i+1}. {w}" for i, w in enumerate(words)]  # numbered list
list(zip(nums, nums[1:]))                     # neighbour pairs
[b - a for a, b in zip(nums, nums[1:])]       # differences between neighbours

# --- unique things ---
{w.lower() for w in words}                    # distinct, case-folded
{len(w) for w in words}                       # the set of lengths present

# --- grouping-ish: a dict of computed values ---
{w: len(w) for w in words}                    # {'apple': 5, 'Fig': 3, ...}
{w: [c for c in w if c in "aeiou"] for w in words}    # vowels per word

# --- flatten ---
pages = [[1, 2], [3], [4, 5, 6]]
[x for p in pages for x in p]                 # [1, 2, 3, 4, 5, 6]

# --- grid ---
[(r, c) for r in range(3) for c in range(3)]        # all 9 cells
[(r, c) for r in range(3) for c in range(3) if r != c]   # off-diagonal

# --- feeding an aggregate, lazily ---
sum(n for n in nums if n > 0)                 # 27
max(len(w) for w in words)                    # 6
any(n < 0 for n in nums)                      # True   — stops at the first -1
", ".join(w for w in words if len(w) == 3)    # 'Fig'

# --- cleaning input ---
raw = ["  ann ", "", " bo", "   "]
[s.strip() for s in raw if s.strip()]         # ['ann', 'bo']
```

That last line is worth a second look: the gate and the shape both call `.strip()`, so it runs twice per item. For a hot loop, the walrus fixes it:

```python
[t for s in raw if (t := s.strip())]          # ['ann', 'bo']
```

---

# Appendix — four things worth knowing later

**Comprehensions are faster than the equivalent loop.** Not by magic — the append is done by the interpreter instead of via an attribute lookup and a method call each time. Expect a modest win, not a transformation. Never contort a comprehension for speed.

**Memory: list vs generator.** `sum([x for x in big])` builds the whole list first; `sum(x for x in big)` never holds more than one item. For anything large, or for a stream you only walk once, drop the brackets.

**`map` and `filter` still exist.** `map(f, xs)` is `(f(x) for x in xs)` and `filter(p, xs)` is `(x for x in xs if p(x))` — both lazy. The comprehension is preferred in Python because it stays readable when you need both at once, and it doesn't need a `lambda`.

**One genuine oddity: comprehensions inside a `class` body.** The comprehension's private scope can't see the class's names — except in the *first* source, which is evaluated outside it.

```python
class C:
    vals = [1, 2, 3]
    doubled = [v * 2 for v in vals]         # fine — `vals` is the first source
    bad     = [v * n for v in vals for n in vals]   # NameError on the second `vals`
```

Rare, confusing, and worth recognising once so it never costs you an hour. Inside a function this never happens.

---

# The one thing to remember

> ## **"For each item from the SOURCE, if it passes the GATE, drop the SHAPE in the basket."**
>
> **Read `for` first, then `if`, then the front. `if` after the `for` filters; `if/else` before the `for` chooses. The basket type — `[]`, `{}`, `{k: v}`, `()` — changes what collects, never how the belt runs.**

That sentence is the entire feature. Say it out loud with your real code and the answer falls out.

And on the days a comprehension makes you squint: **write the loop.** It is the same program, and clear beats clever.

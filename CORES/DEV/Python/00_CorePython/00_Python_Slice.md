# Never Be Afraid of Python Slices Again

There is **one** mental model in this essay. Not two, not a special case for negatives. One.

Learn it in Part 1, then watch it explain every single slice you will ever write — forward, backward, jumping, from the front, from the back. Same model every time.

Our list for the whole essay:

```python
xs = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
```

```
  idx   0     1     2     3     4     5     6
  item  a     b     c     d     e     f     g
```

Seven items. Positions `0` to `6`. Keep this row in your head.

---

# Part 1 — The mental model: a walker on a row

`xs[start:end:step]` is **a person walking along the row, picking things up.**

Three numbers, three jobs. That's the whole thing:

| Number | Its job | Nickname |
|---|---|---|
| **start** | Where you **stand** at the beginning. You pick up whatever you're standing on. | **STAND** |
| **end** | Where the **stop sign** is. You stop the moment you reach it — and you *never* pick up the item there. | **STOP** |
| **step** | Your **footstep**: how far you move, and which way. | **STEP** |

And one sentence, which you will say out loud every time:

> ## **"Stand at `start`. Take a step of `step`. Stop when you reach `end`."**

Everything in Python's slicing is this sentence. Nothing else.

## Watch it once

```python
xs[2:5]     # stand at 2, step +1, stop sign at 5
```

```
  idx   0     1     2     3     4     5     6
  item  a     b     c     d     e     f     g
  walk              TAKE  TAKE  TAKE  STOP
```

You stand at 2 and take `c`. Step to 3, take `d`. Step to 4, take `e`. Step to 5 — that's the stop sign, so you drop your hands and go home.

```python
→ ['c', 'd', 'e']
```

## Why you never pick up the stop sign

This is the one thing that feels arbitrary until you see what it buys you. A stop sign is a **sign**, not an item. Signs aren't groceries. You don't take it.

And because of that:

**The count is easy.** From 2 to 5 is `5 - 2 = 3` items. No off-by-one thinking, ever.

**Two slices at the same number fit together perfectly.** One walk ends at sign 3, the next walk starts standing on 3. Nothing is missed, nothing is doubled:

```python
xs[:3] + xs[3:] == xs      # True. Every time. Any number.
```

If Python *did* pick up the stop sign, the halves would overlap by one and you'd be writing `n-1` all day long.

## What a blank slot means

You're allowed to leave any of the three out. A blank is not a mystery value — it's just **"the obvious thing for the direction I'm walking."**

| Blank slot | What Python fills in |
|---|---|
| no **start** | Stand at the natural beginning: the **first** item if walking right, the **last** item if walking left. |
| no **end** | No stop sign at all — **walk until you fall off the edge.** |
| no **step** | Footstep of `+1`: one item at a time, to the right. |

So `xs[:]` is "stand at the beginning, no stop sign, step of 1" — you walk the whole row and pick up everything.

That's the model. Now we just apply it.

---

# Part 2 — All positive variants

Positive numbers, positive steps. Every combination, each one walked through.

## 2.1 `xs[start:end]` — both given

```python
xs[2:5]
```

```
  idx   0     1     2     3     4     5     6
  item  a     b     c     d     e     f     g
  walk              TAKE  TAKE  TAKE  STOP
```

Stand at 2, step +1, stop sign at 5.

```python
→ ['c', 'd', 'e']
```

## 2.2 `xs[start:]` — no stop sign

```python
xs[2:]
```

```
  idx   0     1     2     3     4     5     6   | edge
  item  a     b     c     d     e     f     g   |
  walk              TAKE  TAKE  TAKE  TAKE  TAKE| fell off
```

Stand at 2. Nobody planted a stop sign, so you keep walking right until the row runs out.

```python
→ ['c', 'd', 'e', 'f', 'g']
```

## 2.3 `xs[:end]` — no standing spot given

```python
xs[:5]
```

```
  idx   0     1     2     3     4     5     6
  item  a     b     c     d     e     f     g
  walk  TAKE  TAKE  TAKE  TAKE  TAKE  STOP
```

No `start`, so you stand at the natural beginning — index 0. Walk right until the sign at 5.

```python
→ ['a', 'b', 'c', 'd', 'e']
```

## 2.4 `xs[:]` — nothing given

```python
xs[:]
```

```
  idx   0     1     2     3     4     5     6   | edge
  item  a     b     c     d     e     f     g   |
  walk  TAKE  TAKE  TAKE  TAKE  TAKE  TAKE  TAKE| fell off
```

Beginning to edge, one at a time. You get the whole list — as a **fresh copy**, which is why `xs[:]` is the everyday way to duplicate a list.

```python
→ ['a', 'b', 'c', 'd', 'e', 'f', 'g']
```

## 2.5 `xs[start:end:step]` — all three

```python
xs[2:5:2]
```

```
  idx   0     1     2     3     4     5     6
  item  a     b     c     d     e     f     g
  walk              TAKE  skip  TAKE  STOP
```

Stand at 2, take `c`. Your footstep is 2 now, so you land on 4 — index 3 never gets visited. Take `e`. Step to 6? No — you'd pass the sign at 5. Stop.

```python
→ ['c', 'e']
```

Notice: **step didn't change what start and end mean.** They're still "where I stand" and "where the sign is." Step only changes how you move between them.

## 2.6 `xs[::step]` — step only

```python
xs[::2]
```

```
  idx   0     1     2     3     4     5     6   | edge
  item  a     b     c     d     e     f     g   |
  walk  TAKE  skip  TAKE  skip  TAKE  skip  TAKE| fell off
```

Beginning to edge, taking every second one.

```python
→ ['a', 'c', 'e', 'g']
```

## 2.7 `xs[start::step]` — start and step

```python
xs[1::2]
```

```
  idx   0     1     2     3     4     5     6   | edge
  item  a     b     c     d     e     f     g   |
  walk        TAKE  skip  TAKE  skip  TAKE  skip| fell off
```

```python
→ ['b', 'd', 'f']
```

This pairs beautifully with 2.6. **`start` sets your phase, `step` sets your rhythm.** `xs[::2]` and `xs[1::2]` are the two halves of an alternating list.

## 2.8 `xs[:end:step]` — stop sign and step

```python
xs[:5:2]
```

```
  idx   0     1     2     3     4     5     6
  item  a     b     c     d     e     f     g
  walk  TAKE  skip  TAKE  skip  TAKE  STOP
```

```python
→ ['a', 'c', 'e']
```

## 2.9 The empty results — and why they're obvious

Slicing **never** raises an error. When the walk collects nothing, you get `[]` in silence. Here's every way that happens, and the model explains all of them instantly.

**The stop sign is behind you:**

```python
xs[5:2]
```

```
  idx   0     1     2     3     4     5     6
  item  a     b     c     d     e     f     g
  walk              STOP              STAND ──→ walking right, away from the sign
```

You're standing at 5 facing right. The sign is at 2, behind your back. You will never reach it, and Python doesn't let you walk in a direction your step doesn't point. You collect nothing.

```python
→ []
```

**You're standing on the stop sign:**

```python
xs[2:2]
```

Your very first act is to arrive at the sign, so you stop before taking anything.

```python
→ []
```

**The stop sign is off the map:**

```python
xs[3:100]
```

There's no index 100, so the sign effectively sits at the edge. You just walk to the end.

```python
→ ['d', 'e', 'f', 'g']
```

**You're standing off the map:**

```python
xs[10:20]
```

There's nothing out there to pick up.

```python
→ []
```

This last pair is a genuine gift: **you never need `if len(xs) > n` around a slice.** `[1][:3]` is `[1]`, not a crash. The price is that a wrong slice returns `[]` instead of complaining, so an empty result is your signal to re-read your two numbers.

---

# Part 3 — Negative positions: nicknames from the other end

Nothing about the model changes here. We're still standing, stepping, stopping. The only new thing is that **positions have a second name.**

```
  idx   0     1     2     3     4     5     6
  item  a     b     c     d     e     f     g
  also -7    -6    -5    -4    -3    -2    -1
```

A negative number counts from the right. `-1` is the last item, `-2` the one before it.

**The translation rule: `-k` means `len(xs) - k`.** Our list has 7 items, so `-3` is position `7 - 3 = 4`.

> **How to read any negative slice: translate the nicknames to real positions first, then walk exactly as in Part 2.** That's all. There is no second set of rules.

Why does the back ruler start at `-1` and not `-0`? Because `0` is already the first item's name, and there's no negative zero. Small detail, one real consequence — see 3.7.

## 3.1 `xs[-3:]` — the last three

`-3` → position 4.

```
  idx   0     1     2     3     4     5     6   | edge
  item  a     b     c     d     e     f     g   |
  walk                          TAKE  TAKE  TAKE| fell off
```

```python
→ ['e', 'f', 'g']
```

## 3.2 `xs[:-3]` — everything except the last three

`-3` → the stop sign goes at position 4.

```
  idx   0     1     2     3     4     5     6
  item  a     b     c     d     e     f     g
  walk  TAKE  TAKE  TAKE  TAKE  STOP
```

```python
→ ['a', 'b', 'c', 'd']
```

These two are the pair you'll use most, and they're still two halves of one walk: `xs[:-3] + xs[-3:] == xs`.

| Want | Write | Say it as |
|---|---|---|
| Last N | `xs[-n:]` | "stand N from the back, no sign" |
| All but the last N | `xs[:-n]` | "sign planted N from the back" |

## 3.3 `xs[-4:-1]` — both nicknames

`-4` → 3.  `-1` → 6.

```
  idx   0     1     2     3     4     5     6
  item  a     b     c     d     e     f     g
  walk                    TAKE  TAKE  TAKE  STOP
```

```python
→ ['d', 'e', 'f']
```

## 3.4 `xs[2:-2]` — mix and match

`-2` → 5. Positions don't care which end you counted from.

```
  idx   0     1     2     3     4     5     6
  item  a     b     c     d     e     f     g
  walk              TAKE  TAKE  TAKE  STOP
```

```python
→ ['c', 'd', 'e']    # trim 2 off the front, 2 off the back
```

## 3.5 `xs[-5:5]` — mixed the other way

`-5` → 2. Same walk as above, written differently.

```python
→ ['c', 'd', 'e']
```

## 3.6 `xs[-6::2]` — nickname plus a step

`-6` → 1. Stand at 1, step 2, no sign.

```python
→ ['b', 'd', 'f']       # identical to xs[1::2]
```

## 3.7 The two negative traps

**Stop sign behind you, in nickname form:**

```python
xs[-3:-5]      # stand at 4, sign at 2 — behind you
→ []
```

Same rule as 2.9. Translate first and it's not mysterious at all.

**The `-0` hole:**

```python
xs[2:-0]       # -0 IS 0. So this reads xs[2:0] — sign at the very front
→ []
```

You wanted "up to the very end," but there's no `-0` to express it. **The fix is the one you already know: to mean the end, write nothing.**

```python
xs[2:]         # ['c', 'd', 'e', 'f', 'g']   ✓
```

Remember this one. It comes back in Part 4 wearing a bigger hat.

---

# Part 4 — Negative step: turn around and walk left

Here's what changes when `step` is negative:

**Your footsteps point left.**

That's it. That's the whole change. Stand, step, stop — same three jobs, same sentence. You're just facing the other way.

Two things follow from it automatically. Both are just the model, applied.

## Consequence 1 — the blanks flip

A blank means "the obvious thing **for the direction I'm walking**." Walking left, the obvious beginning is the *right* end, and falling off the edge means falling off the *left* edge.

| | blank **start** = | blank **end** = |
|---|---|---|
| step **positive** (walking right) | stand on the **first** item | fall off the **right** edge |
| step **negative** (walking left) | stand on the **last** item | fall off the **left** edge |

So `start` is never "the smaller number." It's **where you stand.** Direction decides which is bigger.

## Consequence 2 — the sign must be in front of you

Walking left, you can only reach a stop sign that is **to your left**. A sign on your right is behind your back and you'll never reach it — you just walk off the edge... except Python doesn't even let you start. It hands you `[]`.

> ### The one rule for backward slices: **`start` must be to the RIGHT of `end`.**

Now the walks.

## 4.1 `xs[::-1]` — the famous reverse

No start → stand on the last item. No sign → walk till you fall off the **left** edge.

```
        edge |  0     1     2     3     4     5     6
  item       |  a     b     c     d     e     f     g
  walk  fell |TAKE  TAKE  TAKE  TAKE  TAKE  TAKE  TAKE       ←── walking left
        off  |                                    STAND
```

Read the walk **right to left**, because that's the order you picked things up in.

```python
→ ['g', 'f', 'e', 'd', 'c', 'b', 'a']
```

## 4.2 `xs[::-2]` — backwards, every second

Stand on the last item, footstep of 2 to the left.

```
        edge |  0     1     2     3     4     5     6
  item       |  a     b     c     d     e     f     g
  walk  fell |TAKE  skip  TAKE  skip  TAKE  skip  TAKE       ←── walking left
        off  |                                    STAND
```

```python
→ ['g', 'e', 'c', 'a']
```

## 4.3 `xs[5:2:-1]` — both numbers given

Stand at 5, walk left, sign at 2. The sign is to your left, so this works.

```
  idx   0     1     2     3     4     5     6
  item  a     b     c     d     e     f     g
  walk              STOP  TAKE  TAKE  TAKE                   ←── walking left
                                      STAND
```

Take `f`, step left to 4, take `e`, step to 3, take `d`, step to 2 — sign. Done.

```python
→ ['f', 'e', 'd']
```

## 4.4 `xs[-1:-4:-1]` — same walk, nicknames

`-1` → 6, `-4` → 3. Stand at 6, sign at 3, walking left.

```
  idx   0     1     2     3     4     5     6
  item  a     b     c     d     e     f     g
  walk                    STOP  TAKE  TAKE  TAKE             ←── walking left
                                            STAND
```

```python
→ ['g', 'f', 'e']
```

## 4.5 `xs[3::-1]` — backwards to the very beginning

Stand at 3. No sign, so you fall off the left edge — which means you *do* pick up item `a` on the way out.

```
        edge |  0     1     2     3     4     5     6
  item       |  a     b     c     d     e     f     g
  walk  fell |TAKE  TAKE  TAKE  TAKE                         ←── walking left
        off  |                  STAND
```

```python
→ ['d', 'c', 'b', 'a']
```

## 4.6 `xs[3:0:-1]` — the "where did `a` go?" moment

Same as 4.5, but this time you planted a sign at 0.

```
  idx   0     1     2     3     4     5     6
  item  a     b     c     d     e     f     g
  walk  STOP  TAKE  TAKE  TAKE                               ←── walking left
                          STAND
```

```python
→ ['d', 'c', 'b']       # 'a' is missing!
```

Of course it's missing. **You never pick up the stop sign**, and you planted the sign right on top of `a`.

So how do you say "walk left all the way, *including* the first item"? You'd need a sign one place further left than 0 — and no such position exists. You can't write it. Don't try.

> ### **Walking left, you can never name a stop sign past the front. Leave `end` blank instead.**

```python
xs[3::-1]       # ['d', 'c', 'b', 'a']   ✓  — this is the answer
xs[3:None:-1]   # identical, if you need to pass it as a value
```

`None` is literally the value that means "this slot is blank." Useful when you're building a slice from variables.

## 4.7 `xs[0:3:-1]` — the empty backward slice

Stand at 0, facing left. Sign at 3 — to your **right**, behind your back.

```
  idx   0     1     2     3     4     5     6
  item  a     b     c     d     e     f     g
  walk  STAND             STOP                               ←── you're facing left
        ←── this way is off the edge; the sign is the other way
```

You can never reach that sign.

```python
→ []
```

**This is the single most common backward-slicing bug in Python**, and it's always the same fix: the two numbers are in the wrong order for your direction. Swap them.

## 4.8 `xs[4:0:-2]` — backwards with a bigger step

Stand at 4, footsteps of 2 to the left, sign at 0.

```
  idx   0     1     2     3     4     5     6
  item  a     b     c     d     e     f     g
  walk  STOP  skip  TAKE  skip  TAKE                         ←── walking left
                                STAND
```

```python
→ ['e', 'c']            # 'a' excluded — the sign sits on it
```

## 4.9 `xs[-2::-2]` — nickname, backwards, stepping

`-2` → 5. Stand at 5, step 2 left, no sign.

```
        edge |  0     1     2     3     4     5     6
  item       |  a     b     c     d     e     f     g
  walk  fell |skip  TAKE  skip  TAKE  skip  TAKE             ←── walking left
        off  |                              STAND
```

```python
→ ['f', 'd', 'b']
```

## 4.10 The escape hatch: don't be clever

There is zero shame in this:

```python
xs[2:6][::-1]      # ['f', 'e', 'd', 'c']
xs[-3:][::-1]      # ['g', 'f', 'e']
```

**Grab the chunk going forward, then reverse it.** Two easy moves instead of one clever move you'll have to re-derive later. Use a single backward slice when it reads clearly; use this whenever the numbers start making you squint. It's correct on the first try, every time.

---

# Part 5 — The whole thing on one page

Every variant, with the model spelled out. All results are real Python output.

```python
xs = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
```

## Walking right (step is positive)

| Slice | Stand at | Step | Stop sign at | Result |
|---|---|---|---|---|
| `xs[2:5]` | 2 | +1 | 5 | `['c','d','e']` |
| `xs[2:]` | 2 | +1 | — (edge) | `['c','d','e','f','g']` |
| `xs[:5]` | 0 (start) | +1 | 5 | `['a','b','c','d','e']` |
| `xs[:]` | 0 (start) | +1 | — (edge) | whole list, copied |
| `xs[2:5:2]` | 2 | +2 | 5 | `['c','e']` |
| `xs[::2]` | 0 (start) | +2 | — (edge) | `['a','c','e','g']` |
| `xs[1::2]` | 1 | +2 | — (edge) | `['b','d','f']` |
| `xs[:5:2]` | 0 (start) | +2 | 5 | `['a','c','e']` |
| `xs[1:6:3]` | 1 | +3 | 6 | `['b','e']` |
| `xs[-3:]` | 4 | +1 | — (edge) | `['e','f','g']` |
| `xs[:-3]` | 0 (start) | +1 | 4 | `['a','b','c','d']` |
| `xs[-4:-1]` | 3 | +1 | 6 | `['d','e','f']` |
| `xs[2:-2]` | 2 | +1 | 5 | `['c','d','e']` |
| `xs[-5:5]` | 2 | +1 | 5 | `['c','d','e']` |
| `xs[-6::2]` | 1 | +2 | — (edge) | `['b','d','f']` |
| `xs[5:2]` | 5 | +1 | 2 — **behind you** | `[]` |
| `xs[2:2]` | 2 | +1 | 2 — **you're on it** | `[]` |
| `xs[-3:-5]` | 4 | +1 | 2 — **behind you** | `[]` |
| `xs[2:-0]` | 2 | +1 | 0 — **`-0` is `0`** | `[]` |
| `xs[3:100]` | 3 | +1 | off the map → edge | `['d','e','f','g']` |
| `xs[10:20]` | off the map | +1 | — | `[]` |

## Walking left (step is negative)

| Slice | Stand at | Step | Stop sign at | Result |
|---|---|---|---|---|
| `xs[::-1]` | 6 (last) | −1 | — (left edge) | `['g','f','e','d','c','b','a']` |
| `xs[::-2]` | 6 (last) | −2 | — (left edge) | `['g','e','c','a']` |
| `xs[5:2:-1]` | 5 | −1 | 2 | `['f','e','d']` |
| `xs[6:3:-1]` | 6 | −1 | 3 | `['g','f','e']` |
| `xs[-1:-4:-1]` | 6 | −1 | 3 | `['g','f','e']` |
| `xs[:3:-1]` | 6 (last) | −1 | 3 | `['g','f','e']` |
| `xs[3::-1]` | 3 | −1 | — (left edge) | `['d','c','b','a']` |
| `xs[3:0:-1]` | 3 | −1 | 0 — **`a` excluded** | `['d','c','b']` |
| `xs[2::-1]` | 2 | −1 | — (left edge) | `['c','b','a']` |
| `xs[-3::-1]` | 4 | −1 | — (left edge) | `['e','d','c','b','a']` |
| `xs[4:0:-2]` | 4 | −2 | 0 | `['e','c']` |
| `xs[5::-2]` | 5 | −2 | — (left edge) | `['f','d','b']` |
| `xs[-2::-2]` | 5 | −2 | — (left edge) | `['f','d','b']` |
| `xs[0:3:-1]` | 0 | −1 | 3 — **behind you** | `[]` |
| `xs[2:6][::-1]` | two easy steps | | | `['f','e','d','c']` |

---

# Part 6 — When it surprises you, ask three questions

1. **"Where am I standing, which way am I facing, and where's the sign?"** Say it out loud with your actual numbers. Nine times out of ten the mistake becomes obvious mid-sentence.
2. **Got `[]`?** The sign is behind you. Walking right needs the sign to the right; walking left needs it to the left. Swap your two numbers.
3. **An item missing at the far end?** You planted the sign on top of it. Push the sign one further — or, if it's the front item on a backward walk, **delete the `end` entirely.**

And if any negative numbers are involved: **translate them to real positions first** (`-k` → `len - k`), *then* ask the three questions. Negatives are nicknames, not new rules.

---

# Part 7 — Real tasks, using all of it

```python
n = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
s = "hello world"

# --- taking pieces ---
n[:3]                   # [10, 20, 30]          first three
n[-3:]                  # [80, 90, 100]         last three
n[:-3]                  # [10 ... 70]           all but the last three
n[1:-1]                 # [20 ... 90]           drop first and last
s[:5], s[6:]            # ('hello', 'world')

# --- splitting ---
mid = len(n) // 2
n[:mid], n[mid:]        # two halves, nothing lost or doubled

[n[i:i+3] for i in range(0, len(n), 3)]
# [[10,20,30], [40,50,60], [70,80,90], [100]]   fixed-size chunks

# --- alternating ---
flat = ['a', 1, 'b', 2, 'c', 3]
flat[::2]               # ['a', 'b', 'c']       phase 0
flat[1::2]              # [1, 2, 3]             phase 1
dict(zip(flat[::2], flat[1::2]))    # {'a': 1, 'b': 2, 'c': 3}

# --- backwards ---
s[::-1]                 # 'dlrow olleh'
s == s[::-1]            # palindrome check
n[::-2]                 # [100, 80, 60, 40, 20]
n[7:2:-2]               # [80, 60, 40]
n[-3:][::-1]            # [100, 90, 80]         last three, reversed (the easy way)

# --- rotating ---
k = 3
n[k:] + n[:k]           # [40 ... 100, 10, 20, 30]

# --- neighbours, without index arithmetic ---
list(zip(n, n[1:]))     # [(10,20), (20,30), (30,40), ...]

# --- safety and copies ---
[1][:3]                 # [1]    no error, no length check needed
backup = n[:]           # a copy you can mutate freely
```

---

# Appendix — three facts worth knowing later

**What you can slice.** Anything ordered with a known length: lists, strings, tuples, `range`, `bytes`. Strings give back strings, tuples give back tuples. What you *can't* slice: sets, dicts, generators — no fixed order or no known end. For a lazy iterator use `itertools.islice(it, start, stop, step)`, which refuses negative numbers, because a stream doesn't know where its end is.

**Slices copy.** `n[:]` builds a new list holding the same items. Cheap for small lists, real work for big ones.

**Slices can appear on the left of `=`, and can be deleted.**

```python
y = [0, 1, 2, 3, 4, 5]
y[1:3] = ['x', 'y', 'z']     # [0, 'x', 'y', 'z', 3, 4, 5]  lengths need not match

w = [0, 1, 2, 3, 4, 5]
w[::2] = ['a', 'b', 'c']     # ['a', 1, 'b', 3, 'c', 5]     counts MUST match here

z = [0, 1, 2, 3, 4, 5]
del z[::2]                   # [1, 3, 5]
```

---

# The one thing to remember

> ## **Stand at `start`. Take a step of `step`. Stop when you reach `end` — and never pick up the sign.**
>
> **Blank means "the obvious thing for the way I'm facing." Negative numbers are just nicknames for positions counted from the right.**

That sentence is the entire feature. Say it out loud with your real numbers and the answer falls out.

And on the days a backward slice makes you squint: **grab it forward, then reverse it.** Clear beats clever.

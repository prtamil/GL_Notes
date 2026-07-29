# Sequence Processing

Sequence processing means taking an ordered pile of values and doing something useful with it: answering a question, rearranging it, or building something new out of it.

The shift here is to stop thinking in loops, indices and mutable variables, and start thinking in **verbs**. Each verb is one thing your brain already does when you work with information.

Python hands you comprehensions, built-ins, and the `itertools` / `collections` / `functools` modules. Those are just tools. What you actually want is a vocabulary of sequence verbs that travels with you to any language.

Once the verbs feel automatic, array problems stop reading like iteration instructions and start reading like descriptions of a transformation.

---

# Cognitive Verbs → Python

| Thinking Verb  | Mental Question                                       | Common Python                                                              |
| -------------- | ----------------------------------------------------- | -------------------------------------------------------------------------- |
| **Generate**   | Where does the sequence come from?                    | `range`, `itertools.repeat`, `cycle`, `count`, generator functions          |
| **Observe**    | What is true about the sequence?                       | `len`, `xs[0]`, `xs[-1]`, `any`, `all`, `min`, `max`, `Counter`             |
| **Search**     | Where is what I'm looking for?                        | `next((x for x in xs if p(x)), None)`, `index`, `enumerate`, `bisect`       |
| **Select**     | What should I keep?                                   | `[x for x in xs if p(x)]`, `filter`, `takewhile`, `islice`                  |
| **Reject**     | What should I discard?                                | `[x for x in xs if not p(x)]`, `filterfalse`, `dropwhile`, `xs[n:]`         |
| **Transform**  | How does each element change?                         | `[f(x) for x in xs]`, `map`, `enumerate`                                    |
| **Arrange**    | How should the data be organized?                     | `sorted`, `reversed`, `xs[::-1]`, `random.shuffle`                          |
| **Slice**      | Which part do I need?                                 | `xs[a:b]`, `islice`, `takewhile`, `dropwhile`                               |
| **Split**      | How do I divide the sequence?                         | `xs[:n], xs[n:]`, `batched`, `groupby`, `str.split`                         |
| **Join**       | How do I bring sequences together?                    | `chain`, `+`, `extend`, `dict \| dict`, `str.join`                          |
| **Pair**       | Which elements correspond?                            | `zip`, `dict(zip(k, v))`, `pairwise`, `product`                             |
| **Expand**     | How can one become many?                              | `[y for x in xs for y in f(x)]`, `chain.from_iterable`, `repeat`            |
| **Compress**   | How can I make it smaller?                            | `dict.fromkeys`, `set`, `groupby`                                           |
| **Group**      | Which items belong together?                          | `defaultdict(list)`, `Counter`, `groupby(sorted(...))`                      |
| **Order**      | In what sequence should I process things?             | `sorted`, `reversed`, `heapq`                                               |
| **Scan**       | What is true after each step?                         | `itertools.accumulate`                                                      |
| **Accumulate** | How do I build the final result?                      | `sum`, `functools.reduce`, `"".join`, `dict` building                        |
| **Compare**    | How are these sequences related?                      | `==`, `<`, `set` operations, `difflib`                                      |
| **Classify**   | Into which category does each item belong?            | `map` with a labelling function, `defaultdict(list)`, `bisect`              |
| **Summarize**  | What is the final answer?                             | `len`, `sum`, `min`, `max`, `statistics`, `Counter.most_common`             |
| **Window**     | Which neighboring elements should I examine together? | `pairwise`, `batched`, `zip(xs, xs[1:])`, `deque(maxlen=n)`                 |

---

## The three Python facts that shape all of this

**1. Reach for a comprehension first.** `[f(x) for x in xs if p(x)]` handles Transform, Select and Reject in a single form. Read it *for → if → f*, not left to right. `map` and `filter` are still around, but they only beat a comprehension when you already have a named function to hand them.

**2. You choose lazy or eager on every line.** A comprehension builds a list right away. A generator expression builds nothing until something consumes it. `itertools` is lazy all the way through, and most of what it returns is a **one-shot iterator**: read it twice and the second read comes back empty without complaining. Call `list()` at the moment you need to hold onto something.

**3. The right little data structure deletes whole piles of code.** `Counter` kills your manual histogram loop. `defaultdict(list)` kills the grouping loop. `deque(maxlen=n)` kills the ring-buffer bookkeeping. `bisect` kills the linear scan over sorted data. Spotting which structure a verb is asking for is most of the job.

---

## One small refinement

### **Scan** vs **Accumulate** vs **Summarize**

They sound like the same thing. They aren't.

- **Scan** → _Show me every intermediate state._
    - Python: `itertools.accumulate`

- **Accumulate** → _Build up a result one step at a time._
    - Python: `functools.reduce`, or an explicit loop with a running variable

- **Summarize** → _Extract the final insight or answer._
    - Python: `sum`, `len`, `min`, `max`, `statistics.mean`, `Counter.most_common`

For example:

```text
Sales

100 200 150 300

Scan          list(accumulate(sales))
────────────
100
300
450
750

Accumulate    reduce(add, sales)
────────────
(total is built internally)

Summarize     sum(sales)
────────────
750
```

There's a naming collision here worth pinning down. Python's **`accumulate`** does the **Scan** verb, and Python's **`reduce`** does the **Accumulate** verb. The library named them after how they work; the verbs name them after what you meant.

That split matches how you actually think about a problem. Sometimes you want to **watch the process** (Scan), sometimes you want to **run the process** (Accumulate), and sometimes you only care about **the answer** (Summarize).

None of this vocabulary is Python-specific, even though it maps cleanly onto Python's standard library. The same mental models carry straight over to Clojure, Java Streams, JavaScript arrays, SQL, Spark, Rust iterators, or whatever you pick up next.

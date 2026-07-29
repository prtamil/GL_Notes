# Sequence Processing

Sequence processing is the art of taking an ordered collection of values and answering questions about it, reorganizing it, or producing a new collection.

Instead of thinking in terms of loops, indices, and mutable variables, we think in terms of **verbs**. Each verb represents a single cognitive action that we naturally perform when working with information.

Python provides comprehensions, built-ins, and the `itertools` / `collections` / `functools` modules, but these are merely **tools**. The real goal is to develop a vocabulary of sequence-processing verbs that can be applied regardless of programming language.

Once these verbs become second nature, array problems become descriptions of transformations rather than instructions for iteration.

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

**1. The comprehension is the default.** `[f(x) for x in xs if p(x)]` covers Transform, Select, and Reject in one form — and it reads *for → if → f*, not left to right. `map` and `filter` exist, but they only win when you already have a named function.

**2. Lazy or eager is a choice you make on every line.** A comprehension builds a list; a generator expression builds nothing until you consume it. `itertools` is entirely lazy, and most of its outputs are **one-shot iterators** — consume them twice and the second read is empty, with no error. `list()` at the point where you need to keep something.

**3. Small, sharp data structures replace whole categories of code.** `Counter` replaces manual histogram loops, `defaultdict(list)` replaces grouping loops, `deque(maxlen=n)` replaces ring-buffer bookkeeping, `bisect` replaces linear scans on sorted data. Recognizing which structure a verb wants is most of the work.

---

## One small refinement

### **Scan** vs **Accumulate** vs **Summarize**

These three sound similar, but they represent different ways of thinking.

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

Note the naming collision worth keeping straight: Python's function called **`accumulate`** implements the **Scan** verb, and Python's function called **`reduce`** implements the **Accumulate** verb. The library named them after mechanics; the verbs name them after intent.

This distinction mirrors how humans think: we may want to **watch the process** (Scan), **perform the process** (Accumulate), or **know only the conclusion** (Summarize).

This cognitive vocabulary stays independent of Python while mapping naturally onto its standard library, making it easy to transfer the same mental models to Clojure, Java Streams, JavaScript arrays, SQL, Spark, Rust iterators, or any other data-processing framework.

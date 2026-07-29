

# Sequence Processing

Sequence processing is the art of taking an ordered collection of values and answering questions about it, reorganizing it, or producing a new collection.

Instead of thinking in terms of loops, indices, and mutable variables, we think in terms of **verbs**. Each verb represents a single cognitive action that we naturally perform when working with information.

Clojure provides a rich set of sequence functions, but these functions are merely **tools**. The real goal is to develop a vocabulary of sequence-processing verbs that can be applied regardless of programming language.


Once these verbs become second nature, array problems become descriptions of transformations rather than instructions for iteration.

---

# Cognitive Verbs → Clojure

| Thinking Verb  | Mental Question                                       | Common Clojure Functions                                                |
| -------------- | ----------------------------------------------------- | ----------------------------------------------------------------------- |
| **Generate**   | Where does the sequence come from?                    | `range`, `repeat`, `cycle`, `iterate`, `repeatedly`                     |
| **Observe**    | What is true about the sequence?                      | `count`, `first`, `last`, `some`, `every?`, `frequencies`, `min`, `max` |
| **Search**     | Where is what I'm looking for?                        | `some`, `filter`, `keep-indexed`                                        |
| **Select**     | What should I keep?                                   | `filter`, `keep`                                                        |
| **Reject**     | What should I discard?                                | `remove`                                                                |
| **Transform**  | How does each element change?                         | `map`, `map-indexed`, `replace`                                         |
| **Arrange**    | How should the data be organized?                     | `sort`, `sort-by`, `reverse`, `shuffle`                                 |
| **Slice**      | Which part do I need?                                 | `take`, `drop`, `split-at`, `take-while`, `drop-while`, `subvec`        |
| **Split**      | How do I divide the sequence?                         | `split-with`, `partition-by`, `partition`                               |
| **Join**       | How do I bring sequences together?                    | `concat`, `into`, `merge`, `interleave`                                 |
| **Pair**       | Which elements correspond?                            | `map`, `zipmap`, `interleave`                                           |
| **Expand**     | How can one become many?                              | `mapcat`, `repeat`                                                      |
| **Compress**   | How can I make it smaller?                            | `distinct`, `dedupe`, `partition-by`                                    |
| **Group**      | Which items belong together?                          | `group-by`, `frequencies`                                               |
| **Order**      | In what sequence should I process things?             | `sort`, `sort-by`, `reverse`                                            |
| **Scan**       | What is true after each step?                         | `reductions`                                                            |
| **Accumulate** | How do I build the final result?                      | `reduce`, `into`, `merge-with`                                          |
| **Compare**    | How are these sequences related?                      | `=`, `compare`, custom predicates                                       |
| **Classify**   | Into which category does each item belong?            | `group-by`, `partition-by`                                              |
| **Summarize**  | What is the final answer?                             | `reduce`, `count`, `frequencies`, `min`, `max`, `apply`                 |
| **Window**     | Which neighboring elements should I examine together? | `partition`, `partition-all`, `partition-by`                            |

---

## One small suggestion

I would make one tiny refinement that clarifies the mental model:

### **Scan** vs **Accumulate** vs **Summarize**

These three sound similar, but they represent different ways of thinking.

- **Scan** → _Show me every intermediate state._
    
    - Clojure: `reductions`
        
- **Accumulate** → _Build up a result one step at a time._
    
    - Clojure: `reduce`
        
- **Summarize** → _Extract the final insight or answer._
    
    - Clojure: often `reduce`, but also specialized functions like `count`, `min`, `max`, `frequencies`, or `apply`.
        

For example:

```text
Sales

100 200 150 300

Scan
────────────
100
300
450
750

Accumulate
────────────
(total is built internally)

Summarize
────────────
750
```

This distinction mirrors how humans think: we may want to **watch the process** (Scan), **perform the process** (Accumulate), or **know only the conclusion** (Summarize).

I think this cognitive vocabulary is an excellent foundation. It stays independent of Clojure while mapping naturally to its sequence library, making it easier to transfer the same mental models to Python, Java Streams, JavaScript arrays, SQL, Spark, Rust iterators, or any other data-processing framework.
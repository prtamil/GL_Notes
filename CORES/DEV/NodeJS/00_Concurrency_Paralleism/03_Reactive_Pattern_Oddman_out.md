# Why Reactive / Dataflow Is the Odd One Out Among Concurrency Models

When discussing concurrency and I/O systems, four models consistently appear as complete solutions:

1. Event-driven, non-blocking I/O
2. Communicating Sequential Processes (CSP)
3. Actor model
4. Thread-per-request blocking model
    

Each of these defines a **full execution strategy**: how work is scheduled, how I/O is performed, how blocking behaves, and how failures are handled.

Reactive / Dataflow systems stand apart.  
They solve an important problem — but they do not solve _the same class of problems_ as the other four.

---

## 1. What the four models have in common

The first four models answer the same foundational questions:

- **Who runs code?** (scheduler)
- **What blocks, and what doesn’t?**
- **How does the system wait for I/O?**
- **How many execution units can exist?**
- **What happens when something fails?**
    

They are **horizontal system models**.  
They define how _all_ computation in a system executes.

Reactive / Dataflow does not.

---

## 2. What Reactive / Dataflow actually models

Reactive systems model **data movement**, not execution.

Their core question is:

> _How does data flow through a processing graph, and how is demand communicated upstream?_

They focus on:

- Stream composition
- Transformation pipelines
- Explicit backpressure
- Deterministic propagation
    

They intentionally avoid answering:

- How threads are scheduled
- How I/O readiness is detected
- How CPU time is allocated
- How failures affect unrelated work
    

Those concerns are delegated to an underlying runtime.

---

## 3. Why reactive systems cannot stand alone

A reactive pipeline still needs:

- A scheduler to run operators
- An I/O mechanism to produce data
- A memory model to store buffers
- A failure model for crashes
    

Reactive frameworks therefore **embed themselves inside**:

- Event loops (Node, Netty)
- Thread pools (JVM, .NET)
- Actor systems (Akka)
    

They do not replace these systems — they _assume_ them.

---

## 4. Execution vs flow: the fundamental mismatch

The four core models are **execution-centric**:

- Event-driven → schedules callbacks
- CSP → schedules goroutines
- Actor → schedules processes
- Threads → schedules OS threads
    

Reactive systems are **flow-centric**:

- Operators react to incoming data
- Execution is incidental, not central
- Control flow is implicit in the graph
    

This makes reactive excellent at **pipelines**, but poor as a general-purpose execution model.

---

## 5. Backpressure is not enough

Reactive systems are often associated with backpressure, but:

> **Backpressure alone does not define a concurrency model.**

Node, Go, and Erlang already have backpressure mechanisms rooted in their execution models.  
Reactive systems simply make backpressure _explicit and formal_ — they do not define _how the system runs_.

---

## 6. Why reactive feels “incomplete” in practice

In real systems, reactive frameworks:

- Handle specific data paths
- Are applied selectively
- Require escape hatches to imperative code
- Struggle with CPU-heavy or stateful logic
    

This is not a flaw — it’s a design boundary.

Reactive systems are **tools**, not **foundations**.

---

## 7. The key architectural insight

> **The other four models describe _how the system executes_.  
> Reactive/Dataflow describes _how data moves_.**

That is why it feels like an odd one out.

It solves a different layer of the problem.

---

## 8. Conclusion

Reactive / Dataflow belongs in the list of fundamental models because it introduces a **distinct and powerful idea**: demand-driven data flow.

But it does not belong in the same category as event-driven, CSP, actor, or thread-based models because it is not a complete execution framework.

It is a **vertical abstraction**, not a horizontal one.

Understanding this distinction prevents misuse — and reveals why reactive frameworks always live _on top of_ Node, Go, Erlang, or the JVM, rather than replacing them.
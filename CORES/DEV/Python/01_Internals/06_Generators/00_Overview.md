# Python Generators — Complete Technical Recap

_A senior-level reference: mechanics, memory model, variable scoping, and the full coroutine protocol._

---

## Part I — The Foundational Fact

Everything about generators follows from one structural difference.

A normal function's **frame** — its local variable array, value stack, instruction pointer, and exception state — is allocated when the function is called, lives on the interpreter's call stack, and is **destroyed on return**. That destruction is why a function cannot "pause."

A generator's frame is **owned by the generator object**. It is detached from the call stack and lives as long as the generator object does. Suspension is therefore not magic: it is simply _returning control to the caller without unwinding or freeing the frame_.

Every other property — resumability, per-instance state, `send`, `throw`, `yield from`, and ultimately `async`/`await` — is a consequence of this.

### Compile-time detection

Generator-ness is a **static property of the code object**, decided by the compiler, not by runtime behavior. If the token `yield` or `yield from` appears anywhere in a function body, the compiler sets the `CO_GENERATOR` flag (`0x20`) on the code object.

```python
import dis

def f(path):
    print("opening")          # side effect
    assert path, "path req"   # validation
    yield 1

g = f("")                     # nothing printed, no AssertionError
f.__code__.co_flags & 0x20    # 32 → generator function
```

**Calling the function never executes the body.** It allocates a generator object and returns immediately.

**The practical consequence** (a common interview probe): eager argument validation and eager side effects are silently deferred until the first `next()`. If a caller creates the generator and never iterates, your `assert` never runs and your file never opens. The standard fix is to split the function:

```python
def read_records(path):
    if not path:                      # runs eagerly
        raise ValueError("path required")
    fh = open(path)                   # acquired eagerly
    return _read_records(fh)          # plain return of a generator

def _read_records(fh):
    with fh:
        for line in fh:
            yield parse(line)
```

Related flags in the same family:

|Flag|Value|Meaning|
|---|---|---|
|`CO_GENERATOR`|`0x20`|contains `yield`|
|`CO_COROUTINE`|`0x80`|`async def`|
|`CO_ITERABLE_COROUTINE`|`0x100`|generator marked by `@types.coroutine`|
|`CO_ASYNC_GENERATOR`|`0x200`|`async def` containing `yield`|

A coroutine is _the same object machinery with a different flag_. This is not an analogy — it is the implementation.

---

## Part II — Anatomy of the Generator Object

```python
g.gi_frame          # the suspended frame; None once exhausted
g.gi_code           # the code object (shared across all instances)
g.gi_running        # True only while executing — reentrancy guard
g.gi_yieldfrom      # the delegate, if suspended inside `yield from`
g.gi_frame.f_lasti  # instruction pointer — the bookmark
g.gi_frame.f_back   # None while suspended; linked to the resumer while running
g.gi_frame.f_locals # the live locals (see Part IV)
```

`inspect.getgeneratorstate(g)` returns one of `GEN_CREATED`, `GEN_RUNNING`, `GEN_SUSPENDED`, `GEN_CLOSED`.

Two details worth carrying into an interview:

**`gi_frame` becomes `None` on exhaustion.** This is the observable signal that the frame has been released. It is also why `send()` on an exhausted generator raises `StopIteration` immediately rather than re-running anything.

**`f_back` is `None` while suspended.** A suspended frame is not on any call stack, so it has no caller. `f_back` is wired up only at resume time, pointing at _whoever resumed it_. This means a generator's traceback shows a different caller on different resumes — a real source of confusion when debugging pipelines, because the stack you see is the stack of the consumer, not of the code that created the generator.

**Layout note (CPython 3.11+):** the frame is embedded _inside_ the generator object (`_PyInterpreterFrame` inline) rather than being a separately heap-allocated `PyFrameObject`. Generator creation is therefore a single allocation and quite cheap. A full `PyFrameObject` is materialized lazily only if something actually touches `gi_frame`.

---

## Part III — What `yield` Actually Compiles To

The `YIELD_VALUE` opcode does three things:

1. Pops the top of the value stack — that object becomes the yielded value.
2. Leaves `f_lasti` pointing at the _next_ instruction.
3. Returns control to the caller **without unwinding the frame**.

On resume, execution restarts at that saved offset, and **the value passed in is pushed onto the value stack**.

That last point is the whole reason `yield` is an **expression** rather than a statement:

```python
received = yield "ready"
```

Schematic disassembly (3.11+; exact opcodes drift between versions, the shape does not):

```
RETURN_GENERATOR      # executes at CALL time: builds gen, returns it
POP_TOP
RESUME 0              # ← body actually starts here, on the first next()
LOAD_CONST 'ready'
YIELD_VALUE           # suspend; 'ready' goes to the caller
RESUME 1              # ← re-entry point; the sent value is now on the stack
STORE_FAST received
```

Read that carefully and two facts become obvious:

- A **freshly created generator is suspended before `RESUME 0`** — before the first line of the body. It is _not_ suspended at a `yield`.
- The sent value is materialized by the resume itself. There is nowhere to put a value if you are not paused at a `yield`.

Both explain the priming rule in Part V.

---

## Part IV — Local Variables and Closure Variables

This is where generators stop being "lazy lists" and become a state-machine primitive, and it is the part most candidates cannot explain.

### 4.1 Fast locals

Local variables live in a **fixed-size array** on the frame (`localsplus`), sized at compile time from `co_nlocals`. `LOAD_FAST` / `STORE_FAST` index into it by integer offset — no dictionary lookup, no hashing.

Because the generator owns the frame, **that array persists across suspensions**. This is the concrete mechanism behind the slogan _"the resumption point is the state"_:

```python
def parser():
    header = None          # slot 0
    buf = bytearray()      # slot 1
    count = 0              # slot 2
    while True:
        chunk = yield      # slot 3
        buf += chunk
        count += 1
```

`header`, `buf`, `count`, and `chunk` all survive every suspension. There is no `self.state = AWAITING_HEADER`, no explicit state enum, no state object. The instruction pointer _is_ the state variable, and the fast-locals array _is_ the state struct.

Three consequences:

**Locals are strictly per-instance.** Each call to the generator function allocates a brand-new frame with a brand-new locals array:

```python
def counter():
    n = 0
    while True:
        n += 1
        yield n

a, b = counter(), counter()
next(a)   # 1
next(b)   # 1   ← independent frames, independent `n`
```

**Locals pin objects in memory.** A suspended generator holds strong references to everything in its locals. A generator paused mid-iteration over a 2 GB buffer keeps that buffer alive until the generator is collected or closed. Abandoned generators are a genuine memory-retention vector, and because generators participate in cyclic GC, reclamation can be deferred (see `close()` in Part VI).

**The local set is immutable in shape.** `co_varnames` and `co_nlocals` are fixed at compile time. You cannot add a local to a live generator frame.

### 4.2 `f_locals` — the write-through change (PEP 667)

You can inspect a suspended generator's locals:

```python
g = parser()
next(g)
g.gi_frame.f_locals          # {'header': None, 'buf': bytearray(b''), ...}
```

**Before Python 3.13**, `f_locals` on an optimized (function) frame returned a _snapshot dictionary_, rebuilt from the fast-locals array on each access. Writing to it did **nothing** — the value was silently discarded because there was no write-back:

```python
g.gi_frame.f_locals['count'] = 999   # ≤3.12: silently ignored
```

**Python 3.13 (PEP 667)** changed `f_locals` on optimized frames to return a `FrameLocalsProxy` — a write-through view. Mutations now propagate to the real fast-locals array. This makes debugger-style injection into a live suspended generator actually work, and it removes a long-standing footgun where `sys.settrace` handlers appeared to modify locals but did not.

This is an excellent "do you actually read changelogs" question.

### 4.3 Closure variables: cells

Free variables are a **completely different storage class**, and the distinction matters enormously for generators.

A closed-over variable lives in a **`PyCellObject`** — a one-slot mutable box. Cells are stored in the same `localsplus` array _after_ the locals region (`co_cellvars` then `co_freevars`), but they are accessed with `LOAD_DEREF` / `STORE_DEREF`, which dereference through the cell.

The critical property: **the cell is shared**. The generator's frame does not own it; it holds a reference to a cell that also lives in the enclosing function's frame and in the function object's `__closure__` tuple.

```python
def factory():
    count = 0                     # becomes a CELL (captured by nonlocal)
    def gen():
        nonlocal count
        while True:
            count += 1
            yield count
    return gen

f = factory()
a, b = f(), f()               # two generators, ONE shared cell
next(a)   # 1
next(b)   # 2   ← b sees a's mutation
next(a)   # 3
```

Compare directly against the local-variable version in §4.1, which printed `1` and `1`.

**The rule to memorize:**

||Storage|Opcodes|Sharing|
|---|---|---|---|
|**Local**|fast-locals slot on the frame|`LOAD_FAST` / `STORE_FAST`|private per generator instance|
|**Closure (free/cell)**|`PyCellObject`, shared|`LOAD_DEREF` / `STORE_DEREF`|shared across all closures over the same enclosing frame|
|**Global**|module `__dict__`|`LOAD_GLOBAL` / `STORE_GLOBAL`|fully shared, resolved at access time|

> **Locals give you isolated per-instance state. Cells give you shared mutable state. Globals give you late-bound shared state.** Choosing wrongly between them is the root of most "why do my generators interfere with each other" bugs.

### 4.4 Late binding × laziness — the compound trap

Closures in Python bind **names, not values**, resolved at execution time. Generators defer execution. Combine the two and you get a bug that neither mechanism produces alone:

```python
gens = [(i * x for x in range(3)) for i in range(3)]
[list(g) for g in gens]
# [[0, 2, 4], [0, 2, 4], [0, 2, 4]]
```

`i` is a single local of the list comprehension's scope, captured by one shared cell. All three genexps reference that cell. By the time any of them runs, the comprehension has finished and `i == 2`. Every generator multiplies by 2.

Fix by forcing an eager binding into a **fresh local slot** via a default argument:

```python
gens = [(lambda k=i: (k * x for x in range(3)))() for i in range(3)]
# [[0,0,0], [0,1,2], [0,2,4]]
```

The default argument is evaluated at definition time and stored in a _local_, not a cell.

### 4.5 Generator expressions: the eager/lazy split

`(expr for x in iterable)` desugars to an implicit generator function taking one implicit parameter named `.0`. The **outermost iterable is evaluated eagerly** at creation and bound to `.0`; **everything else is lazy**.

```python
gen = (x for x in undefined_name)      # NameError raised IMMEDIATELY
gen = (undefined_name for x in [1])    # fine until next(gen)
```

The eager evaluation binds the _object_, not the _name_:

```python
data = [1, 2, 3]
gen = (x * 2 for x in data)
data = [10, 20]        # REBINDING — no effect, old list is captured in `.0`
list(gen)              # [2, 4, 6]

data = [1, 2, 3]
gen = (x * 2 for x in data)
data.clear()           # MUTATION — the captured object changes under you
list(gen)              # []
```

**PEP 709 (Python 3.12)** inlined list/dict/set comprehensions into the enclosing frame — they no longer create a function call. **Generator expressions were deliberately excluded**, because they genuinely need a persistent independent frame. So in 3.12+, comprehensions and genexps have materially different scoping machinery.

Also note: `yield` inside a comprehension has been a `SyntaxError` since Python 3.8.

---

## Part V — `next()` vs `send()`

### 5.1 They are one primitive

```c
/* Objects/genobject.c, simplified */
gen_iternext(gen)     -> gen_send_ex(gen, NULL, 0, 0);   /* next()   */
gen_send(gen, arg)    -> gen_send_ex(gen, arg,  0, 0);   /* send(v)  */
gen_throw(gen, exc)   -> resumes with exception set, no value pushed
gen_close(gen)        -> gen_throw(GeneratorExit) + cleanup
```

**`next(g)` is exactly `g.send(None)`.** Same C function, same cost, same state transitions. The only variable is what lands on the value stack as the result of the paused `yield` expression.

So the real distinction is not two mechanisms but two _disciplines_: **one-way iteration** versus **a two-way channel**.

### 5.2 The swap model — the single most important mental model

`send(v)` is a **swap**, not a push:

1. Push `v` as the value of the **currently suspended** `yield` expression.
2. Run forward until the **next** `yield`.
3. Return **that** yield's value.

**The value you receive is unrelated to the value you sent.** It comes from a different, later expression. The off-by-one here is the #1 generator bug.

```python
def accumulate():
    total = 0
    while True:
        n = yield total       # ONE expression that both emits and receives
        total += n

acc = accumulate()
next(acc)         # 0   — arrives at yield#1, emits total=0
acc.send(10)      # 10  — yield#1 RETURNS 10; loop; yield#2 EMITS 10
acc.send(5)       # 15
```

Because the `while` loop makes every yield textually identical, it _looks_ like `send` returns a response to your input. Mentally unroll the loop and the illusion dies: `yield total` at iteration _k_ emits; the same source line at iteration _k+1_ is what returns your value.

### 5.3 Why priming is mandatory

A fresh generator is suspended before `RESUME 0` — before the body starts. There is no paused `yield` expression to receive anything:

```python
g = accumulate()
g.send(10)
# TypeError: can't send non-None value to a just-started generator
```

`None` is permitted only because it is the "no value" sentinel that `next()` uses. The canonical priming decorator, worth having in any codebase with generator-consumers:

```python
from functools import wraps

def primed(fn):
    @wraps(fn)
    def start(*args, **kwargs):
        g = fn(*args, **kwargs)
        g.send(None)
        return g
    return start
```

### 5.4 The lockstep invariant and its consequences

**Every resume consumes exactly one suspension and produces exactly one new one.** From this:

- **A `for` loop can never send.** The iterator protocol calls only `__next__`, which is `send(None)`. Inside a `for`, _every_ `yield` expression evaluates to `None`. If you need to send, you must own the driving loop.
- **`next()` and `send()` interleave freely** — `next()` simply means "resume with `None`."
- **Reentrancy is blocked.** `gi_running` is checked on entry; resuming a generator from inside itself raises `ValueError: generator already executing`.
- **Generators are not thread-safe.** Two threads calling `send()` concurrently is a data race on one frame's value stack. `gi_running` is a diagnostic, not a lock. Guard with a `Lock`, or give each thread its own generator.
- **You cannot rewind.** There is no `prev()`. Buffer with `itertools.tee` (which itself does not support `send`) or materialize.

---

## Part VI — Termination, Exceptions, and Cleanup

```python
def resilient():
    try:
        while True:
            x = yield
            process(x)
    except ValueError as e:
        yield "recovered"          # throw() returns THIS value
    finally:
        release_resources()        # the reliable cleanup hook
```

### `throw(exc)`

Resumes the generator by **raising `exc` at the suspension point** instead of pushing a value. The generator's own `try/except/finally` sees it as an ordinary exception.

- If the generator handles it and yields again, `throw()` returns that yielded value.
- If it propagates, the exception surfaces in _your_ frame, with the generator's frame in the traceback.
- The legacy three-argument form `throw(type, value, tb)` is deprecated as of 3.12; use `throw(exc_instance)`.

### `close()`

Throws `GeneratorExit` at the suspension point.

- `GeneratorExit` inherits from `BaseException`, not `Exception` — so a bare `except Exception:` correctly does **not** swallow it.
- If the generator yields in response, you get `RuntimeError: generator ignored GeneratorExit`.
- If it lets `GeneratorExit` or `StopIteration` propagate, `close()` returns normally.
- **`close()` is also invoked by the garbage collector** via `tp_finalize`. This is what makes `finally` and `with` blocks inside generators dependable — but the timing is _collection time, not abandonment time_. Under CPython refcounting that is usually immediate; under PyPy or in a reference cycle it is not. For deterministic cleanup, use `contextlib.closing(gen)`.
- **Python 3.13+:** `close()` returns the generator's return value if it terminates with `StopIteration`, instead of always returning `None`.

### Return values ride on the exception

```python
def gen():
    yield 1
    return "done"

g = gen()
next(g)                     # 1
try:
    next(g)
except StopIteration as e:
    e.value                 # "done"
```

`return x` inside a generator compiles to raising `StopIteration(x)`. Before Python 3.3, `return` with a value in a generator was a `SyntaxError`.

### PEP 479 — the `StopIteration` leak

A `StopIteration` raised **inside** a generator body is converted to `RuntimeError` (mandatory since 3.7). Previously it silently truncated the generator, producing missing data with no error:

```python
def broken(it):
    while True:
        yield next(it)      # inner StopIteration → RuntimeError, not clean stop

def correct(it):
    while True:
        try:
            yield next(it)
        except StopIteration:
            return
```

Never rely on a bare `next()` on an inner iterator to terminate the outer generator.

---

## Part VII — `yield from`

`yield from` (PEP 380, Python 3.3) is **not** syntactic sugar for a forwarding loop. It establishes a **direct channel**.

While suspended inside `yield from`, `gi_yieldfrom` points at the subgenerator, and `send` / `throw` / `close` are routed **straight to the innermost frame** through a dedicated fast path (the `SEND` opcode in 3.11+). Intermediate frames are not re-entered, so an N-deep delegation chain costs roughly O(1) per level rather than N Python-level round trips.

It also propagates the subgenerator's **return value**:

```python
def inner():
    x = yield "ready"
    return x * 2

def outer():
    got = yield from inner()     # inner's RETURN becomes this expression's value
    yield got

o = outer()
next(o)        # 'ready'   ← the yield belongs to inner
o.send(21)     # 42        ← inner returned 42; outer yields it
```

A hand-written `for v in sub: yield v` loses **all four**: send routing, throw forwarding, close forwarding, and the return value. It is also markedly slower for nested chains.

`yield from` accepts any iterable, not just generators — but the full bidirectional protocol only applies when the delegate is itself a generator.

---

## Part VIII — The Line to `async`/`await`

An event loop **is** a `send` loop:

```python
def run(task):
    to_send = None
    while True:
        try:
            future = task.send(to_send)        # advance to the next await point
        except StopIteration as e:
            return e.value
        to_send = block_until_ready(future)    # or task.throw(err) on failure
```

`await` compiles onto exactly this machinery. asyncio's `Task.__step` is, at its core, `coro.send(None)` and `coro.throw(exc)`. A coroutine is a generator with `CO_COROUTINE` set instead of `CO_GENERATOR` — the difference is which protocol methods are exposed (`__await__` vs `__iter__`), not how suspension works.

**CPython 3.10** added `PyIter_Send`, letting `await`/`yield from` chains report completion via a `PySendResult` enum instead of allocating a `StopIteration` object per step — a measurable win in deep chains. At the Python level you still observe the exception.

**Async generators (PEP 525, 3.6):** `async def` + `yield`, flag `CO_ASYNC_GENERATOR`. Protocol is `__anext__` / `asend` / `athrow` / `aclose`, all of which are _awaitables_ rather than values. `yield from` is forbidden inside them. Because finalization requires a running event loop, cleanup goes through `loop.shutdown_asyncgens()` — or, deterministically, `contextlib.aclosing()`.

**Historical arc:** PEP 255 (2.2, `yield`) → PEP 289 (2.4, genexps) → PEP 342 (2.5, `send`/`throw`/`close` — generators become coroutines) → PEP 380 (3.3, `yield from`) → PEP 492 (3.5, `async`/`await`) → PEP 525 (3.6, async generators) → PEP 479 (3.7, `StopIteration` fix) → PEP 667 (3.13, live `f_locals`).

---

## Part IX — Where `send` Earns Its Keep

### Push parsers and incremental state machines

Invert control: parse state lives in **local variables**, and the resumption point **is** the state.

```python
import struct

@primed
def framed_reader(on_frame):
    buf = bytearray()
    while True:
        buf += yield
        while len(buf) >= 4:
            (n,) = struct.unpack_from(">I", buf)
            if len(buf) < 4 + n:
                break
            on_frame(bytes(buf[4:4+n]))
            del buf[:4+n]

r = framed_reader(handle)
for chunk in socket_stream:
    r.send(chunk)
```

No explicit state enum, no partially-parsed-header attribute. Compare this to the equivalent class-based state machine and the difference in accidental complexity is the whole argument.

### `contextlib.contextmanager`

The canonical stdlib demonstration of the full protocol. `__enter__` calls `next(gen)`; `__exit__` calls `next(gen)` on success or `gen.throw(exc)` on failure, so that `try/finally` inside your generator handles both paths.

### Reconfigurable producers

Adjust batch size, seek position, or apply backpressure mid-stream without tearing down and rebuilding the pipeline.

### Memory and pipeline composition

Generators hold O(1) state regardless of stream length and compose without materializing intermediates:

```python
lines   = (l for l in open(path))
parsed  = (parse(l) for l in lines)
valid   = (p for p in parsed if p.ok)
total   = sum(p.amount for p in valid)   # one pass, constant memory
```

The cost is real: per-item resume overhead and `StopIteration` machinery mean generators lose to list comprehensions on small collections. They win on large or unbounded ones, and on latency-to-first-result.

---

## Part X — Design Guidance

Use plain iteration for data production: laziness, constant memory, composability, and early termination.

Reach for `send()` only when you want **a long-lived object whose state is a program counter** — protocol decoders, schedulers, interactive pipelines.

The coupling is tight. Callers must know the priming discipline and the yield/resume ordering, and the failure modes (`TypeError` on unprimed send, silent off-by-one) are unpleasant. **For a public API, wrap the generator in a class exposing an explicit `feed()` method.** Callers get an ordinary object; you keep the local-variable state machine.

Finally, note what generators are **not**: they are not re-iterable (once exhausted, always exhausted — return a fresh generator from `__iter__` if you need that), they have no `len()`, no indexing, and no rewind.

---

## Part XI — Hard Interview Questions

_One-line answers, using the precise terminology, so each can be expanded on demand._

**Mechanics**

1. **Why is a generator function's body not executed on call?** — The compiler sets `CO_GENERATOR` on the code object, so `CALL` executes `RETURN_GENERATOR`, which allocates a generator object owning an unstarted frame and returns it.
2. **Why is `yield` an expression rather than a statement?** — Because resuming pushes the sent value onto the frame's value stack at the suspension point, so the paused `YIELD_VALUE` must evaluate to something.
3. **What exactly makes a frame resumable?** — Ownership: the generator object owns the `_PyInterpreterFrame`, so `YIELD_VALUE` returns control without unwinding, preserving fast locals, value stack, and `f_lasti`.
4. **Difference between `next(g)` and `g.send(None)`?** — None; both dispatch to `gen_send_ex` with a `NULL`/`None` argument.
5. **Why must a generator be primed before `send`?** — A fresh generator is suspended before `RESUME 0`, not at a `yield`, so there is no paused expression to receive the value — hence `TypeError: can't send non-None value to a just-started generator`.
6. **Why does `send` seem to return the wrong value?** — `send` is a swap: it pushes into the _current_ suspension and returns the value of the _next_ `YIELD_VALUE`, an inherent one-step offset.
7. **Can a `for` loop send into a generator?** — No; the iterator protocol exposes only `__next__`, so every `yield` inside a `for`-driven generator evaluates to `None`.
8. **Why is `gi_frame.f_back` `None`?** — A suspended frame is on no call stack; `f_back` is linked to the resumer only during execution, which is why tracebacks show the consumer, not the creator.

**Variables and scoping**

9. **Where do a generator's locals live, and why do they survive suspension?** — In the frame's fixed-size `localsplus` fast-locals array indexed by `LOAD_FAST`/`STORE_FAST`; it survives because the generator owns the frame.
10. **Two generators from the same generator function — shared or independent locals?** — Independent: each call allocates a fresh frame and fast-locals array.
11. **Two generators closing over the same enclosing frame — shared or independent free variables?** — Shared: free variables live in `PyCellObject`s referenced through `__closure__` and accessed via `LOAD_DEREF`/`STORE_DEREF`.
12. **Contrast fast locals, cell variables, and globals for generators in one sentence.** — Locals give isolated per-instance state, cells give shared mutable state across sibling closures, globals give late-bound module-wide state.
13. **What did PEP 667 change?** — In 3.13, `f_locals` on optimized frames returns a write-through `FrameLocalsProxy` instead of a snapshot dict, so mutations now actually reach the fast-locals array.
14. **Why do all generators in `[(i*x for x in range(3)) for i in range(3)]` yield the same values?** — Late binding plus laziness: all three genexps `LOAD_DEREF` the same cell for `i`, which holds `2` by the time any of them runs.
15. **What is evaluated eagerly in a generator expression?** — Only the outermost iterable, bound to the implicit `.0` parameter; every other clause and condition is lazy.
16. **Rebinding vs mutating the source list of a live genexp?** — Rebinding has no effect (the object is captured in `.0`); mutating does, because the captured object is shared.
17. **Why were comprehensions inlined by PEP 709 but generator expressions not?** — Genexps require a persistent independent frame to support suspension; comprehensions run to completion and need no frame of their own.
18. **How can a suspended generator leak memory?** — Its frame holds strong references to all fast locals, and cyclic-GC finalization may defer `close()`, so large buffers stay pinned after abandonment.

**Protocol and errors**

19. **How does a generator return a value?** — `return x` raises `StopIteration(x)`; callers read it as `e.value`, and `yield from` unwraps it automatically.
20. **What problem did PEP 479 solve?** — A `StopIteration` raised inside a generator body used to silently truncate it; it is now converted to `RuntimeError`.
21. **What does `close()` do, and when is it called implicitly?** — It throws `GeneratorExit` at the suspension point and is invoked by `tp_finalize` during garbage collection, which is what makes `finally` blocks dependable but non-deterministic in timing.
22. **Why does `GeneratorExit` derive from `BaseException`?** — So a broad `except Exception:` cannot accidentally swallow a shutdown request and trigger `RuntimeError: generator ignored GeneratorExit`.
23. **What does `throw()` return?** — The value of the next `yield` if the generator handles the exception and yields again; otherwise the exception propagates to the caller.
24. **What is `gi_running` for, and is it a lock?** — It is a reentrancy guard raising `ValueError: generator already executing`; it is a diagnostic, not a mutex, so generators remain thread-unsafe.

**Delegation and async**

25. **Why prefer `yield from` over a forwarding loop?** — It routes `send`/`throw`/`close` to the innermost delegate via `gi_yieldfrom` and the `SEND` fast path, and propagates the subgenerator's return value.
26. **What is the cost profile of a deep `yield from` chain?** — Roughly O(1) per level through the dedicated delegation path, rather than N Python-level frame re-entries.
27. **How is a coroutine different from a generator, structurally?** — Only the flag (`CO_COROUTINE` vs `CO_GENERATOR`) and the exposed protocol (`__await__`/`send`/`throw` vs `__iter__`/`__next__`); the suspension machinery is identical.
28. **How does an event loop actually drive a coroutine?** — By calling `coro.send(None)` until a `StopIteration`, resuming with `send(result)` or `throw(exc)` when the awaited future completes.
29. **What did `PyIter_Send` (3.10) optimize?** — It reports completion through a `PySendResult` enum, avoiding a `StopIteration` allocation per step in `await`/`yield from` chains.
30. **Why do async generators need `shutdown_asyncgens()` or `aclosing()`?** — `aclose()` is a coroutine requiring a running event loop, so GC-time finalization is unreliable and cleanup must be scheduled explicitly.
31. **How does `contextlib.contextmanager` use the protocol?** — `__enter__` calls `next(gen)`; `__exit__` calls `next(gen)` on success and `gen.throw(exc)` on failure, letting one `try/finally` cover both paths.
32. **Why does an `assert` at the top of a generator function never fire?** — `CO_GENERATOR` defers the entire body to the first resume; eager checks must live in a plain wrapper that returns the inner generator.
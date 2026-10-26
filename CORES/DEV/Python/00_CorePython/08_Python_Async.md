# Never Be Lost in Python Async Again

*Modern Python — 3.12 and later. Every output in this essay is real Python output.*

There is **one** mental model in this essay. Not one for coroutines and another for tasks, not a special case for cancellation. One.

This essay is about **`asyncio` only** — the cooperative half of Python concurrency. Threads and processes are a different mechanism with different rules; they appear here exactly once, in Part 9, as the escape hatch for code that won't cooperate.

---

# Part 1 — The mental model: one worker, and `await` is where it may put you down

```
   THREADS                              ASYNC
   ┌────┐ ┌────┐ ┌────┐                 ┌─────────────────────────────┐
   │ w1 │ │ w2 │ │ w3 │                 │        ONE   WORKER         │
   └────┘ └────┘ └────┘                 └─────────────────────────────┘
   the OS may swap them out             it swaps only where YOU wrote
   at any instruction, invisibly        `await` — visibly, in the source
```

The event loop is **one worker with a job list.** It picks a job, runs it, and keeps running it until the job says *"I'm waiting for something."* Then — and only then — it puts that job down and picks up another.

```
        THE LOOP'S JOB LIST
   ┌────────────────────────────────────────────────────────┐
   │  ready    →  [ job C ]  [ job A ]      run these now    │
   │  waiting  →  job B (until the socket answers)           │
   └────────────────────────────────────────────────────────┘
                          ▲
                   one worker, taking the next ready job
                   and running it until it hits an `await`
```

> ## **There is exactly one worker. `await` marks a point where it is allowed to put your job down and pick up another.**

Say this out loud whenever async surprises you:

> ## **"Where does this hand control back? And is there anything else for the worker to do while it's away?"**

## Fact 1 — calling an `async def` runs nothing

Exactly like a generator function. This is the same "tap, not a bucket" idea from the iterators essay, and it's the first thing that trips people up.

```python
async def work(): return 42

c = work()
type(c)                             # <class 'coroutine'>
inspect.iscoroutine(c)              # True
```

Not one line of the body has run. You have a **plan**, not a result. Drop it without awaiting and Python tells you:

```python
del c
# RuntimeWarning: coroutine 'work' was never awaited
```

That warning is one of the most useful in Python. It means a piece of work you wrote was never actually done.

## Fact 2 — switching happens only at `await`

Between two `await`s, **your code cannot be interrupted.** No other job runs. No lock is needed.

```python
counter = 0
async def bump():
    global counter
    for _ in range(1000):
        counter += 1                    # no await inside → atomic

await asyncio.gather(*(bump() for _ in range(5)))
counter                                 # 5000    — correct, every time
```

Put an `await` in the middle of a read-modify-write and it stops being atomic:

```python
bad = 0
async def racy():
    global bad
    for _ in range(100):
        v = bad
        await asyncio.sleep(0)          # ← control leaves here
        bad = v + 1

await asyncio.gather(*(racy() for _ in range(5)))
bad                                     # 100     — should be 500
```

That is a genuine race condition in single-threaded code. **The `await` is the race.** Which is also the good news: unlike threads, you can *see* every place a race is possible — they're the lines with `await` on them.

## Fact 3 — `await` alone is not concurrency

This is the misconception that costs people the most time.

```python
async def job(n):
    await asyncio.sleep(0.1)
    return n

async def sequential():
    return [await job(i) for i in range(3)]         # ← awaits one at a time

async def with_gather():
    return await asyncio.gather(*(job(i) for i in range(3)))

async def with_taskgroup():
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(job(i)) for i in range(3)]
    return [t.result() for t in tasks]
```

```
  sequential  [0, 1, 2] in 0.32s
  gather      [0, 1, 2] in 0.11s
  TaskGroup   [0, 1, 2] in 0.11s
```

`await job(i)` says *"I need this answer before I continue."* The loop does go and do other work while you're parked — but if there **is** no other work, it just waits. Three sequential awaits take three times as long.

> ### **`await` means "wait for this". `create_task` / `gather` / `TaskGroup` mean "start this now, and let it overlap."** Concurrency comes from the second group, never from the first.

## What async is and isn't for

| | |
|---|---|
| **Good for** | many things waiting at once: network calls, database queries, file I/O, timers, sockets, subprocesses |
| **Useless for** | CPU-bound work. One worker, one core. Async makes waiting cheap; it does not make computation faster. |
| **Dangerous with** | any blocking call. One blocking line stops *everything* — Part 9. |

That's the model. Now we just apply it.

---

# Part 2 — The three nouns: coroutine, task, future

Almost every asyncio confusion is one of these three being mistaken for another.

| Noun | What it is | Made by | Running? |
|---|---|---|---|
| **coroutine** | a plan | calling an `async def` | **no** — inert until awaited |
| **task** | a plan the loop has been *told to run* | `create_task`, `TaskGroup.create_task` | **yes** — scheduled immediately |
| **future** | a placeholder for a value that isn't here yet | libraries, `loop.create_future()` | n/a — it's a slot |

```python
co = job(1)                                     # coroutine  — nothing scheduled
t  = asyncio.create_task(co, name="job-1")      # Task       — now it's running
t.get_name()            # 'job-1'
t.done()                # False

f = asyncio.get_running_loop().create_future()  # Future     — an empty slot
f.set_result("manual")
await f                 # 'manual'

await t                 # 1
t.done()                # True
```

`Task` is a subclass of `Future`, which is why they behave the same when you await them. And **an "awaitable" is anything with `__await__`** — coroutines, tasks, futures, and any object implementing the protocol.

> ### **The single most important line in asyncio is `create_task`. It is the moment a plan becomes work in progress.**

You rarely construct a `Future` yourself; you'll meet them coming out of libraries and out of `run_in_executor`.

---

# Part 3 — Getting in: `asyncio.run` and the boundary

```python
async def main():
    ...

asyncio.run(main())
```

`asyncio.run` creates a loop, runs the coroutine until it finishes, cancels anything left over, shuts down async generators, and closes the loop. **One call, at the top, and nothing else.**

```python
asyncio.run(main(), debug=True)             # turns on slow-callback warnings

with asyncio.Runner(debug=True) as runner:  # 3.11: several runs, one loop
    runner.run(main())
    runner.run(other())
```

## 3.1 The boundary is one-directional and hard

```python
async def nested():
    asyncio.run(api())
# RuntimeError: asyncio.run() cannot be called from a running event loop
```

Sync code can start async code (`asyncio.run`). Async code cannot start a *new* loop inside the current one. And you can't `await` at module level — only inside an `async def` (the REPL and Jupyter cheat by running a loop for you).

This is why async is famously "colour-coded": once a function is `async def`, every caller up the chain must be too, until you reach `asyncio.run`. That's not a design flaw to route around; it's the honest signal that the function may hand control away.

## 3.2 Don't touch `get_event_loop`

```python
asyncio.get_running_loop()      # ✓ inside async code — the one you're on
asyncio.get_event_loop()        # ✗ deprecated behaviour; on 3.14 it raises
                                #   RuntimeError: There is no current event loop
```

Every `loop = asyncio.get_event_loop()` you see in a tutorial predates 3.7. Use `asyncio.run` at the top and `asyncio.get_running_loop()` inside.

---

# Part 4 — Actually concurrent: `TaskGroup`, `gather`, `create_task`

Three ways to make work overlap, in descending order of how often you should reach for them.

## 4.1 `asyncio.TaskGroup` — the modern default (3.11)

```python
async with asyncio.TaskGroup() as tg:
    t1 = tg.create_task(fetch("a"))
    t2 = tg.create_task(fetch("b"))
# both are finished here — the `async with` doesn't exit until they are

t1.result(), t2.result()
```

What it guarantees, and why it's the default:

- **Nothing escapes.** The block does not exit until every child is done. No orphaned tasks, ever.
- **One failure cancels the siblings.** No half-finished fan-outs.
- **Errors arrive as an `ExceptionGroup`**, so you see *all* the failures, not just the first.

```python
async def good(n):
    try:
        await asyncio.sleep(0.2); return f"good{n}"
    except asyncio.CancelledError:
        print(f"good{n} cancelled"); raise

async def bad():
    await asyncio.sleep(0.05); raise ValueError("boom")

try:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(good(1))
        tg.create_task(good(2))
        tg.create_task(bad())
except* ValueError as eg:
    print("caught:", eg.exceptions)

# good2 cancelled
# good1 cancelled
# caught: (ValueError('boom'),)
```

This is **structured concurrency**: the lifetime of the children is bounded by a block in the source. You can see where they start and where they must end.

## 4.2 `asyncio.gather` — still fine, and sometimes right

```python
results = await asyncio.gather(fetch("a"), fetch("b"))       # results in ARGUMENT order
```

Two behaviours to know:

```python
await asyncio.gather(job(1), bad())
# ValueError: boom        ← the first exception propagates immediately...
#                           ...but the other tasks keep running, unsupervised

await asyncio.gather(job(1), bad(), return_exceptions=True)
# [1, ValueError('boom')]  ← nothing raises; you inspect each outcome
```

`return_exceptions=True` is the genuinely useful mode and the reason `gather` survives: **when you want every result regardless of individual failures**, a `TaskGroup` (which cancels everything on the first error) is the wrong shape.

| Want | Use |
|---|---|
| all must succeed; cancel the rest on any failure | `TaskGroup` |
| every outcome, successes and failures alike | `gather(..., return_exceptions=True)` |
| results as they arrive | `as_completed` |
| fire something off and manage it yourself | `create_task` |

## 4.3 `create_task` — and the reference you must keep

```python
t = asyncio.create_task(job(1))
```

Scheduled immediately, runs at the next `await`. The trap:

> ### **The event loop keeps only a *weak* reference to a task. If you don't hold one, it can be garbage-collected mid-flight and silently disappear.**

The documented idiom:

```python
background: set[asyncio.Task] = set()

t = asyncio.create_task(fire(i))
background.add(t)
t.add_done_callback(background.discard)
```

Which is a chore — and one more reason `TaskGroup` is the default: it holds the references for you.

## 4.4 `as_completed` and `wait`

```python
for fut in asyncio.as_completed([job("slow", 0.15), job("fast", 0.05)]):
    print(await fut)
# fast
# slow                    ← arrival order, not argument order
```

```python
done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
for p in pending:
    p.cancel()
```

`wait` takes **tasks**, not bare coroutines, and it does *not* raise on failure — you inspect the `done` set yourself. `FIRST_COMPLETED`, `FIRST_EXCEPTION`, and `ALL_COMPLETED` are the three modes. It's the lowest-level of the four and the one you'll need least.

---

# Part 5 — Cancellation and timeouts

## 5.1 `asyncio.timeout` — the modern one (3.11)

```python
try:
    async with asyncio.timeout(0.1):
        await slow()
except TimeoutError:
    print("gave up")
```

It wraps a **block**, not a single call, so several awaits can share one deadline. `asyncio.timeout_at(when)` takes an absolute loop time instead.

The older `asyncio.wait_for(coro, timeout=...)` still works and wraps exactly one awaitable. Since 3.11, `asyncio.TimeoutError` **is** the builtin `TimeoutError`, so `except TimeoutError` catches both.

## 5.2 Cancellation is an exception

```python
t = asyncio.create_task(work())
t.cancel()
try:
    await t
except asyncio.CancelledError:
    ...
t.cancelled()           # True
```

`t.cancel()` **requests** cancellation: it arranges for `CancelledError` to be raised at the task's current `await`. It doesn't stop anything instantly, and a task with no `await` left to reach can't be cancelled at all.

> ### **`CancelledError` inherits from `BaseException`, not `Exception`.** So `except Exception:` does *not* catch it — which is deliberate, and exactly what you want.

```python
issubclass(asyncio.CancelledError, BaseException)    # True
issubclass(asyncio.CancelledError, Exception)        # False
```

## 5.3 Cleaning up properly

```python
async def cleanup_job():
    try:
        await asyncio.sleep(5)
    except asyncio.CancelledError:
        print("cleaning up")
        raise                       # ← ALWAYS re-raise
    finally:
        print("finally runs")
```

Two rules:

- **Always re-raise `CancelledError`.** Swallowing it tells the loop the task finished normally, and the whole cancellation contract falls apart. (`TaskGroup` will notice and complain.)
- **`finally` runs.** Use it for releasing resources; don't put a long `await` in there, because you're already being torn down.

## 5.4 `shield` — protecting work from a cancelled caller

```python
inner = asyncio.create_task(job("shielded", 0.2))
outer = asyncio.shield(inner)
outer.cancel()

await outer             # CancelledError    — the caller gave up
await inner             # 'shielded'        — the work still finished
```

For the rare case where the *caller* can time out but the operation must complete — committing a transaction, flushing a buffer. Use it sparingly; shielded work that nobody awaits is a leak.

---

# Part 6 — Exceptions: `ExceptionGroup` and `except*`

Concurrency means several things can fail at once, so 3.11 added a container for that.

```python
try:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(fails_with_value_error())
        tg.create_task(fails_with_key_error())
except* ValueError as eg:
    print("value errors:", eg.exceptions)
except* KeyError as eg:
    print("key errors:", eg.exceptions)
```

`except*` is genuinely different from `except`, and the differences matter:

| | `except` | `except*` |
|---|---|---|
| catches | the first matching exception | **every** matching exception in the group |
| how many clauses run | one | **all** that match |
| binds | one exception | an `ExceptionGroup` of the matching ones |
| unmatched parts | — | re-raised as a smaller group |

So more than one `except*` clause can fire for the same group. If you only care that *something* failed, `except* Exception as eg:` works fine.

`TaskGroup` always raises a group — even for a single failure — so `except ValueError:` on its own will **not** catch what a `TaskGroup` throws. That's the most common surprise when migrating from `gather`.

---

# Part 7 — `async with`, `async for`, async generators

The dunders are in the magic-methods essay; here's how they show up in practice.

## 7.1 `async with`

```python
class Fetcher:
    async def __aenter__(self):
        await self.pool.open()
        return self
    async def __aexit__(self, *exc_info):
        await self.pool.close()
        return False                    # never swallow
```

Or the short form:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def session():
    conn = await connect()
    try:
        yield conn
    finally:
        await conn.close()
```

Use `async with` whenever setup or teardown needs to `await`. A sync `__exit__` that calls `asyncio.run` is always wrong.

## 7.2 `async for` and async generators

```python
async def stream(urls):
    for completed in asyncio.as_completed([fetch(u) for u in urls]):
        yield await completed

async for result in stream(urls):
    ...

results = [r async for r in stream(urls)]      # async comprehension
first = await anext(stream(urls))
```

Two rules worth repeating from the iterators essay: **`__aiter__` is a plain method, `__anext__` is `async`**, and `yield from` is a hard `SyntaxError` inside an async generator — delegate with `async for … : yield …`.

## 7.3 `aclosing` — because cleanup is not automatic

```python
from contextlib import aclosing

async with aclosing(ticks(10)) as g:
    async for v in g:
        if v == 2:
            break                       # the generator's `finally` runs here
```

Abandon an async generator without closing it and its `finally` runs whenever garbage collection gets round to it — possibly after the loop has closed. `asyncio.run` calls `shutdown_asyncgens` to limit the damage, but `aclosing` is how you make it deterministic.

---

# Part 8 — Synchronisation

You need less of this than in threaded code, because Fact 2 means most of your critical sections are already atomic. Reach for a primitive only when a section **spans an `await`**.

```python
val = 0
lock = asyncio.Lock()

async def safe():
    global val
    for _ in range(100):
        async with lock:
            v = val
            await asyncio.sleep(0)      # the await is INSIDE the lock
            val = v + 1

await asyncio.gather(*(safe() for _ in range(5)))
val                                     # 500       (100 without the lock)
```

| Primitive | For |
|---|---|
| `asyncio.Lock` | a critical section that spans an `await` |
| `asyncio.Semaphore(n)` | **cap concurrency** — the one you'll use most |
| `asyncio.Event` | "wake everyone when this happens" |
| `asyncio.Condition` | wait for a predicate, with a lock |
| `asyncio.Queue` | hand work between producers and consumers |
| `asyncio.Barrier` (3.11) | release N waiters together |

> **Use `asyncio.Lock`, never `threading.Lock`.** A threading lock blocks the *whole loop* while it waits — see Part 9.

## 8.1 `Semaphore` — rate limiting, and the reason it's the most useful one

Fan-out is easy; fanning out to 10,000 sockets at once is a denial-of-service attack on your own database. A semaphore is the fix and it's two lines:

```python
sem = asyncio.Semaphore(3)

async def limited(url):
    async with sem:                     # at most 3 in flight
        return await fetch(url)

await asyncio.gather(*(limited(u) for u in urls))
```

```
6 jobs, limit 2: peak concurrency 2, 0.18s
```

## 8.2 `Queue` — the pipeline shape

```python
q: asyncio.Queue[int | None] = asyncio.Queue(maxsize=2)

async def producer():
    for i in range(5):
        await q.put(i)                  # blocks when full → backpressure
    await q.put(None)                   # sentinel

async def consumer():
    while (item := await q.get()) is not None:
        process(item)
        q.task_done()
```

`maxsize` gives you backpressure for free: a fast producer is throttled by a slow consumer instead of eating all your memory. `await q.join()` waits until every item has been `task_done()`. Since 3.13 there's `q.shutdown()`, which makes pending and future `get`/`put` raise `QueueShutDown` — a cleaner alternative to sentinel values.

---

# Part 9 — Blocking code: the cardinal sin

One worker. If your code doesn't hand control back, **nothing else runs.** Not other tasks, not timeouts, not the cancellation you just requested.

```python
async def blocking(n):
    time.sleep(0.1)                     # ✗ blocks the whole loop
    return n

async def nonblocking(n):
    await asyncio.sleep(0.1)            # ✓ hands control back
    return n
```

```
  time.sleep     3 jobs in 0.30s        ← no concurrency at all
  asyncio.sleep  3 jobs in 0.11s
```

## 9.1 What blocks

| Blocking | Use instead |
|---|---|
| `time.sleep()` | `await asyncio.sleep()` |
| `requests`, `urllib` | `httpx` (async), `aiohttp` |
| `open()` / `.read()` / `.write()` | `await asyncio.to_thread(...)`, or `aiofiles` |
| any DB driver that isn't async | `asyncpg`, `aiosqlite`, or a thread |
| `subprocess.run` | `asyncio.create_subprocess_exec` |
| `threading.Lock.acquire()` | `asyncio.Lock` |
| `input()` | a thread |
| a long CPU loop | a process pool |

The general test: **if it can take more than a millisecond and there's no `await` in front of it, it's a problem.**

## 9.2 `asyncio.to_thread` — the escape hatch (3.9)

```python
def legacy(n):
    time.sleep(0.1)
    return n

results = await asyncio.gather(*(asyncio.to_thread(legacy, i) for i in range(3)))
# 0.19s instead of 0.30s — the blocking calls now overlap in threads
```

`to_thread` runs the function in the default thread pool and gives you an awaitable. It is the right answer for **blocking I/O** and for third-party libraries you can't replace.

For explicit pool control, or for CPU-bound work:

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

loop = asyncio.get_running_loop()

with ThreadPoolExecutor(max_workers=2) as ex:
    r = await loop.run_in_executor(ex, legacy, 99)          # blocking I/O

with ProcessPoolExecutor() as ex:
    r = await loop.run_in_executor(ex, heavy_maths, data)   # CPU-bound
```

> **Threads for waiting, processes for computing, async for lots of waiting at once.** They compose — `to_thread` is the seam.

## 9.3 Debug mode will tell you

```python
asyncio.run(main(), debug=True)
```

Turns on: warnings for callbacks that take longer than 100ms, warnings for coroutines never awaited, source tracebacks for un-retrieved exceptions, and a check that you're not calling loop methods from the wrong thread. **Run your test suite with it on.**

---

# Part 10 — Streams and subprocesses

Two built-in async I/O facilities worth knowing about, because they're what everything else is built on.

## 10.1 Streams

```python
async def handle(reader, writer):
    data = await reader.readline()
    writer.write(b"echo: " + data)
    await writer.drain()                # ← backpressure. Don't skip it.
    writer.close()
    await writer.wait_closed()

server = await asyncio.start_server(handle, "127.0.0.1", 8888)
async with server:
    await server.serve_forever()
```

```python
reader, writer = await asyncio.open_connection("127.0.0.1", 8888)
writer.write(b"hello\n")
await writer.drain()
line = await reader.readline()          # b'echo: hello\n'
writer.close()
await writer.wait_closed()
```

Note the asymmetry: `write()` is **not** a coroutine (it buffers), and `await writer.drain()` is what waits for the buffer to empty. Skipping `drain()` in a loop is how you write an unbounded memory leak.

## 10.2 Subprocesses

```python
proc = await asyncio.create_subprocess_exec(
    "git", "status", "--short",
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
)
out, err = await proc.communicate()
proc.returncode                         # 0
```

The async twin of `subprocess.run`. Use it instead of `subprocess` inside async code, or a hundred concurrent shell-outs become a hundred sequential ones.

---

# Part 11 — Typing async code

```python
from collections.abc import AsyncIterator, AsyncGenerator, Awaitable, Callable, Coroutine
```

| You write | Its type |
|---|---|
| `async def f(x: int) -> str` | annotate the **result**: `-> str`. The checker knows a call gives `Coroutine[Any, Any, str]`. |
| a variable holding an un-awaited call | `Coroutine[Any, Any, str]` |
| a parameter you'll `await` | `Awaitable[T]` — widest, accepts coroutines, tasks, futures |
| an async generator's return | `AsyncIterator[T]` |
| …if you also `send` into it | `AsyncGenerator[YieldT, SendT]` |
| a callable returning a coroutine | `Callable[[int], Awaitable[str]]` |

```python
async def f(x: int) -> str:             # ← -> str, not -> Coroutine[...]
    return str(x)

typing.get_type_hints(f)                # {'x': int, 'return': str}
type(f(1)).__name__                     # 'coroutine'

async def agen() -> AsyncIterator[int]: # ← AsyncIterator, even though it yields
    yield 1
```

The rule that catches everyone: **annotate the value you'll get after awaiting.** `-> str`, never `-> Coroutine[Any, Any, str]`. Python wraps it for you.

Prefer `Awaitable[T]` for parameters (accept the widest thing you can use) and be concrete about returns — the same accept-wide/return-narrow rule as the type-system essay.

Two useful runtime checks:

```python
inspect.iscoroutinefunction(f)          # True   — is it `async def`?
inspect.isasyncgenfunction(agen)        # True   — is it an async generator?
```

---

# Part 12 — The traps

## 12.1 Forgetting to await

```python
async def main():
    fetch(url)                          # ✗ builds a coroutine, throws it away
    await fetch(url)                    # ✓
```

Symptom: `RuntimeWarning: coroutine 'fetch' was never awaited`, and the work silently didn't happen. Turn warnings into errors in tests.

## 12.2 Awaiting in a loop and calling it concurrency

*(Fact 3.)* `[await f(x) for x in xs]` is sequential. Use `gather` or a `TaskGroup`.

## 12.3 One blocking call

*(Part 9.)* Everything stops. If concurrency mysteriously vanished, look for `time.sleep`, `requests`, or a sync DB driver.

## 12.4 `except Exception` doesn't catch `CancelledError`

*(5.2.)* It's a `BaseException`. And if you *do* catch it, re-raise.

## 12.5 `except ValueError` doesn't catch what a `TaskGroup` raises

*(Part 6.)* `TaskGroup` raises an `ExceptionGroup`. You need `except*`, or `except ExceptionGroup`.

## 12.6 Losing a `create_task` reference

*(4.3.)* The loop holds a weak reference. Keep a strong one, or use a `TaskGroup`.

## 12.7 A race across an `await`

*(Fact 2.)* Read-modify-write with an `await` in the middle is not atomic. Either remove the `await` from the critical section or take an `asyncio.Lock`.

## 12.8 `threading.Lock` in async code

Blocks the loop while waiting. Use `asyncio.Lock`. Same for `queue.Queue` vs `asyncio.Queue`.

## 12.9 Unbounded fan-out

10,000 `create_task`s hit your database with 10,000 connections. Cap it with a `Semaphore`.

## 12.10 A sync `__exit__` that needs to await

Use `__aenter__`/`__aexit__` and `async with`. Calling `asyncio.run` from inside a sync `__exit__` raises if a loop is running, and creates a second loop if one isn't.

## 12.11 Abandoned async generators

*(7.3.)* Cleanup happens at GC time. Use `contextlib.aclosing`.

## 12.12 `asyncio.run` more than once, or inside a loop

One `asyncio.run` per program, at the top. Inside a loop it raises `RuntimeError`.

## 12.13 Reaching for async when threads would do

If you have ten blocking calls and no async library for them, `ThreadPoolExecutor` is simpler than rewriting the world. Async pays off at hundreds or thousands of concurrent waits, or when the ecosystem you're using is already async.

---

# Part 13 — The whole thing on one page

## The core

```python
async def f(): ...          # defines a coroutine FUNCTION
c = f()                     # a coroutine OBJECT — nothing has run
await c                     # run it; may hand control to the loop
asyncio.create_task(c)      # schedule it NOW, concurrently
asyncio.run(main())         # the one entry point, at the top
```

| Concept | One line |
|---|---|
| event loop | one worker, one job list |
| `await` | "I'm waiting" — the only place control switches |
| coroutine | a plan |
| task | a plan that's running |
| future | a slot for a value |
| concurrency | comes from `create_task`/`gather`/`TaskGroup`, never from `await` |

## Running several things

| API | Semantics | Since |
|---|---|---|
| `async with TaskGroup() as tg: tg.create_task(...)` | all must succeed; siblings cancelled on failure; raises `ExceptionGroup` | 3.11 |
| `gather(*aws)` | results in argument order; first exception propagates | — |
| `gather(*aws, return_exceptions=True)` | every outcome, nothing raises | — |
| `as_completed(aws)` | yields futures in **arrival** order | — |
| `wait(tasks, return_when=...)` | `(done, pending)`; never raises | — |
| `create_task(coro)` | fire it off — **keep a reference** | — |

## Timeouts and cancellation

```python
async with asyncio.timeout(2.0):        # 3.11 — wraps a BLOCK
    await a(); await b()

await asyncio.wait_for(coro, 2.0)       # wraps ONE awaitable

task.cancel()                           # requests CancelledError at the next await
task.cancelled()                        # did it end that way?
asyncio.shield(aw)                      # let the caller give up; the work continues

except TimeoutError                     # == asyncio.TimeoutError since 3.11
except asyncio.CancelledError:  ...; raise      # ALWAYS re-raise
```

## Synchronisation

| | |
|---|---|
| `asyncio.Lock` | critical section spanning an `await` |
| `asyncio.Semaphore(n)` | cap concurrency ← the useful one |
| `asyncio.Event` | broadcast a one-shot signal |
| `asyncio.Condition` | wait on a predicate |
| `asyncio.Queue(maxsize=)` | producer/consumer with backpressure |
| `asyncio.Barrier(n)` | release N together (3.11) |

## Escaping to threads and processes

```python
await asyncio.to_thread(blocking_fn, *args)                     # blocking I/O
await loop.run_in_executor(ThreadPoolExecutor(), fn, *args)     # explicit pool
await loop.run_in_executor(ProcessPoolExecutor(), fn, *args)    # CPU-bound
```

## Async dunders

| Syntax | Dunder |
|---|---|
| `async with x` | `__aenter__` / `__aexit__` (both `async`) |
| `async for x in it` | `__aiter__` (plain!) / `__anext__` (`async`) |
| `await x` | `__await__` |
| end of an async iterator | raise `StopAsyncIteration` |

## Async vs threads vs processes

| | async | threads | processes |
|---|---|---|---|
| parallel CPU | ✗ | ✗ (GIL) | ✓ |
| lots of waiting | ✓✓ thousands | ✓ dozens–hundreds | ✗ |
| switches at | `await` only | anywhere | n/a |
| races | only across `await` | everywhere | shared nothing |
| cost per unit | ~KB | ~MB stack | a whole process |

---

# Part 14 — When it surprises you, ask three questions

1. **"Did anything actually start?"** A bare `f()` builds a coroutine and drops it. Look for the `RuntimeWarning`, and check that every fan-out went through `create_task`, `gather`, or a `TaskGroup`.

2. **"Is something blocking?"** If N concurrent jobs take N × the time of one, the loop never got control back. Run with `debug=True` and look for the slow-callback warnings — they name the offender.

3. **"Where can control leave this function?"** Every `await` is a place another task may run and a place cancellation may strike. If shared state is inconsistent across one of them, that's your bug.

And the universal move: **print the timings.** Sequential-vs-concurrent is the one thing async gets wrong silently, and a `time.perf_counter()` either side of the fan-out settles it in ten seconds.

---

# Part 15 — Real code, using all of it

A concurrent fetcher: a pooled session as an async context manager, a semaphore cap, per-request timeouts and retries, three different fan-out shapes, cancellation cleanup, and a thread for the blocking parse.

```python
import asyncio
import random
import time
from collections.abc import AsyncIterator, Iterable
from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True, slots=True)
class Result:
    url: str
    status: int
    body: str
    attempts: int


class Fetcher:
    """Owns a pool and a concurrency cap. Async context manager because
    both opening and closing need to await."""

    def __init__(self, limit: int = 3, timeout: float = 0.5) -> None:
        self._sem = asyncio.Semaphore(limit)
        self._timeout = timeout
        self._live = 0
        self.peak = 0

    async def __aenter__(self) -> Self:
        await asyncio.sleep(0.01)               # open the pool
        return self

    async def __aexit__(self, *exc_info) -> bool:
        await asyncio.sleep(0.01)               # drain and close
        return False                            # never swallow

    async def _get(self, url: str) -> tuple[int, str]:
        await asyncio.sleep(random.uniform(0.02, 0.08))
        if "flaky" in url and random.random() < 0.6:
            raise ConnectionError(f"reset by peer: {url}")
        if "slow" in url:
            await asyncio.sleep(5)
        return 200, f"<body of {url}>"

    async def fetch(self, url: str, retries: int = 3) -> Result:
        async with self._sem:                   # cap in-flight requests
            self._live += 1
            self.peak = max(self.peak, self._live)
            try:
                for attempt in range(1, retries + 1):
                    try:
                        async with asyncio.timeout(self._timeout):
                            status, body = await self._get(url)
                        return Result(url, status, body, attempt)
                    except ConnectionError:
                        if attempt == retries:
                            raise
                        await asyncio.sleep(0.01 * 2 ** attempt)    # backoff
            finally:
                self._live -= 1                 # runs on cancellation too


# --- shape 1: all-or-nothing ---
async def fetch_all(f: Fetcher, urls: Iterable[str]) -> list[Result]:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(f.fetch(u), name=u) for u in urls]
    return [t.result() for t in tasks]


# --- shape 2: report every outcome ---
async def fetch_settled(f: Fetcher, urls: Iterable[str]) -> list[Result | BaseException]:
    return await asyncio.gather(*(f.fetch(u) for u in urls), return_exceptions=True)


# --- shape 3: stream results as they land ---
async def stream(f: Fetcher, urls: Iterable[str]) -> AsyncIterator[Result]:
    for completed in asyncio.as_completed([f.fetch(u) for u in urls]):
        yield await completed


def parse_blocking(body: str) -> int:
    """Pretend this is a blocking C library."""
    time.sleep(0.05)
    return len(body)
```

Using it:

```python
urls = [f"https://x/{i}" for i in range(6)]

# TaskGroup + Semaphore: six requests, never more than three in flight
async with Fetcher(limit=3) as f:
    results = await fetch_all(f, urls)
# TaskGroup    : 6 ok in 0.11s, peak in-flight 3

# gather(return_exceptions=True): keep going past a failure
async with Fetcher(limit=10) as f:
    out = await fetch_settled(f, ["https://x/1", "https://flaky/2", "https://x/3"])
#   settled    : https://x/1 attempt 1
#   settled    : https://flaky/2 attempt 3        ← retried twice, then succeeded
#   settled    : https://x/3 attempt 1

# an async generator, consumed with `async for`
async with Fetcher(limit=10) as f:
    order = [r.url async for r in stream(f, urls[:4])]
# streamed     : 4 results, arrival order

# asyncio.timeout
async with Fetcher(limit=10, timeout=0.2) as f:
    try:
        await f.fetch("https://slow/1", retries=1)
    except TimeoutError:
        ...
# timeout      : gave up on the slow one

# to_thread for the blocking parse
async with Fetcher(limit=10) as f:
    r = await f.fetch("https://x/9")
    size = await asyncio.to_thread(parse_blocking, r.body)
# to_thread    : parsed 21 bytes off the loop

# cancellation, with the semaphore released by `finally`
async with Fetcher(limit=10) as f:
    task = asyncio.create_task(f.fetch("https://slow/9"))
    await asyncio.sleep(0.05)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        ...
# cancellation : task cancelled, semaphore released -> True

# except* on what a TaskGroup raises
try:
    async with Fetcher(limit=10, timeout=0.2) as f:
        await fetch_all(f, ["https://x/1", "https://slow/2"])
except* TimeoutError as eg:
    print(len(eg.exceptions), "TimeoutError(s) in the group")
# except*      : 1 TimeoutError(s) in the group
```

Three things worth pointing at.

**`peak in-flight 3` with six URLs** is the semaphore doing its job. Remove `async with self._sem:` and you get six simultaneous connections — with ten thousand URLs, ten thousand.

**`self._live -= 1` sits in a `finally`.** When the task is cancelled, `CancelledError` fires at whichever `await` is current, the `finally` runs, and the `async with self._sem` releases on the way out. Cancellation cleanup is not something you bolt on; it's `try/finally`, exactly as in sync code.

**The three fan-out shapes are three different failure policies**, not three styles. `fetch_all` cancels everything on the first error. `fetch_settled` reports each outcome independently. `stream` gives you results early so a slow tail doesn't delay the fast ones. Choosing between them is the actual design decision — `TaskGroup` vs `gather` is downstream of it.

---

# Appendix

## A. What landed when

| Version | Relevant |
|---|---|
| 3.5 | `async def`, `await`, `__aiter__`/`__anext__`, `__aenter__`/`__aexit__` |
| 3.6 | async generators, async comprehensions |
| 3.7 | **`asyncio.run`**, `create_task`, `get_running_loop`, `contextvars` |
| 3.8 | `asyncio` as a REPL (`python -m asyncio`) |
| 3.9 | **`asyncio.to_thread`** |
| 3.10 | `aiter()` / `anext()` builtins, `contextlib.aclosing`, strict `zip` |
| **3.11** | **`TaskGroup`, `asyncio.timeout`, `ExceptionGroup` + `except*`, `asyncio.Runner`, `asyncio.Barrier`; `asyncio.TimeoutError` == builtin `TimeoutError`; `@asyncio.coroutine` removed** |
| **3.12** | **eager task factory (`loop.set_task_factory(asyncio.eager_task_factory)`); `current_task`/`all_tasks` in C; broad asyncio speedups** |
| 3.13 | `Queue.shutdown()`, `asyncio.TaskGroup` improvements, free-threaded build (experimental) |
| 3.14 | `get_event_loop` raises with no running loop; further loop speedups |

The 3.11 row is the important one. **If a tutorial predates `TaskGroup` and `asyncio.timeout`, its structure is out of date** even if its code still runs.

## B. Eager tasks (3.12)

By default `create_task` schedules the coroutine to start at the *next* suspension point. The eager factory starts it immediately and only creates a real `Task` if it actually suspends:

```python
loop.set_task_factory(asyncio.eager_task_factory)
```

```python
# lazy  : after create_task, log = []
# eager : after create_task, log = ['started']
```

A measurable win when many of your coroutines complete without ever awaiting anything (cache hits, short-circuit paths). Behaviourally it's a subtle change to ordering — turn it on deliberately, not by reflex.

## C. Things that look async and aren't

| | |
|---|---|
| `asyncio.sleep(0)` | not a no-op — it's the explicit "let others run" yield point |
| `writer.write()` | **not** a coroutine; `await writer.drain()` is the awaiting part |
| `queue.put_nowait()` / `get_nowait()` | sync, raise instead of waiting |
| `task.result()` | sync; raises `InvalidStateError` if the task isn't done |
| `Event.set()` | sync; only `Event.wait()` is awaitable |
| `loop.call_soon()` / `call_later()` | schedule a **plain function**, no await involved |

## D. Debugging

```python
asyncio.run(main(), debug=True)         # slow callbacks, never-awaited, bad threads
asyncio.current_task()                  # who am I?
asyncio.all_tasks()                     # what's still alive?
task.get_name() / task.set_name()       # name your tasks — tracebacks improve enormously
task.get_coro()                         # what is it actually running?
python -m asyncio                       # an await-capable REPL
PYTHONASYNCIODEBUG=1                    # debug mode via the environment
```

**Name your tasks.** `tg.create_task(fetch(u), name=u)` costs nothing and turns "Task-17 failed" into something you can act on.

## E. The ecosystem, briefly

Async only pays off if the libraries you call are async too. The common replacements:

| Sync | Async |
|---|---|
| `requests` | `httpx`, `aiohttp` |
| `psycopg2` | `asyncpg`, `psycopg` (v3 has async) |
| `sqlite3` | `aiosqlite` |
| `redis-py` (sync) | `redis.asyncio` |
| `open()` | `aiofiles`, or `asyncio.to_thread` |
| Flask / Django (sync) | FastAPI, Starlette, Django async views |
| `asyncio` itself | `anyio`, `trio` — different structured-concurrency designs, worth knowing about |

If exactly one library in your stack is blocking, `asyncio.to_thread` is a perfectly respectable answer. Don't rewrite everything for one call.

---

# The one thing to remember

> ## **There is exactly one worker. `await` marks a point where it is allowed to put your job down and pick up another — and that is the only point where anything switches.**
>
> **Calling an `async def` runs nothing; it builds a plan. `await` waits for one plan. Concurrency comes from `create_task`, `gather`, and `TaskGroup` — never from `await` alone. And one blocking call stops the entire program, because there is only ever one worker.**
>
> **Default to `async with asyncio.TaskGroup()` for fan-out, `asyncio.timeout()` for deadlines, `asyncio.Semaphore` for a cap, and `asyncio.to_thread` for anything that refuses to cooperate.**

That is the whole system. Ask "where does this hand control back, and is there anything else to do while it's away?" and the answer falls out.

And when the concurrency mysteriously isn't there: **time it.** If N jobs take N times as long as one, either you awaited them in a loop, or something is blocking.

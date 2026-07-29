# Sequence Processing — Verb 15: Order

## Introduction

For some problems it isn't just **which elements** you have. It's **the order you handle them in**.

**Order** is about setting up, or holding onto, a processing order that means something.

The question you're asking:

> **"In what sequence should these elements be processed?"**

**Arrange** physically shuffles a collection. **Order** is about the sequence you walk through it in.

---

# Order → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Order**|In what sequence should these elements be processed?|`sorted`, `reversed`, `heapq`, `collections.deque`, `bisect.insort`, `iter`|

> **Note:** In practice **Order** reaches for the same functions as **Arrange**. The split is conceptual: **Arrange** changes how the data is laid out, while **Order** cares about the sequence you traverse it in. In Python that difference usually shows up as a **choice of data structure**, not a choice of function.

---

# Common Ordering Patterns

|Pattern|Python|Example Result|
|---|---|---|
|Process in ascending order|`sorted`|`sorted([4,1,3,2])` → `[1, 2, 3, 4]`|
|Process by a custom key|`key=`|`sorted(people, key=itemgetter("age"))`|
|Process in reverse order|`reversed`|`list(reversed([1,2,3]))` → `[3, 2, 1]`|
|Always take the smallest next|`heapq.heappop`|a priority queue, O(log n) per item|
|Process oldest first (FIFO)|`deque.popleft`|a queue|
|Process newest first (LIFO)|`list.pop`|a stack|
|Take the k best without sorting|`heapq.nsmallest`|`nsmallest(3, xs)` → O(n log k)|
|Keep a list ordered as it grows|`bisect.insort`|`insort(xs, 3.5)`|
|Obtain an iterator for traversal|`iter`|`it = iter(xs)`; `next(it)`|

---

# The Python-specific catches

**Dicts and sets behave differently here.** Since 3.7 a `dict` keeps **insertion order**, so a sorted dict stays sorted. A `set` has **no order whatsoever**. Iterating one gives you some arbitrary sequence, and leaning on it is the kind of bug that stays hidden until the data changes.

**Sorting is often part of the algorithm, not the presentation.** `bisect`, `groupby`, medians and interval merging all need sorted input before they mean anything.

**You rarely need a full sort.** `max()` is O(n), `nlargest(k)` is O(n log k), `sorted()` is O(n log n). Sorting an entire list to grab one element is probably the most common bit of casual waste in Python.

---

# One Sentence to Remember

> **Order decides the sequence you process elements in, and usually you get there by picking the right structure — heap, deque, sorted list — rather than by sorting.**

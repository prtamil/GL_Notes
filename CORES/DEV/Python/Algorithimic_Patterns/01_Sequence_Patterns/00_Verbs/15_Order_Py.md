# Sequence Processing — Verb 15: Order

## Introduction

Some problems depend not only on **which elements** exist, but also on **the sequence in which they are processed**.

**Order** is the act of establishing or preserving a meaningful processing order for a sequence.

The mental question is:

> **"In what sequence should these elements be processed?"**

Unlike **Arrange**, which physically reorders a collection, **Order** is about the logical sequence of processing or traversal.

---

# Order → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Order**|In what sequence should these elements be processed?|`sorted`, `reversed`, `heapq`, `collections.deque`, `bisect.insort`, `iter`|

> **Note:** In practice, **Order** often uses the same functions as **Arrange**. The distinction is conceptual: **Arrange** changes the layout of data, while **Order** emphasizes the sequence in which data is traversed or processed. In Python that difference usually shows up as a **data structure choice** rather than a function call.

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

**Dicts and sets differ here.** Since 3.7 a `dict` preserves **insertion order**, so a sorted dict stays sorted. A `set` has **no order at all** — iterating one gives an arbitrary sequence, and relying on it is a bug that hides until the data changes.

**Ordering is often a precondition, not a presentation step.** `bisect`, `groupby`, median, and interval-merging all require sorted input; sorting there is part of the algorithm.

**Full ordering is rarely needed.** `max()` is O(n), `nlargest(k)` is O(n log k), `sorted()` is O(n log n). Sorting to find one element is the most common casually-wasteful line in Python.

---

# One Sentence to Remember

> **Order determines the logical sequence in which elements are processed — often by choosing the right structure (heap, deque, sorted list) rather than by sorting.**

# Key Performance Metrics: Calculation, Root Causes, and Fixes

_A Practical Performance Engineering Guide_

Performance is not a single number. It is a system of signals that describe **user experience, system capacity, and survivability under load**. Each metric answers a specific question—and when interpreted correctly, points directly to concrete fixes.

This guide explains **what to measure, how to calculate it, what it means when it goes wrong, and what to do about it**.

---

## 1. Latency Metrics

Latency measures **how long work takes**.

---

### 1.1 Average Latency

**How to calculate**

```js
Average latency = sum(response times) / number of requests

```

**Root causes when high**

- General slowness
- Inefficient algorithms
- Slow dependencies
    

**Why it lies**  
Averages hide outliers. One slow request can destroy UX without moving the average.

**How to fix**

- Optimize hot paths
- Cache repeated work
- Remove unnecessary synchronous steps
    

**Rule**

> Never optimize using averages alone.

---

### 1.2 p95 / p99 Latency (Tail Latency)

**How to calculate**

1. Collect response times
2. Sort them
3. Pick the 95th / 99th percentile
    

**Root causes**

- Event loop blocking
- Garbage collection pauses
- Slow DB queries
- Queue buildup
- Thundering herd
    

**Why it matters**  
Tail latency reflects **real user pain**.

**How to fix**

- Eliminate synchronous CPU work
- Add worker threads
- Add timeouts and circuit breakers
- Reduce queue depth
- Pre-warm caches
    






---

### 1.3 Max Latency

**How to calculate**

```js
Max latency = max(response times)

```

**Root causes**

- Deadlocks
- Infinite retries
- Stuck IO
- Resource starvation
    

**How to fix**

- Enforce global timeouts
- Cap retries
- Kill stuck requests
    

---

## 2. Time-Based Metrics

---

### 2.1 Time To First Byte (TTFB)

**How to calculate**

```js
TTFB = time(first byte received) - time(request sent)

```

**Root causes when high**

- Authentication before streaming
- DB queries before response
- CPU-heavy middleware
    

**How to fix**

- Stream responses early
- Move heavy work after headers
- Cache auth and config
- Avoid sync work in middleware
    

---

### 2.2 Total Response Time

**How to calculate**

```js
Total time = last byte received - request sent

```

**Root causes**

- Large payloads
- Slow clients
- Inefficient streaming
- Network congestion
    

**How to fix**

- Compress payloads
- Stream instead of buffering
- Chunk large responses
- Reduce payload size
    

---

### 2.3 Queue Wait Time

**How to calculate**

```js
Queue wait = processing start time - enqueue time

```

**Root causes**

- System overloaded
- Too few workers
- Thread pool exhaustion
    

**How to fix**

- Add workers
- Apply backpressure
- Reject early
- Scale horizontally
    

---

## 3. Throughput Metrics

Throughput measures **how much work you can do per unit time**.

---

### 3.1 Requests per Second (RPS)

**How to calculate**

```js
RPS = total requests / time window

```

**Root causes when capped**

- CPU saturation
- IO bottlenecks
- Lock contention
- Event loop blocking
    

**How to fix**

- Reduce per-request cost
- Add worker threads
- Increase parallelism
- Cache aggressively
    

---

### 3.2 Jobs per Second (Workers)

**How to calculate**

```js
Jobs/sec = completed jobs / time window

```

**Root causes**

- Worker pool too small
- CPU-bound tasks
- Serialization overhead
    

**How to fix**

- Increase worker pool
- Batch jobs
- Reduce payload size
- Use binary formats
    

---

### 3.3 Bytes per Second

**How to calculate**

```js
Bytes/sec = bytes transferred / time

```

**Root causes**

- Small buffer sizes
- TCP window collapse
- Disk IO limits
    

**How to fix**

- Tune buffer sizes
- Use streaming
- Reduce syscall frequency
    

---

## 4. Memory Metrics

Memory metrics determine **whether the system survives load**.

---

### 4.1 RSS Memory

**How to calculate**

```js
RSS = process.memoryUsage().rss

```

**Root causes when growing**

- Buffering instead of streaming
- Native memory leaks
- Unreleased workers
- Open streams
    

**How to fix**

- Stream large data
- Close resources explicitly
- Monitor peak RSS
- Set memory limits
    

---

### 4.2 Heap Used

**How to calculate**

```js
heapUsed = process.memoryUsage().heapUsed

```

**Root causes**

- Retained references
- Unbounded caches
- Event listeners leaks
    

**How to fix**

- Clear references
- Add cache eviction
- Remove listeners
- Profile heap snapshots
    

---

### 4.3 GC Pause Time

**How to calculate**

- Measure stop-the-world duration using runtime metrics
    

**Root causes**

- Large heap
- High allocation churn
- Large objects
    

**How to fix**

- Reduce allocations
- Reuse objects
- Stream data
- Tune heap size
    

---

## 5. CPU & Event Loop Metrics

---

### 5.1 CPU Utilization

**How to calculate**

- OS or process CPU %
    

**Root causes**

- CPU-heavy transforms
- JSON parsing
- Compression/encryption
    

**How to fix**

- Move CPU work to worker threads
- Reduce algorithm complexity
- Cache results
    

---

### 5.2 Event Loop Delay

**How to calculate**

- Measure how late scheduled tasks run
    

**Root causes**

- Blocking loops
- Synchronous CPU work
- GC pauses
    

**How to fix**

- Avoid sync loops
- Use async APIs
- Use workers for CPU tasks
    

---

## 6. Queue & Backpressure Metrics

---

### 6.1 Queue Depth

**How to calculate**

```js
Queue depth = items enqueued - items processed

```

**Root causes**

- Producers faster than consumers
- Missing backpressure
    

**How to fix**

- Apply backpressure
- Slow producers
- Reject excess load
    

---

### 6.2 In-Flight Requests

**How to calculate**

```js
In-flight = started - completed

```

**Root causes**

- Slow processing
- Downstream slowness
    

**How to fix**

- Add concurrency limits
- Timeouts
- Bulkheads
    

---

## 7. Error & Reliability Metrics

---

### 7.1 Error Rate

**How to calculate**

```js
Error rate = failed requests / total requests

```

**Root causes**

- Timeouts
- Resource exhaustion
- Dependency failure
    

**How to fix**

- Circuit breakers
- Graceful degradation
- Retries with limits
    

---

### 7.2 Retry Rate

**How to calculate**

```js
Retry rate = retries / requests

```

**Root causes**

- Hidden downstream failures
- Aggressive retry logic
    

**How to fix**

- Exponential backoff
- Jitter
- Retry budgets
    

---

## 8. SLA Metrics (The Contract Layer)

### What SLA Is Built On

SLAs are defined using:

- p95 / p99 latency
- Error rate
- Availability
    

**Example**

```js
p95 latency < 300ms
Error rate < 0.1%
Availability 99.9%

```

**How to fix SLA violations**

- Reduce tail latency
- Shed load
- Prioritize critical traffic
- Scale before saturation
    

---

## Final Mental Model

- **Latency** → user pain
- **Throughput** → capacity
- **Memory** → survival
- **Queues** → overload
- **CPU / event loop** → responsiveness
- **SLA** → promises you must keep
    

---

## The Golden Rule

> **Every metric exists to point to a fix.  
> If you cannot name the fix, you don’t understand the metric yet.**
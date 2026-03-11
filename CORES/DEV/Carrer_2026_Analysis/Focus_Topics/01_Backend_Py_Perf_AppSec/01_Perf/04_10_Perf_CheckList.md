When experienced engineers face a **slow system**, they rarely jump into code immediately. They follow a disciplined mental checklist. This is what I call the **performance engineer mindset**. If you can explain this in interviews, it signals strong real-world experience.

Below is a practical **10-step checklist** many performance engineers implicitly follow.

---

# 1️⃣ Confirm the Problem Is Real

First verify the slowdown is **not perception**.

Check:

- request latency metrics
    
- error rates
    
- traffic changes
    

Example:

```
Normal latency: 120 ms
Current latency: 700 ms
```

If metrics confirm the issue, continue.

---

# 2️⃣ Identify the Scope

Determine **how widespread the problem is**.

Questions:

- Is one endpoint slow or all endpoints?
    
- Is it happening for all users?
    
- Is it only in production?
    

Example:

```
Only /search endpoint slow
Other APIs normal
```

This narrows the investigation.

---

# 3️⃣ Check Recent Changes

Many incidents come from **recent deployments**.

Look at:

- new code deployments
    
- configuration changes
    
- infrastructure changes
    
- database migrations
    

Often the root cause is found here.

---

# 4️⃣ Look at System Metrics

Check **resource utilization**.

Important metrics:

- CPU usage
    
- memory usage
    
- disk IO
    
- network latency
    

Example interpretation:

```
CPU 20% → probably not CPU bound
CPU 95% → CPU bottleneck
```

This tells you **what resource is stressed**.

---

# 5️⃣ Determine CPU vs IO Bottleneck

This is a key mental split.

Ask:

```
Is the program computing?
or waiting?
```

Examples:

CPU-bound problems:

- heavy computation
    
- encryption
    
- parsing
    

IO-bound problems:

- database queries
    
- network calls
    
- disk access
    

Most backend problems are **IO-bound**.

---

# 6️⃣ Check the Database

Databases are **the most common bottleneck**.

Look for:

- slow queries
    
- missing indexes
    
- locks
    
- large scans
    

Useful tool:

```
EXPLAIN ANALYZE
```

Common issues:

```
N+1 queries
table scans
unoptimized joins
```

---

# 7️⃣ Check External Dependencies

Sometimes your service is fine but **another service is slow**.

Examples:

```
payment API
authentication service
third-party API
```

A slow dependency increases latency for everything that calls it.

---

# 8️⃣ Profile the Application

If the problem is inside your code, profiling reveals it.

Python tools:

```
cProfile
py-spy
perf
flamegraphs
```

Goal:

Find which functions consume **most CPU time**.

Often:

```
10% of code → 90% of runtime
```

---

# 9️⃣ Optimize the Real Bottleneck

Only optimize **after identifying the bottleneck**.

Typical fixes:

- add database indexes
    
- reduce queries
    
- introduce caching
    
- batch requests
    
- reduce serialization
    

Avoid optimizing code that **is not part of the bottleneck**.

---

# 🔟 Measure Again

After optimization, verify improvement.

Example:

```
Before: 700 ms
After: 140 ms
```

If improvement is confirmed, deploy safely.

This step is critical because **assumptions are often wrong**.

---

# The Key Philosophy

Performance engineers follow this rule:

```
measure → understand → optimize → verify
```

Not:

```
guess → optimize → hope
```

---

# A Simple Mental Model You Can Use

When an API is slow, investigate in this order:

```
1. traffic increase
2. database queries
3. external APIs
4. network latency
5. application CPU
```

In practice, **database and external services cause most slowdowns**.

---

# Why This Matters for Your Career Path

Your target profile:

```
Backend + Performance + AppSec
```

This checklist is exactly how **senior backend or performance engineers think** during incidents.

If you can calmly explain this reasoning in interviews, you immediately stand out as someone who understands **real production systems**, not just programming.

---

If you'd like, I can also show you something extremely valuable for your goal:

**A simple architecture pattern used by high-performance Python backends to handle very high traffic (millions of requests/day).**
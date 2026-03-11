These kinds of questions are powerful because they test **how you think about systems**, not just coding. A good interviewer can ask one of these and quickly see if someone really understands backend performance.

I’ll also show **how a strong engineer answers**, so you can practice explaining it in interviews.

---

# 1️⃣ “Your API latency suddenly increased from 100 ms to 800 ms. What do you check first?”

This question tests **debugging strategy**.

A weak answer:

> I would optimize the code.

A strong answer shows **systematic thinking**:

1. Check **recent changes**
    
2. Look at **metrics**
    
    - CPU usage
        
    - memory usage
        
    - request rate
        
3. Check **database performance**
    
    - slow queries
        
4. Check **external services**
    
5. Profile the application
    

Example reasoning you can say:

> First I verify whether the latency increase is due to higher load or a code change. Then I check database slow queries and external API latency because most backend slowdowns come from IO rather than CPU.

Interviewers like this answer because it shows **measurement before optimization**.

---

# 2️⃣ “How would you find the bottleneck in a Python backend service?”

They want to see if you know **profiling**.

Good answer:

Steps:

1. Measure request latency
    
2. Use profiling tools
    
3. Identify hot functions
    

Example tools:

```
cProfile
py-spy
perf
flamegraphs
```

Example reasoning:

> I would profile the application under load and generate a flamegraph to identify where most CPU time is spent. That tells me which functions dominate execution time.

This shows **real engineering practice**.

---

# 3️⃣ “When would you use async vs threads vs processes in Python?”

This tests knowledge of the **GIL and concurrency models**.

Strong explanation:

### Async

Best for **IO-bound tasks**

Example:

```
API calls
database queries
network operations
```

### Threads

Good for **concurrent IO**, but limited by GIL for CPU tasks.

### Processes

Best for **CPU-bound work**

Example:

```
image processing
data transformation
encryption
```

A strong candidate also mentions:

> Python’s GIL prevents true CPU parallelism with threads.

That signals deep understanding.

---

# 4️⃣ “Why is your database often the real bottleneck?”

This question checks **system awareness**.

Good reasoning:

Database operations are slow because they involve:

- disk IO
    
- network latency
    
- locking
    
- large datasets
    

Common issues:

```
N+1 queries
missing indexes
table scans
```

Example explanation:

> Most backend performance problems originate from inefficient database queries rather than CPU-heavy code, so analyzing query plans and indexes is critical.

Interviewers love when candidates mention:

```
EXPLAIN ANALYZE
```

---

# 5️⃣ “If your service handles 100 requests/sec and must handle 10,000 requests/sec, what changes?”

This question tests **scaling thinking**.

A strong answer mentions multiple layers.

### Application layer

- async handling
    
- connection pooling
    

### Caching

- Redis
    
- CDN
    

### Database

- indexing
    
- read replicas
    

### Infrastructure

- horizontal scaling
    
- load balancing
    

Example reasoning:

> First reduce unnecessary database calls using caching. Then scale horizontally with multiple workers and ensure the database layer can handle the load using indexes and read replicas.

This shows **architecture-level thinking**.

---

# 🧠 What These Questions Actually Test

They reveal whether someone understands:

```
measurement
bottlenecks
IO vs CPU
database behavior
scaling systems
```

A strong backend engineer always thinks:

```
observe
measure
analyze
optimize
verify
```

---

# Why This Is Perfect for Your Goal

Your target profile:

```
Backend + Performance + AppSec
```

These questions are exactly where **performance engineers stand out** compared to normal backend developers.

And since you already know:

- C / C++
    
- Python backend
    
- systems thinking
    

you are actually **well positioned to master this area quickly**.

---

If you want, I can also show you something extremely useful for your interviews:

**The “performance engineer mindset” — a 10-step checklist experts use whenever a system is slow.**  
Once you learn it, you can debug almost any backend performance issue.
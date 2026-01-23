## Percentiles (p50, p95, p99) — Short, Accurate Summary

Percentiles describe **latency distribution**, not averages.  
They answer: _“How bad is it for the slowest X% of users?”_

Given latencies (ms), sorted:

```js
[100, 110, 120, 130, 140, 150, 160, 170, 800, 2000]
N = 10

```

### What each percentile means

- **p50 (median)**: 50% of requests are ≤ this value
- **p95**: 95% of requests are ≤ this value
- **p99**: 99% of requests are ≤ this value
    

In your example:

- **p50 = 140ms**
- **p95 = 2000ms**
- **p99 = 2000ms**
    

Average (~379ms) hides the fact that **real users hit 800ms–2s delays**.

---

## How to Calculate Percentiles (Exact Method Used in Most Monitoring Systems)

### Step-by-step

1. **Sort** latencies ascending
2. Compute index
    
```js
index = ceil(percentile × N) - 1   // zero-based index

```
    
3. Take the value at that index
    

> Most monitoring systems use **ceiling (no interpolation)** because it surfaces pain instead of smoothing it.

---

## Manual Calculation (Your Data)

### p50

```js
index = ceil(0.50 × 10) - 1 = 4
value = 140ms

```

### p95

```js
index = ceil(0.95 × 10) - 1 = 9
value = 2000ms

```

### p99

```js
index = ceil(0.99 × 10) - 1 = 9
value = 2000ms

```

---

## Code to Calculate Percentiles (Production-Safe Logic)

### JavaScript / Node.js

```js
function percentile(values, p) {
  if (values.length === 0) return null;

  const sorted = [...values].sort((a, b) => a - b);
  const index = Math.ceil(p * sorted.length) - 1;
  return sorted[Math.max(0, index)];
}

const latencies = [100,110,120,130,140,150,160,170,800,2000];

console.log("p50:", percentile(latencies, 0.50));
console.log("p95:", percentile(latencies, 0.95));
console.log("p99:", percentile(latencies, 0.99));

```

### Python

```py
import math

def percentile(values, p):
    if not values:
        return None
    values = sorted(values)
    index = math.ceil(p * len(values)) - 1
    return values[max(0, index)]

latencies = [100,110,120,130,140,150,160,170,800,2000]

print("p50:", percentile(latencies, 0.50))
print("p95:", percentile(latencies, 0.95))
print("p99:", percentile(latencies, 0.99))

```

---

## When Each Metric Matters (Real Systems)

- **p50** → sanity check (median user)
- **p90 / p95** → what _most_ users feel → _business impact_
- **p99** → tail latency → retries, timeouts, cascading failures
- **Average** → almost useless alone
    

> **Rule of thumb:**  
> If p95 is bad, users complain.  
> If p99 is bad, systems break.

---

## One-line mental model (remember this)

> **Percentiles show pain. Averages hide it.**
# Java Thread Lifecycle (Exact Model)

Java defines **six** thread states in `java.lang.Thread.State`.

You can see them via:

`Thread.getState()`

---

## 1️⃣ **NEW**

### What it means

- Thread object is created
    
- No OS thread yet
    
- `run()` has never executed
    

### How you enter

`Thread t = new Thread(runnable);`

### Key truth

> The thread exists only as a Java object.

---

## 2️⃣ **RUNNABLE**

### What it means

- Thread is **eligible to run**
    
- OS thread exists
    
- May or may not be executing _right now_
    

### How you enter

`t.start();`

### Important nuance

- RUNNABLE includes:
    
    - actually running on CPU
        
    - waiting in OS run queue
        

Java does **not** expose a separate “RUNNING” state.

> RUNNABLE = “ready or running”

---

## 3️⃣ **BLOCKED**

### What it means

- Thread is waiting to acquire a **monitor lock**
    
- Another thread holds the `synchronized` lock
    

### How you enter

`synchronized (obj) { ... }  // lock already held`

### What wakes it

- Lock owner exits synchronized block
    

> BLOCKED is **lock contention**, not sleeping.

---

## 4️⃣ **WAITING**

### What it means

- Thread is waiting **indefinitely**
    
- No timeout
    
- Will resume only when **signaled**
    

### How you enter

- `Object.wait()`
    
- `Thread.join()` (without timeout)
    

### What wakes it

- `notify() / notifyAll()`
    
- Target thread terminates (for `join()`)
    

---

## 5️⃣ **TIMED_WAITING**

### What it means

- Thread is waiting for a **bounded time**
    
- Will resume automatically after timeout
    

### How you enter

- `Thread.sleep(ms)`
    
- `Object.wait(ms)`
    
- `Thread.join(ms)`
    

### What wakes it

- Timeout
    
- Interrupt
    
- Notification (for `wait(ms)`)
    

---

## 6️⃣ **TERMINATED**

### What it means

- Thread has finished execution
    
- Cannot be restarted
    
- OS thread is gone
    

### How you enter

- `run()` returns
    
- Uncaught exception escapes `run()`
    

> TERMINATED is final. No transitions out.

---

# Full Lifecycle Diagram (Memorize This)

`NEW  │  │ start()  ▼ RUNNABLE  │   ▲  │   │ (lock acquired)  │   │  │   ├─────► BLOCKED  │   │          │  │   │          │ (lock released)  │   │          ▼  │   │       RUNNABLE  │   │  │   ├─────► WAITING  │   │          │ notify / join ends  │   │          ▼  │   │       RUNNABLE  │   │  │   ├─────► TIMED_WAITING  │   │          │ timeout / interrupt  │   │          ▼  │   │       RUNNABLE  │  │ run() ends / exception  ▼ TERMINATED`

---

# Lifecycle Triggers (Cheat Table)

|From|Trigger|To|
|---|---|---|
|NEW|`start()`|RUNNABLE|
|RUNNABLE|lock unavailable|BLOCKED|
|BLOCKED|lock acquired|RUNNABLE|
|RUNNABLE|`wait()` / `join()`|WAITING|
|WAITING|`notify()` / target ends|RUNNABLE|
|RUNNABLE|`sleep(ms)`|TIMED_WAITING|
|TIMED_WAITING|timeout|RUNNABLE|
|any|uncaught exception|TERMINATED|
|RUNNABLE|`run()` returns|TERMINATED|

---

# Critical Clarifications (Common Confusions)

### ❌ There is NO `RUNNING` state

Java intentionally hides CPU scheduling details.

---

### ❌ BLOCKED ≠ WAITING

- BLOCKED → waiting for **monitor lock**
    
- WAITING → waiting for **signal**
    

Different problems, different debugging paths.

---

### ❌ Sleeping does NOT release locks

`Thread.sleep()`

- Keeps all locks
    
- Other threads stay BLOCKED
    

---

### ❌ Interrupt does NOT kill a thread

- Interrupt moves thread out of WAITING/TIMED_WAITING
    
- Thread must cooperate
    

---

# How This Helps You Debug

When a thread is “stuck”, ask:

1. **BLOCKED?**  
    → Who owns the lock?
    
2. **WAITING?**  
    → Who should notify?
    
3. **TIMED_WAITING?**  
    → Is sleep/join intentional?
    
4. **RUNNABLE but slow?**  
    → CPU starvation or infinite loop
    

This mental checklist saves hours.

---

## One-Sentence Takeaway

> **Java threads move through six states; understanding which state you’re in tells you exactly what problem you’re debugging.**
## C++ `std::atomic`: Modern C++ Atomic Operations and Memory Ordering

### Introduction

Concurrent programs often involve multiple threads accessing shared data. Without proper synchronization, these accesses can lead to **race conditions**, undefined behavior, and incorrect program results. To address this problem, modern C++ introduced a standardized atomic library in **C++11**, available through the header:

```cpp
#include <atomic>
```

The core abstraction provided by this library is:

```cpp
std::atomic<T>
```

This template allows variables of type `T` to be accessed using **atomic operations**, meaning the operations occur as indivisible steps that cannot be interrupted by other threads.

C++ atomics provide two important guarantees:

1. **Atomicity** – operations on the variable happen as a single indivisible action.
    
2. **Memory ordering control** – the programmer can specify how operations should be ordered across threads.
    

Internally, the compiler maps these atomic operations to **CPU atomic instructions and memory barriers** depending on the architecture.

Conceptually the stack looks like this:

```
C++ Program
   ↓
std::atomic<T>
   ↓
Compiler mapping
   ↓
CPU atomic instructions
   ↓
Hardware memory model
```

This design allows developers to write **portable lock-free code** while still achieving performance close to low-level kernel primitives.

---

# Atomic Types in C++

The central abstraction is the template:

```cpp
std::atomic<T>
```

Example:

```cpp
#include <iostream>
#include <atomic>

int main() {

    std::atomic<int> counter{0};

    counter.store(10);

    int value = counter.load();

    std::cout << "counter = " << value << std::endl;

    return 0;
}
```

Here:

```
store()
load()
```

perform **atomic memory accesses** that are safe across threads.

---

# Basic Atomic Operations

C++ atomics provide several basic operations.

### Load

Reads the value atomically.

```cpp
int value = atomicVar.load();
```

### Store

Writes a value atomically.

```cpp
atomicVar.store(42);
```

### Example

```cpp
#include <iostream>
#include <atomic>
#include <thread>

std::atomic<int> shared_value{0};

void writer() {
    shared_value.store(100);
}

void reader() {
    int value = shared_value.load();
    std::cout << "Read value: " << value << std::endl;
}

int main() {

    std::thread t1(writer);
    std::thread t2(reader);

    t1.join();
    t2.join();

    return 0;
}
```

This prevents **data races** when multiple threads read or write the variable.

---

# Read-Modify-Write Atomic Operations

Some operations must **read and modify a variable in one atomic step**.

C++ provides several **read-modify-write operations**.

Common operations:

```
fetch_add()
fetch_sub()
fetch_or()
fetch_and()
fetch_xor()
exchange()
```

These ensure that the entire operation happens **atomically**.

---

## Example: Atomic Counter

```cpp
#include <iostream>
#include <atomic>
#include <thread>

std::atomic<int> counter{0};

void increment() {

    for (int i = 0; i < 100000; i++) {
        counter.fetch_add(1);
    }

}

int main() {

    std::thread t1(increment);
    std::thread t2(increment);

    t1.join();
    t2.join();

    std::cout << "Final counter: " << counter.load() << std::endl;

    return 0;
}
```

Without atomics, this program would suffer from **race conditions**.

---

# Atomic Exchange

`exchange()` replaces the value atomically and returns the previous value.

Example:

```cpp
#include <iostream>
#include <atomic>

int main() {

    std::atomic<int> lock{0};

    int old = lock.exchange(1);

    std::cout << "Old value: " << old << std::endl;
    std::cout << "New value: " << lock.load() << std::endl;

    return 0;
}
```

This operation is commonly used when implementing **spinlocks**.

---

# Compare and Exchange (CAS)

One of the most powerful primitives in lock-free programming is **Compare-and-Swap (CAS)**.

C++ provides two variants:

```
compare_exchange_strong()
compare_exchange_weak()
```

CAS performs:

```
if (current == expected)
    current = desired
else
    expected = current
```

---

## Complete CAS Example

```cpp
#include <iostream>
#include <atomic>

int main() {

    std::atomic<int> value{10};

    int expected = 10;
    int desired = 20;

    if (value.compare_exchange_strong(expected, desired)) {
        std::cout << "CAS succeeded\n";
    }
    else {
        std::cout << "CAS failed\n";
    }

    std::cout << "Final value: " << value.load() << std::endl;

    return 0;
}
```

CAS forms the foundation of many **lock-free data structures**.

---

# Memory Ordering in C++

Besides atomicity, C++ allows programmers to control **memory ordering behavior**.

Memory ordering defines how operations performed by one thread become visible to others.

C++ defines the following ordering modes:

```
memory_order_relaxed
memory_order_acquire
memory_order_release
memory_order_acq_rel
memory_order_seq_cst
```

These correspond closely to the hardware memory ordering models discussed earlier.

---

# Relaxed Ordering

Relaxed ordering guarantees **atomicity but no ordering constraints**.

Example:

```cpp
#include <iostream>
#include <atomic>
#include <thread>

std::atomic<int> counter{0};

void increment() {

    for (int i = 0; i < 100000; i++) {
        counter.fetch_add(1, std::memory_order_relaxed);
    }

}

int main() {

    std::thread t1(increment);
    std::thread t2(increment);

    t1.join();
    t2.join();

    std::cout << "Counter = " << counter.load() << std::endl;

    return 0;
}
```

Use cases:

- statistics counters
    
- performance metrics
    
- non-synchronization variables
    

---

# Acquire and Release Ordering

Acquire and release are used to implement **thread synchronization**.

### Release

Ensures that all previous writes become visible before the release store.

```
store(memory_order_release)
```

### Acquire

Ensures that subsequent reads happen after the acquire load.

```
load(memory_order_acquire)
```

---

## Producer–Consumer Example

```cpp
#include <iostream>
#include <atomic>
#include <thread>

std::atomic<bool> ready{false};
int data = 0;

void producer() {

    data = 42;

    ready.store(true, std::memory_order_release);

}

void consumer() {

    while (!ready.load(std::memory_order_acquire))
        ;

    std::cout << "Data = " << data << std::endl;

}

int main() {

    std::thread p(producer);
    std::thread c(consumer);

    p.join();
    c.join();

    return 0;
}
```

This establishes a **happens-before relationship**.

---

# Acquire-Release Combined

Some operations both read and write a value.

For these cases:

```
memory_order_acq_rel
```

Example:

```cpp
atomicVar.fetch_add(1, std::memory_order_acq_rel);
```

This ensures:

```
previous writes → visible before operation
future reads → occur after operation
```

---

# Sequential Consistency

The strongest ordering mode is:

```
memory_order_seq_cst
```

This enforces a **single global ordering of operations across all threads**.

Example:

```cpp
#include <iostream>
#include <atomic>

std::atomic<int> x{0};

int main() {

    x.store(1, std::memory_order_seq_cst);

    int value = x.load(std::memory_order_seq_cst);

    std::cout << "Value = " << value << std::endl;

    return 0;
}
```

Sequential consistency is easiest to reason about but may reduce performance because it restricts CPU optimizations.

---

# Checking Lock-Free Guarantees

C++ allows programs to determine whether an atomic type is implemented without locks.

Example:

```cpp
#include <iostream>
#include <atomic>

int main() {

    std::atomic<int> x;

    if (x.is_lock_free()) {
        std::cout << "Lock-free implementation\n";
    } else {
        std::cout << "Uses internal locking\n";
    }

    return 0;
}
```

Most modern CPUs support lock-free atomics for primitive types.

---

# Relationship to CPU Instructions

C++ atomic operations are compiled into architecture-specific instructions.

Examples:

|C++ Operation|x86|ARM|RISC-V|
|---|---|---|---|
|fetch_add|LOCK XADD|LDAXR/STXR|AMOADD|
|exchange|XCHG|SWP|AMOSWAP|
|CAS|CMPXCHG|LDAXR/STXR loop|AMOCAS|
|acquire load|normal load|LDAR|acquire load|
|release store|normal store|STLR|release store|

The compiler automatically selects the correct implementation.

---

# Practical Use Cases of C++ Atomics

C++ atomics are commonly used for:

- lock-free data structures
    
- reference counting
    
- concurrent queues
    
- spinlocks
    
- thread-safe counters
    

Because they map closely to hardware instructions, they allow programs to achieve **high concurrency without heavy locking mechanisms**.

---

# Conclusion

The C++ atomic library provides a powerful abstraction for writing concurrent programs that are both portable and efficient. Using `std::atomic<T>`, developers can perform atomic loads, stores, and read-modify-write operations that map directly to hardware instructions.

In addition to atomicity, C++ provides explicit **memory ordering semantics** such as relaxed, acquire, release, and sequential consistency. These ordering modes allow programmers to control how memory operations become visible across threads while balancing correctness and performance.

By combining atomic operations with carefully chosen memory ordering constraints, C++ enables the construction of efficient synchronization mechanisms and lock-free algorithms that scale across modern multi-core processors.
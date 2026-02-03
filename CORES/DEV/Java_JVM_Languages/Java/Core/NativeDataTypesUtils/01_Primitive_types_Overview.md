# Native Data Types in Java (Primitive Types)

When we say **“native data types”** in Java, we mean **primitive types** — values stored **directly**, not as objects.

---

## 1️⃣ Java Primitive (Native) Types

Java has **8 primitive types**:

### Integer types

- `byte` (8-bit)
    
- `short` (16-bit)
    
- `int` (32-bit) ← **default**
    
- `long` (64-bit)
    

### Floating-point types

- `float` (32-bit)
    
- `double` (64-bit) ← **default**
    

### Character type

- `char` (16-bit, UTF-16 code unit)
    

### Logical type

- `boolean` (true / false)
    

These are the **only true native values** in Java.

---

## 2️⃣ Arrays of Native Types

An array of a primitive type is:

> **One object + one contiguous block of native values**

Examples conceptually:

- `int[]` → contiguous 32-bit integers
    
- `float[]` → contiguous IEEE-754 floats
    
- `char[]` → contiguous UTF-16 units
    

Key properties:

- Fixed size
    
- Zero boxing
    
- Predictable layout
    
- Fast indexed access
    

This is the **closest thing to raw memory** Java exposes safely.

---

## 3️⃣ How array access works

When you access an array element:

- JVM computes an address using:
    
    - base address
        
    - index
        
    - element size
        
- JVM performs a **bounds check**
    
- JVM reads or writes the value
    

The JIT can **eliminate bounds checks** in tight loops when it proves safety.

---

## 4️⃣ How `for-each` works on primitive arrays

The enhanced `for` loop:

> **Does not use iterators** for arrays.

It is compiled into:

- index-based traversal
    
- automatic bounds safety
    

Conceptually:

- Starts at index `0`
    
- Stops at `length - 1`
    
- Reads values sequentially
    

This makes it:

- Safe
    
- Efficient
    
- Read-only friendly

### Important limitation (often misunderstood)

`for-each` gives you a **copy of the value**, not a reference to the slot.

This **does NOT modify the array**:

```java
for (int v : values) {
    v = v * 2; // modifies local copy only
}

```

To modify the array, you must use an index-based loop.

---

### When to use `for-each` on `int[]`

Use it when:

- You only **read** values
    
- You want **clarity and safety**
    
- You don’t need the index
    

Avoid it when:

- You need to update elements
    
- You need the index
    
- You need conditional jumps by position
    

---

## 5️⃣ Out-of-bounds access (very important)

Java arrays are **always bounds-checked**.

If you access:

- index < 0
    
- index ≥ array length
    

The JVM throws:

> **`ArrayIndexOutOfBoundsException`**

Why this matters:

- Prevents memory corruption
    
- Guarantees safety
    
- Makes Java memory-safe by design
    

This check is **non-negotiable**.

---

## 6️⃣ Performance truth (senior insight)

- Bounds checks exist
    
- But the JIT often removes them
    
- Unsafe access is not allowed
    
- Safety beats undefined behavior
    

This is why Java can do **high-performance native-style code** without crashes.

---

## 7️⃣ Mental model to lock in

> Primitive types = native values  
> Primitive arrays = native memory  
> for-each = safe sequential access  
> Out-of-bounds = immediate failure, never corruption
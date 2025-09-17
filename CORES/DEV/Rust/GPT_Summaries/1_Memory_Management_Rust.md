## 🦀 **Rust Memory Management Cheat Sheet**

### ✅ **Core mental model**

> Always think:

- **Who owns what?**
- **Who borrows what?**
- **For how long?** (lifetimes)

---

### 🧰 **Ownership**

- Every value has exactly **one owner** 
- When ownership is transferred (move), the previous owner can’t use the value anymore
- Value is automatically dropped (freed) when owner goes out of scope

Example:

```rust
let s = String::from("hello"); // s owns the String
let t = s;                     // ownership moved to t
// println!("{}", s); // error: s no longer owns the String

```
---

### 📌 **Borrowing**

- Use references to let others access data **without taking ownership**
- Immutable borrow: `&T` (many allowed)
- Mutable borrow: `&mut T` (only one allowed, exclusive)

Example:
```rust
let mut s = String::from("hi");

let r1 = &s;      // ok
let r2 = &s;      // ok
// let r3 = &mut s; // error: cannot borrow mutably while immutable borrows exist

```
---

### ⏳ **Lifetimes**

- Lifetimes tell the compiler _how long references must be valid_
- `'a`, `'static`, etc.

Example:
```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}


```
- `'a` ensures the return value won’t outlive both `x` and `y`.
    

---

### 📦 **Heap allocation and sharing**

|Type|Purpose|Owners|Thread-safe|
|---|---|---|---|
|`Box<T>`|Owned, heap-allocated value|Single owner|✔️ (but not `Sync` by itself)|
|`Rc<T>`|Reference-counted shared ownership|Multiple owners, single thread|❌|
|`Arc<T>`|Atomically reference-counted|Multiple owners, multi-thread|✔️|

---

### 🛡️ **Interior mutability**

|Type|What it gives|When to use|
|---|---|---|
|`RefCell<T>`|Mutate data through immutable reference, checked at runtime|Single-threaded|
|`Mutex<T>`|Safe mutable access between threads|Multi-threaded|
|`Cell<T>`|Copy types, fast interior mutability|Single-threaded, small types|

---

### ⚡ **Error handling**

- Use `Result<T, E>` for recoverable errors
- Use `Option<T>` for optional / missing data
- Use `?` operator to propagate errors easily

---

### 🧩 **Thinking checklist**

✅ Should this function **own** the data, or **borrow** it?  
✅ Do I need **mutable access**?  
✅ What **lifetime** is required?  
✅ Am I cloning when I could just borrow?  
✅ Is shared ownership needed (`Rc` / `Arc`)?

---

### 🌱 **Extra tips**

- Everything is immutable by default → make mutable only when needed
- Avoid unnecessary clones → prefer borrowing
- Use iterators (`.iter()`, `.into_iter()`, etc.) instead of manual loops
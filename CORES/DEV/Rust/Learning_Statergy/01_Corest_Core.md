I like this approach—you’re basically asking for **“read code → infer rules → confirm with theory”**, which is exactly how Rust starts to click.

I’ll keep each concept tight: **code first, then the mental model**.

---

# 🧠 1. Ownership

### Code

```rust
fn main() {
    let s1 = String::from("hello");
    let s2 = s1;

    // println!("{}", s1); // ❌ error: value borrowed after move
    println!("{}", s2);
}
```

### What’s happening

- `String` is **heap allocated**
    
- When you assign `s1 → s2`, Rust **moves ownership**
    
- `s1` becomes invalid
    

### Mental model

> At any time, **only ONE owner** of data exists.

Think:

```
s1 ----> "hello"
s2 = s1

After move:
s1 (invalid)
s2 ----> "hello"
```

---

# 🔁 2. Borrowing (`&` and `&mut`)

### Code (immutable borrow)

```rust
fn main() {
    let s = String::from("hello");

    print_len(&s);

    println!("{}", s); // still valid
}

fn print_len(s: &String) {
    println!("Length: {}", s.len());
}
```

### Code (mutable borrow)

```rust
fn main() {
    let mut s = String::from("hello");

    change(&mut s);

    println!("{}", s);
}

fn change(s: &mut String) {
    s.push_str(" world");
}
```

### Rules (VERY important)

- Many `&` (read-only) allowed
    
- Only ONE `&mut` (write)
    
- Cannot mix `&` and `&mut` at same time
    

### Mental model

> Borrowing = “temporary access without ownership”

---

# ⚖️ 3. Move vs Copy

### Code (move)

```rust
fn main() {
    let s1 = String::from("hello");
    let s2 = s1;

    // s1 is invalid
}
```

### Code (copy)

```rust
fn main() {
    let x = 10;
    let y = x;

    println!("x = {}, y = {}", x, y); // both valid
}
```

### Why?

- `String` → **Move** (heap, expensive)
    
- `i32` → **Copy** (stack, cheap)
    

### Mental model

> If data is small and fixed → Copy  
> If data owns heap memory → Move

---

# 🧱 4. Structs & Enums

### Struct

```rust
struct User {
    name: String,
    age: u32,
}

fn main() {
    let user = User {
        name: String::from("Tamil"),
        age: 25,
    };

    println!("{}", user.name);
}
```

---

### Enum

```rust
enum Status {
    Success,
    Error,
}

fn main() {
    let s = Status::Success;

    match s {
        Status::Success => println!("ok"),
        Status::Error => println!("fail"),
    }
}
```

---

### Enum with data (very important)

```rust
enum Message {
    Text(String),
    Number(i32),
}

fn main() {
    let m = Message::Text(String::from("hello"));

    match m {
        Message::Text(msg) => println!("{}", msg),
        Message::Number(n) => println!("{}", n),
    }
}
```

### Mental model

> Enum = “one of many possible types”

Rust enums are like:

- tagged unions (C)
    
- algebraic data types (functional languages)
    

---

# ❗ 5. Result & Option

These are **core to Rust error handling**

---

## Option (value may or may not exist)

```rust
fn main() {
    let x = Some(5);
    let y: Option<i32> = None;

    match x {
        Some(v) => println!("value = {}", v),
        None => println!("no value"),
    }
}
```

### Mental model

> Instead of null → explicit “maybe”

---

## Result (success or failure)

```rust
fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        Err(String::from("division by zero"))
    } else {
        Ok(a / b)
    }
}

fn main() {
    let res = divide(10, 2);

    match res {
        Ok(v) => println!("result = {}", v),
        Err(e) => println!("error = {}", e),
    }
}
```

---

### Cleaner way (`?` operator)

```rust
fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        return Err(String::from("error"));
    }
    Ok(a / b)
}
```

---

### Mental model

> Rust forces you to **handle errors explicitly**

No hidden exceptions.

---

# 🔥 Final Intuition (this is what ties everything together)

Rust is basically enforcing:

1. **Who owns data?**
    
2. **Who can access it right now?**
    
3. **Can this fail? Handle it.**
    

If you internalize these 3, Rust becomes predictable.

---

# 🧭 What to do next (important)

Don’t reread this.

Instead:

- Modify examples
    
- Break them intentionally
    
- Trigger compiler errors
    

That’s how Rust teaches you.

---

If you want, next step I can:  
👉 give **one real mini project** using ALL these concepts together (that’s where understanding locks in)
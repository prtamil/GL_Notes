
# C++ Value Categories — lvalue, rvalue, glvalue, prvalue, xvalue

Modern C++ value categories are easiest to understand using two properties:

1. **Identity**
    
2. **Movability**
    

Since C++11, expressions are classified based on these two questions:

```text
Does this expression identify a specific object?
Can this expression be moved from?
```

---

## 1. Identity

An expression has **identity** when it refers to a specific object or function that can be distinguished from another one.

Example:

```cpp
int x = 10;
```

The expression:

```cpp
x
```

refers to a specific object.

Its address can be observed:

```cpp
&x;
```

So `x` has identity.

A useful mental model is:

```text
identity = "this particular object"
```

---

## 2. Movability

An expression is move-eligible when C++ is allowed to transfer resources from the object it refers to.

Example:

```cpp
std::string s = "hello";

std::move(s);
```

`std::move(s)` means conceptually:

```text
The object still exists,
but its resources may now be transferred.
```

Important:

```text
std::move() does not move anything by itself.
```

It performs a cast that converts an expression into an **xvalue**.

A move constructor or move assignment operator may then perform the actual resource transfer.

---

# Core Two-Axis Model

The complete value-category system can be derived from two properties:

|Identity|Move-eligible|Category|
|---|--:|---|
|Yes|No|`lvalue`|
|Yes|Yes|`xvalue`|
|No|Yes|`prvalue`|
|No|No|Not used|

Or visually:

```text
                         Move-eligible

                      YES             NO
                +---------------+---------------+
                |               |               |
Has identity    |    xvalue     |    lvalue     |
YES             |               |               |
                +---------------+---------------+
                |               |               |
Has identity    |    prvalue    |   not used    |
NO              |               |               |
                +---------------+---------------+
```

This table is the foundation of modern C++ value categories.

---

# 3. lvalue

An **lvalue** is an expression that has identity.

Typical examples:

```cpp
int x = 10;

x;
```

`x` refers to a persistent object.

Properties:

```text
identity      : yes
move-eligible : no
```

Examples of lvalue expressions:

```cpp
x
obj.member
*ptr
arr[3]
```

You can usually take the address of an lvalue:

```cpp
int x = 10;

&x;
```

A useful mental model:

```text
lvalue = expression referring to an identifiable object
```

---

## lvalue Does Not Mean "Assignable"

The old explanation:

```text
lvalue = something that can appear on the left side of =
```

is incomplete.

Example:

```cpp
const int x = 10;
```

`x` is still an lvalue.

But:

```cpp
x = 20;   // error
```

So:

```text
lvalue != assignable
```

The important property is **identity**.

---

# 4. prvalue

`prvalue` means:

```text
pure rvalue
```

A prvalue normally represents a newly computed or produced value.

Examples:

```cpp
42
3.14
x + y
std::string("hello")
```

Example:

```cpp
int x = 10 + 20;
```

The expression:

```cpp
10 + 20
```

is a prvalue.

Properties:

```text
identity      : no
move-eligible : yes
```

Conceptually:

```text
10 + 20
   |
   v
produce value
   |
   v
  30
```

A useful mental model:

```text
prvalue = a value being produced
```

---

# 5. xvalue

`xvalue` means:

```text
expiring value
```

An xvalue has identity, but its resources may be moved.

The most common example is:

```cpp
std::move(x)
```

Example:

```cpp
std::string name = "Tamil";

std::string other = std::move(name);
```

Before the cast:

```cpp
name
```

is an lvalue.

After:

```cpp
std::move(name)
```

the expression is an xvalue.

Properties:

```text
identity      : yes
move-eligible : yes
```

The object `name` still exists.

So it has identity.

But C++ is now allowed to transfer its internal resources.

Conceptually:

```text
name
 |
 | std::move
 v
std::move(name)
 |
 v
xvalue
 |
 v
resources may be moved
```

A useful mental model:

```text
xvalue = identifiable object whose resources may be reused
```

---

# 6. glvalue

`glvalue` means:

```text
generalized lvalue
```

A glvalue is any expression that has identity.

Therefore:

```text
glvalue = lvalue + xvalue
```

Diagram:

```text
glvalue
   |
   +-- lvalue
   |
   +-- xvalue
```

Both lvalues and xvalues identify existing objects.

The defining property is:

```text
glvalue = has identity
```

---

# 7. rvalue

In modern C++, an rvalue is any expression that can be moved from.

Therefore:

```text
rvalue = prvalue + xvalue
```

Diagram:

```text
rvalue
   |
   +-- xvalue
   |
   +-- prvalue
```

The defining property is:

```text
rvalue = move-eligible
```

An rvalue may still have identity.

That is why `xvalue` belongs to both:

```text
glvalue
and
rvalue
```

---

# Complete Value Category Hierarchy

The complete modern C++ hierarchy is:

```text
                         expression
                       /            \
                      /              \
                 glvalue            rvalue
                /      \            /     \
               /        \          /       \
          lvalue        xvalue          prvalue
```

The important overlap is:

```text
                 glvalue             rvalue
                    \                 /
                     \               /
                      \             /
                         xvalue
```

An xvalue belongs to both categories because it has:

```text
identity + move eligibility
```

---

# W-Shaped Value Category Diagram

A useful representation is:

```text
                 glvalue               rvalue
                 /    \                /    \
                /      \              /      \
           lvalue       xvalue       prvalue
              \           |           /
               \          |          /
                \         |         /
                 \        |        /
                  \       |       /
                   \      |      /
                    \     |     /
                     \    |    /
                      \   |   /
                       \  |  /
                        \ | /
                         \|/
```

A cleaner conceptual version:

```text
               has identity        can move from
                    |                   |
                    v                   v

                 glvalue             rvalue
                 /    \              /    \
            lvalue    xvalue        /    prvalue
                        \___________/
```

---

# The Best Mental Model

Do not memorize five unrelated definitions.

Memorize three primary categories:

|Category|Identity|Move-eligible|
|---|--:|--:|
|`lvalue`|Yes|No|
|`xvalue`|Yes|Yes|
|`prvalue`|No|Yes|

Then derive the grouped categories:

```text
glvalue = lvalue + xvalue
rvalue  = xvalue + prvalue
```

Or:

```text
lvalue
identity : yes
movable  : no

xvalue
identity : yes
movable  : yes

prvalue
identity : no
movable  : yes
```

---

# Practical Example

Consider:

```cpp
std::string s = "hello";
```

## `s`

```cpp
s
```

is an lvalue.

```text
identity      : yes
move-eligible : no
```

---

## `std::move(s)`

```cpp
std::move(s)
```

is an xvalue.

```text
identity      : yes
move-eligible : yes
```

The object still exists, but its resources may be transferred.

---

## Temporary Object

```cpp
std::string("hello")
```

is a prvalue.

```text
identity      : no
move-eligible : yes
```

It represents a newly produced value.

---

# Reference Binding

Value categories are especially important because reference binding depends on them.

Consider:

```cpp
void process(const std::string& s);
void process(std::string&& s);
```

Now:

```cpp
std::string x = "hello";
```

Calling:

```cpp
process(x);
```

uses the lvalue overload:

```cpp
process(const std::string&);
```

because:

```text
x = lvalue
```

Calling:

```cpp
process(std::move(x));
```

can use:

```cpp
process(std::string&&);
```

because:

```text
std::move(x) = xvalue = rvalue
```

Calling:

```cpp
process(std::string("hello"));
```

can also use:

```cpp
process(std::string&&);
```

because:

```text
std::string("hello") = prvalue = rvalue
```

This distinction is one of the foundations of **move semantics**.

---

# About the Address-of Operator

A useful observation is:

```cpp
int x = 10;

&x;
```

works because `x` is an lvalue.

But:

```cpp
&42;
```

does not work because `42` is a prvalue.

Still, this is only a useful observation.

The formal way to think about lvalues is:

```text
lvalue = expression with identity
```

---

# Compact i / m Notation

A useful shorthand is:

```text
i = has identity
m = move-eligible

I = no identity
M = not move-eligible
```

Then:

|Notation|Meaning|Category|
|---|---|---|
|`iM`|identity + not movable|`lvalue`|
|`im`|identity + movable|`xvalue`|
|`Im`|no identity + movable|`prvalue`|
|`IM`|no identity + not movable|not used|

So:

```text
iM -> lvalue
im -> xvalue
Im -> prvalue
```

The generalized categories become:

```text
glvalue = i*
        = lvalue + xvalue

rvalue  = *m
        = xvalue + prvalue
```

---

# W-Shape Using i / m Notation

```text
          iM              im              Im
        lvalue          xvalue          prvalue
           \              / \              /
            \            /   \            /
             \          /     \          /
              glvalue           rvalue
```

Where:

```text
iM = identity + not movable
im = identity + movable
Im = no identity + movable
```

---

# Important Correction

This is correct:

```text
iM -> lvalue
im -> xvalue
Im -> prvalue
```

This would be incorrect:

```text
iM -> xvalue
```

because an xvalue requires both:

```text
identity      : yes
move-eligible : yes
```

Therefore:

```text
im -> xvalue
```

---

# One Important Subtlety

Do not interpret:

```text
lvalue = cannot ever be moved
```

too literally.

An lvalue can be explicitly converted into an xvalue:

```cpp
std::string s = "hello";

std::move(s);
```

So:

```text
s
```

is an lvalue expression.

But:

```text
std::move(s)
```

is an xvalue expression.

The underlying object is the same.

What changed is the **value category of the expression**.

This is extremely important:

```text
value categories describe expressions,
not objects themselves.
```

---

# Interview Answer

A concise senior-level answer:

> Since C++11, value categories classify expressions using two main properties: identity and move eligibility. An lvalue has identity, a prvalue produces a value without identity, and an xvalue has identity but represents an object whose resources may be moved. A glvalue is an lvalue or xvalue, so it has identity. An rvalue is a prvalue or xvalue, so it is move-eligible. These categories are fundamental to reference binding, overload resolution, move semantics, and perfect forwarding.

---

# Final Memory Map

```text
                         EXPRESSION
                             |
                 +-----------+-----------+
                 |                       |
              GLVALUE                  RVALUE
           has identity             move-eligible
             /     \                 /      \
            /       \               /        \
       LVALUE       XVALUE         /        PRVALUE
        iM            im          /            Im
                       \_________/
```

Memorize:

```text
lvalue  = identity
xvalue  = identity + movable
prvalue = movable

glvalue = lvalue + xvalue
rvalue  = xvalue + prvalue
```

And remember the most important rule:

```text
VALUE CATEGORIES CLASSIFY EXPRESSIONS, NOT OBJECTS.
```

This entire system exists mainly to support:

```text
reference binding
        +
overload resolution
        +
move semantics
        +
perfect forwarding
```

This version should paste cleanly into a `.md` file and still remain easy to revise later.
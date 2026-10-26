
# C++ Value Categories Explained Through Examples

The easiest way to understand C++ value categories is to stop thinking of them as abstract names and instead ask:

```text
What kind of expression am I looking at?
```

Modern C++ mainly uses these categories:

```text
lvalue
xvalue
prvalue

glvalue = lvalue + xvalue
rvalue  = xvalue + prvalue
```

The three concrete categories to recognize are:

|Category|Has identity|Move-eligible|
|---|--:|--:|
|`lvalue`|Yes|No|
|`xvalue`|Yes|Yes|
|`prvalue`|No|Yes|

The other two are grouped categories:

```text
glvalue = anything with identity
rvalue  = anything move-eligible
```

---

# 1. lvalue

An lvalue is an expression that refers to an identifiable object.

Example:

```cpp
int x = 10;
```

Now:

```cpp
x
```

is an lvalue expression.

Why?

Because `x` refers to a specific object.

```cpp
&x;     // valid
x = 20;
```

Conceptually:

```text
x
|
v
specific int object in memory
```

So:

```text
identity      : yes
move-eligible : no
```

---

## More lvalue Examples

### Named variable

```cpp
int x = 10;

x;
```

`x` is an lvalue.

---

### Dereferenced pointer

```cpp
int x = 10;
int* p = &x;

*p;
```

`*p` is an lvalue because it identifies the object `x`.

```text
p
|
v
address
|
v
*p  ---> x
```

---

### Array element

```cpp
int a[3] = {10, 20, 30};

a[1];
```

`a[1]` is an lvalue.

It refers to one particular array element.

---

### Object member

```cpp
struct User {
    int age;
};

User u;

u.age;
```

`u.age` is an lvalue.

It identifies the `age` member inside `u`.

---

# 2. prvalue

A prvalue is normally an expression that produces a value.

Example:

```cpp
42
```

The literal `42` is a prvalue.

It represents a produced value, not an existing named object.

```text
42
|
v
produced integer value
```

Properties:

```text
identity      : no
move-eligible : yes
```

---

## Arithmetic Expression

```cpp
int x = 10;
int y = 20;

x + y;
```

`x + y` is a prvalue.

The expression computes and produces a new value:

```text
x = 10
y = 20

x + y
  |
  v
 30
```

The variables `x` and `y` are lvalues.

But:

```cpp
x + y
```

is a prvalue.

This is an important distinction.

---

## Literal

```cpp
100;
3.14;
true;
```

These are prvalues.

They represent values being produced.

---

## Temporary Object

```cpp
std::string("hello");
```

This expression is a prvalue.

Conceptually:

```text
construct std::string
        |
        v
temporary value
```

Example:

```cpp
std::string s = std::string("hello");
```

The temporary expression:

```cpp
std::string("hello")
```

is a prvalue.

---

## Function Returning by Value

```cpp
std::string make_name()
{
    return "Tamil";
}
```

Calling:

```cpp
make_name();
```

produces a `std::string` value.

Therefore:

```text
make_name()
```

is a prvalue expression.

---

# 3. xvalue

An xvalue means:

```text
expiring value
```

It refers to an identifiable object whose resources may be moved.

The most common example is:

```cpp
std::move(x)
```

Example:

```cpp
std::string name = "Tamil";
```

The expression:

```cpp
name
```

is an lvalue.

But:

```cpp
std::move(name)
```

is an xvalue.

---

## Why?

`name` still refers to a specific object.

Therefore:

```text
identity = yes
```

But `std::move(name)` tells C++ that the object's resources may be transferred.

Therefore:

```text
move-eligible = yes
```

So:

```text
identity + movable
        |
        v
      xvalue
```

---

## Full Example

```cpp
std::string a = "hello";

std::string b = std::move(a);
```

Before:

```text
a
|
v
"hello"
```

Expression:

```cpp
a
```

is an lvalue.

Then:

```cpp
std::move(a)
```

converts the expression into an xvalue.

Conceptually:

```text
a
|
| std::move
v
xvalue
|
v
resources may be transferred
```

The move constructor may now take ownership of the internal buffer.

After the move:

```text
a still exists
```

but its state is valid but unspecified.

---

# Important: `std::move()` Does Not Move

This is one of the most important facts.

```cpp
std::move(x)
```

does not physically move anything.

It behaves roughly like a cast:

```cpp
static_cast<T&&>(x)
```

Its job is:

```text
lvalue
  |
  | std::move
  v
xvalue
```

The actual move happens later if a move constructor or move assignment operator is called.

---

# 4. glvalue

`glvalue` means:

```text
generalized lvalue
```

A glvalue is any expression that has identity.

Therefore:

```text
glvalue = lvalue + xvalue
```

Example:

```cpp
std::string s = "hello";
```

Both of these expressions are glvalues:

```cpp
s
std::move(s)
```

Why?

Because both refer to the same identifiable object `s`.

But their specific categories are different:

```text
s             -> lvalue
std::move(s)  -> xvalue
```

Both have identity.

Therefore both are glvalues.

---

## Visual Example

```text
              glvalue
             /       \
            /         \
         lvalue      xvalue
            |           |
            |           |
            s      std::move(s)
```

---

# 5. rvalue

An rvalue is any expression that is move-eligible.

Therefore:

```text
rvalue = prvalue + xvalue
```

Examples:

```cpp
42
```

is a prvalue and therefore also an rvalue.

And:

```cpp
std::move(x)
```

is an xvalue and therefore also an rvalue.

Diagram:

```text
              rvalue
             /      \
            /        \
        xvalue      prvalue
           |           |
    std::move(x)      42
```

---

# Complete Example

Consider:

```cpp
std::string a = "one";
std::string b = "two";

std::string c = a;
std::string d = std::move(b);

std::string e = a + b;
```

Now classify each expression.

---

## `a`

```cpp
a
```

is an lvalue.

```text
identity      : yes
move-eligible : no
```

It refers to the named object `a`.

---

## `b`

```cpp
b
```

is also an lvalue.

Named variables are lvalue expressions.

---

## `std::move(b)`

```cpp
std::move(b)
```

is an xvalue.

```text
identity      : yes
move-eligible : yes
```

It still refers to the object `b`, but its resources may be transferred.

---

## `a + b`

For `std::string`:

```cpp
a + b
```

produces a new string value.

So:

```text
a + b
```

is a prvalue.

---

# Side-by-Side Example

Consider:

```cpp
std::string s = "hello";
```

These three expressions show the entire system:

```cpp
s
std::move(s)
std::string("world")
```

Classification:

|Expression|Category|Identity|Movable|
|---|---|--:|--:|
|`s`|lvalue|Yes|No|
|`std::move(s)`|xvalue|Yes|Yes|
|`std::string("world")`|prvalue|No|Yes|

This is the most useful table to memorize.

---

# Reference Binding Example

Value categories become very important with references.

Consider:

```cpp
void f(const std::string& s)
{
}

void f(std::string&& s)
{
}
```

Now:

```cpp
std::string name = "Tamil";
```

---

## Passing an lvalue

```cpp
f(name);
```

`name` is an lvalue.

So it binds to:

```cpp
const std::string&
```

---

## Passing an xvalue

```cpp
f(std::move(name));
```

`std::move(name)` is an xvalue.

It is also an rvalue.

So it can bind to:

```cpp
std::string&&
```

---

## Passing a prvalue

```cpp
f(std::string("Tamil"));
```

The temporary string is a prvalue.

A prvalue is also an rvalue.

Therefore it can bind to:

```cpp
std::string&&
```

---

# Visual Reference Binding

```text
name
 |
 v
lvalue
 |
 v
const T&


std::move(name)
 |
 v
xvalue
 |
 v
T&&


T("temporary")
 |
 v
prvalue
 |
 v
T&&
```

---

# Function Return Examples

Function return type can also help create different expression categories.

---

## Return by Value

```cpp
std::string get_name()
{
    return "Tamil";
}
```

Expression:

```cpp
get_name()
```

is a prvalue.

---

## Return by lvalue Reference

```cpp
std::string global_name = "Tamil";

std::string& get_name()
{
    return global_name;
}
```

Expression:

```cpp
get_name()
```

is an lvalue.

Because it refers to the existing object `global_name`.

---

## Return by rvalue Reference

```cpp
std::string&& get_name(std::string& s)
{
    return std::move(s);
}
```

Calling:

```cpp
get_name(s)
```

produces an xvalue expression.

So:

```text
return T      -> prvalue
return T&     -> lvalue
return T&&    -> xvalue
```

This is a very useful interview rule.

---

# Named rvalue Reference Surprise

Consider:

```cpp
void process(std::string&& s)
{
}
```

Inside the function:

```cpp
s
```

is an lvalue expression.

This surprises many C++ developers.

Even though its type is:

```cpp
std::string&&
```

the expression:

```cpp
s
```

has a name.

Therefore it is an lvalue.

So this:

```cpp
void process(std::string&& s)
{
    consume(s);
}
```

passes an lvalue.

To pass it onward as an rvalue:

```cpp
void process(std::string&& s)
{
    consume(std::move(s));
}
```

Now:

```cpp
std::move(s)
```

is an xvalue.

This gives an important rule:

```text
A named rvalue reference is an lvalue expression.
```

---

# Object vs Expression

This distinction is critical.

Do not say:

```text
this object is an lvalue
```

More accurately:

```text
this expression is an lvalue
```

Example:

```cpp
std::string s = "hello";
```

The same object `s` can be referred to by different expressions.

Expression:

```cpp
s
```

is an lvalue.

Expression:

```cpp
std::move(s)
```

is an xvalue.

Same object.

Different expression category.

Diagram:

```text
                    same object
                        s
                       / \
                      /   \
                     /     \
                    v       v

                  s       std::move(s)

               lvalue       xvalue
```

So:

```text
VALUE CATEGORY BELONGS TO THE EXPRESSION,
NOT TO THE OBJECT.
```

---

# All Categories Together

```text
                         EXPRESSION
                             |
                 +-----------+-----------+
                 |                       |
              GLVALUE                  RVALUE
           has identity             move-eligible
             /     \                 /      \
            /       \               /        \
       LVALUE       XVALUE---------+        PRVALUE
         |             |                       |
         |             |                       |
         x        std::move(x)                42
```

Another view:

```text
lvalue
identity ✓
movable  ✗

xvalue
identity ✓
movable  ✓

prvalue
identity ✗
movable  ✓
```

Then:

```text
glvalue = lvalue + xvalue

rvalue = xvalue + prvalue
```

---

# Easy Recognition Rules

When you see a named variable:

```cpp
x
```

think:

```text
lvalue
```

When you see:

```cpp
std::move(x)
```

think:

```text
xvalue
```

When you see:

```cpp
42
x + y
T{}
T(...)
function_returning_T()
```

think:

```text
prvalue
```

---

# Quick Example Table

|Expression|Category|
|---|---|
|`x`|lvalue|
|`*ptr`|lvalue|
|`arr[0]`|lvalue|
|`obj.member`|lvalue|
|`std::move(x)`|xvalue|
|function returning `T&&`|xvalue|
|`42`|prvalue|
|`x + y`|prvalue|
|`T{}`|prvalue|
|function returning `T`|prvalue|
|function returning `T&`|lvalue|

---

# Final Mental Model

The easiest way to remember everything is:

```text
lvalue
"I have identity."

xvalue
"I have identity, but you may steal my resources."

prvalue
"I am a produced value."
```

Then:

```text
glvalue
= anything with identity

rvalue
= anything whose resources/value may be consumed
```

Or in one diagram:

```text
                        expression

                  identity       movable
                     |              |
                     v              v

                  glvalue        rvalue
                  /    \         /    \
             lvalue    xvalue---+    prvalue
                |         |              |
                x    std::move(x)        42
```

The single most important sentence to remember is:

```text
C++ value categories describe expressions,
not the underlying objects.
```

This example-driven version is probably the better one to revise before interviews, while the earlier one works better as the formal reference.
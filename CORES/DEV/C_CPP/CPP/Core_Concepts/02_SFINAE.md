# SFINAE — Substitution Failure Is Not An Error

**SFINAE** is a C++ template rule: when the compiler substitutes template arguments and the resulting type/expression is invalid, it **does not immediately produce a compilation error**. Instead, that template candidate is removed from overload resolution.

```cpp
template <typename T>
auto size(const T& x) -> decltype(x.size())
{
    return x.size();
}
```

For:

```cpp
std::vector<int> v;
size(v);        // OK: v.size() is valid
```

But:

```cpp
int x = 10;
size(x);        // substitution fails → candidate removed
```

Mental model:

```text
Template candidate
      │
      ▼
Substitute T
      │
      ▼
Is resulting declaration valid?
     / \
   YES  NO
    │    │
    │    └── candidate removed (SFINAE)
    ▼
candidate participates
in overload resolution
```

Historically, SFINAE was heavily used with `std::enable_if`, `decltype`, and `std::void_t`:

```cpp
template<typename T,
         std::enable_if_t<std::is_integral_v<T>, int> = 0>
void process(T x);
```

### Modern C++20+

For most application code, prefer **Concepts + `requires`**:

```cpp
template<typename T>
requires std::integral<T>
void process(T x)
{
}
```

or:

```cpp
template<std::integral T>
void process(T x)
{
}
```

So the evolution to remember is:

```text
C++11/14  → enable_if + SFINAE
C++17     → void_t / if constexpr
C++20+    → Concepts + requires
```

**Interview definition:** SFINAE means an invalid substitution into a template's immediate context removes that candidate from overload resolution instead of making the program immediately ill-formed. In modern C++, Concepts and `requires` provide a clearer way to express most such constraints.

## Copy Ellision

**Elision** means **omission** — something that would normally happen is skipped.

In C++, **copy elision** means the compiler/language avoids creating unnecessary intermediate objects, so the related **copy or move operation does not happen**.

```cpp
Widget makeWidget() {
    return Widget{};
}

Widget w = makeWidget();
```

Without elision, you might imagine:

```text
temporary Widget
      ↓ move/copy
return object
      ↓ move/copy
w
```

With copy elision:

```text
storage for w
     ↑
construct Widget directly here
```

So copy elision is not “faster copying.” It means **no copy/move is performed at all**.

The two important forms are:

- **RVO** — returning an unnamed temporary/prvalue.
    
- **NRVO** — returning a named local object.
    

Since C++17, important prvalue/RVO cases are guaranteed by the language, while NRVO is still generally optional.

```text
                 COPY ELISION
        "elision" = omission / skipping
                       │
          ┌────────────┴────────────┐
          │                         │
         RVO                       NRVO
          │                         │
 return Widget{};              Widget w;
                               return w;
          │                         │
 construct directly           construct directly
 in destination               if NRVO is applied
```
## RVO and NRVO

**RVO** means **Return Value Optimization**.  
**NRVO** means **Named Return Value Optimization**.

Both are forms of **copy elision**: C++ avoids an unnecessary copy/move by constructing the returned object directly in its final destination.

### RVO

```cpp
Widget makeWidget() {
    return Widget{};
}
```

`Widget{}` is an unnamed temporary/prvalue.

Instead of:

```text
temporary
   ↓ move/copy
return object
```

C++ constructs it directly in the destination.

Since **C++17**, important prvalue return cases are guaranteed by the language.

### NRVO

```cpp
Widget makeWidget() {
    Widget w;
    return w;
}
```

Here `w` is a **named local object**, so this is NRVO.

If NRVO is applied, `w` is constructed directly in the caller's destination storage.

NRVO is still generally **optional**, so code must remain correct even if a move/copy is required.

Usually write:

```cpp
return w;
```

not:

```cpp
return std::move(w);
```

because `std::move` can prevent NRVO.

```text
                COPY ELISION
                     │
        ┌────────────┴────────────┐
        │                         │
       RVO                       NRVO
Return Value Optimization   Named Return Value Optimization
        │                         │
 return Widget{};            Widget w;
                             return w;
        │                         │
 unnamed prvalue             named local object
        │                         │
 C++17 important             optional optimization
 cases guaranteed
```
# One Definition Rule (ODR)

The **One Definition Rule** controls how many definitions of the same C++ entity may exist in a program.

A declaration can usually appear many times:

```cpp
extern int count;
void foo();
```

But an ordinary non-`inline` function or global variable with external linkage should have only one definition across the program:

```cpp
int count = 10;

void foo() {
}
```

If the same entity is defined in multiple translation units, there is an **ODR violation**. This often causes a linker error such as `multiple definition`, although some ODR violations are not required to produce a diagnostic.

There is no concept of one definition having higher priority or the last definition winning.

Different namespaces create different entities:

```cpp
namespace A {
    int x = 10;
}

namespace B {
    int x = 20;
}
```

`A::x` and `B::x` are different symbols, so there is no ODR conflict.

Modern C++ also allows some entities, especially **inline functions, inline variables, and templates**, to have definitions in multiple translation units, provided the definitions satisfy the ODR requirements.

### Interview definition

**ODR is the C++ rule that governs how many declarations and definitions of the same entity may exist across translation units. Ordinary external entities generally require one program-wide definition, while inline entities and templates may legally appear in multiple translation units.**

If you want, I can do the next acronym in exactly this same compact revision-note format.
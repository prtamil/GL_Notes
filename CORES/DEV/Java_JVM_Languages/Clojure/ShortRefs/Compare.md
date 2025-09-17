## 🧠 Lexicographical Comparison


```clojure
;Think of `compare` as a universal comparison — works on all comparable types.
(compare 2 5)  ; => -1
(compare 5 5)  ; => 0
(compare 9 4)  ; => 1

(compare "apple" "banana")  ; => -1
(compare "zebra" "zebra")   ; => 0
(compare "zebra" "apple")   ; => 1

(compare :a :b)  ; => -1
(compare :b :a)  ; => 1

(compare [1 2] [1 3]) ; => -1
(compare [1 3] [1 3]) ; => 0
(compare [2] [1 3])   ; => 1


```

## 🧠 What is **Lexicographical Comparison**?

Lexicographical = Dictionary order 📚

Imagine comparing two words letter by letter:

- `"apple"` vs `"apricot"`  
    → Compare `"a"` = `"a"`, then `"p"` = `"p"`, then `"p"` vs `"r"`  
    → Since `"p" < "r"`, `"apple"` < `"apricot"`
    

This is how **vectors**, **lists**, **strings**, etc., are compared in Clojure.

> Clojure's `compare` follows lexicographical comparison for **sequential collections**.

---

### 🔁 Lexicographical Comparison Steps

Given `[x1 x2 x3 ...]` and `[y1 y2 y3 ...]`:

1. Compare `x1` and `y1`
2. If equal, move to next
3. First unequal element decides
4. If all equal but one is shorter → shorter wins

## 💡 Where It's Used

- Sorting sequences
- Tree structures (sets, maps)
- Algorithm comparisons
- Custom sort keys

## 🔄 Are There Other Kinds of Comparison?

Yes — lexicographical is **just one kind**. Others include:

|Comparison Type|Description|
|---|---|
|**Numerical**|Basic numeric `<`, `>`, etc.|
|**Structural**|Deep comparisons of nested data|
|**Element-wise**|Compare each element regardless of order|
|**Set-based**|Compare based on set operations (e.g. subset?)|
|**Custom Comparators**|Your logic (e.g., sort strings by length)|
|**Equality only**|`=` in Clojure (not `<`, `>`)|

---

## 💬 In Clojure:

### Lexicographic for:

- `compare`
- `sort`
- `<=`, `>=` (on sequences too)
- map key ordering (when sorted)

## ✨ TL;DR Mental Model

- **Lexicographic = left to right like dictionary**
- First unequal element wins
- If all equal, shorter wins
- Works across strings, vectors, lists
- Default for sorting in Clojure
# Pattern 34 — Flatten

## Mental Model

Convert a **nested sequence** into a **single linear sequence**.

Unlike **FlatMap**, which transforms then flattens one level, **Flatten** removes the nested structure itself.

---

## Relationship to Cognitive Verb

```text
Structure
     ↓
Flatten
```

Flatten is a **Structure** pattern because it changes the organization of data without changing the values.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Deep Flatten|`[[1 [2]] 3] → 1 2 3`|`flatten`|
|Flatten One Level|`[[1 2] [3 4]]`|`mapcat identity`|
|Map then Flatten|Transform + Flatten|`mapcat`|
|Concatenate Sequences|Join collections|`concat`|
|Flatten Vectors|Nested vectors|`flatten`|
|Flatten Custom|Recursive traversal|`tree-seq`|

> **Note:** `flatten` recursively removes **all nesting**, while `mapcat identity` removes **only one level**.

---

## Common Uses

- Parse nested JSON
    
- Flatten XML trees
    
- Tree traversal
    
- File system traversal
    
- Matrix processing
    
- Graph traversal
    
- Token streams
    
- AST processing
    

---

## Hidden Interview Problems

- Flatten nested list
    
- Flatten binary tree
    
- Flatten JSON
    
- Flatten menu hierarchy
    
- Tree traversal
    
- Nested iterator
    

---

## Recognition Clues

If you hear:

- Nested lists
    
- Nested arrays
    
- Tree to list
    
- One sequence
    
- Collapse nesting
    
- Recursive traversal
    
- Linearize
    

Think:

**→ Flatten**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Structure|
|Pattern|Flatten|
|Input|Nested sequence|
|Output|Linear sequence|
|Deep Flatten|Yes|
|Primary Use|Remove nesting|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Deep Flatten
;;--------------------------------------------------------

(flatten [1 [2 [3 [4]] 5] [6]])

;; =>
(1 2 3 4 5 6)


;;--------------------------------------------------------
;; Flatten One Level
;;--------------------------------------------------------

(mapcat identity
        [[1 2]
         [3 4]
         [5]])

;; =>
(1 2 3 4 5)


;;--------------------------------------------------------
;; Compare flatten vs mapcat
;;--------------------------------------------------------

(flatten [[1 [2]] [3]])

;; =>
(1 2 3)

(mapcat identity
        [[1 [2]] [3]])

;; =>
(1 [2] 3)


;;--------------------------------------------------------
;; Map Then Flatten
;;--------------------------------------------------------

(mapcat #(vector % (* % 10))
        [1 2 3])

;; =>
(1 10 2 20 3 30)


;;--------------------------------------------------------
;; Concatenate Collections
;;--------------------------------------------------------

(concat
 [1 2]
 [3 4]
 [5 6])

;; =>
(1 2 3 4 5 6)


;;--------------------------------------------------------
;; Flatten Characters
;;--------------------------------------------------------

(flatten
 [["a" "b"]
  ["c" ["d" "e"]]])

;; =>
("a" "b" "c" "d" "e")


;;--------------------------------------------------------
;; Flatten Tree
;;--------------------------------------------------------

(tree-seq
 coll?
 seq
 [1 [2 [3 4]] [5]])

;; =>
([1 [2 [3 4]] [5]]
 1
 [2 [3 4]]
 2
 [3 4]
 3
 4
 [5]
 5)


;;--------------------------------------------------------
;; Collect Leaves from a Tree
;;--------------------------------------------------------

(filter
 (complement coll?)
 (tree-seq coll? seq
           [1 [2 [3 4]] [5]]))

;; =>
(1 2 3 4 5)


;;--------------------------------------------------------
;; Flatten Nested Maps Values
;;--------------------------------------------------------

(mapcat vals
        [{:a 1 :b 2}
         {:a 3 :b 4}])

;; =>
(1 2 3 4)


;;--------------------------------------------------------
;; Flatten After Partition
;;--------------------------------------------------------

(flatten
 (partition 2
            [1 2 3 4 5 6]))

;; =>
(1 2 3 4 5 6)
```
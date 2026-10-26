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
;; (1 2 3 4 5 6)


;;--------------------------------------------------------
;; Flatten One Level
;;--------------------------------------------------------

(mapcat identity
        [[1 2]
         [3 4]
         [5]])

;; =>
;; (1 2 3 4 5)


;;--------------------------------------------------------
;; Compare flatten vs mapcat
;;--------------------------------------------------------

(flatten [[1 [2]] [3]])

;; =>
;; (1 2 3)

(mapcat identity
        [[1 [2]] [3]])

;; =>
;; (1 [2] 3)


;;--------------------------------------------------------
;; Map Then Flatten
;;--------------------------------------------------------

(mapcat #(vector % (* % 10))
        [1 2 3])

;; =>
;; (1 10 2 20 3 30)


;;--------------------------------------------------------
;; Concatenate Collections
;;--------------------------------------------------------

(concat
 [1 2]
 [3 4]
 [5 6])

;; =>
;; (1 2 3 4 5 6)


;;--------------------------------------------------------
;; Flatten Characters
;;--------------------------------------------------------

(flatten
 [["a" "b"]
  ["c" ["d" "e"]]])

;; =>
;; ("a" "b" "c" "d" "e")


;;--------------------------------------------------------
;; Flatten Tree
;;--------------------------------------------------------

(tree-seq
 coll?
 seq
 [1 [2 [3 4]] [5]])

;; =>
;; ([1 [2 [3 4]] [5]]
 ;; 1
 ;; [2 [3 4]]
 ;; 2
 ;; [3 4]
 ;; 3
 ;; 4
 ;; [5]
 ;; 5)


;;--------------------------------------------------------
;; Collect Leaves from a Tree
;;--------------------------------------------------------

(filter
 (complement coll?)
 (tree-seq coll? seq
           [1 [2 [3 4]] [5]]))

;; =>
;; (1 2 3 4 5)


;;--------------------------------------------------------
;; Flatten Nested Maps Values
;;--------------------------------------------------------

(mapcat vals
        [{:a 1 :b 2}
         {:a 3 :b 4}])

;; =>
;; (1 2 3 4)


;;--------------------------------------------------------
;; Flatten After Partition
;;--------------------------------------------------------

(flatten
 (partition 2
            [1 2 3 4 5 6]))

;; =>
;; (1 2 3 4 5 6)
```

---

### Readable Clojure Functions

```clojure
(require '[clojure.string :as str])

(defn flatten-one [nested]
  (mapcat identity nested))

(defn flatten-to-depth [depth nested]
  (when (neg? depth)
    (throw (ex-info "Depth must not be negative" {:depth depth})))
  (if (zero? depth)
    nested
    (mapcat (fn [value]
              (if (sequential? value)
                (flatten-to-depth (dec depth) value)
                [value]))
            nested)))

(defn flatten-tree [branch? children root]
  (remove branch?
          (tree-seq branch? children root)))

(defn flatten-map
  ([m]
   (flatten-map [] m))
  ([path m]
   (into {}
         (mapcat (fn [[key value]]
                   (let [next-path (conj path key)]
                     (if (map? value)
                       (flatten-map next-path value)
                       [[(str/join "." (map name next-path))
                         value]])))
                 m))))

(flatten-one [[1 2] [3 4] [5]])
;; => (1 2 3 4 5)

(flatten-to-depth 1 [[1 [2 3]] [4]])
;; => (1 [2 3] 4)

(flatten-to-depth 2 [[1 [2 3]] [4]])
;; => (1 2 3 4)

(flatten [1 [2 [3 4]] "text"])
;; => (1 2 3 4 "text")

(flatten-map {:database {:host "db" :port 5432}
              :debug false})
;; => {"database.host" "db", "database.port" 5432, "debug" false}
```

Core `flatten` recursively follows values for which `sequential?` is true. Strings and maps are therefore leaves rather than collections to explode. Use `mapcat identity` when only one layer should disappear.

### Memory Hooks

|You want|You reach for|
|---|---|
|remove exactly one level|`mapcat identity`|
|remove every sequential level|`flatten`|
|stop after a known depth|a depth-limited recursive function|
|walk a tree|`tree-seq`|
|flatten while transforming|`mapcat f`|
|configuration-style dotted keys|recursive map traversal|

### Key Insight

Define the depth and branch types for a flatten operation. One-level flattening preserves deeper structure. Deep flattening removes all sequential boundaries.

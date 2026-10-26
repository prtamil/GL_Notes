# Pattern 17 — Distinct

## Mental Model

Keep **only the first occurrence** of each unique element and discard all later duplicates.

Unlike **Dedupe**, which removes only **consecutive duplicates**, **Distinct** removes duplicates **regardless of where they appear**.

---

## Relationship to Cognitive Verb

```text
Compress
    ↓
Distinct
```

Distinct is a **Compress** pattern because it reduces a sequence by eliminating repeated values.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Distinct Values|`1 2 3`|`distinct`|
|Distinct by Key|Unique `:id`|`distinct-by` _(custom)_|
|Count Unique Values|`3`|`count` + `distinct`|
|Distinct After Transform|Ignore case|`map` + `distinct`|
|Preserve First Occurrence|Default behavior|`distinct`|
|Convert to Set _(order not preserved)_|`{1 2 3}`|`set`|

> **Note:** `distinct` preserves the **first occurrence and original order**, while `set` removes duplicates but does **not** preserve order.

---

## Common Uses

- Remove duplicate records
    
- Unique IDs
    
- Unique tags
    
- Remove repeated words
    
- Deduplicate search results
    
- Unique user list
    
- Data cleaning
    
- Preprocessing
    

---

## Hidden Interview Problems

- Remove duplicates from an array
    
- Count unique elements
    
- Find unique words
    
- Deduplicate records
    
- Keep first occurrence
    
- Remove repeated IDs
    

---

## Recognition Clues

If you hear:

- Unique
    
- Remove duplicates
    
- Deduplicate
    
- First occurrence
    
- Unique values
    
- Eliminate repeats
    
- Remove repeated items
    

Think:

**→ Distinct**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Compress|
|Pattern|Distinct|
|Removes|All duplicate values|
|Preserves Order|Yes|
|Keeps|First occurrence|
|Primary Use|Deduplication|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs [1 2 1 3 2 4 1 5])


;;--------------------------------------------------------
;; Distinct Values
;;--------------------------------------------------------

(distinct xs)

;; =>
;; (1 2 3 4 5)


;;--------------------------------------------------------
;; Count Unique Values
;;--------------------------------------------------------

(count (distinct xs))

;; => 5


;;--------------------------------------------------------
;; Distinct After Transformation
;;--------------------------------------------------------

(distinct
 (map clojure.string/lower-case
      ["Apple" "APPLE" "Banana" "banana"]))

;; =>
;; ("apple" "banana")


;;--------------------------------------------------------
;; Remove Duplicate Characters
;;--------------------------------------------------------

(apply str
       (distinct "banana"))

;; =>
;; "ban"


;;--------------------------------------------------------
;; Distinct by Key
;;--------------------------------------------------------

(def users
  [{:id 1 :name "Alice"}
   {:id 2 :name "Bob"}
   {:id 1 :name "Alice Updated"}])

(vals
 (into {}
       (map (juxt :id identity))
       users))

;; =>
;; ({:id 1 :name "Alice Updated"}
 ;; {:id 2 :name "Bob"})

;; (Keeps last occurrence. To keep the first occurrence,
;; use a custom reduce.)


;;--------------------------------------------------------
;; Keep First Record by ID
;;--------------------------------------------------------

(reduce
 (fn [acc x]
   (if (contains? acc (:id x))
     acc
     (assoc acc (:id x) x)))
 {}
 users)

;; =>
;; {1 {:id 1 :name "Alice"}
 ;; 2 {:id 2 :name "Bob"}}


;;--------------------------------------------------------
;; Distinct vs Set
;;--------------------------------------------------------

(distinct [3 1 2 3 2 1])

;; =>
;; (3 1 2)

(set [3 1 2 3 2 1])

;; =>
;; #{1 2 3}


;;--------------------------------------------------------
;; Unique Words
;;--------------------------------------------------------

(distinct
 ["the" "cat" "the" "sat" "cat"])

;; =>
;; ("the" "cat" "sat")
```

---

### Readable Clojure Functions

```clojure
(defn distinct-by [key-fn values]
  (letfn [(step [seen remaining]
            (lazy-seq
              (when-let [[value & more] (seq remaining)]
                (let [key (key-fn value)]
                  (if (contains? seen key)
                    (step seen more)
                    (cons value (step (conj seen key) more)))))))]
    (step #{} values)))

(defn distinct-by-last [key-fn values]
  (->> values
       reverse
       (distinct-by key-fn)
       reverse
       vec))

(defn duplicate-values [values]
  (->> values
       frequencies
       (keep (fn [[value count]]
               (when (> count 1) value)))
       set))

(defn contains-duplicates? [values]
  (loop [seen #{}
         remaining (seq values)]
    (if-not remaining
      false
      (let [value (first remaining)]
        (if (contains? seen value)
          true
          (recur (conj seen value) (next remaining)))))))

(distinct-by :id [{:id 1 :name "first"}
                  {:id 1 :name "later"}
                  {:id 2 :name "other"}])
;; => ({:id 1, :name "first"} {:id 2, :name "other"})

(distinct-by-last :id [{:id 1 :name "first"}
                       {:id 1 :name "later"}
                       {:id 2 :name "other"}])
;; => [{:id 1, :name "later"} {:id 2, :name "other"}]

(duplicate-values [1 2 1 3 2 4])
;; => #{1 2}
```

Persistent Clojure values—including vectors, maps, and sets—have value equality and can normally be used as set members or map keys. That removes Python's separate “unhashable nested list” case.

### Memory Hooks

|You want|You reach for|
|---|---|
|unique values, first occurrence order|`distinct`|
|unique values, order irrelevant|`set`|
|unique by a property|`distinct-by`|
|the last value for each property|reverse, distinct, reverse|
|values repeated anywhere|`frequencies`|
|early duplicate detection|a loop with a `seen` set|

### Key Insight

Distinctness is global: once a key has appeared, later occurrences are removed even when separated by other values. Preserving the first or last occurrence is a product decision, so encode it in the function name.

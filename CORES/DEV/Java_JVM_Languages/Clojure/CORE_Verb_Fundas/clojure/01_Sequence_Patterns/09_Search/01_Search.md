# Pattern 26 — First Match

## Mental Model

Traverse a sequence until the **first element satisfying a condition** is found, then **stop immediately**.

Unlike **Filter**, which returns **all matching elements**, **First Match** returns only the first one.

---

## Relationship to Cognitive Verb

```text
Search
   ↓
First Match
```

First Match is a **Search** pattern because it searches until a match is found, then terminates.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|First Matching Element|First even|`some`|
|First Element Satisfying Predicate|`> 10`|`some`|
|First Truthy Value|First non-`nil`|`some`|
|Find Position|Index of first match|`keep-indexed`|
|First Matching Map|Find by `:id`|`some`|
|Search Then Transform|Return computed value|`some`|

> **Note:** `some` stops as soon as a truthy value is returned, making it ideal for early termination.

---

## Common Uses

- Find a user
    
- Find first error
    
- Lookup configuration
    
- Find first available slot
    
- Search logs
    
- Validation
    
- Rule matching
    
- Event detection
    

---

## Hidden Interview Problems

- Find first duplicate
    
- First non-repeating character
    
- First missing value
    
- Search sorted array
    
- First valid record
    
- Find target element
    

---

## Recognition Clues

If you hear:

- First match
    
- Find first
    
- Stop when found
    
- Exists
    
- Search until
    
- First valid
    
- First occurrence satisfying
    

Think:

**→ First Match**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Search|
|Pattern|First Match|
|Stops Early|Yes|
|Returns|First matching value|
|Preserves Order|Yes|
|Primary Use|Early search|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs [3 7 10 12 15 20])


;;--------------------------------------------------------
;; First Even Number
;;--------------------------------------------------------

(some #(when (even? %) %) xs)

;; => 10


;;--------------------------------------------------------
;; First Number Greater Than 10
;;--------------------------------------------------------

(some #(when (> % 10) %) xs)

;; => 12


;;--------------------------------------------------------
;; Does Any Match?
;;--------------------------------------------------------

(boolean
  (some even? xs))

;; => true


;;--------------------------------------------------------
;; First Truthy Value
;;--------------------------------------------------------

(some identity
      [nil false nil "hello" :x])

;; => "hello"


;;--------------------------------------------------------
;; Find First Map by Property
;;--------------------------------------------------------

(def users
  [{:id 1 :name "Alice"}
   {:id 2 :name "Bob"}
   {:id 3 :name "Carol"}])

(some #(when (= 2 (:id %)) %) users)

;; =>
;; {:id 2 :name "Bob"}


;;--------------------------------------------------------
;; Find Index of First Match
;;--------------------------------------------------------

(first
 (keep-indexed
   (fn [i x]
     (when (even? x) i))
   xs))

;; => 2


;;--------------------------------------------------------
;; Return a Computed Value
;;--------------------------------------------------------

(some #(when (even? %)
         (* % 10))
      xs)

;; => 100


;;--------------------------------------------------------
;; Compare filter vs some
;;--------------------------------------------------------

(filter even? xs)

;; =>
;; (10 12 20)

(some #(when (even? %) %) xs)

;; =>
;; 10


;;--------------------------------------------------------
;; Find First Non-empty String
;;--------------------------------------------------------

(some #(when (seq %) %)
      ["" "" "hello" "world"])

;; =>
;; "hello"


;;--------------------------------------------------------
;; First Matching Keyword
;;--------------------------------------------------------

(some #{:error}
      [:info :debug :warn :error :fatal])

;; =>
;; :error
```

---

### Readable Clojure Functions

```clojure
(defn find-first [predicate values]
  (reduce (fn [result value]
            (if (predicate value)
              (reduced {:found? true :value value})
              result))
          {:found? false :value nil}
          values))

(defn first-matching-index [predicate values]
  (first
    (keep-indexed (fn [index value]
                    (when (predicate value) index))
                  values)))

(defn first-computed [compute values]
  (some compute values))

(defn first-duplicate [values]
  (loop [seen #{}
         remaining (seq values)]
    (when remaining
      (let [value (first remaining)]
        (if (contains? seen value)
          value
          (recur (conj seen value) (next remaining)))))))

(defn first-n-matches [amount predicate values]
  (take (max 0 amount) (filter predicate values)))

(defn binary-search-index [values target]
  (let [values (vec values)]
    (loop [low 0
           high (dec (count values))]
      (when (<= low high)
        (let [middle (quot (+ low high) 2)
              value (nth values middle)
              comparison (compare value target)]
          (cond
            (zero? comparison) middle
            (neg? comparison) (recur (inc middle) high)
            :else (recur low (dec middle))))))))

(find-first nil? [1 false nil 3])
;; => {:found? true, :value nil}

(first-matching-index #(> % 10) [3 8 13 21])
;; => 2

(first-duplicate [:a :b :c :b :d])
;; => :b

(drop-while #(not= :start %) [:skip :skip :start :work])
;; => (:start :work)

(binary-search-index [2 4 6 8 10] 8)
;; => 3
```

`some` is concise when matches are guaranteed to be truthy. Use a result map such as `{:found? true :value nil}` when `nil` or `false` can itself be the matching value.

### Memory Hooks

|You want|You reach for|
|---|---|
|first truthy match|`some`|
|first item satisfying a predicate|`some` with `when`|
|a match that may be `nil` or `false`|an explicit `:found?` result|
|first matching index|`keep-indexed`, then `first`|
|first `n` matches|`take` over `filter`|
|tail beginning at the match|`drop-while`|
|sorted input|binary search, not a scan|

### Key Insight

A first-match search stops after it finds a result. `some` uses truth values. Use a separate found flag when `nil` or `false` can match.

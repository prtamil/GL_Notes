# Pattern 22 — Histogram (Frequencies)

## Mental Model

Count **how many times each unique value appears** in a sequence.

Unlike **Group By Key**, which stores the actual elements, a **Histogram** stores only their **counts**.

---

## Relationship to Cognitive Verb

```text
Group
   ↓
Histogram (Frequencies)
```

Histogram is a **Group** pattern that summarizes each group as a **frequency count** instead of keeping all the elements.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Count Frequencies|`{a 3 b 2}`|`frequencies`|
|Frequency After Transform|Ignore case|`map` + `frequencies`|
|Frequency by Property|Count departments|`map` + `frequencies`|
|Sort by Frequency|Most common first|`frequencies` + `sort-by`|
|Top N Frequent|Top 3|`sort-by` + `take`|
|Manual Histogram|Custom counting|`reduce`|

> **Note:** Think of `frequencies` as **`group-by` followed by `count`**.

---

## Common Uses

- Word count
    
- Character frequency
    
- Vote counting
    
- Event statistics
    
- Error frequencies
    
- Log analysis
    
- Category counts
    
- Data summarization
    

---

## Hidden Interview Problems

- Most frequent element
    
- Top K frequent elements
    
- Character count
    
- Word frequency
    
- Count duplicate values
    
- Mode of a dataset
    

---

## Recognition Clues

If you hear:

- Count occurrences
    
- Frequency
    
- Histogram
    
- Distribution
    
- Most common
    
- Top K frequent
    
- Count duplicates
    
- Mode
    

Think:

**→ Histogram (Frequencies)**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Group|
|Pattern|Histogram (Frequencies)|
|Output|Map of value → count|
|Preserves Original Elements|No|
|Aggregation|Count|
|Primary Use|Frequency analysis|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs [1 2 1 3 2 1 4 3 1])


;;--------------------------------------------------------
;; Count Frequencies
;;--------------------------------------------------------

(frequencies xs)

;; =>
;; {1 4
 ;; 2 2
 ;; 3 2
 ;; 4 1}


;;--------------------------------------------------------
;; Character Frequency
;;--------------------------------------------------------

(frequencies "banana")

;; =>
;; {\b 1
 ;; \a 3
 ;; \n 2}


;;--------------------------------------------------------
;; Word Frequency
;;--------------------------------------------------------

(frequencies
 ["the" "cat" "the" "sat" "cat" "the"])

;; =>
;; {"the" 3
 ;; "cat" 2
 ;; "sat" 1}


;;--------------------------------------------------------
;; Frequency After Transformation
;;--------------------------------------------------------

(require '[clojure.string :as str])

(frequencies
 (map str/lower-case
      ["Apple" "APPLE" "Banana" "banana"]))

;; =>
;; {"apple" 2
 ;; "banana" 2}


;;--------------------------------------------------------
;; Frequency by Property
;;--------------------------------------------------------

(def employees
  [{:name "Alice" :dept :IT}
   {:name "Bob"   :dept :HR}
   {:name "Carol" :dept :IT}
   {:name "Dave"  :dept :Sales}
   {:name "Eve"   :dept :IT}])

(frequencies
 (map :dept employees))

;; =>
;; {:IT 3
 ;; :HR 1
 ;; :Sales 1}


;;--------------------------------------------------------
;; Sort by Frequency
;;--------------------------------------------------------

(sort-by val >
         (frequencies xs))

;; =>
;; ([1 4]
 ;; [2 2]
 ;; [3 2]
 ;; [4 1])


;;--------------------------------------------------------
;; Top 2 Most Frequent
;;--------------------------------------------------------

(take 2
      (sort-by val >
               (frequencies xs)))

;; =>
;; ([1 4]
 ;; [2 2])


;;--------------------------------------------------------
;; Manual Histogram
;;--------------------------------------------------------

(reduce
 (fn [m x]
   (update m x (fnil inc 0)))
 {}
 xs)

;; =>
;; {1 4
 ;; 2 2
 ;; 3 2
 ;; 4 1}


;;--------------------------------------------------------
;; Group-By vs Histogram
;;--------------------------------------------------------

(group-by identity xs)

;; =>
;; {1 [1 1 1 1]
 ;; 2 [2 2]
 ;; 3 [3 3]
 ;; 4 [4]}

(frequencies xs)

;; =>
;; {1 4
 ;; 2 2
 ;; 3 2
 ;; 4 1}
```

---

### Readable Clojure Functions

```clojure
(defn frequencies-by [key-fn values]
  (frequencies (map key-fn values)))

(defn weighted-histogram [key-fn weight-fn values]
  (reduce (fn [histogram value]
            (update histogram
                    (key-fn value)
                    (fnil + 0)
                    (weight-fn value)))
          {}
          values))

(defn most-common [amount values]
  (->> values
       frequencies
       (sort-by val >)
       (take amount)))

(defn mode [values]
  (when-let [counts (seq (frequencies values))]
    (key (apply max-key val counts))))

(defn first-non-repeating [values]
  (let [counts (frequencies values)]
    (some (fn [value]
            (when (= 1 (get counts value)) value))
          values)))

(defn expand-histogram [histogram]
  (mapcat (fn [[value count]]
            (repeat count value))
          histogram))

(defn add-histograms [& histograms]
  (apply merge-with + histograms))

(frequencies-by clojure.string/lower-case
                ["RED" "red" "Blue"])
;; => {"red" 2, "blue" 1}

(weighted-histogram :category :amount
                    [{:category :food :amount 12}
                     {:category :travel :amount 20}
                     {:category :food :amount 8}])
;; => {:food 20, :travel 20}

(most-common 2 [:a :b :a :c :a :b])
;; => ([:a 3] [:b 2])

(first-non-repeating "swiss")
;; => \w
```

Normalize values before counting. Merging already-built histograms later is both harder and more error-prone than choosing the correct key at input time.

### Memory Hooks

|You want|You reach for|
|---|---|
|frequency table|`frequencies`|
|frequency by a property|map the property, then `frequencies`|
|weighted totals|`reduce` with `update`|
|top `n` values|sort frequency entries by `val`|
|first unique value|count once, scan original order once|
|reconstruct values|`mapcat repeat`|

### Key Insight

A histogram keeps counts and discards positions. Use it when you do not need the grouped items. It supports modes, duplicate tests, and bucket summaries.

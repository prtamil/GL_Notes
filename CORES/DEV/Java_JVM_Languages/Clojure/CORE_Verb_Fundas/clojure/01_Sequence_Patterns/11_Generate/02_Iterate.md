# Pattern 32 — Iterate

## Mental Model

Generate a sequence by **repeatedly applying the same function** to the previous value.

Unlike **Range**, which advances by a fixed numeric step, **Iterate** advances by applying a transformation rule.

---

## Relationship to Cognitive Verb

```text
Generate
    ↓
Iterate
```

Iterate is a **Generate** pattern because each new element is generated from the previous one.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Repeated Function|`1 2 4 8`|`iterate`|
|Infinite Sequence|Endless values|`iterate` + `take`|
|Finite Iteration|First N values|`take` + `iterate`|
|Custom State|Maps, vectors|`iterate`|
|State Machine|Next state|`iterate`|
|Functional Loop|Replace `while`|`iterate` + `drop-while`|

> **Note:** `iterate` repeatedly applies **f(x) → next x** and produces a lazy sequence.

---

## Common Uses

- Simulation
    
- State machines
    
- Game loops
    
- Numerical methods
    
- Physics simulation
    
- AI search
    
- Random walks
    
- Functional loops
    

---

## Hidden Interview Problems

- Generate powers of two
    
- Fibonacci (with state)
    
- Collatz sequence
    
- Newton's method
    
- BFS/DFS state expansion
    
- Repeated transformations
    

---

## Recognition Clues

If you hear:

- Repeatedly apply
    
- Next state
    
- Update until
    
- Simulation
    
- Current becomes next
    
- Functional loop
    
- State transition
    

Think:

**→ Iterate**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Generate|
|Pattern|Iterate|
|Input|Initial value + Function|
|Output|Generated sequence|
|Lazy|Yes|
|Primary Use|State evolution|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Double Every Time
;;--------------------------------------------------------

(take 6
      (iterate #(* 2 %) 1))

;; =>
;; (1 2 4 8 16 32)


;;--------------------------------------------------------
;; Increment Forever
;;--------------------------------------------------------

(take 10
      (iterate inc 0))

;; =>
;; (0 1 2 3 4 5 6 7 8 9)


;;--------------------------------------------------------
;; Countdown
;;--------------------------------------------------------

(take 6
      (iterate dec 10))

;; =>
;; (10 9 8 7 6 5)


;;--------------------------------------------------------
;; Powers of Three
;;--------------------------------------------------------

(take 6
      (iterate #(* 3 %) 1))

;; =>
;; (1 3 9 27 81 243)


;;--------------------------------------------------------
;; Fibonacci
;;--------------------------------------------------------

(map first
     (take 8
           (iterate
             (fn [[a b]]
               [b (+ a b)])
             [0 1])))

;; =>
;; (0 1 1 2 3 5 8 13)


;;--------------------------------------------------------
;; Collatz Sequence
;;--------------------------------------------------------

(take 12
      (iterate
        #(if (even? %)
           (/ % 2)
           (inc (* 3 %)))
        7))

;; =>
;; (7 22 11 34 17 52 26 13 40 20 10 5)


;;--------------------------------------------------------
;; Newton's Method
;;--------------------------------------------------------

(take 6
      (iterate
        #(/ (+ % (/ 2 %)) 2)
        1.0))

;; =>
;; (1.0
 ;; 1.5
 ;; 1.4166666666666667
 ;; 1.4142156862745099
 ;; 1.4142135623746899
 ;; 1.414213562373095)


;;--------------------------------------------------------
;; State Machine
;;--------------------------------------------------------

(take 5
      (iterate
        (fn [{:keys [x]}]
          {:x (inc x)})
        {:x 0}))

;; =>
;; ({:x 0}
 ;; {:x 1}
 ;; {:x 2}
 ;; {:x 3}
 ;; {:x 4})


;;--------------------------------------------------------
;; Functional Loop
;;--------------------------------------------------------

(first
 (drop-while #(< % 100)
             (iterate #(* 2 %) 1)))

;; =>
;; 128


;;--------------------------------------------------------
;; Compare range vs iterate
;;--------------------------------------------------------

(range 0 10 2)

;; =>
;; (0 2 4 6 8)

(take 5
      (iterate #(+ % 2) 0))

;; =>
;; (0 2 4 6 8)
```

---

### Readable Clojure Functions

```clojure
(defn take-through [stop? values]
  (lazy-seq
    (when-let [items (seq values)]
      (let [value (first items)]
        (cons value
              (when-not (stop? value)
                (take-through stop? (rest items))))))))

(defn fibonacci []
  (map first
       (iterate (fn [[a b]]
                  [b (+ a b)])
                [0 1])))

(defn collatz-next [number]
  (if (even? number)
    (quot number 2)
    (inc (* 3 number))))

(defn collatz-sequence [start]
  (when-not (pos? start)
    (throw (ex-info "Start must be positive" {:start start})))
  (take-through #(= 1 %)
                (iterate collatz-next start)))

(defn converge [step close-enough? initial]
  (some (fn [[previous current]]
          (when (close-enough? previous current)
            current))
        (partition 2 1 (iterate step initial))))

(defn fixpoint [step initial]
  (converge step = initial))

(defn first-cycle-value [step initial]
  (loop [seen #{}
         value initial]
    (if (contains? seen value)
      value
      (recur (conj seen value)
              (step value)))))

(defn state-history [transition initial steps]
  (take (inc steps)
        (iterate transition initial)))

(take 8 (fibonacci))
;; => (0 1 1 2 3 5 8 13)

(collatz-sequence 6)
;; => (6 3 10 5 16 8 4 2 1)

(converge (fn [x] (/ (+ x (/ 2.0 x)) 2.0))
          (fn [a b] (< (Math/abs (- a b)) 1.0e-10))
          1.0)
;; => approximately 1.41421356237

(first-cycle-value {0 1, 1 2, 2 3, 3 1} 0)
;; => 1
```

`iterate` is lazy and unbounded. Pair it with `take`, `take-while`, `take-through`, convergence detection, or cycle detection so the stopping rule is visible.

### Memory Hooks

|You want|You reach for|
|---|---|
|repeatedly apply `f`|`iterate`|
|fixed number of states|`take`|
|stop before a condition|`take-while`|
|include the terminating state|`take-through`|
|multi-value recurrence|put the values in a vector or map|
|convergence|inspect adjacent generated states|
|cycle protection|a `seen` set|

### Key Insight

`iterate` turns a transition function into a lazy state history. Keep all required state in one immutable value. This method supports Fibonacci and state machines.

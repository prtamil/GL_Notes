# 15. Swap and Move Axis

## Mental Model

Swap exchanges two axes. Move removes one axis and inserts it at a new position.

```text
shape [2 3 4]

swap 0 2   -> [4 3 2]
move 0 2   -> [3 4 2]
```

Other axes stay fixed during a swap. They slide during a move.

## Relationship to Cognitive Verb

```text
Relocate -> exchange two axes or reinsert one axis -> transpose by intent
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Exchange two axes|swap two entries in an identity permutation|
|Move one axis|remove and insert its identity entry|
|Iterate an axis|move it to zero|
|Put channels last|move the channel axis to `-1`|
|Batch matrix transpose|swap `-1` and `-2`|
|Full layout control|use `tensor/transpose` directly|

## Shape and Edge Behavior

- Swap is symmetric and is its own inverse.
- Move is not symmetric.
- Reverse the move arguments to undo a move.
- Negative axes count from the right.
- Both operations return views.
- Invalid axes fail before transpose.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.tensor :as tensor])

(defn normalize-axis [rank axis]
  (let [axis (if (neg? axis) (+ rank axis) axis)]
    (when-not (< -1 axis rank)
      (throw (ex-info "Axis is outside the tensor rank"
                      {:axis axis :rank rank})))
    axis))

(defn swap-axis-permutation [rank left right]
  (let [left (normalize-axis rank left)
        right (normalize-axis rank right)]
    (assoc (vec (range rank))
           left right
           right left)))

(defn move-axis-permutation [rank source destination]
  (let [source (normalize-axis rank source)
        destination (normalize-axis rank destination)
        remaining (vec (remove #{source} (range rank)))]
    (vec (concat (subvec remaining 0 destination)
                 [source]
                 (subvec remaining destination)))))

(defn swap-axes [t left right]
  (tensor/transpose
    t
    (swap-axis-permutation (count (dtype/shape t)) left right)))

(defn move-axis [t source destination]
  (tensor/transpose
    t
    (move-axis-permutation (count (dtype/shape t))
                           source
                           destination)))

(def t
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 24))
    [2 3 4]))

(assert (= [4 3 2] (vec (dtype/shape (swap-axes t 0 2)))))
(assert (= [3 4 2] (vec (dtype/shape (move-axis t 0 2)))))
(assert (= [4 2 3] (vec (dtype/shape (move-axis t -1 0)))))

;; Swap is its own inverse.
(let [restored (swap-axes (swap-axes t 0 2) 0 2)]
  (assert (= [2 3 4] (vec (dtype/shape restored))))
  (assert (= (dtype/->vector t) (dtype/->vector restored))))

;; Reverse the arguments to undo a move.
(let [moved (move-axis t 0 2)
      restored (move-axis moved 2 0)]
  (assert (= [2 3 4] (vec (dtype/shape restored))))
  (assert (= (dtype/->vector t) (dtype/->vector restored))))

;; Transpose the final two matrix axes for any leading batch rank.
(let [batch (tensor/new-tensor [5 2 3 4] {:datatype :float32})
      transposed (swap-axes batch -1 -2)]
  (assert (= [5 2 4 3] (vec (dtype/shape transposed)))))

;; Moving channels to the end states the layout intent.
(let [images (tensor/new-tensor [8 3 32 32] {:datatype :float32})
      channels-last (move-axis images 1 -1)]
  (assert (= [8 32 32 3] (vec (dtype/shape channels-last)))))

;; Both operations return views.
(let [source (tensor/reshape
               (dtype/make-container :jvm-heap :int64 (range 24))
               [2 3 4])
      view (move-axis source 1 0)]
  (tensor/mset! view 0 0 0 68)
  (assert (= 68 (tensor/mget source 0 0 0))))
```

## Common Uses

- Iterate a selected axis.
- Convert channel layouts.
- Transpose matrices inside a batch.
- Prepare one axis for a generic operation.
- Restore an earlier axis position.

## Recognition Clues

Look for `swap`, `move`, `bring to front`, `put last`, `channels`, or `batch transpose`.

## Memory Hooks

- Swap means exchange.
- Move means remove and reinsert.
- Other axes slide only during move.
- Swap again to undo a swap.
- Reverse arguments to undo a move.

## Key Insight

Swap and move are readable forms of axis permutation. Use the form that states the intended change.


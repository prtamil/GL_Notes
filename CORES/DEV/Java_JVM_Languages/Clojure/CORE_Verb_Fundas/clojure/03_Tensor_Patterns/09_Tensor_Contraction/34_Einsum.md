# 34. Einsum

## Mental Model

Einstein summation notation names tensor axes with labels.

- Labels after `->` remain in the output.
- Other labels are summed.
- A repeated label in one operand selects its diagonal.

```text
ij,jk->ik
```

This expression multiplies matrices. Label `j` is shared and absent from the output, so it is contracted.

## Relationship to Cognitive Verb

```text
Specify -> label each axis -> keep output labels -> sum all other labels
```

## Clojure Functions and Common Idioms

`dtype-next` has no general `einsum` parser. The small interpreter below supports explicit single-letter labels.

|Expression|Meaning|
|---|---|
|`i,i->`|Vector dot product|
|`i,j->ij`|Outer product|
|`ij,jk->ik`|Matrix multiplication|
|`ij->ji`|Transpose|
|`ii->`|Trace|
|`bij,bjk->bik`|Batch matrix multiplication|

## Shape and Edge Behavior

- Every expression must contain `->`.
- Labels use single ASCII letters.
- Each operand rank must match its label count.
- Equal labels must have equal sizes.
- Output labels must be unique and known.
- An empty output label list returns a Clojure scalar.
- This teaching interpreter does not support ellipsis or label broadcasting.

## Clojure Recipe Book

```clojure
(require '[clojure.string :as str]
         '[tech.v3.datatype :as dtype]
         '[tech.v3.tensor :as tensor])

(defn coordinates [shape]
  (reduce
    (fn [prefixes size]
      (vec (for [prefix prefixes
                 index (range size)]
             (conj prefix index))))
    [[]]
    shape))

(defn parse-einsum [expression]
  (let [parts (str/split expression #"->" -1)]
    (when-not (= 2 (count parts))
      (throw (ex-info "Einsum requires one explicit arrow"
                      {:expression expression})))
    (let [[input-part output-part] parts
          input-parts (str/split input-part #"," -1)
          valid-part? #(boolean (re-matches #"[A-Za-z]*" %))]
      (when-not (and (every? valid-part? input-parts)
                     (valid-part? output-part))
        (throw (ex-info "Einsum supports single-letter labels only"
                        {:expression expression})))
      {:input-labels (mapv #(mapv str %) input-parts)
       :output-labels (mapv str output-part)})))

(defn register-label-size [sizes label size]
  (if-let [known-size (get sizes label)]
    (if (= known-size size)
      sizes
      (throw (ex-info "Equal labels must have equal sizes"
                      {:label label
                       :known-size known-size
                       :new-size size})))
    (assoc sizes label size)))

(defn einsum [expression & operands]
  (let [{:keys [input-labels output-labels]} (parse-einsum expression)]
    (when-not (= (count input-labels) (count operands))
      (throw (ex-info "Operand count does not match the expression"
                      {:expression expression
                       :operand-count (count operands)})))
    (let [shapes (mapv #(vec (dtype/shape %)) operands)]
      (doseq [[labels shape] (map vector input-labels shapes)]
        (when-not (= (count labels) (count shape))
          (throw (ex-info "Operand rank does not match its labels"
                          {:labels labels :shape shape}))))
      (let [label-sizes
            (reduce
              (fn [sizes [labels shape]]
                (reduce (fn [result [label size]]
                          (register-label-size result label size))
                        sizes
                        (map vector labels shape)))
              {}
              (map vector input-labels shapes))
            all-labels (vec (distinct (mapcat identity input-labels)))]
        (when-not (= (count output-labels) (count (distinct output-labels)))
          (throw (ex-info "Output labels must be unique"
                          {:output-labels output-labels})))
        (when-not (every? label-sizes output-labels)
          (throw (ex-info "Output labels must occur in an operand"
                          {:output-labels output-labels})))
        (let [output-set (set output-labels)
              contraction-labels (vec (remove output-set all-labels))
              output-shape (mapv label-sizes output-labels)
              contraction-shape (mapv label-sizes contraction-labels)
              contraction-coordinates (coordinates contraction-shape)
              compute-value
              (fn [output-coordinate]
                (let [output-assignment
                      (zipmap output-labels output-coordinate)]
                  (double
                    (reduce +
                            (map
                              (fn [contracted-coordinate]
                                (let [assignment
                                      (merge output-assignment
                                             (zipmap contraction-labels
                                                     contracted-coordinate))]
                                  (reduce *
                                          (map (fn [operand labels]
                                                 (apply tensor/mget operand
                                                        (mapv assignment labels)))
                                               operands
                                               input-labels))))
                              contraction-coordinates)))))]
          (if (empty? output-shape)
            (compute-value [])
            (tensor/clone
              (tensor/compute-tensor
                output-shape
                (fn [& output-coordinate]
                  (compute-value output-coordinate))
                :float64))))))))

(def matrix-a
  (tensor/->tensor [[1 2 3]
                    [4 5 6]]
                   {:datatype :int64}))
(def matrix-b
  (tensor/->tensor [[7 8]
                    [9 10]
                    [11 12]]
                   {:datatype :int64}))

(assert (= [[58.0 64.0]
            [139.0 154.0]]
           (tensor/->jvm (einsum "ij,jk->ik" matrix-a matrix-b))))

(assert (= 32.0
           (einsum "i,i->"
                   (tensor/->tensor [1 2 3] {:datatype :int64})
                   (tensor/->tensor [4 5 6] {:datatype :int64}))))

(assert (= [[1.0 4.0]
            [2.0 5.0]
            [3.0 6.0]]
           (tensor/->jvm (einsum "ij->ji" matrix-a))))

(assert (= 5.0
           (einsum "ii->"
                   (tensor/->tensor [[1 2] [3 4]]
                                    {:datatype :int64}))))

(assert (= [[10.0 20.0 30.0]
            [20.0 40.0 60.0]]
           (tensor/->jvm
             (einsum "i,j->ij"
                     (tensor/->tensor [1 2] {:datatype :int64})
                     (tensor/->tensor [10 20 30] {:datatype :int64})))))

(let [left (tensor/reshape
             (tensor/->tensor (repeat 12 1) {:datatype :int64})
             [2 2 3])
      right (tensor/reshape
              (tensor/->tensor (repeat 24 1) {:datatype :int64})
              [2 3 4])
      result (einsum "bij,bjk->bik" left right)]
  (assert (= [2 2 4] (vec (dtype/shape result))))
  (assert (every? #(= 3.0 %) (dtype/->vector result))))
```

## Common Uses

- Write matrix and batch matrix multiplication.
- Extract diagonals and traces.
- Compute outer products.
- Express attention operations.
- Describe convolution contractions.

## Recognition Clues

Look for `named axes`, `contract labels`, `trace`, `bilinear form`, or `Einstein notation`.

## Memory Hooks

- Labels name axes.
- Output labels stay.
- Missing output labels sum.
- Repeated labels select matching coordinates.
- Shape errors become label-size errors.

## Key Insight

Einstein notation turns axis bookkeeping into a compact specification. Labels state which dimensions remain and which dimensions contract.


# 30. Convolution

## Mental Model

Correlation multiplies each local window by a kernel and sums the products.

```text
local window * kernel -> sum -> one output value
```

Mathematical convolution flips the kernel first. Most machine learning libraries use correlation but call it convolution.

## Relationship to Cognitive Verb

```text
Filter -> extract a local window -> apply weights -> sum the products
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Machine learning convolution|Correlation without a kernel flip|
|Mathematical convolution|Flip both kernel axes before correlation|
|Valid output|Use no padding|
|Same output for odd kernels|Pad by half of each kernel size|
|Strided output|Move the window by more than one position|
|Multiple channels|Also sum over the input-channel axis|

## Shape and Edge Behavior

- This recipe accepts rank-two input and kernels.
- Kernel dimensions must be positive.
- Stride and padding values must be valid.
- Valid correlation excludes partial edge windows.
- Zero padding supplies values outside the input.
- A large kernel can produce a size-zero output axis.
- Ragged input must be rejected before tensor creation.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.tensor :as tensor])

(defn pad-zero-2d [matrix [pad-rows pad-cols]]
  (let [[rows cols :as shape] (vec (dtype/shape matrix))]
    (when-not (= 2 (count shape))
      (throw (ex-info "Padding requires a rank-two tensor"
                      {:shape shape})))
    (when (some neg? [pad-rows pad-cols])
      (throw (ex-info "Padding must not be negative"
                      {:padding [pad-rows pad-cols]})))
    (tensor/compute-tensor
      [(+ rows (* 2 pad-rows)) (+ cols (* 2 pad-cols))]
      (fn [row col]
        (let [source-row (- row pad-rows)
              source-col (- col pad-cols)]
          (if (and (< -1 source-row rows)
                   (< -1 source-col cols))
            (tensor/mget matrix source-row source-col)
            0)))
      (dtype/elemwise-datatype matrix))))

(defn window-count [axis-size kernel-size step]
  (if (> kernel-size axis-size)
    0
    (inc (quot (- axis-size kernel-size) step))))

(defn correlate-2d
  ([matrix kernel]
   (correlate-2d matrix kernel {}))
  ([matrix kernel {:keys [stride padding]
                   :or {stride [1 1] padding [0 0]}}]
   (let [matrix-shape (vec (dtype/shape matrix))
         kernel-shape (vec (dtype/shape kernel))
         [kernel-rows kernel-cols] kernel-shape
         [row-step col-step] (vec stride)]
     (when-not (= 2 (count matrix-shape) (count kernel-shape))
       (throw (ex-info "Correlation requires rank-two tensors"
                       {:matrix-shape matrix-shape
                        :kernel-shape kernel-shape})))
     (when (some #(not (pos? %))
                 [kernel-rows kernel-cols row-step col-step])
       (throw (ex-info "Kernel sizes and strides must be positive"
                       {:kernel-shape kernel-shape :stride stride})))
     (let [padded (pad-zero-2d matrix padding)
           [rows cols] (vec (dtype/shape padded))
           output-shape [(window-count rows kernel-rows row-step)
                         (window-count cols kernel-cols col-step)]]
       (tensor/clone
         (tensor/compute-tensor
           output-shape
           (fn [output-row output-col]
             (let [start-row (* output-row row-step)
                   start-col (* output-col col-step)]
               (double
                 (reduce +
                         (for [kernel-row (range kernel-rows)
                               kernel-col (range kernel-cols)]
                           (* (tensor/mget padded
                                           (+ start-row kernel-row)
                                           (+ start-col kernel-col))
                              (tensor/mget kernel
                                           kernel-row
                                           kernel-col)))))))
           :float64))))))

(defn flip-kernel [kernel]
  (let [[rows cols :as shape] (vec (dtype/shape kernel))]
    (when-not (= 2 (count shape))
      (throw (ex-info "Kernel must have rank two" {:shape shape})))
    (tensor/compute-tensor
      shape
      (fn [row col]
        (tensor/mget kernel (- rows row 1) (- cols col 1)))
      (dtype/elemwise-datatype kernel))))

(defn convolve-2d
  ([matrix kernel]
   (correlate-2d matrix (flip-kernel kernel)))
  ([matrix kernel options]
   (correlate-2d matrix (flip-kernel kernel) options)))

(def image
  (tensor/reshape
    (tensor/->tensor (range 25) {:datatype :int64})
    [5 5]))

(def box-kernel
  (tensor/->tensor (repeat 3 (vec (repeat 3 (/ 1.0 9.0))))
                   {:datatype :float64}))

(defn close-vector? [expected actual]
  (every? (fn [[left right]]
            (< (Math/abs (- (double left) (double right))) 1.0e-9))
          (map vector expected actual)))

(assert (close-vector?
          [6.0 7.0 8.0 11.0 12.0 13.0 16.0 17.0 18.0]
          (dtype/->vector (correlate-2d image box-kernel))))

;; Correlation does not flip an asymmetric kernel.
(def signal
  (tensor/->tensor [[1 2 3 4 5]] {:datatype :int64}))
(def difference-kernel
  (tensor/->tensor [[1 0 -1]] {:datatype :int64}))

(assert (= [[-2.0 -2.0 -2.0]]
           (tensor/->jvm (correlate-2d signal difference-kernel))))
(assert (= [[2.0 2.0 2.0]]
           (tensor/->jvm (convolve-2d signal difference-kernel))))

;; Padding by half of an odd kernel preserves each axis size.
(assert (= [1 5]
           (vec (dtype/shape
                  (correlate-2d signal difference-kernel
                                {:padding [0 1]})))))

;; Stride two skips alternate window positions.
(assert (= [2 2]
           (vec (dtype/shape
                  (correlate-2d image box-kernel
                                {:stride [2 2]})))))

;; An identity kernel with same padding is a no-op.
(def identity-kernel
  (tensor/->tensor [[0 0 0]
                    [0 1 0]
                    [0 0 0]]
                   {:datatype :int64}))

(assert (= (mapv double (dtype/->vector image))
           (dtype/->vector
             (correlate-2d image identity-kernel
                           {:padding [1 1]}))))
```

## Common Uses

- Blur an image.
- Detect edges.
- Apply a learned spatial filter.
- Compute moving weighted sums.
- Process audio and time-series signals.

## Recognition Clues

Look for `kernel`, `filter`, `weighted neighborhood`, `stride`, `padding`, or `convolution layer`.

## Memory Hooks

- Extract windows.
- Multiply by weights.
- Sum the window axes.
- Correlation keeps the kernel order.
- Convolution flips the kernel.

## Key Insight

Convolution is a weighted window reduction. Kernel orientation, padding, and stride define its exact behavior.


# Part 3 — Tensor Patterns

Part 3 uses Clojure 1.12.6 and `dtype-next` 11.026.

A tensor is an n-dimensional array. Part 1 used rank 1. Part 2 used rank 2. This part keeps the rank open.

```text
rank 0   scalar      5
rank 1   vector      [1 2 3]                    Part 1
rank 2   matrix      [[1 2] [3 4]]              Part 2
rank 3   tensor      [[[...]]]
rank n   tensor      shape = [d0 d1 ... dn-1]
```

An axis is a position in the shape vector. Most tensor operations act along one or more axes.

## Tensor Library

Part 3 uses these namespaces:

|Namespace|Purpose|
|---|---|
|`tech.v3.datatype`|Typed storage, shapes, readers, and writers|
|`tech.v3.datatype.functional`|Element-wise math and reductions|
|`tech.v3.tensor`|Tensor creation, views, selection, reshape, and transpose|
|`tech.v3.tensor.dimensions`|Shape, stride, and layout metadata|

The root `deps.edn` file pins the library version.

`dtype-next` stores tensor values in a typed linear buffer. A dimension object maps n-dimensional indices into that buffer.

This design supports zero-copy views. A view can change the shape, axis order, or selected region without moving values.

## Course Conventions

- Shape values use Clojure vectors, such as `[2 3 4]`.
- Axes start at zero.
- Negative axes count from the right.
- The last axis changes fastest in row-major order.
- Input tensors must be finite and rectangular.
- Practical examples use typed `dtype-next` tensors.
- Small persistent-vector examples explain the algorithm when useful.
- Functions with `!` mutate tensor storage.
- Other functions return values or views.

`dtype-next` tensors use mutable storage. A view can share that storage with its source.

Use `tensor/clone` when an operation requires independent storage.

## Differences From NumPy

The two libraries use similar models, but their application programming interfaces differ.

|Concept|NumPy|`dtype-next`|
|---|---|---|
|Shape|tuple|vector-like shape|
|Rank-0 array|supported|use a Clojure scalar in this course|
|Strides|bytes|elements through `tensor.dimensions/strides`|
|Broadcasting|automatic for many operations|usually explicit|
|Axis reduction|`sum(axis=k)`|`tensor/reduce-axis`|
|Element-wise math|array operators|`tech.v3.datatype.functional`|
|General `einsum`|built in|course helpers explain each contraction|

The lessons do not copy NumPy syntax. They preserve the tensor concepts and use idiomatic Clojure.

## Pattern Families

- **Foundations:** shape, rank, axes, indexing, and strides.
- **Traversal:** axis iteration, nested traversal, and flat traversal.
- **Slicing:** basic slicing, open axes, index selection, and masks.
- **Structure:** reshape, flatten, axis permutation, move axis, squeeze, and expand.
- **Broadcasting:** compatibility rules, alignment, and outer operations.
- **Reduction:** one axis, retained axes, multiple axes, and argmin or argmax.
- **Combination:** concatenate, stack, split, tile, and repeat.
- **Windows:** patch extraction, pooling, and convolution.
- **Contraction:** dot, matrix multiplication, batched multiplication, `tensordot`, and `einsum` notation.
- **Generation:** constants, ranges, coordinate tensors, identity tensors, and diagonals.

## Roadmap

|#|Section|Lessons|
|---|---|---|
|01|Tensor Foundations|1 Shape and Rank · 2 Axes · 3 Indexing · 4 Strides and Memory|
|02|Tensor Traversal|5 Axis Iteration · 6 Nested Traversal · 7 Flat Traversal|
|03|Tensor Slicing|8 Basic Slicing · 9 Open Axes · 10 Index Selection · 11 Boolean Masking|
|04|Tensor Structure|12 Reshape · 13 Flatten · 14 Permute Axes · 15 Swap and Move Axis · 16 Squeeze and Expand|
|05|Tensor Broadcasting|17 Broadcasting Rules · 18 Axis Alignment · 19 Outer Operations|
|06|Tensor Reduction|20 Reduce Along an Axis · 21 Keep Dimensions · 22 Multi-Axis Reduction · 23 Argmin and Argmax|
|07|Tensor Combination|24 Concatenate · 25 Stack · 26 Split · 27 Tile and Repeat|
|08|Tensor Windows|28 Patch Extraction · 29 Pooling · 30 Convolution|
|09|Tensor Contraction|31 Dot and Matrix Multiplication · 32 Batch Matrix Multiplication · 33 Tensor Dot · 34 Einstein Summation|
|10|Tensor Generation|35 Zeros, Ones, and Full · 36 Range and Linear Space · 37 Coordinate Grids · 38 Identity and Diagonal|

## Shape Rules

Three rules apply throughout this part.

1. Predict the output shape before you run an operation.
2. Name the axis that an operation changes.
3. Know whether the result shares storage with its input.

These rules find most tensor errors early.

## Reading the Examples

Each recipe book is complete and runnable. Assertions check important behavior.

The examples use different axis sizes, such as `[2 3 4]`. Equal sizes can hide an axis error.

## Course Sequence

```text
Part 1   Sequence Patterns          complete
Part 2   Matrix Processing          complete
Part 3   Tensor Patterns            current
```


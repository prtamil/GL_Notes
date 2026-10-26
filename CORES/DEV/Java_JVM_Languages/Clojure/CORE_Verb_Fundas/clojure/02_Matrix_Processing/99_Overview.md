# Matrix Processing Roadmap

This part uses Clojure 1.12.6 and persistent vectors. The root `deps.edn` file pins this version.

Each lesson states its shape rules and edge behavior. Each recipe contains executable checks for its main examples.

## Matrix Traversal

1. [Row Traversal](01_Matrix_Traversal/01_Row_Traversal.md)
2. [Column Traversal](01_Matrix_Traversal/02_Column_Traversal.md)
3. [Diagonal Traversal](01_Matrix_Traversal/03_Diagonal_Traversal.md)
4. [Anti-Diagonal Traversal](01_Matrix_Traversal/04_AntiDiagonal.md)
5. [Spiral Traversal](01_Matrix_Traversal/05_Spiral.md)
6. [Zigzag Traversal](01_Matrix_Traversal/06_Zigzag.md)
7. [Snake Traversal](01_Matrix_Traversal/07_SnakePath.md)
8. [Boundary Traversal](01_Matrix_Traversal/08_BoundaryPath.md)

## Matrix Neighborhood

9. [Four-Neighborhood](02_Matrix_Neighborhood/09_Four_Neighborhood.md)
10. [Eight-Neighborhood](02_Matrix_Neighborhood/10_Eight_Neighborhood.md)
11. [Radius Neighborhood](02_Matrix_Neighborhood/11_Radius_Neighborhood.md)

## Matrix Window Patterns

12. [Sliding Window in Two Dimensions](03_Matrix_Window_Patterns/12_Sliding_Window_2D.md)
13. [Block and Tile](03_Matrix_Window_Patterns/13_Block_Tile.md)
14. [Patch Extraction](03_Matrix_Window_Patterns/14_Patch_Extraction.md)
15. [Convolution Window](03_Matrix_Window_Patterns/15_Convolution_Window.md)

## Matrix Structure

16. [Transpose](04_Matrix_Structure/16_Transpose.md)
17. [Rotate 90 Degrees](04_Matrix_Structure/17_Rotate_90.md)
18. [Rotate 180 Degrees](04_Matrix_Structure/18_Rotate_180.md)
19. [Rotate 270 Degrees](04_Matrix_Structure/19_Rotate_270.md)
20. [Flip Horizontal](04_Matrix_Structure/20_Flip_Horizontal.md)
21. [Flip Vertical](04_Matrix_Structure/21_Flip_Vertical.md)
22. [Reshape](04_Matrix_Structure/22_Reshape.md)
23. [Flatten](04_Matrix_Structure/23_Flatten.md)

## Matrix Search

24. [Find a Cell](05_Matrix_Search/24_Find_Cell.md)
25. [Connected Components](05_Matrix_Search/25_Connected_Components.md)
26. [Flood Fill](05_Matrix_Search/26_Flood_Fill.md)

## Matrix Scan

27. [Prefix Sum and Integral Image](06_Matrix_Scan/27_Prefix_Sum.md)

## Matrix Generation

28. [Identity Matrix](07_Matrix_Generation/28_Identity_Matrix.md)
29. [Coordinate Grid](07_Matrix_Generation/29_Coordinate_Grid.md)
30. [Checkerboard](07_Matrix_Generation/30_Checkerboard.md)

## Core Data Rules

- Use a vector of row vectors for a reusable matrix value.
- Use `[]` as the standard empty matrix.
- Use `mapv` when a function must return a matrix.
- Accept ragged rows only when each row can remain independent.
- Reject ragged rows when an operation requires a rectangle.
- Keep coordinate order as `[row column]`.
- State whether a range end is inclusive or exclusive.
- Keep boundary behavior explicit.
- Prefer pure functions. Use `!` only for shared mutable state.

## Learning Order

Start with traversal and neighborhoods. Continue with windows, transforms, search, scans, and generation.

Each section reuses the coordinate rules from the prior sections.

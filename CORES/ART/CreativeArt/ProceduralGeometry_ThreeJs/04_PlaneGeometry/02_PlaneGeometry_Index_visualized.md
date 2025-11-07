```txt
grid:
------
6 --- 7 --- 8
|     |     |
3 --- 4 --- 5
|     |     |
0 --- 1 --- 2

flattened:
----------

[0,1,2,3,4,5,6,7,8]

formulae:
---------
index = row * numColumns + col

so given row,col we get index from above formulae

```

```js
for (let row = 0; row < heightSegments; row++) {
  for (let col = 0; col < widthSegments; col++) {
	  //It will move 
  }
}
```

```txt
squareGrid:
===========
topLeftIndex    --- topRightIndex
 |                              |
 |                              |
bottomLeftIndex --- bottomRightIndex

This is Square grid we get 2 traiangles

triangle1:
==========
topLeftIndex
 |                   \
 |                    \
bottomLeftIndex  ---- bottomRightIndex

triangle2:
=========
                        topRightIndex
           /                |
         /                  |
 bottomLeftIndex         bottomRightIndex
```

```js
// Loop through each cell (subdivided rectangle) in the grid
//Think: vertices are points, squares are gaps between points. You always have 1 more point than gaps.
//Thats why in vertices we include last vertex and index we have focusing on squares so its equvalent to heightSegment 

/*
	reasong for row < heightSegments
	Indices define the squares (cells) between vertices. 
	Since squares exist only between points, we loop over `segments` for rows and columns when creating indices, 
	using the extra vertices at the top and right edges only as boundaries for the topmost and rightmost squares.
*/
const verticesPerRow  = numOfCols + 1; // Number of vertex points in each horizontal row
for (let row = 0; row < numOfRows; row++) {
  for (let col = 0; col < numOfCols; col++) {

    // Find indices of the 4 corners of this cell
    const bottomLeftIndex  = row * verticesPerRow  + col;          // index of bottom-left vertex
    const bottomRightIndex = row * verticesPerRow  + (col + 1);    // index of bottom-right vertex
    const topLeftIndex     = (row + 1) * verticesPerRow  + col;    // index of top-left vertex
    const topRightIndex    = (row + 1) * verticesPerRow  + (col + 1); // index of top-right vertex
    // Create two triangles using the corner indices
    indices.push([bottomLeftIndex, topLeftIndex, bottomRightIndex]); // first triangle
    indices.push([topLeftIndex, topRightIndex, bottomRightIndex]);   // second triangle
  }
}
```
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
export const vertexIndexAt = (row, col, verticesPerRow) => {
  return row * verticesPerRow + col;
};

const verticesPerRow = numOfCols + 1;

for (let row = 0; row < numOfRows; row++) {
  for (let col = 0; col < numOfCols; col++) {

    const bottomLeftIndex  = vertexIndexAt(row,     col,     verticesPerRow);
    const bottomRightIndex = vertexIndexAt(row,     col + 1, verticesPerRow);
    const topLeftIndex     = vertexIndexAt(row + 1, col,     verticesPerRow);
    const topRightIndex    = vertexIndexAt(row + 1, col + 1, verticesPerRow);

    indices.push([bottomLeftIndex, topLeftIndex, bottomRightIndex]);
    indices.push([topLeftIndex, topRightIndex, bottomRightIndex]);
  }
}

```
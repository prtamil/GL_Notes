
**Row Major Algorithm**

We use row-major order because it matches the way most graphics libraries store a 2D grid in a flat array, and it’s easier to go row by row when generating geometry.
In row-major, you store all columns of row 0, then all columns of row 1, and so on. In column-major, you would store all rows of column 0, then all rows of column 1, which is less intuitive for a plane.

For a plane grid, row-major is simpler because looping `for row → for col` matches the memory layout naturally: `index = rowIndex * verticesPerRow + colIndex`. Column-major would swap rows and columns in the formula, which is harder to visualize.
In short, row-major matches “think row by row, left to right,” which aligns with how we imagine a plane grid.


**Code**
```js
// Plane parameters
const width = 1.0;
const height = 1.0;
const widthSegments = 2;
const heightSegments = 2;

//Easy to remmber variables  
//Width = cols,  Height = Rows
const numOfRows = heightSegments;
const numOfCols = widthSegments;

// Step size between vertices
const gridSpacingX = width / numOfCols;   // horizontal step
const gridSpacingY = height / numOfRows; // vertical step

// Arrays to hold geometry data
const positions = [];
const indices = [];
const normals = [];
const uvs = [];

// Center offsets (translate)
const centerX = width / 2;
const centerY = height / 2;

//Multiply/Divide with ratios=> Scale
//Add/Subtract with value => Translate,Move

//Row Major Layout.  Thats why row is first
//Its easier for geometric algorithms to work this way 

// === Generate vertex positions ===
//looping thro 0,1,2 so <= heightSegment its inclusive of last index
//Vertices exist at the edges, so we need the `=` to include the last vertex row.
/*
  reason for rowIndex <= numOfRows
  Vertices:  Vertices are the points on the grid, including all edges, 
  so we include the last row and column to cover the entire plane. 
  That’s why the vertex loops use `<= segments`, ensuring every corner point of the plane is generated.
*/
for (let rowIndex = 0; rowIndex <= numOfRows; rowIndex++) {
  const yPos = rowIndex * gridSpacingY;   // step along Y axis (grid spacing)
  const y = yPos - centerY;               // center the grid vertically

  for (let colIndex = 0; colIndex <= numOfCols; colIndex++) {
    const xPos = colIndex * gridSpacingX; // step along X axis (grid spacing)
    const x = xPos - centerX;             // center the grid horizontally
    const z = 0.0;
 
    positions.push([x, y, z]);             // vertex position      positions.push([x, -y, z]);             // fixes texturing
    normals.push([0, 0, 1]);               // normal facing +Z
    let u = colIndex / numOfCols;
    let v = 1 - (rowIndex / numOfRows);
    uvs.push([u,v]);
  }
}
// === Generate indices (triangles) ===
const verticesPerRow  = numOfCols + 1; // Number of vertex points in each horizontal row 2 rows 3 vertex

// Loop through each cell (subdivided rectangle) in the grid
//Think: vertices are points, squares are gaps between points. You always have 1 more point than gaps.
//Thats why in vertices we include last vertex and index we have focusing on squares so its equvalent to heightSegment 

/*
	reasong for row < heightSegments
	Indices define the squares (cells) between vertices. 
	Since squares exist only between points, we loop over `segments` for rows and columns when creating indices, 
	using the extra vertices at the top and right edges only as boundaries for the topmost and rightmost squares.
*/
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


// === Print results ===
console.log("Vertices:");
positions.forEach((p, i) => console.log(`${i}: [${p.join(", ")}]`));

console.log("\nTriangles (indices):");
indices.forEach((tri, i) => console.log(`${i}: [${tri.join(", ")}]`));

console.log("\n Normals: \n ",{normals});
console.log("\n UVS: \n", {uvs});
```

**ReFactored Code**

```js
// === Plane Parameters ===
const width = 1.0;
const height = 1.0;
const widthSegments = 2;
const heightSegments = 2;

// Derived values
const numRows = heightSegments;
const numCols = widthSegments;
const gridSpacingX = width / numCols;
const gridSpacingY = height / numRows;
const centerX = width / 2;
const centerY = height / 2;

// === Geometry Data Containers ===
const positions = [];
const normals = [];
const uvs = [];
const indices = [];

// === Helper Functions ===

// 1️⃣ Generate vertex positions
function generatePositions(numRows, numCols, gridSpacingX, gridSpacingY, centerX, centerY) {

  function computeX(col) {
    return col * gridSpacingX - centerX;
  }

  function computeY(row) {
    return row * gridSpacingY - centerY;
  }

  function computeZ() {
    return 0.0;                 // in a 2D grid on XY plane, Z is constant
  }

  const positions = [];

  for (let row = 0; row <= numRows; row++) {
    const yPosition = computeY(row);

    for (let col = 0; col <= numCols; col++) {
      const xPosition = computeX(col);
      const zPosition = computeZ();

      positions.push([xPosition, yPosition, zPosition]);
    }
  }

  return positions;
}

// 2️⃣ Generate normals (all facing +Z)
function generateNormals(positions) {
  return positions.map(() => [0, 0, 1]);
}

// 3️⃣ Generate UV coordinates
function generateUVs(numRows, numCols) {
	function horizontalPercent(col, numCols) {
	  return col / numCols;   // how far we are across the grid (left → right)
	}
	
	function verticalPercent(row, numRows) {
	  return row / numRows;   // how far we are down the grid (bottom → top)
	}
	
	function flipVertical(percentage) {
	  return 1 - percentage;  // UV space expects top to be 1 and bottom to be 0
	}
	
	function computeUV(col, row, numCols, numRows) {
	  const u = horizontalPercent(col, numCols);
	  const v = flipVertical(verticalPercent(row, numRows));
	  return [u, v];
	}
	  const uvs = [];
	  for (let row = 0; row <= numRows; row++) {
	    for (let col = 0; col <= numCols; col++) {
	      const [u,v] = computeUV(col,row, numCols, numRows)
	      uvs.push([u,v]);
	    }
	  }
	  return uvs;
}

function generateIndices(numRows, numCols) {

  const verticesPerRow = numCols + 1;

  // ────────────────────────────────────────────
  // Convert (row, col) position -> 1D vertex index
  // ────────────────────────────────────────────
  function flattenGridPosition(row, col) {
    return row * verticesPerRow + col;
  }

  // ────────────────────────────────────────────
  // Get the 4 vertex indices of a quad in the grid
  // ────────────────────────────────────────────
  function quadCornerVertices(row, col) {
    const bottomLeft  = flattenGridPosition(row,     col);
    const bottomRight = flattenGridPosition(row,     col + 1);
    const topLeft     = flattenGridPosition(row + 1, col);
    const topRight    = flattenGridPosition(row + 1, col + 1);

    return { bottomLeft, bottomRight, topLeft, topRight };
  }

  // ────────────────────────────────────────────
  // A quad → two triangles (because WebGL draws triangles only)
  // ────────────────────────────────────────────
  function trianglesFromQuad(corners) {
    return [
      [corners.bottomLeft, corners.topLeft, corners.bottomRight],
      [corners.topLeft, corners.topRight, corners.bottomRight]
    ];
  }

  const indices = [];

  // iterate every quad in the grid
  for (let row = 0; row < numRows; row++) {
    for (let col = 0; col < numCols; col++) {

      const corners = quadCornerVertices(row, col);
      const triangles = trianglesFromQuad(corners);

      indices.push(...triangles);
    }
  }

  return indices;
}

// === Build Plane Geometry ===
const positionsData = generatePositions(numRows, numCols, gridSpacingX, gridSpacingY, centerX, centerY);
const normalsData = generateNormals(positionsData);
const uvsData = generateUVs(numRows, numCols);
const indicesData = generateIndices(numRows, numCols);

// === Log results ===
console.log("Vertices:");
positionsData.forEach((p, i) => console.log(`${i}: [${p.join(", ")}]`));

console.log("\nTriangles (indices):");
indicesData.forEach((tri, i) => console.log(`${i}: [${tri.join(", ")}]`));

console.log("\nNormals:");
console.log(normalsData);

console.log("\nUVs:");
console.log(uvsData);

```
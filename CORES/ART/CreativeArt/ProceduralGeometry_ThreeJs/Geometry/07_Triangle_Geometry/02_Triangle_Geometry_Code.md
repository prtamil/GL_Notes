
# Basic code 
```js
function makeTriangleGeometry(segments = 4) {
  const positions = [];
  const uvs = [];
  const normals = [];
  const indices = [];

  const A = new THREE.Vector3(0, 1, 0);
  const B = new THREE.Vector3(-1, -1, 0);
  const C = new THREE.Vector3(1, -1, 0);

  // Generate vertices
  for (let i = 0; i <= segments; i++) {
    for (let j = 0; j <= segments - i; j++) {
      const s = i / segments;
      const t = j / segments;

      const u = 1 - s - t;
      const v = s;
      const w = t;

      const P = new THREE.Vector3()
        .addScaledVector(A, u)
        .addScaledVector(B, v)
        .addScaledVector(C, w);

      positions.push(P.x, P.y, P.z);

      uvs.push(v, w);
      normals.push(0, 0, 1);
    }
  }

  // Correct index function
  const vertexIndex = (i, j) => (i * (i + 1)) / 2 + j;

  // Build faces
  for (let i = 1; i <= segments; i++) {
    for (let j = 0; j < segments - i + 1; j++) {
      const a = vertexIndex(i, j);
      const b = vertexIndex(i - 1, j);
      const c = vertexIndex(i, j + 1);

      indices.push(a, b, c);

      if (j < segments - i) {
        const d = vertexIndex(i - 1, j + 1);
        indices.push(c, b, d);
      }
    }
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute("normal", new THREE.Float32BufferAttribute(normals, 3));
  geometry.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
  geometry.setIndex(indices);
  return geometry;
}


```

# Refactored Code 
```js
function makeTriangleGeometry(segments = 4) {
  const positions = [];
  const uvs = [];
  const normals = [];
  const indices = [];

  // Corner vertices of the large triangle
  const A = new THREE.Vector3(0, 1, 0);     // top vertex
  const B = new THREE.Vector3(-1, -1, 0);    // bottom-left
  const C = new THREE.Vector3(1, -1, 0);     // bottom-right

  // -----------------------------------------------------
  // 1. Generate a single vertex using barycentric coords
  // -----------------------------------------------------
  function createVertex(baryU, baryV, baryW) {
    return new THREE.Vector3()
      .addScaledVector(A, baryU)
      .addScaledVector(B, baryV)
      .addScaledVector(C, baryW);
  }

  // -----------------------------------------------
  // 2. Generate UV — here we use (v, w) for clarity
  // -----------------------------------------------
  function createUV(baryV, baryW) {
    return [baryV, baryW];
  }

  // -----------------------------------------------
  // 3. Normal is constant (triangle lies in XY plane)
  // -----------------------------------------------
  function createNormal() {
    return [0, 0, 1];
  }

  // --------------------------------------------------------------
  // 4. Convert a vertex at (row, col) into a linear vertex index
  // Row layout example for segments = 4:
  // row 0 → 1 vertex
  // row 1 → 2 vertices
  // row 2 → 3 vertices
  // ...
  // Formula = triangular number + col
  // --------------------------------------------------------------
  function vertexIndex(row, col) {
    return (row * (row + 1)) / 2 + col;
  }

  // -------------------------------------------------------------
  // 5. Build all vertices (positions, uv, normals)
  // Each row contains (segments - row + 1) vertices
  // -------------------------------------------------------------
  function buildVerticesConcept() {

  // We build a triangular grid using barycentric coordinates.
  // Each grid point is a weighted mix of the triangle’s 3 corners.
  //
  //   baryU + baryV + baryW = 1
  //
  // baryV and baryW increase as we move across rows and columns.
  // baryU is simply "whatever is left" so the 3 weights always sum to 1.

  for (let row = 0; row <= segments; row++) {

    // In a triangular grid, each row gets shorter as we go down.
    for (let col = 0; col <= segments - row; col++) {

      // -----------------------------
      // 1. Compute barycentric weights
      // -----------------------------

      // "row" controls how far we move toward vertex V.
      const baryV = row / segments;

      // "col" controls how far we move toward vertex W.
      const baryW = col / segments;

      // Whatever is left belongs to vertex U.
      const baryU = 1 - baryV - baryW;

      // (These three always sum to 1 and locate a point inside the triangle)


      // --------------------------------------------
      // 2. Convert barycentric coordinates to a point
      // --------------------------------------------
      //
      // createVertex() takes the 3 weights and returns the actual 3D position.
      //
      // Geometrically:
      //   P = baryU * U_vertex
      //     + baryV * V_vertex
      //     + baryW * W_vertex
      //
      const P = createVertex(baryU, baryV, baryW);

      positions.push(P.x, P.y, P.z);


      // ------------------------
      // 3. Generate UV coordinates
      // ------------------------
      //
      // We treat baryV and baryW as UV components.
      //
      // Geometrically:
      //   • V-direction maps to U texture axis
      //   • W-direction maps to V texture axis
      //
      const uv = createUV(baryV, baryW);
      uvs.push(...uv);


      // -------------------------
      // 4. Add the vertex normal
      // -------------------------
      //
      // For a flat triangle this is constant.
      //
      const normal = createNormal();
      normals.push(...normal);
    }
  }
}

  // -------------------------------------------------------------
  // 6. Build triangles (indices)
  // Two triangles form each small diamond-shaped subdivision
  // except the diagonal boundary
  // -------------------------------------------------------------
  function buildFacesConcept() {
  const indices = [];

  // We go row-by-row through the triangular grid.
  // Row 0 has 1 vertex
  // Row 1 has 2 vertices
  // Row 2 has 3 vertices
  // ...
  // Row N has N+1 vertices

  for (let row = 1; row <= segments; row++) {

    // Each row has (segments - row + 1) cells before it closes to the side.
    for (let col = 0; col < segments - row + 1; col++) {

      // --- Vertex references (conceptual names) ---
      //
      //  bottomLeft ---- bottomRight
      //       |   \          |
      //       |    \         |
      //       |     \        |
      //    topLeft ---- topRight

      const topLeft     = vertexIndex(row, col);
      const bottomLeft  = vertexIndex(row - 1, col);
      const topRight    = vertexIndex(row, col + 1);

      // Every cell always contains **one guaranteed triangle**:
      //   (topLeft, bottomLeft, topRight)
      //
      // This is the left-leaning triangle in the rhombus-like cell.
      indices.push(topLeft, bottomLeft, topRight);

      // The second triangle exists only if there is a bottom-right vertex:
      //
      //   (topRight, bottomLeft, bottomRight)
      //
      // Without this check we would try to form a triangle across
      // the outer diagonal boundary of the big triangle.
      if (col < segments - row) {
        const bottomRight = vertexIndex(row - 1, col + 1);
        indices.push(topRight, bottomLeft, bottomRight);
      }
    }
  }

  return indices;
}


  // Build full geometry
  buildVertices();
  buildFaces();

  // -------------------------------------------------------------
  // 7. Build THREE.js BufferGeometry
  // -------------------------------------------------------------
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute(
    "position",
    new THREE.Float32BufferAttribute(positions, 3)
  );
  geometry.setAttribute(
    "normal",
    new THREE.Float32BufferAttribute(normals, 3)
  );
  geometry.setAttribute(
    "uv",
    new THREE.Float32BufferAttribute(uvs, 2)
  );
  geometry.setIndex(indices);

  return geometry;
}

```
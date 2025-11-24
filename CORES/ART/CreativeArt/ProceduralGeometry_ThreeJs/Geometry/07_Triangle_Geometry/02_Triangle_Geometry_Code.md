
# Basic code 
```js
function makeTriangleGeometry(segments = 4) {
  const positions = [];
  const uvs = [];
  const normals = [];
  const indices = [];

  // Triangle vertices in 3D
  const A = new THREE.Vector3(0, 1, 0);
  const B = new THREE.Vector3(-1, -1, 0);
  const C = new THREE.Vector3(1, -1, 0);

  // Generate vertices
  let index = 0;
  for (let i = 0; i <= segments; i++) {
    for (let j = 0; j <= segments - i; j++) {
      const s = i / segments;
      const t = j / segments;

      const u = 1 - s - t;
      const v = s;
      const w = t;

      // Position: P = uA + vB + wC
      const P = new THREE.Vector3()
        .addScaledVector(A, u)
        .addScaledVector(B, v)
        .addScaledVector(C, w);

      positions.push(P.x, P.y, P.z);

      // UV: Use barycentric v,w
      uvs.push(v, w);

      // Normal: Along +Z
      normals.push(0, 0, 1);

      index++;
    }
  }

  // Function to compute vertex index in linear array
  const vertexIndex = (i, j) =>
    i * (segments + 1) - (i * (i - 1)) / 2 + j;

  // Build faces (two triangles per quad except leftmost diagonal)
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

// Usage
const geometry = makeTriangleGeometry(6);
const material = new THREE.MeshNormalMaterial({ wireframe: true });
scene.add(new THREE.Mesh(geometry, material));

```
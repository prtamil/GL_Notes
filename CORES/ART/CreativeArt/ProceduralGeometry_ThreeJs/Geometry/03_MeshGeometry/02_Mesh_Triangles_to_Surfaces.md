# 🧩 From Triangles to Surfaces in Three.js (WebGL 2 / GLSL ES 3.00)

---

## 🧭 1. Overview

Triangles alone form shapes —  
but _patterns_ of triangles form **surfaces**.

A **surface** is a connected 2D manifold made by reusing vertices between triangles.  
Instead of drawing thousands of individual triangles separately, the GPU uses **connectivity patterns** to minimize redundant vertex processing.

WebGL 2 provides three major modes for triangle connectivity:

| Mode                      | GL Constant         | Connection Rule                                | Example          |
| ------------------------- | ------------------- | ---------------------------------------------- | ---------------- |
| **Independent Triangles** | `gl.TRIANGLES`      | Each 3 vertices = 1 triangle                   | Random mesh      |
| **Triangle Strip**        | `gl.TRIANGLE_STRIP` | Each vertex after first 2 forms a new triangle | Ribbons, terrain |
| **Triangle Fan**          | `gl.TRIANGLE_FAN`   | All triangles share first vertex               | Circles, cones   |

Three.js doesn’t expose `TRIANGLE_STRIP` or `FAN` directly, but understanding them helps you **think procedurally** when generating `BufferGeometry`.

---

## 🔺 2. Triangle Connectivity

### 🔸 gl.TRIANGLES

Each 3 vertices form a triangle:

$(v0,v1,v2), (v3,v4,v5), ...$


### 🔸 gl.TRIANGLE_STRIP

After the first two vertices, each new vertex creates a new triangle:

$(v0,v1,v2) (v1,v2,v3) (v2,v3,v4) ...$

This reuses vertices heavily — good for continuous bands like **grids**, **tubes**, or **terrain strips**.

### 🔸 gl.TRIANGLE_FAN

All triangles share the first vertex:

$(v0,v1,v2) (v0,v2,v3) (v0,v3,v4) ...$

Perfect for circular or radial geometries — **disks, cones, or domes**.

---

## 🧮 3. Indexed Surfaces

A **surface mesh** is best built using _indexed geometry_.

```js
const geometry = new THREE.BufferGeometry();

// Grid 2x2 (4 vertices, 2 triangles)
const positions = new Float32Array([
  0, 0, 0,
  1, 0, 0,
  0, 1, 0,
  1, 1, 0
]);

const indices = new Uint16Array([
  0, 1, 2,
  2, 1, 3
]);

geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
geometry.setIndex(new THREE.BufferAttribute(indices, 1));

```

Reusing vertices lets the GPU:

- Share normals (smooth shading)
- Optimize memory and bandwidth
- Reduce vertex shader executions
    

---

## 🧠 4. Mental Model: Surface as Vertex Weaving

Imagine vertices as _nails on a cloth frame_ and triangles as _threads_ connecting them.

- `gl.TRIANGLES` → tie each 3 nails independently
- `gl.TRIANGLE_STRIP` → weave a long ribbon of triangles
- `gl.TRIANGLE_FAN` → spin cloth around a central nail
    

This model helps when building procedural geometry:

- **Grid** → use nested loops to generate `(x, y)` vertex positions
- **Index pattern** → connect `(i, j)` to `(i+1, j)` and `(i, j+1)`
- **Normals** → cross product of triangle edges
    

---

## 🧩 5. Procedural Grid Example

```js
const widthSegments = 4;
const heightSegments = 4;

const positions = [];
const indices = [];

for (let y = 0; y <= heightSegments; y++) {
  for (let x = 0; x <= widthSegments; x++) {
    positions.push(x, y, 0);
  }
}

for (let y = 0; y < heightSegments; y++) {
  for (let x = 0; x < widthSegments; x++) {
    const a = y * (widthSegments + 1) + x;
    const b = a + 1;
    const c = a + (widthSegments + 1);
    const d = c + 1;
    indices.push(a, b, d, a, d, c);
  }
}

const geometry = new THREE.BufferGeometry();
geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
geometry.setIndex(indices);

```

This produces a continuous surface (plane) made of **reused vertices**.

---

## 🔢 6. Shaders (GLSL ES 3.00)

### Vertex Shader

```js
#version 300 es
precision highp float;

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec3 color;

uniform mat4 modelViewMatrix;
uniform mat4 projectionMatrix;
uniform mat3 normalMatrix;

out vec3 vColor;
out vec3 vNormal;

void main() {
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  vColor = color;
  vNormal = normalize(normalMatrix * normal);
}

```

### Fragment Shader

```js
#version 300 es
precision highp float;

in vec3 vColor;
in vec3 vNormal;
out vec4 fragColor;

void main() {
  vec3 lightDir = normalize(vec3(0.6, 0.8, 0.75));
  float diffuse = max(dot(vNormal, lightDir), 0.0);
  vec3 shaded = vColor * (0.3 + 0.7 * diffuse);
  fragColor = vec4(shaded, 1.0);
}

```

---

## 🎨 7. The Role of Attributes in Surfaces

|Attribute|Purpose|Interpolation|
|---|---|---|
|**position**|Vertex location|Defines surface shape|
|**normal**|Lighting direction|Smooth between triangles|
|**color**|Per-vertex hue|Blends across faces|
|**uv**|Texture coordinate|Maps image onto surface|

All attributes are **interpolated per fragment** using **barycentric coordinates**.

---

## 🧮 8. Surface Normals Mental Model

Each triangle has a **face normal**:

$n=normalize((v1​−v0​)×(v2​−v0​))$


If a vertex belongs to multiple triangles, its **vertex normal** is the average of adjacent face normals — giving smooth shading.
```js
      ▲
     / \
    /   \
───●─────●───
  ↖ normals average here

```


---

## 🧱 9. Surface Types in Procedural Geometry

|Surface|Construction|Best GL mode|Shape Type|
|---|---|---|---|
|**Plane/Grid**|Nested loop over X,Y|TRIANGLES / STRIP|Flat|
|**Cylinder**|Sweep circle along height|STRIP|Curved|
|**Sphere**|Sweep lat-long grid|STRIP / indexed|Closed|
|**Disk**|Central vertex + ring|FAN|Radial|
|**Cone**|Center + circle|FAN / TRIANGLES|Pointed|

You can build all of these using only positions + index patterns.

---

## 🔍 10. GPU Primitive Expansion

When drawing with indices:

`0, 1, 2, 2, 1, 3`

the GPU reconstructs triangles internally:

`(v0,v1,v2) (v2,v1,v3)`

and interpolates all varyings.

---

## 🧠 11. Procedural Thinking Pattern

To generate surfaces:

1. **Decide vertex layout** (grid, radial, polar)
2. **Store vertex attributes** (position, normal, color)
3. **Define index connectivity** (triplets)
4. **Upload to GPU** as `BufferGeometry`
5. **Draw with gl.TRIANGLES**
    

Your mental model:

> _Surfaces are vertex arrays plus index logic that define how the cloth of geometry is woven._

---

## ⚙️ 12. WebGL 2 Primitive Efficiency

|Mode|Vertex Reuse|Topology|Use Case|
|---|---|---|---|
|TRIANGLES|Low|Independent|Arbitrary meshes|
|TRIANGLE_STRIP|High|Linear|Terrain, ribbons|
|TRIANGLE_FAN|Medium|Radial|Disks, cones|

Triangle strips are GPU-efficient but less flexible to index arbitrarily,  
so Three.js internally uses **indexed gl.TRIANGLES** for universal compatibility.

---

## 🌈 13. Diagram – From Vertex Grid to Surface

```js
Vertex Grid:
●──●──●──●
│╲ │╲ │╲ │
●──●──●──●
│╲ │╲ │╲ │
●──●──●──●

Indices connect each 2x2 cell into 2 triangles:
(a,b,c), (b,c,d)

```

Result: a connected, shaded, fillable **surface**.

---

## 🧬 14. Procedural Surface Summary

|Concept|Description|Mental Analogy|
|---|---|---|
|Vertex|Lattice node|Nail on cloth|
|Index|Connection map|Thread pattern|
|Normal|Direction of light|Cloth tilt|
|UV|Texture coordinate|Pattern layout|
|Mode|TRIANGLES / STRIP|Weaving method|
|Shading|Normal interpolation|Cloth highlight|

---

## 🧩 15. The Surface Abstraction Ladder

```js
POINT → LINE → TRIANGLE → SURFACE
  │        │        │         │
  0D       1D       2D        2D connected
  isolated linked   filled     continuous
  data     edges    faces      manifolds

```

Each level increases **connectivity** and **data reuse**.

---

## 🧭 16. TL;DR Summary — WebGL 2 Surfaces

```js
- Surfaces are made of connected triangles
- Each vertex carries position, normal, uv, color
- Indices control triangle order and connectivity
- GPU fills area using barycentric interpolation
- gl.TRIANGLE_STRIP/FAN provide efficient connection
- Three.js Mesh uses gl.TRIANGLES for generality

```

---

## 💡 17. Takeaway Mental Model

> A **surface** is a _continuum of triangles_  
> stitched together by _shared vertices_  
> and _interpolated attributes_.

Procedural geometry =  
**Define vertices → Define connection logic → Let GPU fill the rest.**
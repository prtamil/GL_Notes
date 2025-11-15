# 🔺 Understanding `Mesh` (Triangles) in Three.js (WebGL 2 / GLSL ES 3.00)

---

## ⚙️ 1. Overview

If **Points** are 0D and **Lines** are 1D, then **Triangles** are the first truly 2D primitive.  
They define **surfaces** — the fundamental building blocks of all 3D rendering.

In Three.js, every visible 3D model — cube, plane, character, or terrain — is made of triangles.

Internally, `THREE.Mesh` renders geometry using:

```js
gl.drawElements(gl.TRIANGLES, indexCount, gl.UNSIGNED_SHORT, 0);
```


Each **triplet of vertices** forms one **filled triangle** in 3D space.

---

## 🧠 2. Geometric Foundation

A triangle is defined by **three ordered vertices**:

$T=(v0​,v1​,v2​)$


Each vertex carries attributes:

$vi​=\{{position,normal,uv,color,...}\}$


### Orientation

Triangle orientation (the order of vertices) determines its **front face** using the **right-hand rule**:

```js
Counter-clockwise → Front face
Clockwise         → Back face

```

This order affects:

- Which side is visible (`THREE.FrontSide`, `THREE.BackSide`)
- How lighting (normals) behave
    

---

## 🧩 3. BufferGeometry Setup

```js
const geometry = new THREE.BufferGeometry();

// 3 vertices × 3 floats = 9 floats (one triangle)
const positions = new Float32Array([
  0, 0, 0,
  1, 0, 0,
  0, 1, 0
]);
geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

// Vertex colors
const colors = new Float32Array([
  1, 0, 0,   // red
  0, 1, 0,   // green
  0, 0, 1    // blue
]);
geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

// Optional index (useful for sharing vertices)
geometry.setIndex([0, 1, 2]);

```

---

## 🧮 4. Indexed vs Non-Indexed Triangles

**Non-indexed:**

```js
positions = [v0, v1, v2, v3, v4, v5]
drawArrays(gl.TRIANGLES)

```

Each vertex belongs only to one triangle.

**Indexed:**

```js
positions = [v0, v1, v2, v3]
indices   = [0, 1, 2, 1, 2, 3]
drawElements(gl.TRIANGLES)

```

Vertices are reused across triangles — crucial for smooth shading and efficiency.

---

## 🔢 5. WebGL 2 Shader Programs

### Vertex Shader (`#version 300 es`)

```js
#version 300 es
precision highp float;

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec3 color;

uniform mat4 modelViewMatrix;
uniform mat4 projectionMatrix;
uniform mat3 normalMatrix;

out vec3 vNormal;
out vec3 vColor;

void main() {
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  vNormal = normalize(normalMatrix * normal);
  vColor = color;
}

```

### Fragment Shader (`#version 300 es`)

```js
#version 300 es
precision highp float;

in vec3 vNormal;
in vec3 vColor;
out vec4 fragColor;

void main() {
  vec3 lightDir = normalize(vec3(0.5, 0.8, 0.6));
  float diff = max(dot(vNormal, lightDir), 0.0);
  vec3 shaded = vColor * (0.2 + diff * 0.8);
  fragColor = vec4(shaded, 1.0);
}

```

---

## 🧬 6. GPU Primitive Behavior — `gl.TRIANGLES`

The GPU interprets vertex data as **groups of 3 vertices per triangle**:

```js
(v0, v1, v2)
(v3, v4, v5)

```

For indexed geometry:

```js
index[0], index[1], index[2] → first triangle
index[3], index[4], index[5] → next triangle

```

Each triangle becomes a **filled polygon** with smooth color and normal interpolation across its surface.

---

## 🎨 7. Three.js Material

```js
const material = new THREE.MeshLambertMaterial({
  vertexColors: true,
  side: THREE.FrontSide
});

```

You can use:

- `MeshBasicMaterial` → no lighting (debug view)
- `MeshLambertMaterial` → simple lighting
- `MeshStandardMaterial` → physically based (PBR)
- `RawShaderMaterial` → custom GLSL (as above)
    

---

## 🧭 8. Diagram — Vertex to Fragment Flow

```js
BufferGeometry
 ├─ position  → vertex location
 ├─ normal    → lighting orientation
 ├─ color     → vertex hue
 └─ index     → connectivity (triplets)
       │
       ▼
Vertex Shader (#version 300 es)
   → gl_Position
   → vNormal, vColor
       │
       ▼
Rasterizer (gl.TRIANGLES)
   → fills interior pixels
   → interpolates normals/colors
       │
       ▼
Fragment Shader
   → lighting + color output

```

---

## 🌈 9. Attribute Interpolation Mental Model

Each vertex attribute (e.g. color, normal) is **linearly interpolated** across the triangle’s surface:

```js
v0 ●───● v1
    ╲  │
     ╲ │
      ╲● v2

```

At any pixel inside, the GPU computes:

$Ap​=a0​⋅w0​+a1​⋅w1​+a2​⋅w2​$


where $wi​$​ are **barycentric weights** — representing the pixel’s relative position inside the triangle.
This is why smooth shading and gradients appear naturally.

---

## 🔍 10. Barycentric Thinking (Procedural Geometry Key)

Barycentric coordinates $(w0​,w1​,w2​)$ satisfy:

$w0​+w1​+w2​=1$


They describe how any point lies inside a triangle.

GPU rasterization uses barycentric weights to:

- Interpolate vertex colors → smooth color blends
- Interpolate vertex normals → smooth lighting
- Interpolate texture coordinates (UVs)
    

This is the **heart of fragment shading**.

---

## 💡 11. Face Culling

OpenGL/Three.js uses vertex winding order to remove hidden faces.

```js
renderer.setFaceCulling(THREE.CullFaceBack);

```
If the triangle’s vertices appear clockwise in screen space → it’s a **back face** → can be culled.

This optimization skips unseen polygons.

---

## 🧭 12. Visual Summary of Modes

|Primitive|Vertex Grouping|Connection|
|---|---|---|
|`gl.POINTS`|single vertex|isolated dot|
|`gl.LINES`|2 vertices|single edge|
|`gl.LINE_STRIP`|N vertices|continuous polyline|
|`gl.TRIANGLES`|3 vertices|filled polygon|

---

## 🧩 13. Procedural Mental Model

|Concept|Description|Three.js Role|
|---|---|---|
|Vertex|Corner of triangle|`position` attribute|
|Index|Connectivity (triplets)|`geometry.index`|
|Normal|Orientation for lighting|`normal` attribute|
|UV|Texture coordinate|`uv` attribute|
|Barycentric Weights|Interpolation math|GPU rasterizer|
|Material|Light & color logic|Shader program|

Think of it like:

> _Each triangle is a canvas stretched between three vertices;  
> the GPU paints that canvas by interpolating vertex data._

---

## 🔺 14. GPU Pipeline — WebGL 2 Summary

```js
CPU → BufferGeometry
       (position, normal, color, index)
       │
       ▼
Vertex Shader (#version 300 es)
   → gl_Position, vColor, vNormal
       │
       ▼
Rasterizer (gl.TRIANGLES)
   → fills pixel interiors
   → interpolates all varyings
       │
       ▼
Fragment Shader
   → lighting, texture, output

```

---

## 🧠 15. Core Memory Summary

|Concept|Analogy|GPU Behavior|
|---|---|---|
|Vertex|Corner point|Input to shader|
|Index|Triangle builder|Triplets form faces|
|Normal|Surface direction|Affects lighting|
|UV|Texture map coordinate|Controls sampling|
|gl.TRIANGLES|Mode|Three vertices per face|
|Barycentric|Interpolation weights|Fill logic|
|Face culling|One-sided cloth|Removes backs|

---

## 🧬 16. Example — Simple Triangle (WebGL 2)

```js
const geometry = new THREE.BufferGeometry();

const positions = new Float32Array([
  0, 0, 0,
  1, 0, 0,
  0, 1, 0
]);
const colors = new Float32Array([
  1, 0, 0,
  0, 1, 0,
  0, 0, 1
]);
geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

const material = new THREE.MeshBasicMaterial({
  vertexColors: true,
  side: THREE.DoubleSide
});

scene.add(new THREE.Mesh(geometry, material));

```

---

## 🧭 17. Dimensional Trinity Recap

|Type|Primitive|Connectivity|Dimension|Three.js Object|
|---|---|---|---|---|
|**Points**|`gl.POINTS`|none|0D|`THREE.Points`|
|**Lines**|`gl.LINES` / `gl.LINE_STRIP`|pairs / sequence|1D|`THREE.Line*`|
|**Triangles**|`gl.TRIANGLES`|triplets|2D|`THREE.Mesh`|

---

## 🧩 18. The Procedural Geometry Ladder (Mental Model)

```js
POINT → LINE → TRIANGLE
  │        │         │
  0D       1D        2D
  isolated connected filled
  samples  edges     surfaces

```

> “In WebGL 2, geometry evolves by increasing vertex connectivity.  
> gl.POINTS draws vertices, gl.LINES connects them, gl.TRIANGLES fills them.”

---

## 💡 19. TL;DR — WebGL 2 Mesh Summary

```js
THREE.Mesh → gl.TRIANGLES

position → vertex corners
index → triplet order
normal → lighting direction
uv → texture sampling
color → vertex hue
GPU fills interior using barycentric interpolation

```
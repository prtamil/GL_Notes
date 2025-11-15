# From Surfaces to Volumes in Three.js (WebGL 2 / GLSL ES 3.00)

---

## ⚙️ 1. Overview

Surfaces describe **boundaries** of objects.  
Volumes describe **the interior** — everything that exists _within_ those boundaries.

Three.js, being a **surface renderer**, doesn’t directly support true volumetric geometry like tetrahedral meshes.  
However, by understanding **volumetric thinking**, you can simulate or approximate 3D volume using:

1. **Voxel grids** (3D points or cubes)
2. **Layered surfaces** (shells)
3. **Ray-marched fields** (SDFs)
4. **Instanced meshes** (many cubes or spheres forming volume)
    

---

## 🧠 2. Dimensional Progression

|Dim|GL Primitive|Concept|Geometry Type|Example|
|---|---|---|---|---|
|0D|`gl.POINTS`|Sample|Vertex|Starfield|
|1D|`gl.LINES`|Connection|Edge|Wireframe|
|2D|`gl.TRIANGLES`|Boundary|Surface|Mesh|
|3D|_none (conceptual)_|Interior|Volume|Voxel / SDF|

OpenGL / WebGL draw only **surfaces** — but we can represent 3D interiors via **densely sampled surfaces or fields**.

---

## 🧩 3. The Volume as Discrete Voxels

Think of **voxels** (volume + pixel) as 3D points on a regular grid:

$V(x,y,z)=value (density, color, temperature...)$


Each voxel can be rendered as:

- a small cube (`THREE.BoxGeometry`)
- a point (`THREE.Points`)
- or skipped (if empty)
    

Example (voxel grid renderer):

```js
const positions = [];
const colors = [];

for (let z = 0; z < 10; z++) {
  for (let y = 0; y < 10; y++) {
    for (let x = 0; x < 10; x++) {
      const density = Math.random();
      if (density > 0.5) {
        positions.push(x, y, z);
        colors.push(density, 0.5, 1.0 - density);
      }
    }
  }
}

const geometry = new THREE.BufferGeometry();
geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

const material = new THREE.PointsMaterial({ vertexColors: true, size: 0.1 });
const points = new THREE.Points(geometry, material);
scene.add(points);

```

This creates a **3D cloud** — a sampled interior visualization.

---

## 🔢 4. WebGL 2 Shader (Voxel / Point Volume)

### Vertex Shader (`#version 300 es`)

```js
#version 300 es
precision highp float;

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;

uniform mat4 modelViewMatrix;
uniform mat4 projectionMatrix;

out vec3 vColor;

void main() {
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  gl_PointSize = 4.0;
  vColor = color;
}

```

### Fragment Shader

```js
#version 300 es
precision highp float;

in vec3 vColor;
out vec4 fragColor;

void main() {
  fragColor = vec4(vColor, 1.0);
}

```

This renders each voxel as a point — a minimal volumetric sample.

---

## 🧮 5. Marching Cubes: Surfaces from Volume

To convert volume data back to visible geometry,  
algorithms like **Marching Cubes** or **Marching Tetrahedra** are used.

They scan voxel values and generate triangles along **isosurfaces** (constant-density boundaries).

Three.js even provides:

```js
THREE.MarchingCubes
```

which generates a mesh from a scalar field texture.

Mental model:

> Volume → samples → field → extracted surface

---

## 🧬 6. Signed Distance Fields (SDFs)

An SDF defines for each point ppp in space a scalar value:

$d(p)=distance to surface (negative inside, positive outside)$


Example:

- Sphere SDF → $d(p)=∥p−c∥−r$
- 
    

SDFs allow:

- **Raymarching** in fragment shaders (true volumetric look)
- **Soft blends** between shapes
- **Procedural implicit geometry**
    

In Three.js, SDF rendering often uses custom fragment shaders with raymarching loops.

---

## 🔦 7. Raymarching a Volume (Concept)

A fragment shader can simulate 3D traversal through a volume:

```js

for (int i = 0; i < 100; i++) {
  vec3 p = rayOrigin + rayDir * t;
  float d = sdf(p);
  if (d < 0.001) { hit = true; break; }
  t += d;
}

```

Each pixel _steps through space_, evaluating the SDF.  
This produces real volumetric depth — shadows, fog, translucent surfaces.

---

## 🧱 8. Instanced Mesh Volumes

Efficient volume rendering in Three.js can use **`InstancedMesh`**:

```js
const cube = new THREE.BoxGeometry(1,1,1);
const material = new THREE.MeshLambertMaterial({ color: 0x3399ff });
const count = 1000;

const mesh = new THREE.InstancedMesh(cube, material, count);

for (let i = 0; i < count; i++) {
  const matrix = new THREE.Matrix4().makeTranslation(
    Math.random()*10,
    Math.random()*10,
    Math.random()*10
  );
  mesh.setMatrixAt(i, matrix);
}
scene.add(mesh);

```

Each instance represents one voxel cube — the GPU draws all at once.

---

## 🧭 9. Volume as 3D Texture (WebGL 2 Feature)

WebGL 2 introduces **3D textures**, ideal for volumetric data:

```js
uniform sampler3D volumeTex;
vec4 density = texture(volumeTex, vec3(x, y, z));

```

These can represent:

- medical scans (CT/MRI)
- clouds / fog fields
- procedural noise
    

Three.js exposes this via `THREE.Data3DTexture`.

---

## 🎨 10. Mental Model: Layers to Volume

Think of a volume as _stacked surfaces_:

```js
Layer z=0 ─── Surface 1
Layer z=1 ─── Surface 2
Layer z=2 ─── Surface 3
     ...
Together ─── Volume

```

Each 2D slice contributes to the 3D form — exactly how MRI and CT visualize bodies.

---

## 🧠 11. Attribute Parallelism

|Attribute|Surface|Volume Equivalent|
|---|---|---|
|position|vertex (x,y,z)|voxel center (x,y,z)|
|normal|surface orientation|gradient of field|
|color|vertex hue|scalar field (density, temp, etc.)|
|index|triangle connectivity|voxel grid connectivity|
|interpolation|barycentric|trilinear (x,y,z)|

---

## 🧮 12. Trilinear Interpolation (3D Analogue)

In 2D, attributes interpolate over triangles.  
In 3D volumes, interpolation occurs **inside cubes** using trilinear blending.

$f(x, y, z) = \sum_{i=0}^{1} \sum_{j=0}^{1} \sum_{k=0}^{1} w_{ijk} f_{ijk}$



where $f_{ijk}$  values at cube corners.  
This is the basis for smooth volumetric shading.

---

## 🧩 13. Procedural Volume Thinking

To procedurally model a volume:

1. Define a **scalar field function**  
    e.g. `f(x, y, z) = sin(x)*cos(y) - z`
    
2. Sample it on a grid → store as density
3. Use thresholds to extract a surface (`f = 0`)
4. Render as mesh or points
    

You’ve now defined geometry implicitly.

---

## 🧭 14. Three.js Volume Representation Summary

|Type|Geometry|Three.js Representation|GLSL Concept|
|---|---|---|---|
|Surface|Triangles|`THREE.Mesh`|`gl.TRIANGLES`|
|Point Cloud|Samples|`THREE.Points`|`gl.POINTS`|
|Volume|3D field|`Data3DTexture`, `InstancedMesh`, or raymarching|`sampler3D`|

---

## 🌈 15. GPU Concept: Volume Rasterization vs Raymarching

- **Rasterization** fills 2D screen space → surfaces only
- **Raymarching** traverses 3D space → volume visualization
    

WebGL 2 lacks direct 3D rasterization; thus, volume rendering is done in fragment shaders by simulating depth sampling.

---

## 🧬 16. Procedural Mental Model

|Concept|Description|Analogy|
|---|---|---|
|Voxel|3D pixel|Cell in cube lattice|
|Scalar Field|Function over space|Density, temperature|
|Isosurface|f(x,y,z)=0 boundary|Shape of constant density|
|SDF|Signed distance field|Distance map of volume|
|Instancing|Repeated geometry|Particles filling space|

---

## 🧩 17. Geometry Dimensional Ladder (Full)

```js
POINT → LINE → TRIANGLE → SURFACE → VOLUME
  │        │        │         │         │
  0D       1D       2D        2D+conn   3D interior
  sample   edge     face       manifold  field

```

Each level adds a new **connectivity dimension**:

- Points connect to lines
- Lines enclose triangles
- Triangles weave surfaces
- Surfaces enclose volumes
    

---

## 🧱 18. TL;DR — WebGL 2 Volume Model Summary

```js
- Volumes = 3D fields sampled as voxels
- Rendered using instanced cubes, points, or raymarching
- WebGL 2 adds sampler3D for 3D textures
- Three.js supports Data3DTexture and MarchingCubes
- True 3D geometry arises from field evaluation (SDF)
- Surfaces are boundaries; volumes are interiors

```

---

## 🧩 19. Core Takeaway Mental Model

> “A **volume** is a scalar field —  
> surfaces are merely its level sets,  
> triangles are how we approximate those sets,  
> and vertices are how we describe their edges.”

Procedural geometry =  
**Think in fields → sample in space → connect samples → draw.**
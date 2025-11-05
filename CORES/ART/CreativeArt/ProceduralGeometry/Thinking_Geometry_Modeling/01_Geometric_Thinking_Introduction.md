# 🧠 Geometry as Logic

### A practical mental model for procedural geometry

> **Geometry is not data — geometry is logic.  
> Coordinates are only the result of that logic.**

In graphics, beginners see arrays of floats and buffers of numbers:

`[ x1, y1, z1,  x2, y2, z2,  ... ]`

and assume that _geometry = storing coordinates._

But experts think differently:

**Geometry is rules that _produce_ coordinates.**

Coordinates are merely the expression — not the idea.

---

## 1 — Geometry = Rules → Representation

Every shape in graphics can be described in two layers:

|Layer|What it is|Question you ask|
|---|---|---|
|**Logic (abstract)**|rules, functions, generative systems|_How is this shape defined?_|
|**Representation (concrete)**|sampled points, vertex buffers, mesh data|_How do I store/use the result?_|

> You don’t _have_ a sphere.  
> You have a rule that produces points that lie on a sphere.

Example — sphere rule:

$$
P(u,v)=(sin⁡(u).cos(⁡v),sin(⁡u).sin⁡(v),cos⁡(u))
$$

You evaluate (sample) this rule to produce coordinates — _when you need them._

---

## 2 — The Geometry Pipeline (the clean 3-stage model)

`GENERATE  →  TRANSFORM  →  PROJECT`

|Stage|What happens|Output|
|---|---|---|
|**GENERATE**|logic produces geometry|points / surfaces / volume|
|**TRANSFORM**|move/rotate/scale geometry|same geometry, different placement|
|**PROJECT**|convert 3D world → 2D screen|final pixels|

Short pseudocode:

```js
vec3 p = GENERATE(u, v);  // rule
p = TRANSFORM(M, p);      // placement
pixel = PROJECT(camera, p);

```
Keep this order in your mind: **create → move → draw.**

---

## 3 — Generation vs Transformation

Exactly one generates geometry; the other only moves it.

|Component|Action|Mental model|
|---|---|---|
|**Generative / Parametric / Procedural**|produces geometry|“A shape is a function.”|
|**Affine transformations**|move existing geometry|“Move space, not points.”|

Generative creates new vertices.  
Affine transformations reuse them with different placement.

---

## 4 — The Generative Geometry Map

_(What actually creates geometry)_

Use this like a menu — pick a category when designing shapes.

|Category|Logic idea|What it generates|
|---|---|---|
|**Parametric functions**|P(u,v) → (x,y,z)|planes, circles, spheres, NURBS|
|**Noise / Sampling**|sample a function or heightfield|terrain, textures, clouds|
|**Implicit / SDF**|F(x,y,z)=0 defines a surface|metaballs, boolean CSG|
|**Marching / Extraction**|convert volumes → mesh|caves, voxel → mesh|
|**Recursive / Fractals**|rule expands itself|L-systems, fractal edges|
|**Agent / Turtle**|behavior emits points|roads, vines, trails|
|**Grammar / Procedural rules**|production rules|cities, architecture|
|**Simulation**|physics produces form|cloth drapes, particle strands|
|**Stochastic (random+constraint)**|controlled randomness|scattering rocks/trees|
|**IO-driven**|data becomes geometry|scanned meshes, photogrammetry|

> If the geometry comes from a rule → **generative**  
> If the geometry just gets moved → **affine**

---

## 5 — Core Tools (the thinking tools of 3D)

|Tool|Helps you reason about|
|---|---|
|**Vectors**|relationships, directions, offsets|
|**Barycentric coordinates**|interpolation, skinning, blending|
|**Quaternions**|rotation without gimbal lock|
|**Affine matrices**|hierarchical transforms, scene graphs|
|**Projection matrices**|how 3D becomes 2D on screen|

These are not data-storage techniques —  
they are **thinking tools.**

---

## 6 — A concrete example (showing the pipeline)

**Goal:** Make a flower of N petals.

```js
// GENERATE   (parametric)
vec3 petal(t) { return vec3(cos(t), sin(t), 0); }

// TRANSFORM  (affine instancing)
for (int i = 0; i < N; ++i)
    draw( rotate(petal, angle * i) );

```

- The petal shape came from a _rule_.
    
- Multiplying by rotation matrices simply _places_ petals.
    

---

## 7 — A checklist before writing any procedural geometry

1. **How should this shape be generated?**  
    Pick a method from the generative map.
    
2. **How will you sample it?**  
    Uniform grid, adaptive sampling, agent steps…
    
3. **How will it be transformed or instanced?**  
    Translation, rotation, scene graph hierarchy.
    

This keeps code modular and prevents messy logic.

---

## 8 — The final mental model (print this)

```js
Geometry = logic.
Coordinates = the result.

GENERATE  →  TRANSFORM  →  PROJECT
function  →  matrix      →  pixels

```

When you think this way, you stop pushing coordinate arrays around  
and start designing **systems that create shapes.**

---

### End of Preface

The rest of your learning will build on this foundation.
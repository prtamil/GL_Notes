# 🔍 Deep Dive: Generating vs Sampling

> **A parametric function defines geometry.  
> Sampling turns it into vertices.**

This distinction is the backbone of procedural generation.

---

## 1 — Generating = Defining the shape (continuous world)

When you define a shape using a rule, you are in the **continuous domain**:

Example:

$P(u,v)=(sin⁡u⋅cos⁡v,  sin⁡u⋅sin⁡v,  cos⁡u)$


That formula defines a sphere.

No vertices exist yet.

This is **pure logic**:

- It knows what points _would_ exist for any values of `u` and `v`.
- Infinite resolution is possible.
- Reality-independent — doesn’t care about performance or GPU.
    

You are **describing** the shape, not producing data.

---

## 2 — Sampling = turning logic into vertices (discrete world)

Sampling means:

> “Choose values for the parameters and evaluate the function to get actual points.”

You choose a _sampling strategy_:

```js
for (v = 0 → 1 step Δv)
  for (u = 0 → 1 step Δu)
      emit( P(u, v) ); // now we have a vertex

```

Now P(u, v) **produces coordinates**.

Those go into:

- vertex buffers,
- index buffers,
- or whatever your engine uses.
    

### Sampling controls:

- resolution,
- performance,
- detail.
    

---

## 3 — Sampling Strategies (the missing mental map)

|Type|What it means|When to use|
|---|---|---|
|**Uniform grid sampling**|evenly spaced u, v steps|planes, spheres, grids|
|**Adaptive sampling**|sample more where curvature is high|Bézier/NURBS, CAD quality|
|**Stratified sampling**|avoids clustering in random distributions|scattering foliage/rocks|
|**Importance sampling**|sample in high-interest areas|SDF raymarching, shadows|
|**Agent/time sampling**|parameter is time, t→t+Δt|turtles, trails, animation|

Uniform grid is easiest:

```js
float du = 1.0 / (resolutionU - 1);
float dv = 1.0 / (resolutionV - 1);

```

But adaptive sampling helps avoid waste.

---

## 4 — Sampling decisions affect visual quality

Example: parametric sine wave

$P(t)=(t,sin⁡(t),0)$


- **Large Δt** → jagged polyline, low detail
- **Small Δt** → smooth curve, more vertices
    

This is fundamental:

> More samples = smoother, but more expensive.

---

## 5 — Generation Answer vs Sampling Answer

When designing geometry, always answer two separate questions:

|Question|Type|Example|
|---|---|---|
|**What is the rule?**|generation|`P(u,v) = (cos(u), sin(u), v)`|
|**How do I walk through the rule?**|sampling|`u = 0..1, step = 0.01`|

Generation is the idea.  
Sampling is how you extract the idea.

---

## 6 — Sampling domains: not always rectangular

Most beginners think:

> “Sampling = nested for-loops with u and v.”

But sampling works on **any parameter domain**:

|Rule type|Domain|
|---|---|
|Curve|1D parameter (`t`)|
|Surface|2D domain (`u`, `v`)|
|Volume / SDF|3D sampling grid (`x`, `y`, `z`)|
|Turtle / agent|time steps (`t+=Δt`)|
|Noise sampling|uniform or stratified (`(x,y)` or `(x,y,z)`)|

The structure of the domain determines topology.

> You don’t push vertices into arrays.  
> You **walk the domain** and receive vertices.

---

## 7 — Parametric example breakdown (plane → sphere → torus)

### Plane

Rule:

$P(u,v)=(u,v,0)$

Sampling:

`u in [0,1], v in [0,1]`

Topology: rectangular grid.

---

### Sphere

Rule:

$P(u,v)=(sin⁡u.cos⁡v,sin⁡u.sin⁡v,cos⁡u)$

Sampling:

`u = latitude v = longitude`

Topology: triangle strips.

---

### Torus

Rule:

$P(u,v)=((R+rcosv)cosu, (R+rcosv)sinu, rsinv)$

Sampling:

`u loops around big ring v loops around tube`

Topology: donut-like cylinder that wraps on both ends.

> Notice how topology changes depending on rules **and domain**.

---

## 8 — Sampling affects topology too

Example: Spiral via agent

Generation:

```js
pos += dir * step;
dir = rotate(dir, angle);

```

Sampling:

`step = Δt (time)`

Sampling step determines:

- how smooth the spiral is,
- how dense the points are.
    

---

## 9 — Visual mental model

```txt
Rule (continuous) → Sampling (discrete) → Geometry (mesh)

```

```js
P(u,v)          sample grid          vertex buffer
  │                 │                    │
  ▼                 ▼                    ▼
continuous      discrete points     triangles / render

```

The GPU only sees sampled output.

---

## 10 — The short checklist (for real projects)

Before writing any procedural shape:

✅ 1. Define the rule (generation)  
✅ 2. Define how to walk it (sampling)  
✅ 3. Decide how to place it (transform)

> Shape = rule  
> Quality = sampling  
> Composition = transform

---

# One-sentence summary

> _Generation defines geometry. Sampling creates vertices._

Once this is internalized, you stop thinking in arrays of numbers,  
and start thinking in **systems that create geometry.**
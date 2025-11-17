- **Why different geometries use different parameters**
- **Whether a universal parameter system exists**
- **How parameters are chosen**
- **All major parameter types used in advanced graphics**
- **How experts actually think when designing geometry mappings**
    

I will make this **solid enough for long-term reference** but still intuitive.

---

# ⭐ 1. Why do different geometries use different parameters?

Because **every geometry lives naturally in a different mathematical “space.”**

Examples:

|Shape|Natural space|Natural parameters|
|---|---|---|
|Plane|Cartesian 2D|(u, v)|
|Circle|Polar|(r, θ)|
|Sphere|Spherical surface|(φ, θ)|
|Triangle|Simplex|(u, v, w) barycentric|
|Torus|Product of two circles|(θ₁, θ₂)|

Each shape has a **built-in structure** that makes one parameterization easy and others painful.

### Key principle:

> **Choose parameters that match the symmetry and constraints of the geometry.**

That’s it.

---

# ⭐ 2. Is there a universal single way to parameterize everything?

## **YES—but it is too general to be practical.**

There exists a universal idea:

> **Any geometry = mapping function F from a parameter domain D into ℝ³**  
> **P = F(u, v)** or **P = F(t)**

But this does **not tell you what D should be.**  
You still need to design the domain.

### Universal theoretical options exist:

1. **Triangulate everything → use barycentric patches**
2. **Use a square domain everywhere → UV mapping**
3. **Use implicit surfaces f(x,y,z)=0 (signed distance fields)**
4. **Use voxel grids**
5. **Use NURBS patches**
    

But in practice:

- some produce distortions
- some require many patches
- some are inefficient for simple shapes
- some are hard to control
    

So: **universal systems exist, but they are not universally ideal.**

---

# ⭐ 3. How parameterizations are actually created (not trial & error)

This is important:

Parameterizations are not random.  
They follow **3 deep mathematical rules**.

---

# ⭐ Rule 1 — **Match symmetry**

If shape has…

- circular symmetry → use (r, θ)
- rotational symmetry → use (θ, z)
- spherical symmetry → use (φ, θ)
    

This reduces equations and avoids distortions.

---

# ⭐ Rule 2 — **Use minimal dimensions**

A shape’s dimension tells you how many parameters you need:

|Dim|Example|Required Parameters|
|---|---|---|
|0D|point|none|
|1D|line, curve|1 parameter t|
|2D|surfaces|2 parameters (u, v)|
|3D|solids (rarely used)|3 parameters (u, v, w)|

So a sphere _surface_ only needs 2 parameters, not 3.

---

# ⭐ Rule 3 — **Use a simple domain**

You want the parameter domain to be a simple shape:

- Interval [0,1]
- Square [0,1]×[0,1]
- Circle or ring
- Triangle (for barycentric)
    

These domains map easily into buffers and grid loops.

Loop structure determines parameter choice:

```js
for u in 0..1:
    for v in 0..1:
        P = F(u,v)

```

This is the core of all procedural geometry.

---

# ⭐ 4. Parameter Types Used in Advanced Graphics (Complete List)

### **A. Cartesian Parameters**

Used when geometry aligns to axes or grid.

- (x, y) plane
- (u, v) plane subdivided grid
- box faces
    

Good for: **planes, quads, heightmaps, voxel meshes**

---

### **B. Polar Parameters**

Used for circular symmetry.

- radius r
- angle θ
    

Good for: **circle, disk, annulus, polar grids, spirals**

---

### **C. Cylindrical Parameters**

Used for extrusion around a circle.

- angle θ
- height h
    

Good for: **cylinder, cone, tube, pipe**

---

### **D. Spherical Parameters**

Used for closed surfaces of revolution.

- polar φ
- azimuth θ
    

Good for: **sphere, hemisphere, geodesic patches**

---

### **E. Toroidal Parameters**

Used when the surface is circle × circle.

- θ₁
- θ₂
    

Good for: **torus, torus knot base**

---

### **F. Barycentric Parameters**

Used for any triangular region.

- u, v, w (u+v+w=1)
    

Good for: **triangular patches, triangulated surfaces, GPU interpolation**

This is a _huge_ concept in graphics (shading, rasterization, barycentric interpolation).

---

### **G. Parametric Curve Parameters**

Used for 1D curves.

- t ∈ [0,1]
    

Good for:  
**splines, animation paths, cables, hair, ribbons, tracks**

---

### **H. UV Mapping Parameters**

Used to unwrap surfaces into 2D textures.

(u, v) → (x, y, z) mapping

Good for:  
**any mesh, texture mapping, displacement mapping**

---

### **I. Implicit Parameters**

Used for signed distance surfaces.

f(x,y,z) = 0

Good for:  
**metaballs, fractal surfaces, procedural worlds**

Advanced but extremely powerful.

---

### **J. NURBS / Bezier / Subdivision Parameters**

Used in CG, CAD, modeling.

- (u, v) control patches
    

Good for:  
**smooth editable surfaces, cars, aircraft, industrial design**

---

### **K. Manifold & Chart Parameters** _(advanced)_

If shape is too complex, break it into patches.

Each patch has local (u, v).  
This is how **UV maps** and **game asset models** work.

---

# ⭐ 5. How professionals choose parameters (the mindset)

Here is the mental process graphics programmers use:

---

## **Step 1 — Identify geometric symmetry**

- rotational? use angle
- radial? use radius
- spherical? use φ,θ
- grid-like? use u,v
    

---

## **Step 2 — Identify dimension**

- curve → 1 parameter
- surface → 2 parameters
    

---

## **Step 3 — Choose simplest domain**

Do I want loops like:

- for t?
- for u,v?
- for θ,r?
    

Pick a domain that gives clean, uniform loops.

---

## **Step 4 — Write mapping function**

F(parameters) → (x,y,z)

Example for sphere:  
F(θ,φ) = (r sinφ cosθ, r sinφ sinθ, r cosφ)

---

## **Step 5 — Generate indices according to parameter topology**

- grid → row/col index formula
- circular → wrap around (modulo)
- barycentric → triangle indices
    

---

# ⭐ 6. So is parameter selection trial & error?

**No. It is structured, not random.**

You follow:

1. geometry dimension
2. geometry symmetry
3. natural coordinate system
4. simplest domain that matches shape
5. mapping function
    

This yields _the correct_ parameterization.

---

# ⭐ 7. The Deep Truth (why you feel confused)

You are discovering something fundamental:

> **Parameters are not coordinates.**  
> Coordinates describe positions.  
> Parameters generate the positions.

PARAMETERS = “instructions to build geometry”  
COORDINATES = “final vertex positions in 3D”

This changes everything.

---

# ⭐ 8. Final Summary (ideal for notes)

### **Geometry is created by mapping from a parameter domain into 3D:**

`Geometry = F(parameters)`

Parameters are chosen by:

1. **Matching symmetry**
2. **Matching dimension**
3. **Using simplest domain**
4. **Using natural coordinate system**
5. **Avoiding distortion**
    

This is how ALL procedural geometry—from planes to Mandelbulbs—is designed.
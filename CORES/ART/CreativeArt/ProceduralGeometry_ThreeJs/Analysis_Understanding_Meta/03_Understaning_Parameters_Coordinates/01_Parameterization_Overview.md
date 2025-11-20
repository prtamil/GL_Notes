# **Parameterization in Geometry: A Reference Guide**

Parameterization is a fundamental concept in geometry and computer graphics. It allows us to represent points on a surface or curve as functions of one or more variables—called **parameters**—rather than as fixed coordinates. Proper parameterization is crucial for generating meshes, UV mapping, procedural shapes, and other graphics applications.

---

## **1. What are Parameters?**

- **Parameters (u, v, etc.)** are **normalized variables** that describe a position along the topology of a surface or curve.
- They **do not represent physical coordinates themselves**, but fractions or percentages along a given direction of the geometry.
    
- Conceptually:
    
    - **Plane:** u → horizontal fraction, v → vertical fraction
    - **Circle:** u → fraction along circumference
    - **Ring (annulus):** u → fraction along radius, v → fraction along angle
        

> Parameters are independent of the geometry’s actual size or resolution.

---

## **2. Introducing Parameters into Equations**

The first step in parameterization is **rewriting the geometry in parametric form**:

1. Identify **what varies** along the surface.
2. Introduce normalized parameters u, v ∈ [0,1].
3. Replace the original variable with a scaled version of the parameter.
    

**Examples:**

- **Plane** (width W, height H):
    
	```js
	x = u * W
	y = v * H
	z = 0

	```
    
- **Circle** (radius r):
    
	```js
	theta = u * 2π
	x = r * cos(theta)
	y = r * sin(theta)

	```
    
- **Ring (annulus)** (inner radius r_inner, outer radius r_outer):
    
```js
r = r_inner + u * (r_outer - r_inner)
theta = v * 2π
x = r * cos(theta)
y = r * sin(theta)

```
    

> **Key Idea:** Introducing parameters is **conceptual**; it generalizes the equation independent of resolution or segment count.

---

## **3. Normalizing Parameters (0→1)**

Once parameters u and v exist symbolically, we need **specific numeric values** to generate points. This is done by **normalizing the parameter using segments**, which define how finely we sample the geometry.

- Let `uSegments` and `vSegments` be the number of divisions along u and v directions.
    
- Compute the normalized value for each segment index:
    

```js
u = i / uSegments
v = j / vSegments

```

- i, j = segment indices (0..Segments)
    
- u, v ∈ [0,1] → **fraction along the surface**
    

> Segments control **sampling density**, not the parameter’s conceptual range.

---

## **4. Mapping Parameters to Physical Coordinates**

After calculating normalized values:

1. **Plug u, v into parametric equations** to get actual coordinates (x, y, z).
2. **Map to width, radius, or angle** as needed:
    

- Plane: `x = u * W, y = v * H`
- Circle: `theta = u * 2π; x = r * cos(theta)
- Ring: `r = lerp(r_inner, r_outer, u); theta = v * 2π; x = r * cos(theta), y = r * sin(theta)`
    

> Normalization separates the **conceptual parameter space** from **physical geometry**.

---

## **5. Indexing and Segments**

- **Segment indices** allow discrete sampling: `i = 0..uSegments`, `j = 0..vSegments`.
- These indices produce **evenly spaced points** along u and v.
- Once points are generated, **triangles or quads** can be formed using indices to create a mesh.
    

---

## **6. Summary of Parameterization Process**

1. **Identify geometry and topology** (plane, circle, ring, sphere, etc.)
2. **Decide parameters** u, v based on how you traverse the geometry
3. **Write parametric equations** using u, v instead of raw coordinates
4. **Decide sampling** using segments along each parameter direction
5. **Calculate normalized u, v values**: `u = i / uSegments`
6. **Map normalized parameters to physical coordinates**
7. **Optionally calculate UVs, normals, and indices** for rendering
    

> Parameterization allows for **resolution-independent, reusable, and generalized geometry generation**.

---

## **7. Mental Model**

- **Parameters** = fraction along topology (0→1)
- **Segments** = discrete sampling along parameters
- **Parametric equation** = function mapping parameters → coordinates
    

Analogy:

- Think of a **race track** 100m long.
    
    - u = fraction along track (0 → 1)
    - 8 cones along track → segment indices 0..8 → u = i / 8
    - Map u → actual position x = u * 100m
        

---

This framework works **universally** for **planes, circles, rings, spheres, tori, or any parametric surface**.
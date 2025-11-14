# Refactored Code

1. Theta => Angular Name based on geometry
2. Phi => Radial Name based on geometry

```txt
R(φ, θ) = ( r(φ) cos θ,  r(φ) sin θ )

```

```js
for each φ: (Radial)
    r = radiusAt(φ)
    for each θ: (Angle)
        angle = angleAt(θ)
        vertex = polarToCartesian(r, angle)

```



```js
/**
 * Convert a 2D polar grid coordinate (radialStep, angularStep)
 * into a 1D vertex index in the flattened vertex buffer.
 */
function polarGridIndex(radialStep, angularStep, angularCount) {
  return radialStep * angularCount + angularStep;
}

/**
 * Generate triangle indices for RingGeometry.
 *
 * - radial segments  (phi)   → inner → outer direction
 * - angular segments (theta) → around the ring
 *
 * Each grid cell between these samples is split into 2 triangles.
 */
function generateRingIndices(phiSegments, thetaSegments) {
  const indices = [];
  const angularCount = thetaSegments + 1; // vertices per radial row

  for (let radialStep = 0; radialStep < phiSegments; radialStep++) {
    for (let angularStep = 0; angularStep < thetaSegments; angularStep++) {

      // Four vertices of the current quad (cell)
      const a = polarGridIndex(radialStep,     angularStep, angularCount);
      const b = polarGridIndex(radialStep + 1, angularStep, angularCount);
      const c = polarGridIndex(radialStep + 1, angularStep + 1, angularCount);
      const d = polarGridIndex(radialStep,     angularStep + 1, angularCount);

      // Two triangles of the quad
      indices.push(a, b, d);  // Triangle 1
      indices.push(b, c, d);  // Triangle 2
    }
  }

  return indices;
}


```

# 🔍 **Why this version is much clearer**

I use clear geometric names:

- **radialStep** → movement outward (inner → outer radius)
- **angularStep** → movement around the circle (theta)
- **polarGridIndex()** → maps the (radial, angular) grid coordinate → into the 1D vertex array

### ✔ Uses _geometric naming_ (radial, angular)

Matches how the ring is conceptually sampled.

### ✔ Separates concerns

1. Convert grid → 1D index
2. Loop the grid
3. Add triangles
    

### ✔ Shows the quad structure explicitly

```js
(a) ---- (d)
 |        |
(b) ---- (c)

```

### ✔ One small helper (`polarGridIndex`) explains everything

You immediately know:  
“Ah! It flattens the radial–angular grid of the ring.”
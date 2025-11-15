# Refactored code


```js

// ---------- Math Utility ----------
const lerp = (a, b, t) => a + (b - a) * t;


// Convert polar position → UV
const polarToUV = (radius, angle, outerRadius) => {

    // -------------------------
    // Step 1: Convert polar → Cartesian (x,y)
    // -------------------------
    const x = Math.cos(angle) * radius;
    const y = Math.sin(angle) * radius;

    // -------------------------
    // Step 2: Normalize x,y to the domain [-1, +1]
    //         (by dividing by outerRadius)
    // -------------------------
    const xNorm = x / outerRadius;   // -1 → +1
    const yNorm = y / outerRadius;   // -1 → +1

    // -------------------------
    // Step 3: Shift & scale from [-1,+1] → [0,1]
    //         (add 1 → [0,2], multiply 0.5 → [0,1])
    // -------------------------
    const u = (xNorm + 1) * 0.5;
    const v = (yNorm + 1) * 0.5;

    return { u, v };
};


// ---------- Generate UVs with simple for-loops ----------
// We are regeneratiing Vertices then we are modifying its Range
function generateRingUVs(
    innerRadius,
    outerRadius,
    thetaSegments,
    phiSegments,
    thetaStart,
    thetaLength
) {
    const uvs = [];

    for (let radialIndex = 0; radialIndex <= phiSegments; radialIndex++) {

        const radPercent  = radialIndex / phiSegments;
        const radius = lerp( innerRadius, outerRadius,rt);

        for (let angularIndex = 0; angularIndex <= thetaSegments; angularIndex++) {

            const angPercent = angularIndex / thetaSegments;
            const angle = lerp(thetaStart, thetaLength,at);

            const { u, v } = polarToUV(radius, angle, outerRadius);
            uvs.push(u, v);
        }
    }

    return uvs;
}

```

# ✅ **Ring UV Mapping — 3 Steps**

### **Step 1 — Convert ring grid (radial %, angular %) into a polar coordinate (radius, angle)**

For every vertex:

- Compute **radial percentage**:  
    `radPercent = radialIndex / phiSegments`
    
- Interpolate the radius using `lerp`:  
    `radius = lerp(innerRadius, outerRadius, radPercent)`
    
- Compute **angular percentage**:  
    `angPercent = angularIndex / thetaSegments`
    
- Interpolate the angle using `lerp`:  
    `angle = lerp(thetaStart, thetaStart + thetaLength, angPercent)`
    

This produces the vertex’s **polar position**.

---

### **Step 2 — Convert polar coordinate → Cartesian and normalize to [-1, +1]**

- Convert polar to Cartesian:  
    `x = cos(angle) * radius`  
    `y = sin(angle) * radius`
    
- Normalize using the max radius (outerRadius):  
    `xNorm = x / outerRadius`  
    `yNorm = y / outerRadius`
    

Now xNorm and yNorm are in **[-1 → +1]**.

---

### **Step 3 — Map normalized coordinates into UV space [0 → 1]**

Use the standard shift + scale:

- `u = (xNorm + 1) * 0.5`
- `v = (yNorm + 1) * 0.5`
    

This produces the final UV coordinates per vertex.

---

# ⭐ **Ultra-Short Summary (for notes)**

- **Step 1:** Convert grid → polar (radius, angle) using lerp
    
- **Step 2:** Convert polar → Cartesian → normalize to [-1, +1]
    
- **Step 3:** Shift & scale to UV [0,1]
# ✅ **UV From Existing Vertices (no radius/angle regeneration)**

### ✔ We assume you have something like:

```js
const vertices = geometry.attributes.position.array;

```

### ✔ Then compute UV for each vertex:

```js
function generateUVsFromVertices(vertices, outerRadius) {
    const uvs = [];

    for (let i = 0; i < vertices.length; i += 3) {

        // -------------------------
        // Step 1 — Read existing vertex (x,y)
        // -------------------------
        const x = vertices[i];
        const y = vertices[i + 1];

        // -------------------------
        // Step 2 — Normalize to [-1, +1]
        // -------------------------
        const xNorm = x / outerRadius;
        const yNorm = y / outerRadius;

        // -------------------------
        // Step 3 — Map to UV [0 → 1]
        // -------------------------
        const u = (xNorm + 1) * 0.5;
        const v = (yNorm + 1) * 0.5;

        uvs.push(u, v);
    }

    return uvs;
}

```
---

# 🔍 Why this works

Because the ring’s vertex positions already follow:

```js
x = cos(angle) * radius
y = sin(angle) * radius

```

So radius/angle is implicitly encoded in `(x,y)`.

UV generation needs only:

```js
(x, y) → normalize → 0-1 UV

```

Thus **no need to recalc radius or angle**.

---

# ⭐ Short Summary

If you already have the vertex positions:

- **Step 1:** Use vertex.x and vertex.y
- **Step 2:** Normalize using outerRadius
- **Step 3:** Convert to UV (0→1)
    

Done.
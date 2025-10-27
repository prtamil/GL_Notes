Here’s the **Version 2: Dynamic / Animated Procedural Geometry Template** — designed for **real-time geometry updates** (e.g. water waves, morphing meshes, cloth simulation, procedural deformation).

It extends the static geometry template by adding **time, update frequency, and buffer management** sections — essential for mastering **GPU-friendly animation**.

---

## 🌀 Dynamic Procedural Geometry Template

> **Goal:** Design and understand geometries that _change over time_ — modifying vertex data dynamically while maintaining performance and visual stability.

---

### 🧠 1. Shape Concept

- What base shape am I starting from? (plane, sphere, cube, etc.)
- What will change over time?
    - positions / normals / colors / uvs / indices ?
- Is the motion **procedural** (math-driven) or **data-driven** (simulation, noise, texture input)?
- How often does it update?  
    (every frame / event-based / partial updates)
- Static vs Dynamic:
    
    - ☐ Static (computed once)
    - ☑ Dynamic (updated per frame)
        

---

### ⏱️ 2. Time and Update Model

- What drives animation?
    
    - elapsed time (`t`),
    - frame count (`tick`),
    - user input,
    - noise function, etc.
        
- Formula for time evolution:
    
    `time = clock.getElapsedTime() 
    `value = base + sin(freq * time + phase) * amp`
    
- Update frequency:
    
    - Every frame (`requestAnimationFrame`)
    - Fixed time step (e.g. physics sim)
        
- Does the motion loop or evolve infinitely?
    

---

### 📍 3. Dynamic Vertex Position Formula

- Base coordinate formula:
    
    `x = ix * segment_width - width_half
    ` y = iy * segment_height - height_half
	`z = f(x, y, t)`
    
- Example deformations:
    
    - **Wave:** `z = sin(x * freq + t) * amp`
    - **Noise:** `z = perlin(x * s, y * s, t) * amp`
    - **Morph:** interpolate between two geometries
        
- Should I store **original positions** for reference?  
    → `basePositions = positions.slice()`
    

**Performance note:**  
Always reuse arrays; avoid reallocating per frame.

---

### 🔁 4. Geometry Update Flow

```js
function updateGeometry(time) {
  const pos = geometry.attributes.position.array
  for (let i = 0; i < pos.length; i += 3) {
    const x = basePos[i]
    const y = basePos[i + 1]
    pos[i + 2] = Math.sin(x * freq + time) * amp
  }
  geometry.attributes.position.needsUpdate = true
  geometry.computeVertexNormals()
}

```

- Which attributes need updating?  
    ☐ position  
    ☐ normal  
    ☐ uv  
    ☐ color
    
- Do I recalc normals each frame?
    
    - Yes → smoother lighting
    - No → better performance
        
- Do I use morph targets instead of raw updates?
    

---

### 🧮 5. Buffer Management

- Draw usage hint:
    
    `geometry.attributes.position.usage = THREE.DynamicDrawUsage`
    
- Update pattern:
    
    - Frequent partial changes → `DynamicDrawUsage`
    - Full geometry re-creation → heavy (avoid)
        
- Is index buffer static?  
    (usually yes, unless topology changes)
    
- Should I update GPU only for changed range?  
    → `updateRange = { offset, count }`
    

**Goal:** Keep GPU updates minimal and memory reuse maximal.

---

### 🌈 6. Animated UVs / Colors (Optional)

- Should texture scroll or pulse?
    
    `uv.x += scrollSpeed * time`
    
- Vertex colors changing over time?
    
    - Gradient mapping by height / time / speed
        
- Recalculate color buffer each frame?
    
    - If yes → mark `.needsUpdate = true`
        

---

### ⚙️ 7. Scene Integration

- Material type:
    
    - Standard / Physical / ShaderMaterial?
        
- Does lighting react properly?
    
    - Recompute normals if needed.
        
- Shadow behavior:
    
    - Dynamic geometry may need `castShadow = true`.
        
- Is camera fixed or moving with the shape?
    

---

### 📊 8. Performance Considerations

- Vertex count = ?
- Frame budget = ? (ms/frame)
- Use typed arrays efficiently:
    - Avoid `.push()` inside update loop.
- Batch updates:
    
    - Group multiple updates in one loop.
        
- For large meshes:
    - Consider **Instancing** or **Compute shaders**.
        

**Checklist:**  
✅ Avoid memory reallocations  
✅ Keep `.needsUpdate` minimal  
✅ Profile with `renderer.info.render.calls`

---

### 🧩 9. Debug and Visualization

- Wireframe toggle key:
    `mesh.material.wireframe = !mesh.material.wireframe`
    
- Bounding box helper:
    `scene.add(new THREE.BoxHelper(mesh))`
    
- Show vertex normals:
    
    `const helper = new THREE.VertexNormalsHelper(mesh, 0.1, 0x00ff00) 
    `scene.add(helper)`
    
- Visualize waves / displacements:  
    (Use grid lines or color height by vertex `z`)
    

---

### 🔭 10. Experiment Extensions

- Procedural Noise: Perlin / Simplex / Curl noise
- Morph target blending between shapes
- GPU-based updates via **ShaderMaterial** (vertex shader deformation)
- Hybrid updates: CPU for logic, GPU for final transform
- Dynamic LOD based on camera distance
- Integrate physics (cloth, spring, wind simulation)
    

---

### 🧩 11. Full Animation Loop Skeleton

```js
const clock = new THREE.Clock()

function animate() {
  requestAnimationFrame(animate)
  const t = clock.getElapsedTime()

  updateGeometry(t)

  renderer.render(scene, camera)
}
animate()

```

---

### 🧭 Summary Flow

`Base Shape → Time Model → Vertex Formula → Buffer Update → Normals → Material → Render → Optimize → Extend`
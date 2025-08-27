## 1. What is a `GPUBuffer`?

A `GPUBuffer` is just a chunk of memory that lives on the GPU.  
It’s similar to a **buffer in Vulkan/DirectX/Metal**.

- You allocate it with a **size** and **usage flags**.
- You can **write data into it from the CPU** or **let the GPU write into it** (via shaders/compute).
- Then you **bind** it (via a bind group) so shaders can use it.

---

## 2. GPUBuffer Usage Types

When you create a buffer, you pass a combination of usage flags (bitmask).  
Each flag tells WebGPU how you intend to use that memory.

### Common Usage Flags:

1. **`GPUBufferUsage.MAP_READ`**
    - CPU can **map and read** the buffer after GPU writes.
    - Example: reading back results from a compute shader.

2. **`GPUBufferUsage.MAP_WRITE`**
    - CPU can **map and write** directly into buffer memory.
    - Example: uploading initial data to the GPU without staging.

3. **`GPUBufferUsage.COPY_SRC`**
    - Buffer can be a **source in a copy operation**.
    - Example: copying from GPU to CPU-visible buffer.

4. **`GPUBufferUsage.COPY_DST`**
    - Buffer can be a **destination in a copy operation**.
    - Example: uploading data from CPU → GPU.

5. **`GPUBufferUsage.INDEX`**
    - Buffer holds **index data** for indexed drawing.

6. **`GPUBufferUsage.VERTEX`**
    - Buffer holds **vertex attributes**.

7. **`GPUBufferUsage.UNIFORM`**
    - Buffer is used as a **uniform buffer** (read-only in shaders).
    - Example: camera matrices, lighting data.

8. **`GPUBufferUsage.STORAGE`**
    - Buffer is used as a **storage buffer** (read-write in shaders).
    - Example: particle positions array, compute shader outputs.

9. **`GPUBufferUsage.INDIRECT`**
    - Buffer can be used in **indirect draw/dispatch calls**.
    - Example: GPU computes how many particles to draw, then uses buffer as argument for `drawIndirect`.


---

## 3. Typical Usage Patterns

- **Vertex Buffers** → `VERTEX | COPY_DST`  
    (you upload vertex data from CPU and bind as vertex input)
    
- **Index Buffers** → `INDEX | COPY_DST`  
    (same but for indices)
    
- **Uniform Buffers** → `UNIFORM | COPY_DST`  
    (small constant data like matrices, updated per frame)
    
- **Storage Buffers** → `STORAGE | COPY_DST | COPY_SRC`  
    (big arrays for compute, like particle positions, can read/write in compute)
    
- **Readback Buffers** → `MAP_READ | COPY_DST`  
    (GPU writes → copy → CPU reads results)
    
- **Upload Buffers** → `MAP_WRITE | COPY_SRC`  
    (CPU writes → copy → GPU uses it)
    

---

## 4. Example

```js
//Create a buffer for 100 particles (vec4 = 16 bytes each) 
const particleBuffer = device.createBuffer({ 
    size: 100 * 16,   usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST | GPUBufferUsage.COPY_SRC, 
});
```


- This buffer can be used in compute shaders (`STORAGE`)
- You can upload data from CPU (`COPY_DST`)
- You can read results back (`COPY_SRC`)

---

✅ So the main thing to remember:

- **GPUBuffer itself is just memory**.
- **Usage flags define how you can interact with it**.
- **Bind groups & layouts decide how shaders see them**.
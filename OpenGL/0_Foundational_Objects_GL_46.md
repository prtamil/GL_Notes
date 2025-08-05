## ✅ Well-known objects you already mentioned

- **Buffer Objects** – store vertex data, index data, uniforms, shader storage, etc.
    
- **Texture Objects** – store images, mipmaps, cube maps, arrays.
    
- **Framebuffer Objects (FBOs)** – define rendering targets (attachments: textures/renderbuffers).
    

---

## 🧩 Additional core OpenGL objects

|Object|Purpose|
|---|---|
|**Vertex Array Objects (VAO)**|Capture all vertex input state: enabled attributes, buffer bindings, attribute formats.|
|**Renderbuffer Objects**|Offscreen rendering storage, usually used as FBO attachments (often for depth/stencil).|
|**Shader Objects**|Individual compiled shader stages (vertex, fragment, geometry, tess control/eval, compute).|
|**Program Objects**|Linked set of shaders; defines a complete shader pipeline.|
|**Program Pipeline Objects**|(from ARB_separate_shader_objects, core in 4.1+) Allow mixing/matching separate shader stages without a full link.|
|**Sampler Objects**|Store sampling state (filtering, wrap modes) separately from textures, so multiple textures can share the same sampling rules.|
|**Transform Feedback Objects**|Capture output from the vertex, tessellation, or geometry stage into buffers.|
|**Query Objects**|Measure things like number of samples passed, primitives generated, elapsed GPU time.|
|**Sync Objects**|Synchronization primitives: fences, sync objects for coordinating CPU/GPU.|

---

## 📦 Newer / more specialized objects in 4.6

|Object|Purpose|
|---|---|
|**Texture Views**|Allow reinterpretation of an existing texture’s storage (e.g., reinterpret as different format or view subset of layers).|
|**Sparse Textures / Sparse Buffers**|Manage large virtual textures/buffers without fully allocating memory.|
|**Buffer Textures**|Special textures backed by buffer objects, useful for large 1D arrays.|
|**Atomic Counter Buffers**|Used with atomic counters in shaders.|
|**Shader Storage Buffer Objects (SSBOs)**|Provide large read-write data storage for shaders.|
|**Uniform Buffer Objects (UBOs)**|Store uniform data, share across multiple programs.|

---

## 🧪 Rare / advanced

|Object|Purpose|
|---|---|
|**Pixel Buffer Objects (PBOs)**|Specialized buffer usage for asynchronous pixel transfers (uploads/downloads).|
|**Indirect Buffer Objects**|Contain draw parameters for indirect drawing commands.|
|**Clip Control Objects**|(Not an object, but clip control state from 4.5+).|
|**Debug Objects**|Debug groups and markers (from KHR_debug). Not “objects” in strict sense, but part of debug system.|

---

### 🧠 Summary

In modern OpenGL, everything you manage on the GPU is usually encapsulated in some type of object:

- Data (buffers, textures, renderbuffers)
- Shaders & programs
- State containers (VAOs, samplers, pipelines)
- Queries & sync

Objects are created by `glGen*`, configured with `glBind*` and `gl*` calls, and deleted with `glDelete*`.
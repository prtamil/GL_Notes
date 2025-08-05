# 📦 **✨ Chapter 6 (Texture Mapping) – self-questions list**

_(Grouped by perspective, but you can mix them)_

---

## 👨‍💻 **Seasoned engine programmer questions**

_(focus: “how do I actually use this in real rendering?”)_

## ✅ What is a texture _object_? What is stored in it?  
## ✅ What is a texel? How is it different from a pixel?  
## ✅ Why do we store texture data in GPU memory instead of CPU RAM?  
## ✅ What does `glTexImage2D` do behind the scenes?  
## ✅ Why do we call `glGenTextures` / `glBindTexture` before upload?  
## ✅ What is the difference between texture and sampler?  
## ✅ How do filtering modes (GL_LINEAR / GL_NEAREST) affect final visual output?  
	Filtering modes tell the GPU **how to pick a color** when a texture is being sampled, especially when:

- The texture is **larger** than the screen region (minification)
    
- The texture is **smaller** than the screen region (magnification)
    

These are the most common:

| Constant     | Meaning                             |
| ------------ | ----------------------------------- |
| `GL_NEAREST` | **Nearest-neighbor** sampling       |
| `GL_LINEAR`  | **Bilinear interpolation** (smooth) |
## ✅ What is the wrap mode? Why do we need GL_REPEAT vs GL_CLAMP_TO_EDGE?  
Wrap mode in OpenGL defines **how texture coordinates outside the standard [0, 1] range** are handled during texture sampling.

### 🔍 Why Texture Coordinates Go Outside [0, 1]

In your shader (typically fragment shader), when mapping textures onto geometry (e.g., a quad or 3D model), you often compute UVs that are:

- Repeating across a surface (`>1.0`)
    
- Partially clipped or overshooting (`<0.0`)
    
- Dynamically manipulated for effects like scrolling or distortion
    

This is where **wrap mode** kicks in.

---

### 🎨 `glTexParameteri` → `GL_TEXTURE_WRAP_S/T/R`

- `GL_TEXTURE_WRAP_S`: Horizontal wrap mode (U coordinate)
    
- `GL_TEXTURE_WRAP_T`: Vertical wrap mode (V coordinate)
    
- `GL_TEXTURE_WRAP_R`: For 3D textures (W coordinate)
    

### Common values:

| Wrap Mode            | Description                                                               |
| -------------------- | ------------------------------------------------------------------------- |
| `GL_REPEAT`          | UVs wrap around (like tiles). `1.1` → `0.1`, `-0.2` → `0.8`               |
| `GL_MIRRORED_REPEAT` | Like `GL_REPEAT`, but alternates mirror-flipped (good for reducing seams) |
| `GL_CLAMP_TO_EDGE`   | Clamps UVs outside [0,1] to nearest edge texel. Prevents repetition.      |
| `GL_CLAMP_TO_BORDER` | Clamps to a defined border color (needs extra setup).                     |

---

### 🎯 Why Use `GL_REPEAT` vs `GL_CLAMP_TO_EDGE`

| Use Case                               | Recommended Wrap Mode | Reason                                   |
| -------------------------------------- | --------------------- | ---------------------------------------- |
| Tiling textures (e.g., floor, wall)    | `GL_REPEAT`           | Repeats texture seamlessly for tiling    |
| Sprite sheets or UI (atlas)            | `GL_CLAMP_TO_EDGE`    | Avoids bleeding from neighboring sprites |
| Skyboxes or fullscreen quads           | `GL_CLAMP_TO_EDGE`    | Ensures edge texels are used cleanly     |
| Special effects (procedural, mirrored) | `GL_MIRRORED_REPEAT`  | Can reduce visible tiling artifacts      |
### 🧪 Example Code

```cpp
// Set wrap mode for a 2D texture
glBindTexture(GL_TEXTURE_2D, texID);
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);  // U
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);  // V

```
---

### 🧠 Visual Intuition

Imagine sampling a texture at coordinate `(1.3, -0.2)`:

|Wrap Mode|What Happens|
|---|---|
|`GL_REPEAT`|`(0.3, 0.8)` — wrapped around|
|`GL_CLAMP_TO_EDGE`|`(1.0, 0.0)` — stuck at edge|
|`GL_MIRRORED_REPEAT`|`(0.3, 0.2)` — flipped (like mirror)|

---

### ✅ When to Choose What

- Use `GL_REPEAT` **when you intentionally want tiling** (e.g., brick walls, terrains).
- Use `GL_CLAMP_TO_EDGE` **when precision is key**, like for **UI textures**, **spritesheets**, or **non-repeating backgrounds**.
- If you see **artifact seams**, especially in atlases, switch to `GL_CLAMP_TO_EDGE`.
## ✅ When we do `texture(sampler, uv)` in fragment shader — what really happens inside GPU?  
Great question. Let's break down what _actually_ happens inside the GPU when you call this in your **fragment shader**:

glsl

CopyEdit

`vec4 color = texture(mySampler, uv);`

This single line triggers a **complex hardware pipeline** under the hood. Here's a step-by-step conceptual breakdown:

---

### 🔬 Step-by-Step: What Happens in GPU When You Call `texture(...)`

---

#### 1. **UV Coordinates Are Interpolated**

From the **vertex shader**, texture coordinates (`uv`) are passed as a `varying` (now called `in` in GLSL 3.3+).  
During rasterization:

- The hardware interpolates the `uv` for each pixel/fragment (usually perspective-correct).
    

`in vec2 uv; // coming from vertex shader, interpolated`

---

#### 2. **Sampler State & Texture Unit Are Queried**

The `sampler` refers to:

- A bound **texture object** (`glBindTexture`)
    
- A bound **sampler object** (or sampler state set via `glTexParameter`)
    

This combination defines:

- **Filtering** (`GL_LINEAR`, `GL_NEAREST`)
    
- **Wrap mode** (`GL_REPEAT`, `GL_CLAMP_TO_EDGE`)
    
- **Mipmap settings**
    
- **Border color**
    
- **Anisotropic filtering**, etc.
    

---

#### 3. **UV Coordinate Processing (Wrap Mode)**

If `uv` is outside [0, 1]:

- The **wrap mode** kicks in: `GL_REPEAT`, `CLAMP_TO_EDGE`, etc.
    
- Transforms the UV to stay within texture bounds appropriately.
    

---

#### 4. **Texel Location Computed**

Next, the GPU calculates the **texture coordinates in texel space**:

- Suppose the texture is 512×512
    
- `uv = (0.5, 0.25)` → texel = `(256, 128)`
    

The exact texel position might not be integer-aligned, so:

---

#### 5. **Filtering Mode Applied**

If filtering is:

- `GL_NEAREST`: Chooses the closest texel.
    
- `GL_LINEAR`: Samples the 4 nearest texels and interpolates based on UV offset (bilinear interpolation).
    
- Mipmapping: If enabled, uses multiple mip levels and blends (trilinear interpolation).
    

GPU may compute:

- Derivatives of UV to pick correct mip level (`dFdx`, `dFdy` implicitly)
    
- LOD (Level of Detail) selection happens automatically unless manually overridden (`textureLod`)
    

---

#### 6. **Texel(s) Fetched From GPU Memory**

- The GPU fetches the texel(s) from texture memory (VRAM or texture cache).
    
- If it's a 2D texture, it fetches from a 2D texel grid.
    
- Uses caching and prefetching for performance.
    

If **bindless textures** are used (OpenGL 4.4+), the pointer to the texture lives in the shader instead of traditional binding points.

---

#### 7. **Color Value Returned**

- The final color value (`vec4`) is computed after all interpolation and filtering.
    
- Any **sRGB correction**, **swizzling**, or **texture format decoding** (e.g., `GL_RGBA8`, `GL_R16F`, etc.) is applied.
    

Then:


`vec4 color = ... // returned final pixel color`

---

### 📦 Summary: `texture(sampler, uv)` triggers...

|Stage|What Happens|
|---|---|
|1️⃣ Interpolation|UV from vertex shader interpolated|
|2️⃣ Sampler State Lookup|Reads texture settings (filter, wrap)|
|3️⃣ UV Wrapping|Handles out-of-range UVs|
|4️⃣ Texel Coordinate Calculation|Converts UV to texel positions|
|5️⃣ Filtering & Mipmapping|Applies GL_LINEAR, mip LOD, etc.|
|6️⃣ Memory Fetch|Samples from texture memory or cache|
|7️⃣ Return Final Color|After interpolation, correction, decoding|

---

### ⚙ Bonus: GPU Hardware Involvement

- Dedicated **texture units** do most of this.
    
- They are optimized to run in parallel across many fragments.
    
- Most modern GPUs have **cache hierarchies for texture fetches** to avoid repeated VRAM access.
    

---

### 🧠 Visual Metaphor

Imagine:

- Your `uv` is a pointer to a spot on a painting.
    
- The GPU decides how to read that spot (with a magnifying glass? blurry? repeat painting?)
    
- Then it grabs the color, blends if needed, and gives it to your pixel.
## ✅ How do mipmaps change sampling at different distances?  

Great question. **Mipmaps** (short for _multum in parvo_, meaning "many in one") fundamentally change how textures are sampled **based on distance and screen size**, improving performance and visual quality.

---

### 🧠 TL;DR:

**Mipmaps are precomputed, downscaled versions of a texture.**  
When a fragment is far away (small on screen), the GPU **samples a lower-res mipmap level** instead of the full-resolution texture to:

- Avoid aliasing
    
- Improve cache efficiency
    
- Reduce GPU memory bandwidth
    

---

### 🔁 How Mipmaps Work

Given a base texture of size `512x512`, mipmaps look like this:

|Mipmap Level|Size|
|---|---|
|0|512 × 512|
|1|256 × 256|
|2|128 × 128|
|3|64 × 64|
|...|...|
|9|1 × 1|

All mipmaps are powers of two and automatically generated with `glGenerateMipmap`.

---

### 🧬 When Are Mipmaps Used?

When your texture is **rendered at a reduced size** on screen (e.g. distant terrain, or a tiny object in 3D space), sampling the full-res texture causes:

- **Aliasing** (jagged artifacts)
    
- **Wasted bandwidth**
    

Instead, the GPU chooses a mipmap level based on **how fast the UVs change per pixel** — the **screen-space derivative of UV** (`dFdx`, `dFdy`).

---

### 🔍 Sampling Decision



`vec4 color = texture(sampler2D, uv);`

Internally:

- GPU computes **texture LOD (Level of Detail)** using derivatives of UV.
    
- Picks the best mip level (e.g., level 3 → 64x64) based on distance/screen coverage.
    

You can override with:


`textureLod(sampler2D, uv, mip_level);  // force LOD`

---

### 🎯 Real-World Example

Imagine a wall texture:

- **Close to camera** → full res (512×512) is sampled.
    
- **Far away** → 64×64 or 16×16 is sampled instead.
    
- Result: smoother visuals without shimmering.
    

#### 🎞️ Without Mipmaps:

- Distant textures may flicker or look noisy (aliasing).
    
- All samples come from level 0 — wasteful.
    

#### 🎞️ With Mipmaps:

- Samples come from appropriate resolution.
    
- Less aliasing, better performance.
    

---

### 🔄 Filtering Modes with Mipmaps

When using mipmaps, the following filtering modes apply:

|Min Filter|Meaning|
|---|---|
|`GL_NEAREST_MIPMAP_NEAREST`|Nearest texel from nearest mipmap level|
|`GL_LINEAR_MIPMAP_NEAREST`|Linear texel filter from nearest mipmap level|
|`GL_NEAREST_MIPMAP_LINEAR`|Nearest texel from **2 mipmaps**, blend mipmaps|
|`GL_LINEAR_MIPMAP_LINEAR`|**Trilinear filtering** (linear in texel + mip) ✅ Best quality|


```cpp
glSamplerParameteri(sampler, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
glSamplerParameteri(sampler, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
glSamplerParameteri(sampler, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
glSamplerParameteri(sampler, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
```

---

### 🖼️ Visual Summary

Imagine a texture-covered plane stretching into the distance:

```txt
Camera
  |
  V
[High-Res Texture Near]     (LOD 0)
     [Mid Mip Level]        (LOD 3)
         [Blurry Far]       (LOD 6 or 7)

```

Each LOD handles a region based on how large the object appears in screen space.

---

### 💡 Why It Matters

|Benefit|Explanation|
|---|---|
|✅ Less Aliasing|Avoids high-frequency noise at distance|
|✅ Better Performance|Lower-res textures are faster to sample|
|✅ Memory Efficient|Reduces over-fetching from VRAM|

---

### 🧪 OpenGL Usage Example

```cpp
// Step 1: Create texture
GLuint texture;
glGenTextures(1, &texture);
glBindTexture(GL_TEXTURE_2D, texture);
// Upload texture image here...
glGenerateMipmap(GL_TEXTURE_2D);

// Step 2: Create a sampler object
GLuint sampler;
glGenSamplers(1, &sampler);

// Configure sampler settings
glSamplerParameteri(sampler, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
glSamplerParameteri(sampler, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
glSamplerParameteri(sampler, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
glSamplerParameteri(sampler, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

// Step 3: Bind the texture and sampler to the same texture unit
GLuint textureUnit = 0; // e.g., GL_TEXTURE0

glActiveTexture(GL_TEXTURE0 + textureUnit);
glBindTexture(GL_TEXTURE_2D, texture);
glBindSampler(textureUnit, sampler); // Sampler bound separately


//Fragment
uniform sampler2D myTexture;

void main() {
    vec4 color = texture(myTexture, uv);
}

```

## ✅ Why do we generate mipmaps? What would go wrong without them?  

We **generate mipmaps** to solve two major problems in texture sampling:

---

### 🎯 1. **Avoid Aliasing at a Distance**

When an object is far from the camera, it covers fewer pixels on the screen — but its texture might still be huge (e.g., 1024×1024).

Without mipmaps:

- The GPU samples texels that are **much smaller** than the pixel footprint.
    
- Result: **aliasing**, **shimmering**, and **moiré patterns** during motion.
    

#### 🔍 Why this happens:

- Texture sampling becomes **undersampled**.
    
- High-frequency texel details are not filtered properly → pixel "jumps" or flickers on camera movement.
    

---

### 📉 2. **Wasted Performance and Bandwidth**

Without mipmaps:

- The GPU **always fetches from the highest-resolution level** (`level 0`) even if only 4×4 pixels are visible on screen.
    
- Massive overfetch from VRAM → poor cache utilization.
    

#### 💡 With mipmaps:

- GPU picks a **lower-res version of the texture** that matches screen size (via automatic LOD).
    
- Result: Less memory traffic, faster sampling, better texture cache hit rates.
    

---

### 🔧 What Are Mipmaps?

Mipmaps are **precomputed, power-of-two downscaled versions** of the original texture:

| Level | Size      |
| ----- | --------- |
| 0     | 1024×1024 |
| 1     | 512×512   |
| 2     | 256×256   |
| ...   | ...       |
| N     | 1×1       |

When you enable mipmapping and do:

cpp

CopyEdit

`glGenerateMipmap(GL_TEXTURE_2D);`

OpenGL builds this whole chain.

---

### ⚠️ What Goes Wrong Without Mipmaps?

#### ❌ Visual Issues:

- Aliasing: sparkly or flickering noise on distant textures
    
- Moiré patterns: distorted patterns due to interference of sampling
    

#### ❌ Performance Issues:

- Every pixel samples from large textures (even if just 2–3 pixels shown on screen)
    
- Reduced texture cache efficiency → **slower rendering**
    

---

### ✅ With Mipmaps:

- **Level-of-detail (LOD)** is chosen automatically by the GPU based on screen size
    
- You can use **trilinear filtering** (`GL_LINEAR_MIPMAP_LINEAR`) to blend between mip levels smoothly
    


`glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);`

This avoids harsh transitions between mip levels.

---

### 🧪 Real-World Analogy:

> Imagine printing a high-res poster (1024×1024) and sticking it on a matchbox.  
> From far away, it just looks noisy.  
> Instead, you should print a low-res version suited to the matchbox size.  
> That’s what mipmaps do automatically — pick the right texture resolution for the right size.

---

### 🧠 Summary

| With Mipmaps                     | Without Mipmaps                     |
| -------------------------------- | ----------------------------------- |
| ✅ Less aliasing (better quality) | ❌ Aliasing, shimmering, moiré       |
| ✅ Faster sampling                | ❌ Over-fetching from memory         |
| ✅ Smooth LOD transitions         | ❌ No level-of-detail control        |
| ✅ Modern pipeline compatible     | ❌ Considered outdated for 3D render |

## ✅ What’s the GPU pipeline path from CPU buffer → texture → fragment shader → framebuffer?
### 🧭 Overview: The Pipeline Path

```
CPU Buffer (image data)
   ↓
Upload to GPU (Texture Memory)
   ↓
Texture Sampling (Fragment Shader)
   ↓
Fragment Coloring
   ↓
Framebuffer Write

```

We’ll break this down into **concrete steps** with **OpenGL objects** and what happens inside the **GPU hardware**.

---

### 🧱 1. CPU Uploads Texture Data (Client Side → GPU VRAM)

You start by loading image data (e.g., PNG, JPEG) into CPU memory, then do:

```
glGenTextures(1, &tex);
glBindTexture(GL_TEXTURE_2D, tex);
glTexImage2D(..., data);  // Upload CPU buffer to GPU texture memory
glGenerateMipmap(GL_TEXTURE_2D);  // Optional, but recommended

```

#### GPU Action:

- Allocates space in **dedicated GPU memory (VRAM)**
    
- Optionally creates **mipmap chain**
    
- Applies **texture format conversion** if needed
    

Now texture data lives in GPU.

---

### 🎯 2. Texture Is Sampled in Fragment Shader

In the shader:

```
uniform sampler2D tex;
in vec2 uv;  // interpolated from vertex shader
void main() {
    vec4 color = texture(tex, uv);
}

```
#### GPU Action:

- Uses **interpolated UV coords**
    
- Finds the correct **mipmap level** using derivatives (`dFdx/dFdy`)
    
- Applies:
    
    - **Wrap mode** (`GL_REPEAT`, etc.)
        
    - **Filtering** (`GL_LINEAR`, `GL_NEAREST`)
        
- **Fetches texels** from texture memory
    
- Returns a `vec4` color
    

The sampled color is now part of your fragment.

---

### 🎨 3. Fragment Shader Computes Final Color

You might combine texture sample with lighting:

```
vec3 litColor = texture(tex, uv).rgb * diffuseLighting;

```

This is your **final pixel color**, output by:

```
out vec4 fragColor;

```

---

### 🖼️ 4. Output Goes to Framebuffer

Final fragment color is written to:

- **Default framebuffer** → onscreen image
    
- Or a **user FBO** (for deferred shading, post-processing, etc.)
    

```
glBindFramebuffer(GL_FRAMEBUFFER, 0);  // Default framebuffer

```

#### GPU Action:

- Applies:
    
    - **Depth test**
        
    - **Alpha blending**
        
    - **Stencil operations** (if enabled)
        
- Converts fragment to appropriate **pixel format** (`GL_RGBA8`, `sRGB`, etc.)
    
- Stores result in the **framebuffer attachment**
    

---

### 🧬 Entire Flow in a Table

| Stage              | Object / API                   | Data          | GPU Action                   |
| ------------------ | ------------------------------ | ------------- | ---------------------------- |
| **1. Upload**      | `glTexImage2D`                 | CPU buffer    | Copies to texture memory     |
| **2. Sampling**    | `texture()` in fragment shader | UV coords     | Computes LOD, fetches texels |
| **3. Shading**     | GLSL math                      | RGB, lighting | Computes final color         |
| **4. Framebuffer** | `glBindFramebuffer`            | Color/depth   | Writes to screen or FBO      |

---

### 🧠 Visual Summary

```
[CPU Image Data]
      ↓ glTexImage2D
[GPU Texture Memory]
      ↓ texture(sampler, uv)
[Fragment Shader Output]
      ↓ Raster Ops
[Framebuffer Pixel]

```

---

### 📦 Optional: Intermediate Buffers

If you use **Framebuffer Objects (FBOs)**, you can redirect the fragment output to a **texture**, not the screen:

```
glBindFramebuffer(GL_FRAMEBUFFER, myFBO);
glFramebufferTexture2D(...);

```

Then use the output texture for **post-processing**, **bloom**, **shadow maps**, etc.

---

### 🧪 Example Shader Setup

```
uniform sampler2D albedoTex;

in vec2 fragUV;
out vec4 fragColor;

void main() {
    vec4 texColor = texture(albedoTex, fragUV);
    fragColor = texColor;  // Final output to framebuffer
}

```

---

### ✅ Summary

| Concept       | What It Does                       |
| ------------- | ---------------------------------- |
| **Texture**   | Stores image data on GPU           |
| **Sampler**   | Defines how texture is accessed    |
| **Shader**    | Samples texture and produces color |
| **Framebuffer | Receives final pixel for display   |

---

## 🛠 **Professional engine programmer questions**

_(focus: practical game engine, real-time renderer, multipass)_

✅ Why do we often store normal maps, roughness maps, metalness maps — not just color?  
✅ How do we manage multiple textures per material? (diffuse, specular, etc.)  
✅ How do shaders get UV coordinates? Who provides them?  
✅ When sampling: what happens if UV is outside [0,1]?  
✅ How do FBOs (framebuffer objects) let us render to textures?  
✅ Why do we often downsample textures for post-processing (e.g., bloom)?  
✅ What are texture units? Why do we need to set active texture before binding?  
✅ What happens if we forget to set correct texture unit in shader?  
✅ What’s the cost difference between sampling once vs. sampling multiple times per fragment?  
✅ Why is texture sampling “expensive” compared to arithmetic?  
✅ When do we need to think about texture compression?  
✅ Why do we sometimes use texture arrays or 3D textures instead of many 2D textures?

---

## 🎓 **Graphics researcher / professor questions**

_(focus: why it exists, what’s mathematically happening, quality, aliasing)_

✅ What is a texture mathematically? (function from UV to color)  
✅ Why do we sample using normalized coordinates (0→1)?  
✅ What is aliasing? How does texture filtering help?  
✅ What is minification? What is magnification?  
✅ Why do we get shimmering on distant surfaces without mipmaps?  
✅ What is anisotropic filtering? Why do we need it when viewing at grazing angles?  
✅ What happens when we sample a texel that doesn’t align perfectly with the pixel?  
✅ Why do we interpolate between multiple texels?  
✅ What is the difference between sampling in vertex shader vs. fragment shader?  
✅ What is sRGB texture? Why does gamma matter?  
✅ Why can sampling textures in fragment shader create artifacts if UV derivatives are too large?  
✅ What is the difference between “point sampling” and “linear sampling” at GPU level?

---

## 🧪 **✅ Super practical wrap-up questions (tie it all together)**

✅ What data lives on CPU, what data lives on GPU?  
✅ How do we go from image file (PNG/JPEG) → GPU texture?  
✅ At fragment shader stage, what do we really get when we call `texture()`?  
✅ What decisions change quality vs. speed in texture mapping?  
✅ Why do some games have “texture shimmering” or blurry textures?  
✅ How do you debug “wrong texture shows on object”?  
✅ What parts of texture mapping happen _only once_ at load time, and what parts happen _every frame_?

---
# Questions on Buffers and Shaders
💡 **Absolutely!** You’re basically building a _mental self-question workbook_ — exactly how serious graphics programmers, engine devs, and researchers keep sharp.  
Let’s do the same round-table:

> 👨‍💻 Seasoned engine programmer (Carmack/Sweeney style) → practical, “how it really runs on GPU”  
> 🛠 Professional engine programmer → real-world usage in engines / renderers  
> 🎓 Graphics researcher → deeper theory: why, math, data flow

We’ll split into two parts:

- **Part A: GPU Buffers** (VBOs, UBOs, SSBOs)
    
- **Part B: Shaders** (vertex, fragment, etc.)
    

All questions go from _newbie level → advanced, but still answerable by yourself_.

---

## 🧵 **Part A: GPU Buffers – Questions to ask yourself**

---

## 👨‍💻 **Seasoned engine programmer: GPU Buffers**

✅ What is a buffer object really? (memory block in GPU RAM)  
✅ What kinds of data do we usually put into GPU buffers?  
✅ What is the difference between a VBO (Vertex Buffer Object) and an EBO/IBO (Element / Index Buffer Object)?  
✅ Why do we use index buffers?  
✅ What is the difference between static and dynamic draw in glBufferData?  
✅ When I call glBufferSubData, what really happens?  
✅ What happens if the buffer is in use by the GPU and we update it from CPU?  
✅ How big can a buffer be?  
✅ What is VAO (Vertex Array Object) and why do we need it with buffers?  
✅ How does the GPU know where in the buffer to find position, normal, UV?  
✅ Why do we bind buffers to different targets (GL_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER, etc.)?  
✅ What is the difference between a buffer used as vertex data vs. uniform data?

---

## 🛠 **Professional engine programmer: GPU Buffers**

✅ What data might change every frame vs stay static?  
✅ Why might we want to have multiple dynamic buffers instead of reusing one?  
✅ Why do we sometimes “triple buffer” dynamic vertex data?  
✅ What is a Uniform Buffer Object (UBO)? When do we use it?  
✅ What is a Shader Storage Buffer Object (SSBO)? Why more flexible than UBO?  
✅ Why do we often align data in UBOs (std140, std430)?  
✅ How do we debug wrong offsets in UBO / SSBO?  
✅ What happens if we use wrong buffer binding index in shader?  
✅ Why do big models often have many VBOs?  
✅ When would we combine multiple objects into one big VBO?  
✅ What are the tradeoffs: one big buffer vs many small buffers?

---

## 🎓 **Graphics researcher: GPU Buffers**

✅ In theory, what is a buffer? (linear memory range)  
✅ Why do we need explicit buffer bindings?  
✅ How do attributes in vertex shader map to offsets in VBO?  
✅ Why do UBOs have alignment rules?  
✅ Why do SSBOs allow arbitrary reads/writes but UBOs don’t?  
✅ What is the difference between buffer read-only vs read-write?  
✅ How do GPU cache lines affect buffer performance?  
✅ Why do we need to “orphan” buffers (glBufferData NULL then refill)?  
✅ What happens if we read/write same buffer in two shaders in parallel?  
✅ Why can't we just use CPU RAM directly instead of GPU buffer?

---

---

## 🧵 **Part B: Shaders – Questions to ask yourself**

---

## 👨‍💻 **Seasoned engine programmer: Shaders**

✅ What is a shader program?  
✅ What is the difference between vertex shader and fragment shader?  
✅ What data does vertex shader run on?  
✅ What data does fragment shader run on?  
✅ Why are there usually more fragment shader invocations than vertex shader?  
✅ What are uniforms? When are they set?  
✅ Why do we often pass data as attributes vs uniforms?  
✅ What happens when we change a uniform while shader is running?  
✅ Why can’t vertex shader access texture coordinates of neighboring vertices?  
✅ Why do we write shaders in GLSL? What compiles them?

---

## 🛠 **Professional engine programmer: Shaders**

✅ How does shader get vertex position from buffer?  
✅ What does the vertex shader _output_? (clip space pos + varyings)  
✅ How does fragment shader get interpolated varyings?  
✅ Why do we sometimes get “flat shading”?  
✅ What are built-in variables like gl_Position, gl_FragCoord?  
✅ Why do we sometimes compute lighting in vertex shader vs fragment shader?  
✅ Why is it slower to sample textures in fragment shader?  
✅ What is the cost difference between a `texture()` call vs arithmetic?  
✅ How do we organize complex materials with many shader files?  
✅ How do engines compile and manage many shader variants?

---

## 🎓 **Graphics researcher: Shaders**

✅ Why does vertex shader run per vertex, fragment shader per pixel?  
✅ What is perspective-correct interpolation?  
✅ Why do we get artifacts if derivatives (dFdx/dFdy) are too large?  
✅ What is the difference between per-vertex and per-fragment lighting?  
✅ What are tessellation shaders and geometry shaders for?  
✅ Why do we have compute shaders? How are they different?  
✅ Why can’t fragment shader write to arbitrary framebuffer pixels?  
✅ Why do we separate vertex & fragment shaders instead of monolithic shader?  
✅ What is branch divergence in fragment shader and why does it hurt performance?  
✅ Why do shaders run in _SIMD_ on GPU?


# Questions for GL understanding and get offer letters
ok guys last query give me suppose each guys want to recruit junior person in your team and what would you ask that guy so if they answer correctly you immediatly feel safe and absolutly know that jr. person can do the task and you hand out appoinment letter. ask as much question you want in opengl

###### ChatGPT said:

🔥 **Ohhh — love this!**  
A _real_ round table of seasoned hiring managers, each from their world:

> 👨‍💻 Carmack/Sweeney type → deeply practical, low-level GPU mindset  
> 🛠 Unreal/Unity pro team lead → pragmatic, task-focused, needs someone who can ship  
> 🎓 Graphics researcher / prof → conceptual, theory-driven, clean mental models

Each one will list:  
✅ _What they'd ask a junior graphics dev specifically for OpenGL / realtime rendering_  
✅ _What answers would make them say: “yep, this person gets it — hire them!”_

I’ll keep it beginner-to-mid-level, but enough to _prove_ the candidate isn’t just copying code blindly.

---

## 👨‍💻 **Seasoned engine programmer (Carmack/Sweeney style)**

_(goal: confirm candidate _really_ understands GPU pipeline & data flow)_

**Questions:**  
✅ “Explain, step by step, how to draw a textured quad on screen in OpenGL.”  
✅ “What is the difference between a texel and a pixel?”  
✅ “When you call `glTexImage2D` what really happens?”  
✅ “Where do UV coordinates come from? Who sets them?”  
✅ “What is a framebuffer object (FBO) and why do we need it?”  
✅ “Explain what happens when you call `texture(sampler, uv)` in fragment shader.”  
✅ “Why do we need mipmaps?”  
✅ “What is the difference between `GL_LINEAR` and `GL_NEAREST` filter?”  
✅ “Why can’t you read from and write to the same texture in the same pass?”  
✅ “What’s the difference between VAO and VBO?”

**If they answer confidently and correctly, I instantly know:**  
→ _They actually wrote real OpenGL code, not just tutorials._  
→ _They understand data flow CPU → GPU → raster → shader → framebuffer._

---

## 🛠 **Professional game engine programmer / Unreal/Unity team lead**

_(goal: candidate can actually build, debug, and ship a feature)_

**Questions:**  
✅ “Imagine I give you a PNG — describe exactly how you’d show it on a spinning cube in OpenGL.”  
✅ “How do you bind multiple textures in one shader?”  
✅ “What is a uniform? How do you set it in C++?”  
✅ “What’s the difference between a uniform and a vertex attribute?”  
✅ “How do you handle resizing the window and keep rendering correct?”  
✅ “Suppose texture looks stretched / wrong on mesh. How do you debug it?”  
✅ “Why do we use index buffers?”  
✅ “What is backface culling? When might we disable it?”  
✅ “How do you render scene to texture and then apply blur?”  
✅ “Why do we separate vertex shader and fragment shader?”

**Right answers prove:**  
→ _They know real-world rendering pipeline & can debug it._  
→ _They understand resource binding, state changes, multiple passes._

---

## 🎓 **Graphics researcher / prof**

_(goal: strong conceptual model — candidate truly “gets” graphics)_

**Questions:**  
✅ “What is texture mapping mathematically?”  
✅ “Why do we interpolate varyings from vertex to fragment shader?”  
✅ “Explain aliasing in textures and how mipmaps reduce it.”  
✅ “Why do we sample textures in fragment shader, not vertex shader?”  
✅ “What is the difference between object space, world space, view space, clip space, NDC, screen space?”  
✅ “Why do we use normalized [0–1] texture coordinates?”  
✅ “What is the difference between sampling and filtering?”  
✅ “What happens if you don’t generate mipmaps but set min filter to use them?”  
✅ “Why do GPUs run shaders in SIMD and why does that matter?”  
✅ “What is perspective-correct interpolation and why do we need it?”

**If they can answer:**  
→ _They understand _why_ graphics works, not just how to call API._

---

## 🧠 **✅ In summary:**

If a junior can answer:

- ✅ How to load texture → GPU → draw with shader
    
- ✅ What texture coordinates do, where they come from
    
- ✅ Why filters, mipmaps, and wrap modes exist
    
- ✅ What happens in vertex shader & fragment shader
    
- ✅ Difference between texels and pixels
    
- ✅ How data flows CPU → GPU → framebuffer
    

Then even a seasoned team would say:

> “Great, you’ll learn the rest on the job. Welcome aboard.”

---

⚡ **If you'd like:**

- I can merge all these into an **Obsidian/Markdown study sheet**
    
- Or make a _one-page “OpenGL interview quick reference”_
    

Just say:  
✔ _“Yes, give me the interview sheet!”_  
✔ _“Draw a data flow diagram too!”_
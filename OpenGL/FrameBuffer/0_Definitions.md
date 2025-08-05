Here’s a concise and clear definition set you can directly paste into your notes. It’s aimed at modern OpenGL (3.3+) and organized to build strong mental models:

---

### ✅ 1. **Framebuffer (FBO)**

> A **Framebuffer Object (FBO)** is an off-screen rendering target created by the user.  
> It acts like a customizable container (a rack) where you **attach color, depth, and stencil buffers** — either as textures or renderbuffers.  
> Used for post-processing, shadow maps, reflections, G-buffer, etc.

🧠 Think of it as:

> "A blank canvas I define, attach parts to, and paint on — instead of painting directly on the window."

---

### ✅ 2. **Renderbuffer**

> A **Renderbuffer** is a non-readable OpenGL buffer used **only for rendering**, typically for **depth** or **depth+stencil** attachments.  
> Unlike textures, renderbuffers **cannot be sampled** in shaders.

🧠 Use when:

- You don’t need to **sample** from the buffer (e.g. depth testing only)
    
- It’s a **performance-optimized write-only** format for attachments
    

---

### ✅ 3. **Default Framebuffer**

> The **Default Framebuffer** is the one provided by the windowing system (OS/platform), representing the screen (the visible window).  
> It has built-in **color, depth, and stencil buffers**, and is what you see after `glSwapBuffers()` or `glfwSwapBuffers()`.

🧠 Think of it as:

> "The screen’s backbuffer where OpenGL draws by default — like the final canvas I present to the user."

---

### 🧩 4. **Attachment**

> An **Attachment** is a storage target (like a texture or renderbuffer) that is connected (attached) to a framebuffer.  
> Types:

- `GL_COLOR_ATTACHMENT0` → Color buffer
    
- `GL_DEPTH_ATTACHMENT` → Depth buffer
    
- `GL_STENCIL_ATTACHMENT` → Stencil buffer
    
- `GL_DEPTH_STENCIL_ATTACHMENT` → Combined
    

🧠 You attach these using:

- `glFramebufferTexture2D()` → for textures
    
- `glFramebufferRenderbuffer()` → for renderbuffers (Depth, Stencil, Combined)
    

---

### 🔄 Summary Table

| Concept                     | User-defined?  | Sample-able? | Used for                         | Attached to     |
| --------------------------- | -------------- | ------------ | -------------------------------- | --------------- |
| **Framebuffer**             | ✅ Yes         | N/A          | Offscreen rendering container    | Has attachments |
| **Renderbuffer**            | ✅ Yes         | ❌ No        | Depth/Stencil fast writes        | Framebuffer     |
| **Default FBO**             | ❌ No (system) | ❌ No        | Final screen output              | Provided by OS  |
| **Texture (as attachment)** | ✅ Yes         | ✅ Yes       | Post-processing, sampling result | Framebuffer     |
|                             |                |              |                                  |                 |

---


Let’s make it crystal clear and easy to remember:

---

### 🎯 Quick Rules:

| Attachment Target             | What It Attaches                    | Function Used                                               | Common Usage                |
| ----------------------------- | ----------------------------------- | ----------------------------------------------------------- | --------------------------- |
| `GL_COLOR_ATTACHMENTi`        | **Color Texture**                   | `glFramebufferTexture2D()`                                  | Post-processing, G-buffer   |
| `GL_DEPTH_ATTACHMENT`         | **Depth Renderbuffer**              | `glFramebufferRenderbuffer()`                               | Depth testing only          |
| `GL_STENCIL_ATTACHMENT`       | **Stencil Renderbuffer**            | `glFramebufferRenderbuffer()`                               | Rare (stencil-only ops)     |
| `GL_DEPTH_STENCIL_ATTACHMENT` | **Depth+Stencil RB** or **Texture** | `glFramebufferRenderbuffer()` or `glFramebufferTexture2D()` | Shadow maps, depth pre-pass |

---

### 🧠 Mental Model:

- **`glFramebufferTexture2D()`** → attaches **textures** (readable, used in shaders)
- **`glFramebufferRenderbuffer()`** → attaches **renderbuffers** (write-only, faster, not sampleable)
    

---

### 🧪 Example:

```cpp
// Attach a color texture
glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, colorTex, 0);

// Attach a depth renderbuffer
glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depthRBO);

// Attach a combined depth-stencil renderbuffer
glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, depthStencilRBO);

```

---

### ⚠️ Note:

You **can** attach a depth **texture** instead of a renderbuffer if you need to **sample depth** in a shader (e.g., for **shadow mapping**):

```cpp
glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, depthTex, 0);

```

---
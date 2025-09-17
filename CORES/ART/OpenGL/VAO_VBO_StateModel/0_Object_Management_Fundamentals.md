# 1. Classic 3.3 Style (Classic bind style)
Sure! Let’s keep it **simple, practical, and modern (OpenGL 4.6 core)**.

Almost all object management in OpenGL follows this **foundational pattern**:

```cpp
GLuint id;
glGen*(...) → create / allocate
glBind*(...) → make current / configure
gl*(...) → set parameters or upload data
glDelete*(...) → destroy

```

Below I’ll summarize the **core objects** you usually manage, with the typical idiomatic OpenGL 4.6 C API code snippets for each:

---

## 📦 **1. Buffers**

Store data: vertices, indices, uniforms, shader storage, etc.

```cpp
GLuint buffer;
glGenBuffers(1, &buffer);
glBindBuffer(GL_ARRAY_BUFFER, buffer);  // or GL_ELEMENT_ARRAY_BUFFER, GL_UNIFORM_BUFFER, etc.
glBufferData(GL_ARRAY_BUFFER, size, data, GL_STATIC_DRAW);
// Use: draw, read, etc.
glDeleteBuffers(1, &buffer);

```

---

## 🎨 **2. Textures**

```cpp
GLuint tex;
glGenTextures(1, &tex);
glBindTexture(GL_TEXTURE_2D, tex);
glTexImage2D(GL_TEXTURE_2D, level, internalFormat, width, height, border, format, type, data);
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
// Use: glBindTexture and draw
glDeleteTextures(1, &tex);

```

---

## 🖼 **3. Framebuffers**

```cpp
GLuint fbo;
glGenFramebuffers(1, &fbo);
glBindFramebuffer(GL_FRAMEBUFFER, fbo);
glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex, 0);
GLenum status = glCheckFramebufferStatus(GL_FRAMEBUFFER);
// Use: glBindFramebuffer to render into it
glDeleteFramebuffers(1, &fbo);

```

---

## ✏️ **4. Vertex Array Objects (VAOs)**

Store vertex attribute state.

```cpp
GLuint vao;
glGenVertexArrays(1, &vao);
glBindVertexArray(vao);
glEnableVertexAttribArray(0);
glVertexAttribPointer(0, size, type, normalized, stride, pointer);
glBindVertexArray(0);
// Use: glBindVertexArray(vao) before draw
glDeleteVertexArrays(1, &vao);

```

---

## 📦 **5. Shader and Program Objects**

Compile shaders, link into a program.

```cpp
GLuint vs = glCreateShader(GL_VERTEX_SHADER);
glShaderSource(vs, 1, &vertexSource, NULL);
glCompileShader(vs);

GLuint fs = glCreateShader(GL_FRAGMENT_SHADER);
glShaderSource(fs, 1, &fragmentSource, NULL);
glCompileShader(fs);

GLuint program = glCreateProgram();
glAttachShader(program, vs);
glAttachShader(program, fs);
glLinkProgram(program);

// Use: glUseProgram(program)
glDeleteShader(vs);
glDeleteShader(fs);
glDeleteProgram(program);

```

---

## 🧪 **6. Sampler Objects**

Store filtering / wrap modes separately from textures.

```cpp
GLuint sampler;
glGenSamplers(1, &sampler);
glSamplerParameteri(sampler, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
glSamplerParameteri(sampler, GL_TEXTURE_WRAP_S, GL_REPEAT);
// Use: glBindSampler(textureUnit, sampler)
glDeleteSamplers(1, &sampler);

```

---

## ⏱ **7. Query / Sync Objects**


Example: time query.

```cpp
GLuint query;
glGenQueries(1, &query);
glBeginQuery(GL_TIME_ELAPSED, query);
// draw...
glEndQuery(GL_TIME_ELAPSED);
GLuint time;
glGetQueryObjectuiv(query, GL_QUERY_RESULT, &time);
glDeleteQueries(1, &query);

```

---

## ⚙️ **General idioms to remember**

✅ **Create** → `glGen*` or `glCreate*`  
✅ **Bind** → `glBind*`  
✅ **Set parameters / data** → `gl*Parameteri`, `gl*Data`, etc.  
✅ **Delete** → `glDelete*`

Modern OpenGL prefers:

- Few global states (use VAOs, UBOs, etc.)
    
- Immutable storage when possible (`glBufferStorage`, `glTexStorage2D`)
    
- Direct state access (DSA, e.g., `glCreateBuffers`, `glNamedBufferData`), introduced in 4.5, so you don't always need to bind to configure.

# 2. DSA Style 4.5+ Direct State Access Style
Since OpenGL **4.5** (and also core in 4.6), we have **Direct State Access (DSA)** — which lets you create/configure objects _without_ binding them to context targets first.  
This style is **cleaner, less error-prone, and preferred** in modern OpenGL code.

Here are the same examples rewritten in **DSA style**:

---

## 📦 **1. Buffers (DSA)**

```cpp
GLuint buffer;
glCreateBuffers(1, &buffer);
glNamedBufferData(buffer, size, data, GL_STATIC_DRAW);
// Use: glBindBuffer(GL_ARRAY_BUFFER, buffer) if needed in pipeline
glDeleteBuffers(1, &buffer);

```

Or, if you use shader storage / uniform buffers:

```cpp
// glBindBufferBase(GL_SHADER_STORAGE_BUFFER, bindingIndex, buffer);

```

---

## 🎨 **2. Textures (DSA)**

```cpp
GLuint tex;
glCreateTextures(GL_TEXTURE_2D, 1, &tex);
glTextureStorage2D(tex, levels, internalFormat, width, height);
glTextureSubImage2D(tex, level, xoffset, yoffset, width, height, format, type, data);
// Set params directly:
glTextureParameteri(tex, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
glTextureParameteri(tex, GL_TEXTURE_WRAP_S, GL_REPEAT);
glDeleteTextures(1, &tex);

```

---

## 🖼 **3. Framebuffers (DSA)**

```cpp
GLuint fbo;
glCreateFramebuffers(1, &fbo);
glNamedFramebufferTexture(fbo, GL_COLOR_ATTACHMENT0, tex, level);
// Check status:
GLenum status = glCheckNamedFramebufferStatus(fbo, GL_FRAMEBUFFER);
// Use: glBindFramebuffer(GL_FRAMEBUFFER, fbo) before draw
glDeleteFramebuffers(1, &fbo);

```

---

## ✏️ **4. Vertex Array Objects (VAOs)**

Note: VAOs are still bound to configure attribute pointers:

```cpp
GLuint vao;
glCreateVertexArrays(1, &vao);
// Setup attributes directly:
glVertexArrayAttribFormat(vao, attribIndex, size, type, normalized, relativeOffset);
glVertexArrayAttribBinding(vao, attribIndex, bindingIndex);
glEnableVertexArrayAttrib(vao, attribIndex);
// Bind buffer to binding index:
glVertexArrayVertexBuffer(vao, bindingIndex, buffer, offset, stride);
// Use: glBindVertexArray(vao)
glDeleteVertexArrays(1, &vao);

```

---

## ✒️ **5. Shader and Program Objects**

No big change; still:

```cpp
GLuint vs = glCreateShader(GL_VERTEX_SHADER);
glShaderSource(vs, 1, &vertexSource, NULL);
glCompileShader(vs);

GLuint fs = glCreateShader(GL_FRAGMENT_SHADER);
glShaderSource(fs, 1, &fragmentSource, NULL);
glCompileShader(fs);

GLuint program = glCreateProgram();
glAttachShader(program, vs);
glAttachShader(program, fs);
glLinkProgram(program);
// Use: glUseProgram(program)
glDeleteShader(vs);
glDeleteShader(fs);
glDeleteProgram(program);

```
---

## 🧪 **6. Sampler Objects**

```cpp
GLuint sampler;
glCreateSamplers(1, &sampler);
glSamplerParameteri(sampler, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
glSamplerParameteri(sampler, GL_TEXTURE_WRAP_S, GL_REPEAT);
// Use: glBindSampler(textureUnit, sampler)
glDeleteSamplers(1, &sampler);

```

---

## ⏱ **7. Query Objects (DSA)**

No DSA-specific creation (still glGenQueries):

```cpp
GLuint query;
glGenQueries(1, &query);
glBeginQuery(GL_TIME_ELAPSED, query);
// draw...
glEndQuery(GL_TIME_ELAPSED);
GLuint time;
glGetQueryObjectuiv(query, GL_QUERY_RESULT, &time);
glDeleteQueries(1, &query);

```

---

## ✅ **Summary of DSA vs classic bind**

|Classic|Modern DSA|
|---|---|
|glGenBuffers + glBindBuffer + glBufferData|glCreateBuffers + glNamedBufferData|
|glGenTextures + glBindTexture + glTexImage2D|glCreateTextures + glTextureStorage2D + glTextureSubImage2D|
|glGenFramebuffers + glBindFramebuffer + glFramebufferTexture|glCreateFramebuffers + glNamedFramebufferTexture|
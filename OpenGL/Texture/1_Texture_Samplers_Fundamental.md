**modern OpenGL 3.3+ two‑textures version**, ready to keep as reference in Obsidian:

- Covers:  
    ✅ 2 texture objects  
    ✅ 2 sampler objects  
    ✅ 2 texture units  
    ✅ Shader combining both
    
- Includes _why each step matters_, in comments.
    

This is **the minimal but complete mental model code** for multi‑texture.

---

## 🎨 **🌱 Modern OpenGL: two textures pipeline**

---

## ✅ **1️⃣ Create & upload two textures**

```cpp
GLuint tex1, tex2;
glGenTextures(1, &tex1);
glGenTextures(1, &tex2);

// tex1: simple red/green checker
glBindTexture(GL_TEXTURE_2D, tex1);
unsigned char data1[] = {
    255,0,0,255,   0,255,0,255,
    0,255,0,255,   255,0,0,255
};
glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,2,2,0,GL_RGBA,GL_UNSIGNED_BYTE,data1);
glGenerateMipmap(GL_TEXTURE_2D);

// tex2: black/white checker
glBindTexture(GL_TEXTURE_2D, tex2);
unsigned char data2[] = {
    255,255,255,255, 0,0,0,255,
    0,0,0,255,       255,255,255,255
};
glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,2,2,0,GL_RGBA,GL_UNSIGNED_BYTE,data2);
glGenerateMipmap(GL_TEXTURE_2D);

```

---

## ✅ **2️⃣ Create two sampler objects**

```cpp
GLuint sampler1, sampler2;
glGenSamplers(1,&sampler1);
glGenSamplers(1,&sampler2);

// same filter/wrap, or customize
glSamplerParameteri(sampler1, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
glSamplerParameteri(sampler1, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
glSamplerParameteri(sampler1, GL_TEXTURE_WRAP_S, GL_REPEAT);
glSamplerParameteri(sampler1, GL_TEXTURE_WRAP_T, GL_REPEAT);

glSamplerParameteri(sampler2, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
glSamplerParameteri(sampler2, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
glSamplerParameteri(sampler2, GL_TEXTURE_WRAP_S, GL_REPEAT);
glSamplerParameteri(sampler2, GL_TEXTURE_WRAP_T, GL_REPEAT);

```
---

## ✅ **3️⃣ Shader uniforms: tell shader which drawer to look in**

```cpp
shader.use();
shader.setInt("tex1", 0); // tex1 uses texture unit 0
shader.setInt("tex2", 1); // tex2 uses texture unit 1

```

---

## ✅ **4️⃣ VAO / VBO (simple quad)**

```cpp
float quad[] = {
    // pos      // texcoord
    -1.0f,-1.0f,  0.0f,0.0f,
     1.0f,-1.0f,  1.0f,0.0f,
     1.0f, 1.0f,  1.0f,1.0f,
    -1.0f, 1.0f,  0.0f,1.0f
};
unsigned int indices[] = {0,1,2, 2,3,0};

GLuint vao,vbo,ebo;
glGenVertexArrays(1,&vao);
glGenBuffers(1,&vbo);
glGenBuffers(1,&ebo);

glBindVertexArray(vao);

glBindBuffer(GL_ARRAY_BUFFER,vbo);
glBufferData(GL_ARRAY_BUFFER,sizeof(quad),quad,GL_STATIC_DRAW);

glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,ebo);
glBufferData(GL_ELEMENT_ARRAY_BUFFER,sizeof(indices),indices,GL_STATIC_DRAW);

// pos attribute
glVertexAttribPointer(0,2,GL_FLOAT,GL_FALSE,4*sizeof(float),(void*)0);
glEnableVertexAttribArray(0);
// texcoord attribute
glVertexAttribPointer(1,2,GL_FLOAT,GL_FALSE,4*sizeof(float),(void*)(2*sizeof(float)));
glEnableVertexAttribArray(1);

```

---

## ✅ **5️⃣ Vertex shader**

```cpp
#version 330 core
layout(location=0) in vec2 aPos;
layout(location=1) in vec2 aTex;

out vec2 TexCoord;

void main() {
    gl_Position = vec4(aPos,0.0,1.0);
    TexCoord = aTex;
}

```

---

## ✅ **6️⃣ Fragment shader (blend two textures)**

```cpp
#version 330 core
in vec2 TexCoord;
out vec4 FragColor;

uniform sampler2D tex1;
uniform sampler2D tex2;

void main() {
    vec4 c1 = texture(tex1, TexCoord);
    vec4 c2 = texture(tex2, TexCoord);
    FragColor = mix(c1, c2, 0.5); // simple average
}

```

---

## ✅ **7️⃣ Rendering: bind both textures & samplers to texture units**

```cpp
shader.use();

// Drawer 0 → tex1 + sampler1
glActiveTexture(GL_TEXTURE0);                    // select drawer 0
glBindTexture(GL_TEXTURE_2D, tex1);              // put tex1 into drawer 0
glBindSampler(0, sampler1);                      // put sampler1 into drawer 0

// Drawer 1 → tex2 + sampler2
glActiveTexture(GL_TEXTURE1);                    // select drawer 1
glBindTexture(GL_TEXTURE_2D, tex2);              // put tex2 into drawer 1
glBindSampler(1, sampler2);                      // put sampler2 into drawer 1

glBindVertexArray(vao);
glDrawElements(GL_TRIANGLES,6,GL_UNSIGNED_INT,0);

```

---

## ✅ **🌱 Mental model summary:**

|Shader uniform|Drawer (texture unit)|Texture|Sampler|
|---|---|---|---|
|tex1|0|tex1|sampler1|
|tex2|1|tex2|sampler2|

Fragment shader samples both → GPU checks drawer numbers → uses correct texture+sampler.


## Python Psuedocode Summary
```py
# Step 1️⃣ Create two textures and upload data
tex1 = glGenTexture()
tex2 = glGenTexture()

# Upload texture 1 (checkerboard RGBA)
glBindTexture(tex1)
upload_pixels(data1)          # data1 = red, green, blue, yellow checker
glGenerateMipmap()

# Upload texture 2 (black & white checker)
glBindTexture(tex2)
upload_pixels(data2)
glGenerateMipmap()

# Step 2️⃣ Create two samplers with filtering/wrapping
sampler1 = glGenSampler()
set_sampler_params(sampler1, min_filter="LINEAR_MIPMAP_LINEAR", wrap="REPEAT")

sampler2 = glGenSampler()
set_sampler_params(sampler2, min_filter="LINEAR_MIPMAP_LINEAR", wrap="REPEAT")

# Step 3️⃣ Create VAO + VBO for a fullscreen quad with texcoords
vao = glGenVertexArray()
vbo = glGenBuffer()
setup_quad(vao, vbo)
# attributes: location=0 → pos, location=1 → texcoord

# Step 4️⃣ Compile shaders
shader = compile_shader(vertex_shader_code, fragment_shader_code)

# Step 5️⃣ Tell shader which texture units to use
shader.use()
shader.set_uniform("tex1", 0)   # tell tex1 → use drawer 0
shader.set_uniform("tex2", 1)   # tell tex2 → use drawer 1

# Step 6️⃣ Rendering loop
while rendering:
    clear_screen()

    # Bind textures and samplers to texture units
    glActiveTexture(0)                 # drawer 0
    glBindTexture(tex1)
    glBindSampler(0, sampler1)

    glActiveTexture(1)                 # drawer 1
    glBindTexture(tex2)
    glBindSampler(1, sampler2)

    # Draw quad
    glBindVertexArray(vao)
    draw_elements()

# Done!

```

### 🎯 _Same texture, two different samplers_ using **OpenGL 3.3+ best practices**

---

## 🔧 **Goal**

- One texture (`tex`)
- Two sampler objects:
    
    - `samplerLinear` → smooth filtering
        
    - `samplerNearest` → pixelated look
        
- In fragment shader, blend both samplers
    
- Clean modern OpenGL structure using **VAO + VBO + Samplers**
    

---

## 🧠 **Conceptual Diagram**

```
        ┌────────────┐
        │ Texture    │ (same image)
        └────┬───────┘
             │
   ┌─────────┴──────────────┐
   │                        │
Sampler A             Sampler B
(GL_LINEAR)          (GL_NEAREST)
   │                        │
   └──────┬────────┬────────┘
          │        │
        Shader samples both

```


---

## 🧪 **Python Pseudocode with PyOpenGL-style API**

```py
# 1. Generate texture and load image data
tex = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, tex)
glTexImage2D(GL_TEXTURE_2D, ...)  # Load image pixels
glGenerateMipmap(GL_TEXTURE_2D)
# No need to set filter/wrap here!

# 2. Create Sampler A (smooth)
samplerLinear = glGenSamplers(1)
glSamplerParameteri(samplerLinear, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
glSamplerParameteri(samplerLinear, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

# 3. Create Sampler B (pixelated)
samplerNearest = glGenSamplers(1)
glSamplerParameteri(samplerNearest, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_NEAREST)
glSamplerParameteri(samplerNearest, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

# 4. During rendering
glActiveTexture(GL_TEXTURE0)
glBindTexture(GL_TEXTURE_2D, tex)
glBindSampler(0, samplerLinear)

glActiveTexture(GL_TEXTURE1)
glBindTexture(GL_TEXTURE_2D, tex)
glBindSampler(1, samplerNearest)

# 5. Pass texture units to shader
glUniform1i(glGetUniformLocation(program, "texA"), 0)
glUniform1i(glGetUniformLocation(program, "texB"), 1)

# 6. Shader: blend both versions
# Fragment Shader (GLSL 330)

"""
#version 330 core

in vec2 TexCoord;
out vec4 FragColor;

uniform sampler2D texA;  // linear
uniform sampler2D texB;  // nearest

void main() {
    vec4 colorA = texture(texA, TexCoord);
    vec4 colorB = texture(texB, TexCoord);
    FragColor = mix(colorA, colorB, 0.5);  // Blend both
}
"""

```
---

## 🧼 **Summary (Best Practice Recap)**

|Element|Stores|Set via|
|---|---|---|
|Texture|Image / mipmaps|`glTexImage2D`, etc.|
|Sampler|Filtering & wrapping|`glSamplerParameteri`|
|Shader|Access by sampler|`uniform sampler2D`|
|Connection|Texture unit|`glBindTexture`, `glBindSampler`|
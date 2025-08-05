Perfect! Now that you’re comfortable with the **VAO-VBO mental model**, let’s extend it to include **per-vertex color data**.

---

# 🎨 Goal: Draw a Colored Triangle

We'll pass **2D positions + RGB colors** to the vertex shader and forward the color to the fragment shader.

---

## 📦 Vertex Data: Position + Color

Each vertex has 5 floats:

- `x, y` (position)
    
- `r, g, b` (color)
    

```cpp

float vertices[] = {
    // Positions     // Colors (RGB)
     0.0f,  0.5f,     1.0f, 0.0f, 0.0f,  // Top (red)
    -0.5f, -0.5f,     0.0f, 1.0f, 0.0f,  // Left (green)
     0.5f, -0.5f,     0.0f, 0.0f, 1.0f   // Right (blue)
};

```

---

## 🧠 Step-by-Step Recap with Color

### 1️⃣ Generate and bind VAO & VBO

```cpp
unsigned int VAO, VBO;
glGenVertexArrays(1, &VAO);
glGenBuffers(1, &VBO);

glBindVertexArray(VAO);
glBindBuffer(GL_ARRAY_BUFFER, VBO);
glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);

```

---

### 2️⃣ Set up Vertex Attribute Pointers

#### 🔹 Position Attribute → location = 0

```cpp
glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)0);
glEnableVertexAttribArray(0);

```

#### 🔹 Color Attribute → location = 1

```cpp
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)(2 * sizeof(float)));
glEnableVertexAttribArray(1);

```
Why `2 * sizeof(float)`? Because the color starts **after 2 floats (x, y)** in each vertex.

---

### 3️⃣ Unbind (optional)

```cpp
glBindBuffer(GL_ARRAY_BUFFER, 0);
glBindVertexArray(0);

```

---

## 💡 Vertex Shader (GLSL)

```glsl
#version 330 core
layout (location = 0) in vec2 aPos;
layout (location = 1) in vec3 aColor;

out vec3 vertexColor;

void main() {
    gl_Position = vec4(aPos, 0.0, 1.0);
    vertexColor = aColor; // pass color to fragment shader
}

```

---

## 💡 Fragment Shader (GLSL)

```glsl
#version 330 core
in vec3 vertexColor;
out vec4 FragColor;

void main() {
    FragColor = vec4(vertexColor, 1.0); // RGB + Alpha
}

```

---

## ▶️ Drawing in Render Loop

```cpp
glUseProgram(shaderProgram);
glBindVertexArray(VAO);
glDrawArrays(GL_TRIANGLES, 0, 3);

```

---

# ✅ Final Visual

You'll get a triangle:

- 🔴 Top is Red
- 🟢 Left is Green
- 🔵 Right is Blue  
    **→ with automatic color interpolation across the surface.**

---

## 🔁 Summary Table (Now with Color)

| Attribute | Location | Size | Offset              | Description               |
| --------- | -------- | ---- | ------------------- | ------------------------- |
| Position  | 0        | 2    | `0`                 | x, y                      |
| Color     | 1        | 3    | `2 * sizeof(float)` | r, g, b                   |
| Stride    | -        | 5    | `5 * sizeof(float)` | bytes between each vertex |
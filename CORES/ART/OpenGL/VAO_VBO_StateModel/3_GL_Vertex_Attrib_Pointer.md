### Imagine this:

You have a **parking lot** where:

- Each **row** is a vertex
- Each row has **multiple car slots** (attributes)
- Each **slot** holds part of the vertex data: position, color, etc.

Let’s break this down visually:

### 🎯 Vertex Data (Interleaved):

```cpp
float vertices[] = {
  //  x     y     r     g     b
   0.0f, 0.5f,  1.0f, 0.0f, 0.0f,  // Vertex 1
  -0.5f,-0.5f,  0.0f, 1.0f, 0.0f,  // Vertex 2
   0.5f,-0.5f,  0.0f, 0.0f, 1.0f   // Vertex 3
};

```

---

## 🔧 Your Job: Tell OpenGL how to park

```cpp
// Position
glVertexAttribPointer(
    0,                // location 0 in shader
    2,                // 2 values (x, y)
    GL_FLOAT,
    GL_FALSE,
    5 * sizeof(float),// total size of a row (stride)
    (void*)0          // offset to pos in row
);

// Color
glVertexAttribPointer(
    1,                 // location 1
    3,                 // 3 values (r, g, b)
    GL_FLOAT,
    GL_FALSE,
    5 * sizeof(float), // same stride
    (void*)(2 * sizeof(float))  // offset to color in row
);

```
---

## 📐 Visually: Parking Lot Table

| Row (Vertex) | Slot 0 | Slot 1 | Slot 2 | Slot 3 | Slot 4 |     |
| ------------ | ------ | ------ | ------ | ------ | ------ | --- |
| Vertex 1     | x      | y      | r      | g      | b      |     | 
| Vertex 2     | x      | y      | r      | g      | b      |     |
| Vertex 3     | x      | y      | r      | g      | b      |     |

- **Stride**: the **width** of a row = 5 floats = 20 bytes
- **Pointer (offset)**: where a car (attribute) is parked within that row:
    - Position → offset 0
    - Color → offset 2 floats (8 bytes)
 

---

## ✅ TL;DR

| Term          | Meaning in this model                      |
| ------------- | ------------------------------------------ |
| **Vertex**    | One full row in the lot                    |
| **Attribute** | A specific **slot** inside the row         |
| **Stride**    | Total row size in bytes (skip to next row) |
| **Pointer**   | Start offset of attribute within the row   |
| 

# 🎮 GPU Indexing Playbook

## 🔹 1D

- **Flatten (trivial):**

`index = x`

- **Unflatten:**

`x = index`

✅ Example: `index=5 → x=5`

---

## 🔹 2D

- **Flatten (x,y → index):**

`index = y * width + x`

- **Unflatten (index → x,y):**
    
`x = index % width y = index / width`

✅ Example: `width=4`

- `(x=2, y=1) → index=6`
    
- `index=6 → (x=2, y=1)`
    

---

## 🔹 3D

- **Flatten (x,y,z → index):**

`index = z * (height * width) + y * width + x`

- **Unflatten (index → x,y,z):**

`x = index % width y = (index / width) % height z = index / (width * height)`

✅ Example: `width=4, height=3`

- `(x=1, y=2, z=0) → index=9`
    
- `index=9 → (x=1, y=2, z=0)`
    

---

## 🧠 Memory Tricks

- **Flattening = multiply + add** (row-major order):  
    inner dimension (x), then y, then z.
    
- **Unflattening = divide + mod** (reverse process).
    
- Always **mod (%)** for the current axis, **divide (/) for moving outward**.
    

---

## 🏆 TL;DR Formulas

- **2D → 1D:** `i = y*W + x`
    
- **1D → 2D:** `x = i % W, y = i / W`
    
- **3D → 1D:** `i = z*H*W + y*W + x`
    
- **1D → 3D:** `x = i % W, y = (i/W) % H, z = i/(W*H)`
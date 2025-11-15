# Geometric Overview
A **ring** is a 2D parametric grid:
- **φ axis** → interpolates radius
- **θ axis** → interpolates angle

A ring has _two radii_:

- **innerRadius**
- **outerRadius**
    

And between them lies an entire **band of vertices**.
This band is defined in a **grid**:

```js
radius direction = φ axis (inner → outer)
angle direction  = θ axis (0 → 2π)

```

This is why you need **two parameters**:

|Parameter|Meaning|Why needed?|
|---|---|---|
|**angle** (θ)|sweeps around the circle|defines _direction_|
|**radius** (φ)|moves from inner → outer|defines _distance from center_|

```txt
                     θ (angle)
                0° → → → → → → → 360°
                  ┌───────────────────┐
                  │        outerRadius│
                  │      ●──●──●──●──●│   ← row: φ = 1.0
                  │    ●──●──●──●──●   │
                  │  ●──●──●──●──●     │
φ (radius) ↓      │●──●──●──●──●       │
(inner→outer)     │  ●──●──●──●──●     │
                  │    ●──●──●──●──●   │
                  │      ●──●──●──●──●│   ← row: φ = 0.0 = innerRadius
                  └───────────────────┘

```

# 🧩 **What the diagram shows**

### **φ (phi) direction — vertical**

- Moves from **innerRadius → outerRadius**
- This is your **row index** in the loop
- Parametric domain:
    
    `φ ∈ [0, 1] r(φ) = lerp(innerRadius, outerRadius, φ)`
    

### **θ (theta) direction — horizontal**

- Sweeps around the ring
- This is your **col index** in the loop
- Parametric domain:
    
    `θ ∈ [thetaStart, thetaStart + thetaLength]`
    

---

# 🧮 **Parametric Equation (used in your code)**

```cpp
x(φ, θ) = r(φ) * cos(θ)
y(φ, θ) = r(φ) * sin(θ)
z(φ, θ) = 0

where
r(φ) = innerRadius + φ * (outerRadius - innerRadius)
θ    = thetaStart + t * thetaLength

```

# 🗺️ ASCII Diagram with Labels

```md
                                  θ direction →
                      (changing angle around circle)
              col=0     col=1     col=2     col=3     ...  

            ┌──────────────────────────────────────────────┐  φ = 1.0
            │        ●────────●────────●────────●          │  
            │        |         |         |         |       │
 outerRadius│        ●────────●────────●────────●          │  
(φ = 1.0)   │        |         |         |         |       │
            │        ●────────●────────●────────●          │  
            │        |         |         |         |       │
            │        ●────────●────────●────────●          │  
            ├──────────────────────────────────────────────┤  
 innerRadius│        ●────────●────────●────────●          │  φ = 0.0
(φ = 0.0)   └──────────────────────────────────────────────┘  

             ↑
             φ direction (changing radius)
             inner → outer

```

# 🎯 Summary

A **ring** is a 2D parametric grid:

- **φ axis** → interpolates radius
- **θ axis** → interpolates angle
    

Your loops:

```js
for phi (rows)
  compute radius
  for theta (cols)
    compute angle
    vertex = (r*cosθ, r*sinθ, 0)

```

Exactly map to the parametric surface.
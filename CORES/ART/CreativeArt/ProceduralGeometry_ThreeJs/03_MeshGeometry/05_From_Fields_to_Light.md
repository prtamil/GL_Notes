# 💡 _From Fields to Light — How Illumination Emerges from Continuous Geometry_

---

## 🌌 1. Recap: Where We Stand

In _“From Volumes to Fields”_, we saw that geometry can be defined as a **scalar field** —  
a function:

$f(\mathbf{\overrightarrow p}) \to \mathbb{R}$ 

that describes space by distance.  
The **surface** is the set of points where `f(p) = 0`.

Now we move from _where_ space is defined → to _how_ light interacts with it.

If the field defines the world’s **matter**,  
then its **gradient** defines how light feels upon it.

---

## ⚙️ 2. The Gradient — The Hidden Normal of the Field

The _gradient_ of an SDF is a vector field representing how the distance changes in space:

$$
\nabla f(p) = \left( \frac{\partial f}{\partial x}, \frac{\partial f}{\partial y}, \frac{\partial f}{\partial z} \right)
$$


Geometrically, this is the **surface normal**.  
It points outward, perpendicular to the surface, in the direction where the distance grows fastest.

In GLSL:

```js
vec3 estimateNormal(vec3 p) {
  const float eps = 0.001;
  return normalize(vec3(
    scene(p + vec3(eps, 0.0, 0.0)) - scene(p - vec3(eps, 0.0, 0.0)),
    scene(p + vec3(0.0, eps, 0.0)) - scene(p - vec3(0.0, eps, 0.0)),
    scene(p + vec3(0.0, 0.0, eps)) - scene(p - vec3(0.0, 0.0, eps))
  ));
}

```

Every SDF carries its own normals **implicitly** — they arise from the function’s shape.

> 🧠 **Mental model:**  
> A triangle needs a normal attribute.  
> A field _is_ its own normal — its slope is its direction.

---

## ☀️ 3. Light as a Function Over Fields

Once we can derive normals, we can apply **lighting models** just as in rasterization — but now _evaluated per-ray hit_, not per vertex.

At a raymarch hit point `p`, compute:

```js
vec3 N = estimateNormal(p);
vec3 L = normalize(lightPos - p);
vec3 V = normalize(cameraPos - p);

```

And use your favorite BRDF:

**Lambert diffuse:**

```js
float diffuse = max(dot(N, L), 0.0);

```

**Blinn–Phong specular:**

```js
vec3 H = normalize(L + V);
float specular = pow(max(dot(N, H), 0.0), shininess);

```

Combine for base lighting:

```js
vec3 color = baseColor * diffuse + specular * vec3(1.0);

```

So, a fully procedural object now _shades itself_ without a mesh or material map — everything arises from `f(p)` and its derivative.

---

## 🔦 4. Shadow Marching — Light Through the Field

Shadows are just another raymarch — but from the **hit point toward the light**.

If any field point blocks the way (distance < ε before reaching light), the point is in shadow.

```js
float shadow(vec3 ro, vec3 rd) {
  float res = 1.0;
  float t = 0.02;
  for (int i = 0; i < 50; i++) {
    float d = scene(ro + rd * t);
    if (d < 0.001) return 0.0; // in shadow
    res = min(res, 10.0 * d / t);
    t += d;
    if (t > lightDist) break;
  }
  return clamp(res, 0.0, 1.0);
}

```

Soft shadows emerge naturally because distance fields inherently _know how far light travels before being blocked_.

> 💬 Shadows are not geometry occlusion — they are **field integration**.

---

## 🌫️ 5. Ambient Occlusion — Sampling the Field’s Density

Ambient occlusion can also arise from the field:  
how much nearby space “blocks” the sky.

```js
float ao(vec3 p, vec3 n) {
  float occ = 0.0, sca = 1.0;
  for (int i = 0; i < 5; i++) {
    float h = 0.01 + 0.12 * float(i) / 4.0;
    float d = scene(p + n * h);
    occ += (h - d) * sca;
    sca *= 0.95;
  }
  return clamp(1.0 - occ, 0.0, 1.0);
}

```

This measures how much _space near the surface is solid_.  
Dense surroundings → darker AO.

Again, no geometry needed — only the field itself.

---

## 🌈 6. Light as a Function Composition

Just like geometry was composed using `min()`, `max()`, and `smoothMin()`,  
lighting can also be composed functionally:

- **Additive light sources:** `sum(light1, light2)`
- **Soft blending:** use falloff functions (`1.0 / dist²`)
- **Procedural color fields:** color = `palette(f(p))`
- **Volumetric scattering:** integrate along the ray
    

Every layer of light becomes a **function over space**, not an object in space.

---

## 🧩 7. The Full Raymarch Pipeline

|Stage|Operation|Output|
|---|---|---|
|1|Compute ray from camera|`ro`, `rd`|
|2|March through space|`p` where `scene(p) < ε`|
|3|Estimate normal|`∇f(p)`|
|4|Evaluate lighting model|color|
|5|Optional secondary rays|shadow, reflection, AO|
|6|Composite color|final pixel|

All steps are pure math on continuous fields.  
No vertex buffers. No UVs. No topology issues.

---

## 🧠 8. Gradient Intuition — Light Feels the Slope

Imagine standing on a hill.  
If the hill is steep, light hits sharply; if it’s flat, light glances off.

That’s exactly what the **gradient** tells light in an SDF —  
the **steepness** of space’s change.

> The steeper the field, the sharper the highlight.

So shading becomes “how light feels the slope of distance space.”

---

## ⚡ 9. Field-Based Shading Summary

|Concept|Mesh Rasterization|Field Raymarching|
|---|---|---|
|Surface normal|vertex attribute|∇f(p)|
|Shadow|geometry occlusion|secondary field query|
|AO|triangle density|distance sampling|
|Specular|dot(N, H)|dot(∇f, H)|
|Light transport|fragment ops|ray integration|

---

## 🌍 10. Beyond Surfaces — Lighting the Infinite

Because the field exists everywhere, you can shade _volumetric matter_, not just surfaces.  
Additive density raymarching:

```js
color += exp(-density * t) * sampleColor(p);

```

Now the light doesn’t stop at `f(p)=0` —  
it _flows through_ continuous density.  
This is how fog, gas, nebulae, or translucent SDF worlds emerge.

---

## 🧬 11. Conceptual Bridge: From Fields to Light

|Domain|Function|Meaning|
|---|---|---|
|Geometry|f(p)|distance to surface|
|Normal|∇f(p)|direction of change|
|Lighting|L(f, ∇f, p)|energy response|
|Shading|color(f, p)|final visual field|

In the end, **geometry and light become inseparable** — both are just transformations of the same function of space.

---

## 🌟 12. Mental Summary Diagram

```js
       f(p): Signed Distance Field
                │
           ∇f(p): Normal
                │
       L(p, N): Lighting Function
                │
     color(p): Shaded Result

```

Each layer is a derivative or composition of the last.  
From a single field, light, form, and beauty emerge.

---

## 🧘 13. Core Intuition

> A field defines what _is_.  
> Its gradient defines what _faces_.  
> Light is what _responds_.

Together they create the entire visible universe — no triangles required.

---

## 🧠 Core Memory Phrase

> “When geometry becomes a function, light becomes its derivative.”
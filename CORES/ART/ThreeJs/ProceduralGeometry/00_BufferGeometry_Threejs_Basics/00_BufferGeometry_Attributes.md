
## Three.js BufferGeometry + BufferAttribute — One-page reference

```text
                 THREE.BufferGeometry
                        │
        ┌───────────────┼────────────────┐
        │               │                │
    position          normal             uv
        │               │                │
 BufferAttribute   BufferAttribute   BufferAttribute
        │
   Float32Array

Optional:
        │
      index
        │
 BufferAttribute
        │
 Uint16Array / Uint32Array
```

`BufferGeometry` is the **container describing a geometry**: vertex attributes, optional indices, groups, bounds, and draw ranges. `BufferAttribute` is one stream of per-vertex data such as position, normal, UV, color, or a custom attribute. ([Three.js](https://threejs.org/docs/pages/BufferGeometry.html?utm_source=chatgpt.com "BufferGeometry - Three.js Docs"))

### `BufferAttribute`

```js
new THREE.BufferAttribute(
    typedArray,
    itemSize,
    normalized = false
);
```

Mental model:

```text
array
    actual numbers

itemSize
    how many numbers form ONE item

normalized
    integer data → normalized shader range
```

Example:

```js
const positions = new Float32Array([
    0, 0, 0,
    1, 0, 0,
    1, 1, 0
]);

const attr =
    new THREE.BufferAttribute(positions, 3);
```

Means:

```text
array.length = 9
itemSize     = 3

count = 9 / 3 = 3 vertices
```

Important properties:

```text
attribute.array
attribute.itemSize
attribute.count
attribute.normalized
attribute.usage
attribute.needsUpdate
```

Useful accessors:

```js
getX(i)
getY(i)
getZ(i)

setX(i, x)
setXY(i, x, y)
setXYZ(i, x, y, z)
```

After changing data:

```js
attribute.needsUpdate = true;
```

Three.js then knows the GPU-side data must be updated. ([Three.js](https://threejs.org/docs/pages/BufferAttribute.html?utm_source=chatgpt.com "BufferAttribute - Three.js Docs"))

---

### `BufferGeometry`

Create:

```js
const geometry = new THREE.BufferGeometry();
```

Attach attributes:

```js
geometry.setAttribute(
    'position',
    positionAttribute
);

geometry.setAttribute(
    'normal',
    normalAttribute
);

geometry.setAttribute(
    'uv',
    uvAttribute
);
```

Read them:

```js
geometry.getAttribute('position');
geometry.getAttribute('normal');
geometry.getAttribute('uv');
```

Remove:

```js
geometry.deleteAttribute('color');
```

Indices:

```js
geometry.setIndex(indices);
geometry.getIndex();
```

Useful methods:

```js
computeVertexNormals()

computeBoundingBox()
computeBoundingSphere()

setDrawRange(start, count)

translate(x, y, z)
rotateX(angle)
rotateY(angle)
rotateZ(angle)
scale(x, y, z)

toNonIndexed()

dispose()
```

If there is **no index**, Three.js treats each consecutive group of three position entries as a triangle. With an index, each three indices selects the vertices of a triangle. ([Three.js](https://threejs.org/docs/pages/BufferGeometry.html?utm_source=chatgpt.com "BufferGeometry - Three.js Docs"))

---

# Example: build a circle yourself

Let's create a **filled circle made of triangles**, without `CircleGeometry`.

Think of it as a triangle fan:

```text
              v2
           /      \
        v3          v1
          \   C   /
        v4          v0
           \      /
              v5
```

The center is one vertex:

```text
C = vertex 0
```

Then vertices around the circumference:

```text
vertex 1
vertex 2
vertex 3
...
```

For each segment:

```text
triangle =
center,
current,
next
```

Code:

```js
const geometry = new THREE.BufferGeometry();

const radius = 2;
const segments = 32;

const vertices = [];

// center vertex
vertices.push(
    0, 0, 0
);

// circumference vertices
for (let i = 0; i <= segments; i++) {

    const angle =
        (i / segments) * Math.PI * 2;

    const x =
        Math.cos(angle) * radius;

    const y =
        Math.sin(angle) * radius;

    vertices.push(
        x, y, 0
    );
}

const positions =
    new Float32Array(vertices);

geometry.setAttribute(
    'position',
    new THREE.BufferAttribute(
        positions,
        3
    )
);
```

At this point our position buffer looks conceptually like:

```text
vertex 0   center
           0,0,0

vertex 1
           cos(0), sin(0), 0

vertex 2
           cos(angle1), sin(angle1), 0

vertex 3
           cos(angle2), sin(angle2), 0

...
```

Now create the triangle indices:

```js
const indices = [];

for (let i = 1; i <= segments; i++) {

    indices.push(
        0,          // center
        i,          // current
        i + 1       // next
    );
}

geometry.setIndex(indices);
```

So our topology becomes:

```text
triangle 0

0 1 2


triangle 1

0 2 3


triangle 2

0 3 4


triangle 3

0 4 5
```

etc.

Then:

```js
geometry.computeVertexNormals();
```

Create the mesh:

```js
const material =
    new THREE.MeshBasicMaterial({
        color: 0x44aa88,
        side: THREE.DoubleSide
    });

const circle =
    new THREE.Mesh(
        geometry,
        material
    );

scene.add(circle);
```

---

## What exactly did we build?

Your JavaScript generated:

```text
MATH

angle
sin()
cos()

      ↓

VERTEX POSITIONS

Float32Array

      ↓

BufferAttribute

itemSize = 3

      ↓

BufferGeometry

attributes.position

      +

index

      ↓

TRIANGLES

0 1 2
0 2 3
0 3 4
...
```

And the renderer eventually turns that into approximately:

```text
Three.js
   ↓
GPU vertex buffer

[position buffer]

   +

GPU index buffer

[index buffer]

   ↓
drawIndexed / glDrawElements

   ↓
GPU
```

The key realization is:

> **The circle does not exist as a "circle" anymore.**

After your generation algorithm runs, the GPU only sees:

```text
vertices
+
indices
+
triangles
```

That is the foundation of procedural geometry.

Your next exercise should be a **ring**, because one small change forces you to understand two vertex loops and indexed triangle topology:

```text
outer ring  ○
inner ring  ○

connect them:

a ----- b
|     / |
|   /   |
c ----- d
```

Once you can generate that comfortably, `BufferGeometry` is already starting to become intuitive.
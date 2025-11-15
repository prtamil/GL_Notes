# Calculating Index on Circle
```js
// indices

		for ( let i = 1; i <= segments; i ++ ) {

			indices.push( i, i + 1, 0 );

		}
```

This can be re Written 
```js
//Edge is 1 because we alreay given origin (0,0,0) as initial edge
	// center point

		vertices.push( 0, 0, 0 );

//So 0th Index is (0,0,0) center vertices.  we know its 0ths index by above code 

for (let edge = 1; edge <= segments; edge++) {

    indices.push(
        currentEdgeVertex(edge),
        nextEdgeVertex(edge),
        centerVertexIndex()
    );

}

function centerVertexIndex() {
    return 0;
}

function currentEdgeVertex(i) {
    return i;
}

function nextEdgeVertex(i) {
    return i + 1;
}

```

## 🧠 Mental Model

> "For every perimeter vertex, make a triangle between:  
> → that vertex  
> → the next vertex  
> → and the center"

## ✅ Why loop from `1` to `segments`?

Because:

- `0` is the center
- Segment vertices start from index `1`
- The last vertex at `segments + 1` duplicates the first to close the circle

# ✅ Quick recap of the index pattern

We generate triangles in this order:

```js
(currentEdgeVertex, nextEdgeVertex, centerVertexIndex)
```


Which in actual code is:

```js
indices.push(i, i + 1, 0);
```

---

## 💡 Key Idea: The order of these indices matters

A triangle’s vertex ordering determines its **normal direction**.

### In WebGL / Three.js:

- Vertices are assumed to be listed in **counter-clockwise (CCW)** order when looking at the triangle front.
- CCW = front-face
- CW = back-face
    

Three.js does **backface culling by default**, meaning CW triangles are not drawn.

---

## ✅ Why the center vertex goes last

Look at a triangle fan around the circle:

```txt
triangle 1: (1, 2, 0)
triangle 2: (2, 3, 0)
triangle 3: (3, 4, 0)
...

```

Order (1, 2, 0) means:

1. go to point 1 on circle edge
2. go to point 2 on circle edge
3. go to the center
    

That traces a **counter-clockwise (CCW)** triangle when viewed from the front (Z+ direction).

```txt
    (v2)
     •
    / \
   /   \
(v1)---(v0 center)  <-- vertices are listed CCW

```

So Three.js treats it as a front-facing triangle and renders it.

---

## 🚫 What would happen if we did:

`indices.push(i, 0, i + 1);`

Order would be:

1. edge point
2. center
3. next edge point
    

This produces **clockwise (CW)** ordering — so with default backface culling,

> ✅ The circle would disappear / be invisible.

That's why the index order is not arbitrary — it sets winding direction.

---

## 🧠 Mental model

Think of your finger tracing the edges of a triangle.

- If you trace **CCW**, the triangle faces you
- If you trace **CW**, it faces away (and gets culled)

Putting center last ensures the trace direction is CCW.

---

## 🔥 TL;DR — Why center is last?

|Reason|Explanation|
|---|---|
|Triangle winding order|Determines what is front-facing|
|Visibility|Wrong order = triangle culled (not drawn)|
|Normals|Affects shading (normals point correct direction)|

If we push `(center, current, next)`, faces turn backward.

If we push `(current, next, center)`, faces turn forward → correct.

---

### ✔ Final one-line explanation

> We place the center vertex last so the vertex order becomes **counter-clockwise**, which makes the triangle front-facing and visible.
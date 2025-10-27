**What we are doing**
Since we are wrapping a 2D texture over an existing 3D geometry, we assign each vertex a **UV ratio** that ranges from 0 to 1. These UV values represent how far along the texture each vertex lies — `0` marks the start edge of the texture, and `1` marks the end. By mapping these normalized ratios to the geometry’s vertices, we tell the renderer exactly how the texture should stretch and align across the surface, ensuring it fits smoothly regardless of the texture’s actual size or resolution

since we are wrapping uv over existing geometry we take uv ratio for each vertex ranging from 0 to 1 this is the context we are using uv

```txt
Texture 
=======

(0,1) ┌──────────────┐ (1,1)
      │              │
      │   TEXTURE    │
      │              │
(0,0) └──────────────┘ (1,0)

```

**Code**
```js
for (let rowIndex = 0; rowIndex <= heightSegments; rowIndex++) {
  for (let colIndex = 0; colIndex <= widthSegments; colIndex++) {
    let u = colIndex / widthSegments;
    let v = 1 - (rowIndex / heightSegments)
    uvs.push([u, v]);
  }
}
```

|Concept|Meaning|
|---|---|
|`u = colIndex / widthSegments`|Fractional horizontal position in texture|
|`v = 1 - (rowIndex / heightSegments)`|Fractional vertical position (flipped to match texture coordinates)|
|Purpose|To linearly map every vertex of the plane to a corresponding point on the 2D texture image|

```
if we have 
widthSegments = 2
heightSegments = 2

remember row majar.  we start from row and complete column and move to next row
then 
(0,1.0) ───── (0.5,1.0) ───── (1.0,1.0)
   │              │               │
   │              │               │
(0,0.5) ───── (0.5,0.5) ───── (1.0,0.5)
   │              │               │
   │              │               │
(0,0.0) ───── (0.5,0.0) ───── (1.0,0.0)

```
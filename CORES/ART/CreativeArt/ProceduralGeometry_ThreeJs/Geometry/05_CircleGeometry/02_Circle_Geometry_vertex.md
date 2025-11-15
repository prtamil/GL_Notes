# 🌀 Sampling a Circle Using Angles

_A mental model for understanding the segment loop in Three.js CircleGeometry_

When we draw a circle in Three.js using `CircleGeometry`, the outer rim of the circle is made by computing points along the circumference. The code that generates these points looks like this:

```js
vertices.push( 0, 0, 0 );
for ( let s = 0, i = 3; s <= segments; s ++, i += 3 ) {

    const segment = thetaStart + s / segments * thetaLength;

    vertex.x = radius * Math.cos( segment );
    vertex.y = radius * Math.sin( segment );
    vertices.push( vertex.x, vertex.y, vertex.z );

}

```

# Re Written
```js

//ReWritten
for ( let s = 0, i = 3; s <= segments; s ++, i += 3 ) {
	
	const percentAlongCircle = s / segments;
	const start = thetaStart;
	const end = thetaStart + thetaLength;
    const segment = lerp(start, end,  percentAlongCircle);

    vertex.x = radius * Math.cos( segment );
    vertex.y = radius * Math.sin( segment );
    vertices.push( vertex.x, vertex.y, vertex.z );

}

```

This tiny loop holds three core concepts:

1. **Angles** (`theta`)
2. **Interpolation / LERP**
3. **Converting an angle into (x,y) coordinates via cosine/sine**
    

Let’s break those down.

---

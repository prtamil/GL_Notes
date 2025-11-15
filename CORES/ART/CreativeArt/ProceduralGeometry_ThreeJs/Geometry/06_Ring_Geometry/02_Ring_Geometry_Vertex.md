# Refactored Code
```js
// -------------------------------------------------------------
//  Math Utilities (unchanged logic, geometric names)
// -------------------------------------------------------------
const lerp = (a, b, t) => a + (b - a) * t;

// θ direction (angular)
function computeAngularPosition(angularIndex, angularSegments, thetaStart, thetaLength) {
  const t = angularIndex / angularSegments;  // normalize 0 → 1
  return lerp(thetaStart, thetaStart + thetaLength, t);
}

// φ direction (radial)
function computeRadialPosition(radialIndex, radialSegments, innerRadius, outerRadius) {
  const t = radialIndex / radialSegments;  // normalize 0 → 1
  return lerp(innerRadius, outerRadius, t);
}

// Convert polar coordinates → Cartesian
function toCartesian(radial, angular) {
  return {
    x: radial * Math.cos(angular),
    y: radial * Math.sin(angular),
    z: 0
  };
}

// -------------------------------------------------------------
//  Pure Vertex Generation Using Loops (same structure)
// -------------------------------------------------------------
function generateRingVerticesPure(
  innerRadius,
  outerRadius,
  angularSegments,    // formerly thetaSegments
  radialSegments,     // formerly phiSegments
  thetaStart,
  thetaLength
) {

  const vertices = [];

  for (let radialIndex = 0; radialIndex <= radialSegments; radialIndex++) {

    const radial = computeRadialPosition(
      radialIndex,
      radialSegments,
      innerRadius,
      outerRadius
    );

    for (let angularIndex = 0; angularIndex <= angularSegments; angularIndex++) {

      const angular = computeAngularPosition(
        angularIndex,
        angularSegments,
        thetaStart,
        thetaLength
      );

      const p = toCartesian(radial, angular);

      vertices.push(p.x, p.y, p.z);
    }
  }

  return vertices;
}

```
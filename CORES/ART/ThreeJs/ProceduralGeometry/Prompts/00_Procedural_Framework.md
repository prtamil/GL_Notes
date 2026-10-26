---
title: "Procedural Geometry from First Principles — Three.js"
aliases:
  - Procedural Geometry Framework
  - Three.js Procedural Geometry Guide
tags:
  - threejs
  - procedural-geometry
  - parameterization
  - topology
  - buffer-geometry
type: learning-roadmap
status: active
---

# Procedural Geometry from First Principles — Three.js

## Intro

This guide is a catalogue of geometry lessons. Each lesson starts with an idea and ends with a working Three.js `BufferGeometry`. Three.js is the laboratory. The main subject is the construction of geometry from mathematical rules.

A shape starts as a continuous idea. A mesh is finite data. The work is to convert the idea into samples, convert the samples into vertices, and connect the vertices into primitives.

```text
IDEA
  ↓
PARAMETERIZATION
  ↓
DOMAIN AND RANGE
  ↓
SAMPLING
  ↓
VERTEX GENERATION
  ↓
NEIGHBORHOOD
  ↓
TOPOLOGY
  ↓
ATTRIBUTES
  ↓
THREE.JS BufferGeometry
```

A **parameter** is an input that selects a location. A **domain** is the permitted range of that input. A **position function** maps the input to a point in space.

```text
P(t)    → (x, y, z)
P(u, v) → (x, y, z)
```

Sampling converts a continuous domain into finite values. For `n` segments in `[a, b]`, use:

```text
step = (b - a) / n
tᵢ = a + i × step
i = 0, 1, 2, …, n
```

This rule makes `n + 1` samples because it includes both boundaries. A closed shape can use a duplicated seam sample or connect the last sample to the first sample. The correct choice depends on the topology and attributes.

The domain dimension and the space dimension are different concepts. Use both labels in this guide:

| Geometry | Domain dimension | Space dimension |
|---|---:|---:|
| Point | 0 | 2D or 3D |
| Line segment | 1 | 2D or 3D |
| Circle circumference | 1 | 2D |
| Annulus | 2 | 2D |
| Sphere surface | 2 | 3D |
| Torus surface | 2 | 3D |

A circle circumference is a curve. A disk is a filled circle. An annulus is a flat filled ring. A torus is a donut-shaped surface in 3D space. Use these names consistently.

Geometry and topology are also different concepts:

```text
geometry = positions and other vertex values
topology = connections between vertices
```

The same positions can form different lines or triangles when the index data changes. A physical point can also require more than one rendering vertex. This duplication is necessary when faces need different normals, UV coordinates, colors, or other attributes.

This guide is exhaustive by **construction family**, not by every possible shape. It covers ordered samples, loops, fans, strips, grids, ring stacks, profiles, extrusion, revolution, sweep, loft, parametric surfaces, and deformation. New shapes become variations of these families.

To request a full lesson from ChatGPT, use this prompt:

```text
Teach me unit [unit number and name] from my procedural geometry guide.

Use this sequence:
1. Explain the shape and draw its logical structure.
2. Define the domain dimension and the space dimension.
3. Define each parameter and its domain.
4. Derive the position formula from first principles.
5. Select a sampling rule.
6. Predict the vertex count.
7. Number the vertices and identify their neighbors.
8. Derive the indices and predict the primitive count.
9. Build the Three.js BufferGeometry manually.
10. Render points and wireframe before the solid mesh.
11. Add the required attributes.
12. Test boundaries, seams, and winding.
13. Introduce one error and explain the result.
14. Change the parameters and compare the result.

Do not use a built-in Three.js geometry for the first implementation.
Do not give me the complete code at the start.
Give me one stage at a time and ask me to predict important values.
```

## Part 0 — First-Principles Framework

Part 0 defines the method that all later units use. Complete these units before the shape catalogue.

### 0.1 Parameterization

- **Question:** Which values select a location on the geometry?
- **Method:** Use one parameter for a curve and two parameters for a surface.
- **Domain:** Write each interval before code is written.
- **Lesson result:** Explain what each parameter changes on the final shape.

### 0.2 Domain, range, and range mapping

- **Question:** Which input values are valid, and which output values can the function produce?
- **Method:** Map an input interval `[a, b]` to an output interval `[c, d]`.
- **Rule:** `mapped = c + (value - a) × (d - c) / (b - a)`.
- **Lesson result:** Test the two boundaries and the midpoint. Calculate output minima and maxima.

### 0.3 Sampling and resolution

- **Question:** How many finite values represent the continuous domain?
- **Method:** Separate segment count from sample count.
- **Rule:** An open interval with `n` segments has `n + 1` boundary-inclusive samples.
- **Lesson result:** Predict the sample count before the loop runs.

### 0.4 Vertex generation

- **Question:** How does each sample become `x`, `y`, and `z`?
- **Method:** Write `P(t)` or `P(u, v)` before array code is written.
- **Storage:** Store positions as `[x₀, y₀, z₀, x₁, y₁, z₁, …]`.
- **Lesson result:** Explain every value in the position array.

### 0.5 Neighborhood and topology

- **Question:** Which logical samples are adjacent?
- **Method:** Write neighbor rules such as `i ↔ i + 1` or `(row, column) ↔ adjacent cells`.
- **Topology:** Convert the neighbor rules into point, line, or triangle indices.
- **Lesson result:** Draw the numbered vertices and derive the index array without trial and error.

### 0.6 Minimal `BufferGeometry`

- **Input:** A typed position array and an optional index array.
- **Construction:** Use `setAttribute('position', ...)` and `setIndex(...)`.
- **Output:** Render the same data as `THREE.Points`, a line primitive, or `THREE.Mesh`.
- **Lesson result:** Trace the data from JavaScript to the GPU.

```js
const geometry = new THREE.BufferGeometry();

geometry.setAttribute(
  'position',
  new THREE.BufferAttribute(new Float32Array(positions), 3)
);

geometry.setIndex(indices);
```

### 0.7 Verification contract

- **Predict:** State the vertex count, index count, and primitive count.
- **Inspect:** Display points, vertex numbers, edges, wireframe, axes, and normals when applicable.
- **Test:** Check boundaries, symmetry, winding, seams, and degenerate primitives.
- **Break:** Change one index or sample rule and explain the failure.
- **Compare:** Inspect the equivalent Three.js built-in geometry only after the manual version works.
- **Complete:** Rebuild the important part without copying the first implementation.

## Part 1 — Points and Straight 1D Geometry

These units introduce discrete positions and one-parameter straight geometry. The position rule is simple, so the main work is sampling, storage, ordering, and line topology.

### 1.1 Single point

- **Class:** `0D domain → 3D space`.
- **Parameters:** One explicit position `(x, y, z)`.
- **Topology:** One point and no index array.
- **Count:** One vertex.
- **Lesson target:** Store one position in a `Float32Array` and render it with `THREE.Points`.

### 1.2 Point set

- **Class:** Discrete samples in 2D or 3D space.
- **Parameters:** A discrete index `i` and a position rule or position list.
- **Topology:** No connections between samples.
- **Count:** One vertex for each sample.
- **Lesson target:** Generate a point cloud and calculate its coordinate ranges.

### 1.3 Line segment

- **Class:** `1D domain → 2D or 3D space`.
- **Parameter:** `t ∈ [0, 1]`.
- **Vertex rule:** `P(t) = A + t(B - A)`.
- **Topology:** Connect the two boundary vertices.
- **Count:** Two vertices and one line segment.
- **Lesson target:** Derive linear interpolation and render the segment.

### 1.4 Sampled line segment

- **Class:** `1D domain → 2D or 3D space`.
- **Parameter:** `t ∈ [0, 1]` with `n` segments.
- **Vertex rule:** Evaluate `P(tᵢ)` for each sample.
- **Topology:** Connect `i` to `i + 1`.
- **Count:** `n + 1` vertices and `n` line segments.
- **Lesson target:** Separate the mathematical segment from its sampling resolution.

### 1.5 Ray with a finite display range

- **Class:** A half-infinite mathematical curve displayed with a finite domain.
- **Parameter:** `t ∈ [0, t_max]`.
- **Vertex rule:** `P(t) = origin + t × direction`.
- **Topology:** Connect consecutive samples.
- **Lesson target:** Explain why rendering requires a finite display range.

### 1.6 Infinite line with a finite display range

- **Class:** An infinite mathematical curve displayed with a finite domain.
- **Parameter:** `t ∈ [-t_max, t_max]`.
- **Vertex rule:** `P(t) = origin + t × direction`.
- **Topology:** Connect consecutive samples.
- **Lesson target:** Show that the domain selects the visible part of an infinite object.

### 1.7 Open polyline

- **Class:** A piecewise linear `1D domain → 2D or 3D space`.
- **Parameters:** An ordered control-point index.
- **Vertex rule:** Use each control point as a vertex.
- **Topology:** Connect vertex `i` to vertex `i + 1`.
- **Count:** For `m` vertices, use `m - 1` segments.
- **Lesson target:** Build an open chain with `THREE.Line` or explicit line indices.

### 1.8 Piecewise sampled polyline

- **Class:** A sampled piecewise linear curve.
- **Parameters:** Segment index and local value `t ∈ [0, 1]`.
- **Vertex rule:** Interpolate between each pair of control points.
- **Topology:** Preserve the order across segment boundaries.
- **Lesson target:** Convert local segment parameters into one continuous sample sequence.

## Part 2 — Parametric Curves and Closed Loops

These units use one continuous parameter. The position function creates the curve. The topology usually connects consecutive samples. Closed curves also require a seam rule.

### 2.1 Closed polyline

- **Class:** A piecewise linear closed curve.
- **Parameters:** An ordered control-point index.
- **Vertex rule:** Use each control point once.
- **Topology:** Connect `i` to `i + 1` and connect the last vertex to the first.
- **Count:** With `m` vertices, use `m` line segments.
- **Lesson target:** Add wrap-around topology without duplicating the first position.

### 2.2 Circle circumference

- **Class:** `1D domain → 2D space`.
- **Parameter:** `θ ∈ [0, 2π)`.
- **Vertex rule:** `P(θ) = (cx + r cos θ, cy + r sin θ, 0)`.
- **Topology:** Connect consecutive samples and connect the last sample to the first.
- **Count:** With `s` unique samples, use `s` vertices and `s` line segments.
- **Lesson target:** Explain angular sampling, wrap-around, and the difference between a circle circumference and a disk.

### 2.3 Circular arc

- **Class:** `1D domain → 2D space`.
- **Parameter:** `θ ∈ [θ_start, θ_end]`.
- **Vertex rule:** Use the circle rule with a restricted domain.
- **Topology:** Connect consecutive samples without wrap-around.
- **Count:** `s + 1` vertices and `s` line segments.
- **Lesson target:** Show that a new domain can create a new shape without a new position formula.

### 2.4 Ellipse circumference

- **Class:** `1D domain → 2D space`.
- **Parameter:** `θ ∈ [0, 2π)`.
- **Vertex rule:** `P(θ) = (cx + a cos θ, cy + b sin θ, 0)`.
- **Topology:** Use a closed loop.
- **Lesson target:** Compare equal-angle samples with their unequal distances along the curve.

### 2.5 Sine curve

- **Class:** `1D domain → 2D space`.
- **Parameter:** `t ∈ [t_min, t_max]`.
- **Vertex rule:** `P(t) = (t, A sin(ft + phase), 0)`.
- **Topology:** Connect consecutive samples.
- **Lesson target:** Control amplitude, frequency, phase, and visible range independently.

### 2.6 Archimedean spiral

- **Class:** `1D domain → 2D space`.
- **Parameter:** `θ ∈ [θ_start, θ_end]`.
- **Vertex rule:** `r(θ) = a + bθ`, then `P(θ) = (r cos θ, r sin θ, 0)`.
- **Topology:** Connect consecutive samples.
- **Lesson target:** Compose a scalar radius function with circular parameterization.

### 2.7 Logarithmic spiral

- **Class:** `1D domain → 2D space`.
- **Parameter:** `θ ∈ [θ_start, θ_end]`.
- **Vertex rule:** `r(θ) = ae^(bθ)`, then use the circular position rule.
- **Topology:** Connect consecutive samples.
- **Lesson target:** Compare linear radial growth with exponential radial growth.

### 2.8 Helix

- **Class:** `1D domain → 3D space`.
- **Parameter:** `θ ∈ [θ_start, θ_end]`.
- **Vertex rule:** `P(θ) = (r cos θ, pitch × θ, r sin θ)`.
- **Topology:** Connect consecutive samples.
- **Lesson target:** Add an independent linear axis to a circular curve.

### 2.9 Lissajous curve

- **Class:** `1D domain → 2D or 3D space`.
- **Parameter:** `t` over a selected time interval.
- **Vertex rule:** Use sinusoidal functions with different frequencies for each axis.
- **Topology:** Connect consecutive samples and close only when the frequency ratio permits closure.
- **Lesson target:** Relate frequency ratios to symmetry and closure.

### 2.10 Quadratic Bézier curve

- **Class:** `1D domain → 2D or 3D space`.
- **Parameter:** `t ∈ [0, 1]` with control points `A`, `B`, and `C`.
- **Vertex rule:** Derive the point with two interpolation levels or the quadratic formula.
- **Topology:** Connect consecutive curve samples.
- **Lesson target:** Render the control polygon, intermediate points, and final curve.

### 2.11 Cubic Bézier curve

- **Class:** `1D domain → 2D or 3D space`.
- **Parameter:** `t ∈ [0, 1]` with four control points.
- **Vertex rule:** Derive the point with repeated interpolation or cubic basis functions.
- **Topology:** Connect consecutive curve samples.
- **Lesson target:** Explain endpoint tangents and control-point influence.

### 2.12 Catmull–Rom curve

- **Class:** A piecewise `1D domain → 2D or 3D space` curve.
- **Parameters:** Segment index and local `t ∈ [0, 1]`.
- **Vertex rule:** Use four neighboring control points for each segment.
- **Topology:** Join samples across all segments.
- **Lesson target:** Implement the formula before comparison with `THREE.CatmullRomCurve3`.

### 2.13 Equal-distance curve resampling

- **Class:** A new sampling method for any one-parameter curve.
- **Input:** A densely sampled curve and its adjacent distances.
- **Method:** Build cumulative length and find samples at target distances.
- **Topology:** Preserve the curve order.
- **Lesson target:** Compare equal-parameter samples with approximately equal-distance samples.

### 2.14 Closed-curve seam

- **Class:** A topology and attribute study for any closed curve.
- **Method:** Compare a wrapped unique sample set with a duplicated endpoint.
- **Topology:** Use modulo indexing or an explicit duplicate.
- **Lesson target:** State when geometry can wrap and when UV or other attributes require duplication.

## Part 3 — Flat Filled Shapes

These units create surfaces in a plane. The boundary describes the shape, but triangles fill the interior. The main topology patterns are one triangle, two-triangle quads, triangle fans, ring strips, and polygon triangulation.

### 3.1 Triangle

- **Class:** `2D domain → 2D or 3D space`.
- **Parameters:** Barycentric values `u ≥ 0`, `v ≥ 0`, and `u + v ≤ 1`.
- **Vertex rule:** The mesh boundary uses corners `A`, `B`, and `C`.
- **Topology:** One ordered triangle such as `0, 1, 2`.
- **Count:** Three vertices, three indices, and one triangle.
- **Lesson target:** Connect winding, face direction, and material side settings.

### 3.2 Quad

- **Class:** `2D domain → 2D or 3D space`.
- **Parameters:** `u, v ∈ [0, 1]`.
- **Vertex rule:** Use four corners or bilinear interpolation.
- **Topology:** Split the quad into two triangles.
- **Count:** Four vertices, six indices, and two triangles.
- **Lesson target:** Compare both possible diagonals and explain the effect on a non-planar quad.

### 3.3 Rectangle

- **Class:** A parameterized quad in a plane.
- **Parameters:** Width, height, center, and optional rotation.
- **Vertex rule:** Generate four corners from half-width and half-height.
- **Topology:** Use two triangles with consistent winding.
- **Lesson target:** Derive corners instead of storing fixed coordinates.

### 3.4 Regular polygon

- **Class:** A flat polygon with `N` boundary vertices.
- **Parameter:** Boundary angle `θᵢ = θ₀ + 2πi/N`.
- **Vertex rule:** `P(θᵢ) = (cx + r cos θᵢ, cy + r sin θᵢ, 0)`.
- **Topology:** Use a center fan for the filled convex polygon.
- **Count:** With a center and `N` unique boundary vertices, use `N + 1` vertices and `N` triangles.
- **Lesson target:** Create triangles, squares, pentagons, and higher polygons with one generator.

### 3.5 Star polygon

- **Class:** A flat polygon with alternating radii.
- **Parameter:** An ordered boundary index and angle.
- **Vertex rule:** Alternate between an outer radius and an inner radius.
- **Topology:** Use a center fan for a simple radial star. Inspect winding near sharp points.
- **Lesson target:** Separate boundary generation from interior triangulation.

### 3.6 Disk

- **Class:** `2D polar domain → 2D space`.
- **Parameters:** `θ ∈ [0, 2π)` and `r ∈ [0, R]`.
- **Vertex rule:** `P(r, θ) = (cx + r cos θ, cy + r sin θ, 0)`.
- **Topology:** Start with one center vertex and one boundary ring. Use a triangle fan.
- **Count:** With `s` unique boundary vertices, use `s + 1` vertices and `s` triangles.
- **Lesson target:** Distinguish a disk from a circle circumference and compare with `THREE.CircleGeometry`.

### 3.7 Circular sector

- **Class:** A restricted polar surface.
- **Parameters:** `θ ∈ [θ_start, θ_end]` and `r ∈ [0, R]`.
- **Vertex rule:** Use a center and an open arc.
- **Topology:** Connect the center to each adjacent arc pair.
- **Count:** With `s` angular segments, use `s + 2` vertices and `s` triangles.
- **Lesson target:** Create a filled sector by changing the angular domain.

### 3.8 Annulus

- **Class:** `2D polar domain → 2D space`.
- **Parameters:** `θ ∈ [0, 2π]` and `r ∈ [R_inner, R_outer]`.
- **Vertex rule:** Generate an inner ring and an outer ring with matching angular samples.
- **Topology:** Treat the two rings as grid rows. Use two triangles for each angular cell.
- **Count:** With a duplicated seam and `s` angular segments, use `2(s + 1)` vertices and `2s` triangles.
- **Lesson target:** Build a flat filled ring and compare with `THREE.RingGeometry`.

### 3.9 Annular sector

- **Class:** A restricted annulus surface.
- **Parameters:** A limited angular interval and an inner-to-outer radial interval.
- **Vertex rule:** Generate two open arcs with matching samples.
- **Topology:** Use two triangles for each angular cell. Do not wrap the ends.
- **Lesson target:** Combine the arc and annulus construction rules.

### 3.10 Multi-ring disk

- **Class:** A polar grid in a plane.
- **Parameters:** Angular segment index and radial segment index.
- **Vertex rule:** Sample multiple radii from the center to the outer boundary.
- **Topology:** Connect adjacent radial rows. Handle the center as a special row or a single vertex.
- **Count:** For `s` angular segments and `q` radial segments, derive the count from the selected center representation.
- **Lesson target:** Compare a triangle fan with a general polar grid.

### 3.11 Rounded rectangle

- **Class:** A piecewise boundary with four lines and four quarter arcs.
- **Parameters:** Width, height, corner radius, and corner-segment count.
- **Vertex rule:** Generate each corner arc around its own center.
- **Topology:** Triangulate the ordered convex boundary or connect it to a center.
- **Lesson target:** Join several local parameterizations into one closed boundary.

### 3.12 Convex polygon triangulation

- **Class:** A filled polygon from an ordered convex boundary.
- **Parameters:** A list of boundary vertices.
- **Vertex rule:** Use the supplied boundary positions.
- **Topology:** Create a fan from one boundary vertex or from a center point.
- **Count:** A polygon with `N` boundary vertices needs `N - 2` triangles without a center vertex.
- **Lesson target:** Derive a general triangulation for a convex boundary.

### 3.13 Concave polygon *(advanced)*

- **Class:** A filled polygon with inward boundary angles.
- **Input:** An ordered, non-self-intersecting boundary.
- **Problem:** A simple fan can place triangles outside the polygon.
- **Topology:** Study ear clipping after convex triangulation is clear.
- **Lesson target:** Explain why boundary order alone does not make every triangulation valid.

### 3.14 Polygon with a hole *(advanced)*

- **Class:** A planar region with one outer boundary and one or more inner boundaries.
- **Input:** Separate ordered loops with consistent orientation.
- **Problem:** The topology must preserve the empty regions.
- **Lesson target:** Understand the problem before comparison with a triangulation utility such as `ShapeUtils.triangulateShape()`.

## Part 4 — Grids and Deformed Surfaces

A rectangular grid is a two-parameter domain stored in one-dimensional arrays. The logical grid supplies the neighborhood. A position function converts the grid into a plane, a height field, or a general parametric patch.

### 4.1 Rectangular point grid

- **Class:** `2D domain → 2D or 3D space`.
- **Parameters:** Row `j` and column `i`, or normalized values `u, v ∈ [0, 1]`.
- **Vertex rule:** Generate one position for each `(i, j)` pair.
- **Storage:** Use `index(i, j) = j(columns + 1) + i`.
- **Count:** `(columns + 1)(rows + 1)` vertices.
- **Lesson target:** Convert a logical 2D structure into a flat position array.

### 4.2 Triangulated plane grid

- **Class:** A rectangular point grid with triangle topology.
- **Neighborhood:** Each cell has top-left, top-right, bottom-left, and bottom-right vertices.
- **Topology:** Use two triangles for each cell.
- **Count:** For `u_segments × v_segments`, use `2u_segmentsv_segments` triangles.
- **Lesson target:** Generate every grid index without hard-coded faces.

### 4.3 Alternate grid diagonals

- **Class:** Two topology choices for the same grid positions.
- **Method:** Use one diagonal for all cells, alternate diagonals, or select a diagonal from a rule.
- **Topology:** Keep winding consistent for both choices.
- **Lesson target:** Observe how triangulation affects a deformed surface.

### 4.4 Height field

- **Class:** `2D domain → 3D space`.
- **Parameters:** Horizontal coordinates `x` and `z`.
- **Vertex rule:** `P(x, z) = (x, h(x, z), z)`.
- **Topology:** Reuse the plane-grid indices.
- **Lesson target:** Change geometry without changing topology.

### 4.5 Sine-wave surface

- **Class:** A height field.
- **Parameters:** `x`, `z`, amplitude, spatial frequency, and phase.
- **Vertex rule:** Use one or more sine functions for height.
- **Topology:** Reuse the grid.
- **Lesson target:** Separate spatial frequency from mesh resolution.

### 4.6 Radial-wave surface

- **Class:** A height field based on distance from a center.
- **Parameters:** `x`, `z`, center, amplitude, and frequency.
- **Vertex rule:** Calculate `d = length((x, z) - center)` and use `h = A sin(fd + phase)`.
- **Topology:** Reuse the grid.
- **Lesson target:** Convert Cartesian coordinates to a radial scalar input.

### 4.7 Polar grid

- **Class:** `2D polar domain → 2D or 3D space`.
- **Parameters:** Radius and angle.
- **Vertex rule:** Convert polar samples to Cartesian positions.
- **Topology:** Connect adjacent angles and adjacent radial rows.
- **Lesson target:** Compare polar-grid topology with rectangular-grid topology.

### 4.8 Generic parametric surface

- **Class:** `2D domain → 3D space`.
- **Parameters:** `u ∈ [u_min, u_max]` and `v ∈ [v_min, v_max]`.
- **Vertex rule:** Evaluate `P(u, v)` at each grid sample.
- **Topology:** Reuse one standard grid-index generator.
- **Lesson target:** Change only `P(u, v)` to create different surfaces.

### 4.9 Bilinear patch

- **Class:** A four-corner parametric surface.
- **Parameters:** `u, v ∈ [0, 1]` and four corner positions.
- **Vertex rule:** Interpolate first in one direction and then in the other direction.
- **Topology:** Use the standard grid.
- **Lesson target:** Create a ruled or warped quad surface from four corners.

### 4.10 Bézier surface patch *(advanced)*

- **Class:** A control-point-based `2D domain → 3D space` surface.
- **Parameters:** `u, v ∈ [0, 1]` and a control-point grid.
- **Vertex rule:** Apply Bézier basis functions in both parameter directions.
- **Topology:** Use the standard grid.
- **Lesson target:** Extend the one-parameter Bézier idea to two parameters.

## Part 5 — Polyhedra and Extruded Solids

These units create closed triangle surfaces from faces, profiles, and repeated layers. A triangle mesh represents the boundary of the solid. It does not store the filled volume.

### 5.1 Tetrahedron

- **Class:** A closed polyhedron in 3D space.
- **Input:** Four non-coplanar corner positions.
- **Topology:** Four triangular faces with outward winding.
- **Count:** Four shared positions and four triangles.
- **Lesson target:** Build the smallest closed triangular surface.

### 5.2 Square pyramid

- **Class:** A base polygon connected to one apex.
- **Parameters:** Base size, height, and center.
- **Vertex rule:** Generate four base corners and one apex.
- **Topology:** Four side triangles and two base triangles.
- **Lesson target:** Separate physical corners from vertices needed for flat normals and UV coordinates.

### 5.3 Cube, face by face

- **Class:** Six planar quad faces in 3D space.
- **Parameters:** Center and side length.
- **Vertex rule:** Generate four vertices for each face.
- **Topology:** Two triangles per face with outward winding.
- **Count:** Twenty-four rendering vertices and twelve triangles.
- **Lesson target:** Prioritize clear face data before vertex sharing.

### 5.4 Cube with shared corners

- **Class:** The same cube with shared position indices.
- **Vertex rule:** Generate eight physical corners.
- **Topology:** Reuse the corners across twelve triangles.
- **Count:** Eight positions and twelve triangles.
- **Lesson target:** Explain why smooth normals appear when hard-edged faces share normal values.

### 5.5 Box

- **Class:** A cube generalized by three independent dimensions.
- **Parameters:** Width, height, depth, and center.
- **Vertex rule:** Use half-extents to generate the corners or face vertices.
- **Topology:** Reuse the cube face pattern.
- **Lesson target:** Separate topology from size parameters.

### 5.6 Triangular prism

- **Class:** A triangle profile repeated at two depths.
- **Parameters:** Three profile points and a depth interval.
- **Vertex rule:** Generate front and back copies of the profile.
- **Topology:** Two triangular caps and three quad sides.
- **Lesson target:** Learn the simplest profile extrusion.

### 5.7 Regular prism

- **Class:** A regular polygon repeated at two depths.
- **Parameters:** Side count, radius, and depth.
- **Vertex rule:** Reuse the regular-polygon boundary at two depth values.
- **Topology:** Triangulate both caps and connect corresponding boundary edges.
- **Lesson target:** Create triangular, square, pentagonal, and higher prisms with one generator.

### 5.8 Extruded convex polygon

- **Class:** An arbitrary convex profile repeated through depth.
- **Input:** An ordered convex boundary and two depth values.
- **Vertex rule:** Duplicate the profile for the front and back layers.
- **Topology:** Reverse one cap winding and connect matching boundary edges.
- **Lesson target:** Generalize prism construction beyond regular profiles.

### 5.9 Octahedron

- **Class:** A regular polyhedron with triangular faces.
- **Input:** Six axis-aligned corner positions.
- **Topology:** Eight outward-facing triangles.
- **Count:** Six shared positions and eight triangles.
- **Lesson target:** Derive face connections from symmetry.

### 5.10 Icosahedron

- **Class:** A regular polyhedron with twenty triangular faces.
- **Input:** Twelve positions derived with the golden ratio.
- **Topology:** Twenty outward-facing triangles.
- **Lesson target:** Study a larger explicit vertex-and-face table before sphere subdivision.

### 5.11 General indexed polyhedron

- **Class:** A closed surface defined by a position table and a face table.
- **Input:** Unique positions and ordered polygon faces.
- **Method:** Triangulate each face and preserve outward winding.
- **Lesson target:** Validate manifold edges by checking that each closed-surface edge belongs to two faces.

## Part 6 — Ring-Based and Parametric 3D Surfaces

Many curved surfaces are grids whose rows form rings. One parameter moves around a ring. A second parameter moves between rings. The same topology can create cylinders, cones, frustums, spheres, ellipsoids, toruses, and capsules.

### 6.1 Ring-stack foundation

- **Class:** `2D domain → 3D space`.
- **Parameters:** Angular value `u` and layer value `v`.
- **Vertex rule:** Generate one ring for each layer. Keep the angular sample order consistent.
- **Topology:** Connect ring `j` to ring `j + 1` with two triangles per angular cell.
- **Count:** With duplicated seams, `s` angular segments, and `h` layer segments, use `(s + 1)(h + 1)` vertices and `2sh` triangles.
- **Lesson target:** Build one reusable ring-stack index generator.

### 6.2 Open cylinder

- **Class:** A ring-stack surface without caps.
- **Parameters:** `θ ∈ [0, 2π]`, height value `v ∈ [0, 1]`, radius, and height.
- **Vertex rule:** `P(θ, v) = (r cos θ, y_min + v × height, r sin θ)`.
- **Topology:** Use the ring-stack indices.
- **Lesson target:** Generate the curved side and close only the angular seam.

### 6.3 Capped cylinder

- **Class:** An open cylinder plus two disk surfaces.
- **Parameters:** The side parameters and two cap domains.
- **Vertex rule:** Keep cap vertices separate from side vertices when normals or UV coordinates differ.
- **Topology:** Use a triangle fan or radial grid for each cap. Reverse the bottom-cap winding.
- **Lesson target:** Explain why one physical rim often needs separate side and cap vertices.

### 6.4 Cone

- **Class:** A ring stack whose radius reaches zero.
- **Parameters:** Angle and normalized height.
- **Vertex rule:** Use `r(v) = r_base(1 - v)`.
- **Topology:** Connect the rings and treat the apex as a special case.
- **Lesson target:** Detect and remove degenerate triangles at a collapsed ring.

### 6.5 Frustum

- **Class:** A ring stack with different end radii.
- **Parameters:** Angle, normalized height, bottom radius, and top radius.
- **Vertex rule:** Use `r(v) = r_bottom + v(r_top - r_bottom)`.
- **Topology:** Reuse the cylinder side and optional cap rules.
- **Lesson target:** Show that a cylinder and a cone are special frustums.

### 6.6 UV sphere

- **Class:** `2D angular domain → 3D space`.
- **Parameters:** Longitude `θ ∈ [0, 2π]` and polar angle `φ ∈ [0, π]`.
- **Vertex rule:** `P(θ, φ) = (r sin φ cos θ, r cos φ, r sin φ sin θ)`.
- **Topology:** Connect adjacent longitude and latitude samples. Treat both poles carefully.
- **Count:** With duplicated longitude seams, use `(longitude_segments + 1)(latitude_segments + 1)` stored vertices. Avoid one degenerate triangle per pole cell.
- **Lesson target:** Explain seam duplication, repeated pole positions, and sphere triangle counts.

### 6.7 Hemisphere

- **Class:** A sphere with a restricted polar domain.
- **Parameters:** Full longitude and half of the sphere's polar interval.
- **Vertex rule:** Reuse the sphere formula.
- **Topology:** Reuse the sphere grid and add an optional disk cap.
- **Lesson target:** Create a new surface by changing the domain instead of changing the formula.

### 6.8 Ellipsoid

- **Class:** A scaled sphere surface.
- **Parameters:** Two sphere angles and three axis radii.
- **Vertex rule:** Scale the X, Y, and Z components independently.
- **Topology:** Reuse the sphere indices.
- **Lesson target:** Explain why scaled position vectors are not generally correct ellipsoid normals.

### 6.9 Torus

- **Class:** `2D periodic domain → 3D space`.
- **Parameters:** Major angle `u ∈ [0, 2π]`, tube angle `v ∈ [0, 2π]`, major radius `R`, and tube radius `r`.
- **Vertex rule:** `P(u, v) = ((R + r cos v) cos u, r sin v, (R + r cos v) sin u)`.
- **Topology:** Use a grid that wraps in both parameter directions.
- **Count:** With duplicated seams, use `(major_segments + 1)(tube_segments + 1)` vertices and `2 × major_segments × tube_segments` triangles.
- **Lesson target:** Build the three-dimensional donut surface and compare it with `THREE.TorusGeometry`.

### 6.10 Capsule

- **Class:** A cylinder joined to two hemispheres.
- **Parameters:** Angle, axial layer, radius, cylinder length, and cap angles.
- **Vertex rule:** Generate a continuous sequence of bottom-cap, cylinder, and top-cap rings.
- **Topology:** Use one ring-stack connection rule and special pole handling.
- **Lesson target:** Join several radius-and-height rules without a visible gap.

### 6.11 Straight tube or pipe

- **Class:** A hollow cylinder with inner and outer surfaces.
- **Parameters:** Angle, height, inner radius, and outer radius.
- **Vertex rule:** Generate outer rings and inner rings. Reverse the inner-surface orientation.
- **Topology:** Connect both side surfaces and use annular caps when required.
- **Lesson target:** Construct a closed hollow solid from cylinder and annulus rules.

### 6.12 Möbius strip *(advanced)*

- **Class:** A one-sided `2D domain → 3D space` surface.
- **Parameters:** A loop parameter and a strip-width parameter.
- **Vertex rule:** Apply a half-twist while the strip travels around the loop.
- **Topology:** Join the final row to the first row with reversed cross-strip orientation.
- **Lesson target:** Study a seam whose orientation changes after one loop.

### 6.13 Superellipsoid *(optional)*

- **Class:** A sphere-like parametric surface with shape exponents.
- **Parameters:** Two angles, axis scales, and exponent values.
- **Vertex rule:** Replace standard sine and cosine terms with signed-power terms.
- **Topology:** Reuse the sphere grid.
- **Lesson target:** Produce rounded boxes and pinched forms by changing formula parameters.

## Part 7 — Procedural Modeling Operations

These units transform profiles, paths, layers, or existing mesh positions. They combine the construction families from the earlier parts. The operation must define both the new positions and the connections between generated layers.

### 7.1 Basic extrusion

- **Input:** An ordered 2D profile and two depth values.
- **Parameters:** Profile index and depth layer.
- **Vertex rule:** Copy the profile at the front and back depth.
- **Topology:** Create front and back caps. Connect corresponding boundary edges.
- **Lesson target:** Turn a flat convex profile into a closed 3D mesh.

### 7.2 Multi-step extrusion

- **Input:** A profile and several depth samples.
- **Parameters:** Profile sample and depth sample.
- **Vertex rule:** Copy the profile at each depth layer.
- **Topology:** Connect adjacent profile layers as a grid.
- **Lesson target:** Recognize extrusion as `profile samples × depth samples`.

### 7.3 Tapered extrusion

- **Input:** A multi-step extrusion and a scale function `s(v)`.
- **Vertex rule:** Scale each profile layer around its local center.
- **Topology:** Keep the layered topology unchanged.
- **Lesson target:** Separate the layer transformation from the connection rule.

### 7.4 Twisted extrusion

- **Input:** A multi-step extrusion and an angle function `angle(v)`.
- **Vertex rule:** Rotate each profile layer around the extrusion axis.
- **Topology:** Keep the layered topology unchanged.
- **Lesson target:** Relate layer resolution to visible twist quality.

### 7.5 Combined taper and twist

- **Input:** One profile and two layer functions.
- **Vertex rule:** Apply scale and rotation in a stated order.
- **Topology:** Reuse the extrusion indices.
- **Lesson target:** Show that transformation order changes the result.

### 7.6 Surface of revolution

- **Input:** A sampled 2D profile in radius-height space.
- **Parameters:** Profile index and revolution angle.
- **Vertex rule:** Rotate each profile point around an axis.
- **Topology:** Connect neighboring rotated profile copies.
- **Lesson target:** Build a lathe-style surface and compare it with `THREE.LatheGeometry`.

### 7.7 Procedural vase

- **Input:** A radius function over height.
- **Parameters:** Height and revolution angle.
- **Vertex rule:** Evaluate the profile radius and revolve the result.
- **Topology:** Reuse the surface-of-revolution indices.
- **Lesson target:** Control a complex object with a small set of profile functions.

### 7.8 Straight-path sweep

- **Input:** A profile and a straight path.
- **Parameters:** Profile sample and path sample.
- **Vertex rule:** Place one profile copy at each path sample.
- **Topology:** Connect adjacent profile copies.
- **Lesson target:** Establish the sweep data structure before curved-path orientation is added.

### 7.9 Path tangent

- **Input:** A sampled curve `C(t)`.
- **Rule:** Approximate the tangent with `C(t + ε) - C(t)` or adjacent samples.
- **Method:** Normalize and display the tangent at several path samples.
- **Lesson target:** Explain why a path position alone cannot orient a swept profile.

### 7.10 Local sweep frame

- **Input:** A path tangent and a reference direction.
- **Rule:** Calculate two perpendicular vectors that form a local frame with the tangent.
- **Test:** Display the tangent, normal, and binormal at each sample.
- **Lesson target:** Detect frame flips and near-parallel reference vectors.

### 7.11 Tube along a curve

- **Input:** A path, a circular profile, and a local frame at each path sample.
- **Vertex rule:** Orient one profile ring in each local frame.
- **Topology:** Connect adjacent rings.
- **Lesson target:** Build a manual tube before comparison with `THREE.TubeGeometry`.

### 7.12 Parallel-transport frame *(advanced)*

- **Input:** Consecutive path tangents and an initial frame.
- **Method:** Transport the frame with the smallest required rotation.
- **Purpose:** Reduce sudden frame flips and unwanted twist.
- **Lesson target:** Compare this frame with a fixed-reference frame.

### 7.13 Loft

- **Input:** Two or more profiles with matching sample counts.
- **Parameters:** Profile sample and layer index.
- **Vertex rule:** Use supplied profiles or interpolate between them.
- **Topology:** Connect corresponding samples in adjacent profiles.
- **Lesson target:** Explain why profile order and sample correspondence are required.

### 7.14 Bend deformation

- **Input:** Existing positions and a bend axis.
- **Vertex rule:** Convert distance along the axis into a rotation angle.
- **Topology:** Keep the original indices.
- **Lesson target:** Distinguish a vertex deformation from a node or object transform.

### 7.15 Twist deformation

- **Input:** Existing positions and a twist axis.
- **Vertex rule:** Rotate each position by an angle based on its coordinate along the axis.
- **Topology:** Keep the original indices.
- **Lesson target:** Apply the twisted-extrusion idea to an existing mesh.

### 7.16 Bulge and wave deformation

- **Input:** Existing positions and a scalar deformation function.
- **Vertex rule:** Offset or scale positions from height, distance, or time.
- **Topology:** Keep the original indices.
- **Lesson target:** Build several effects by changing one position function.

### 7.17 Operation composition

- **Input:** Two or more generation or deformation rules.
- **Method:** State the order, coordinate space, and center of each operation.
- **Test:** Reverse the operation order and compare the result.
- **Lesson target:** Treat complex procedural models as compositions of simple rules.

## Part 8 — Normals, UVs, Colors, and Vertex Attributes

A rendering vertex contains a set of related attribute values. A position tells the GPU where the vertex is. A normal affects lighting. A UV coordinate selects a texture location. Colors, tangents, and custom attributes supply more data. Two faces can share a rendering vertex only when all required attribute values can also be shared.

### 8.1 Position attribute

- **Input:** Generated `x`, `y`, and `z` values.
- **Storage:** Use a typed array with `itemSize = 3`.
- **Checks:** Verify `count = array.length / itemSize`.
- **Lesson target:** Read and change the position of a selected vertex by index.

### 8.2 Index attribute

- **Input:** Point, line, or triangle connections.
- **Storage:** Use a suitable integer array or pass an integer list to `setIndex()`.
- **Checks:** Verify that every index refers to an existing vertex.
- **Lesson target:** Change topology without changing the position attribute.

### 8.3 One triangle normal

- **Input:** Triangle positions `A`, `B`, and `C`.
- **Rule:** Calculate `edge_1 = B - A` and `edge_2 = C - A`.
- **Normal:** Normalize `cross(edge_1, edge_2)`.
- **Test:** Reverse the triangle winding and inspect the normal direction.
- **Lesson target:** Connect winding order with cross-product order.

### 8.4 Face normals for a mesh

- **Input:** The position and triangle-index arrays.
- **Method:** Process three indices at a time and calculate one normal per triangle.
- **Display:** Draw a line from each triangle center in the normal direction.
- **Lesson target:** Inspect the orientation of every face.

### 8.5 Vertex normals

- **Input:** Face normals and vertex-to-face adjacency.
- **Method:** Accumulate the normals of adjacent faces at each shared vertex. Normalize each result.
- **Comparison:** Compare the manual values with `computeVertexNormals()`.
- **Lesson target:** Explain why shared vertices produce averaged normals.

### 8.6 Flat and smooth shading

- **Flat case:** Give each face independent rendering vertices and one face-normal direction.
- **Smooth case:** Share vertices and use averaged vertex normals.
- **Test:** Render both forms with the same positions and material.
- **Lesson target:** Separate surface shape from the normal data used for lighting.

### 8.7 Hard edges and crease rules

- **Input:** Two adjacent faces and the angle between their normals.
- **Method:** Select an angle threshold for vertex sharing.
- **Topology:** Duplicate a vertex when adjacent faces must use different normal values.
- **Lesson target:** Create a mesh that contains both smooth regions and hard edges.

### 8.8 UV coordinates on a quad and grid

- **Class:** A mapping from the geometry domain to texture space.
- **Parameters:** `u, v ∈ [0, 1]`.
- **Storage:** Use a UV attribute with `itemSize = 2`.
- **Rule:** Reuse normalized grid parameters as UV coordinates.
- **Lesson target:** Render a UV test texture and detect flipped or stretched cells.

### 8.9 Cylindrical UV coordinates

- **Parameters:** Angle and height.
- **Rule:** Map angle to U and normalized height to V.
- **Seam:** Duplicate the seam position so that U can be both `0` and `1`.
- **Lesson target:** Explain why equal positions can require different UV values.

### 8.10 Spherical UV coordinates

- **Parameters:** Longitude and latitude.
- **Rule:** Map longitude to U and polar angle to V.
- **Seams:** Inspect the longitude seam and compressed UVs at the poles.
- **Lesson target:** Connect the sphere's parameters directly to its UV coordinates.

### 8.11 Torus UV coordinates

- **Parameters:** Major angle and tube angle.
- **Rule:** Map the two periodic parameters to U and V.
- **Seams:** Duplicate both periodic boundaries when the texture coordinates require it.
- **Lesson target:** Manage two independent attribute seams.

### 8.12 Vertex colors

- **Input:** A scalar value such as height, distance, curvature estimate, or parameter value.
- **Rule:** Map the scalar range to a color range.
- **Storage:** Use an RGB or RGBA color attribute.
- **Lesson target:** Visualize generated data without a texture.

### 8.13 Tangent attribute *(advanced)*

- **Input:** Triangle positions, normals, and UV coordinates.
- **Method:** Derive tangent directions from position changes and UV changes.
- **Requirement:** Use valid UVs and consistent triangle data.
- **Lesson target:** Understand tangent space before comparison with Three.js tangent utilities.

### 8.14 Custom attribute

- **Input:** One or more values for each rendering vertex.
- **Examples:** Phase, displacement weight, selection value, or layer index.
- **Storage:** Select an item size that matches the shader input.
- **Lesson target:** Generate a `phase` attribute and read it in a shader.

### 8.15 Attribute consistency

- **Rule:** All per-vertex attributes must describe the same logical vertex order.
- **Check:** Compare the counts of position, normal, UV, color, and custom attributes.
- **Failure test:** Shift one attribute by one vertex and inspect the result.
- **Lesson target:** Treat a rendering vertex as a complete attribute record.

## Part 9 — Dynamic Geometry and Mesh Engineering

This part verifies that a generator is correct, measurable, and safe to update. The main topics are representation choice, data counts, partial updates, bounds, draw control, and GPU resource lifetime.

### 9.1 Indexed and non-indexed geometry

- **Input:** One completed triangle mesh.
- **Method:** Build one version with shared positions and one version with repeated positions.
- **Measure:** Compare position count, index count, memory use, normals, and UV behavior.
- **Lesson target:** Select a representation from attribute needs, not only from position count.

### 9.2 Vertex sharing and duplication

- **Share when:** Position, normal, UV, color, and custom values are identical.
- **Duplicate when:** A hard edge, UV seam, material boundary, or other attribute discontinuity exists.
- **Test:** Count physical points and rendering vertices separately.
- **Lesson target:** Explain every duplicated vertex in a generated mesh.

### 9.3 Vertex-count formulas

- **Input:** Grid, ring-stack, sphere, and torus generators.
- **Method:** Derive the count from logical rows, columns, seams, poles, centers, and caps.
- **Test:** Compare the predicted value with `position.count`.
- **Lesson target:** Detect loop-bound and seam errors before visual inspection.

### 9.4 Primitive-count formulas

- **Input:** Line, fan, grid, ring-stack, and polyhedron topology.
- **Method:** Derive line or triangle counts from cells and boundaries.
- **Test:** For an indexed triangle mesh, compare the prediction with `index.count / 3`.
- **Lesson target:** Explain the complete index count before rendering.

### 9.5 Resolution study

- **Input:** One curve and one surface generator.
- **Method:** Test segment counts such as 8, 16, 32, 64, and 128.
- **Measure:** Record visual error, vertex count, triangle count, and update cost.
- **Lesson target:** Select resolution from an observed requirement instead of an arbitrary value.

### 9.6 Mesh validation

- **Checks:** Test finite values, valid index ranges, expected counts, winding, degenerate triangles, seams, boundaries, and symmetry.
- **Method:** Add assertions before `BufferGeometry` is created.
- **Display:** Use points, vertex numbers, edges, wireframe, axes, and normal helpers.
- **Lesson target:** Find data errors without relying only on the final shaded result.

### 9.7 Dynamic position updates

- **Input:** A position attribute that changes after the first render.
- **Method:** Change values in its typed array and set `position.needsUpdate = true`.
- **Usage:** Select dynamic usage before the attribute is first used when frequent changes are expected.
- **Lesson target:** Animate `P(u, v, time)` without replacing the geometry each frame.

### 9.8 Partial attribute updates

- **Input:** An attribute in which only a known component range changes.
- **Method:** Register the changed component range before the update.
- **Check:** Distinguish component offsets from vertex indices.
- **Lesson target:** Update only the required part of a large attribute.

### 9.9 Dynamic normals

- **Input:** A mesh whose positions change over time.
- **Problem:** Old normals no longer describe the changed surface.
- **Method:** Recalculate the required face or vertex normals and mark the normal attribute for update.
- **Lesson target:** Explain lighting errors caused by stale normal data.

### 9.10 Bounding box and bounding sphere

- **Input:** Generated or modified positions.
- **Method:** Calculate coordinate minima and maxima. Estimate a center and radius.
- **Comparison:** Use `computeBoundingBox()` and `computeBoundingSphere()` after the manual calculation.
- **Update rule:** Recalculate required bounds after position data changes.
- **Lesson target:** Connect geometry bounds with culling, fitting, and interaction.

### 9.11 Draw range

- **Input:** A complete position or index buffer.
- **Method:** Use `setDrawRange(start, count)` to select the submitted section.
- **Count rule:** The count refers to vertices for non-indexed geometry and indices for indexed geometry.
- **Lesson target:** Create a progressive line or triangle-growth effect without rebuilding the arrays.

### 9.12 Geometry groups

- **Input:** One geometry that needs more than one material region.
- **Method:** Assign non-overlapping vertex or index ranges to groups.
- **Check:** Ensure that each required element belongs to the correct group.
- **Lesson target:** Keep material regions separate from geometric shape generation.

### 9.13 Geometry mutation and object transforms

- **Geometry mutation:** Change or transform the stored positions.
- **Object transform:** Change the position, rotation, or scale of the rendered object.
- **Test:** Apply both methods and inspect the local-space data.
- **Lesson target:** Select the correct operation for permanent shape change or scene placement.

### 9.14 GPU resource disposal

- **Input:** Geometry that the application no longer uses.
- **Method:** Remove references from the scene and call `geometry.dispose()`.
- **Reason:** JavaScript garbage collection does not automatically release all GPU resources managed by Three.js.
- **Lesson target:** Create and remove generated meshes without an unintended GPU resource leak.

### 9.15 Final generator test

- **Select:** Choose a shape that is not listed in this guide.
- **Classify:** State its domain dimension, space dimension, parameters, and construction family.
- **Derive:** Write its samples, vertex rule, neighborhood, topology, attributes, and count formulas.
- **Build:** Create the `BufferGeometry` without a built-in shape generator.
- **Explain:** Account for every position, index, seam, and duplicated vertex.
- **Lesson target:** Prove that the framework transfers to unfamiliar geometry.

Parts 1–2 build ordered one-parameter geometry. Parts 3–4 build filled two-parameter geometry. Parts 5–6 build closed and curved surfaces in 3D space. Part 7 combines the generators into modeling operations. Parts 8–9 complete the data for rendering and updates.

Finish this guide before subdivision surfaces, Delaunay triangulation, Voronoi diagrams, marching cubes, implicit meshing, or constructive solid geometry. Those subjects extend the same framework, but they require additional algorithms.

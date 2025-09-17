---
date: 8-February-2024
---

```python
function rasterize(primitives):
    for each primitive in primitives:
        // Step 1: Primitive Assembly
        vertices = primitive.vertices
        
        // Step 2: Clipping and Culling
        if primitive is outside_view_frustum(vertices):
            continue // Skip this primitive
        
        // Step 3: Projection
        projected_vertices = project_vertices(vertices)
        
        // Step 4: Rasterization
        for each triangle in primitive.triangulate():
            // Get bounding box of triangle
            min_x, min_y, max_x, max_y = get_triangle_bounding_box(projected_vertices)
            
            // Clip bounding box to screen boundaries
            min_x = max(0, min(screen_width - 1, min_x))
            min_y = max(0, min(screen_height - 1, min_y))
            max_x = max(0, min(screen_width - 1, max_x))
            max_y = max(0, min(screen_height - 1, max_y))
            
            // Iterate over pixels in bounding box
            for x from min_x to max_x:
                for y from min_y to max_y:
                    if point_inside_triangle(x, y, projected_vertices):
                        // Step 5: Fragment Processing
                        fragment_color = shade_fragment(x, y, triangle)
                        fragment_depth = calculate_depth(x, y, triangle)
                        
                        // Step 6: Pixel Output
                        if fragment_depth < depth_buffer[x][y]:
                            depth_buffer[x][y] = fragment_depth
                            frame_buffer[x][y] = fragment_color

```
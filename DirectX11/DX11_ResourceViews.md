---
date: 8-February-2024
---

# Resource View
## Introduction
In DirectX 11 (DX11), resources represent GPU-accessible memory objects used for storing various types of data such as textures, buffers, and surfaces. Resource views, on the other hand, are specialized objects that provide a way to access and interpret the data stored in these resources.
## Difference between Resources and Resource View 
1. **Resources**:
    
    - Resources in DX11 are GPU memory objects that store data.
    - Examples of resources include textures (2D, 3D, and cube maps) and buffers (vertex buffers, index buffers, constant buffers).
    - Resources are typically created and managed by the application, and they store raw data in a specific format.
2. **Resource Views**:
    
    - Resource views provide a way to interpret or access the data stored in resources.
    - They allow the GPU to interpret resource data in different ways, such as treating a 2D texture as a depth stencil buffer or accessing specific mip levels or array slices of a texture.
    - Resource views do not store data themselves; instead, they provide a view into the underlying resource's data.
    - Examples of resource views include shader resource views (SRVs), render target views (RTVs), depth stencil views (DSVs), and unordered access views (UAVs).
## Types of ResourceView available in DX11
1. **Shader Resource Views (SRVs)**:
    - Shader Resource Views allow resources (such as textures and buffers) to be bound to shader stages as input resources.
    - They provide read-only access to the data stored in the bound resource, allowing shaders to sample textures or read data from buffers.
2. **RenderTarget Views (RTVs)**:
    - RenderTarget Views allow resources (typically render targets) to be bound as targets for rendering operations.
    - They provide write access to the data stored in the bound resource, allowing shaders to write color values during rendering.
3. **Depth Stencil Views (DSVs)**:
    - Depth Stencil Views allow resources (such as depth stencil buffers) to be bound as targets for depth and stencil operations during rendering.
    - They provide both read and write access to the depth and stencil data stored in the bound resource.
4. **Unordered Access Views (UAVs)**:
    - Unordered Access Views allow resources (such as buffers and textures) to be bound as unordered access targets for compute shaders.
    - They provide read-write access to the data stored in the bound resource, allowing compute shaders to perform arbitrary read and write operations.
5. **Constant Buffer Views (CBVs)**:
    - Constant Buffer Views allow constant buffers to be bound to shader stages as constant buffers.
    - They provide read-only access to the data stored in the bound constant buffer, allowing shaders to access constant data during execution.
---
date: 23-April-2024
---

# Introduction
  From my observation there are two types of heaps available in dx12
## 1. Resource Heap Types
1. **D3D12_HEAP_TYPE_DEFAULT**: This heap type is intended for resources that are directly and frequently accessed by the GPU, such as render-target, depth-stencil textures, other textures, vertex and index buffers used for rendering, etc. (VRAM)
2. **D3D12_HEAP_TYPE_UPLOAD**: This heap type is used for resources that need to be frequently updated by the CPU, such as vertex and index buffers that are updated every frame. (RAM)
3. **D3D12_HEAP_TYPE_READBACK**: This heap type is used for resources that need to be frequently read back by the CPU, such as render targets that need to be processed by the CPU after being rendered by the GPU. (RAM)
4. **D3D12_HEAP_TYPE_CUSTOM**: This heap type allows for more flexible control over the heap configuration, and can be used to allocate resources with specific memory properties.
  
## 2. Descriptor Heap Types
1. **D3D12_DESCRIPTOR_HEAP_TYPE_CBV_SRV_UAV**: This type of descriptor heap is used for storing Constant Buffer Views (CBVs), Shader Resource Views (SRVs), and Unordered Access Views (UAVs).
2. **D3D12_DESCRIPTOR_HEAP_TYPE_RTV**: This type of descriptor heap is used for storing Render Target Views (RTVs).
3. **D3D12_DESCRIPTOR_HEAP_TYPE_DSV**: This type of descriptor heap is used for storing Depth/Stencil Views (DSVs).
4. **D3D12_DESCRIPTOR_HEAP_TYPE_SAMPLER**: This type of descriptor heap is used for storing (non-static) Samplers.


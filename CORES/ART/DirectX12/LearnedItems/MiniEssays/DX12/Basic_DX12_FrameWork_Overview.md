## Building a Basic DX12 Framework

### Introduction

DirectX 12 (DX12) offers graphics developers powerful tools to create high-performance applications. This mini-essay introduces the foundational components of a basic DX12 framework. As beginners, we aim to construct a simple yet functional framework to understand DX12's core operations.

### Overview of the Framework

A basic DX12 framework revolves around four key virtual methods:

1. **OnInit**: Initializes the pipeline and assets.
    
    - `LoadPipeline()`: Sets up GPU configurations.
    - `LoadAssets()`: Prepares geometry, shaders, and constants.
2. **OnUpdate**: Handles frame updates.
    
3. **OnRender**: Executes rendering commands.
    
    - `PopulateCommandList()`: Records GPU actions.
    - `ExecuteCommandList()`: Executes the recorded commands.
    - `WaitForPreviousFrame()`: Synchronizes GPU and CPU operations.
4. **OnDestroy**: Cleans up resources.
    
    - Ensures all GPU tasks are complete before releasing resources.

---

### Details of Framework Methods

#### **OnInit: Loading the Pipeline and Assets**

DX12 requires two primary components: the **Pipeline** and **Assets**.

- **Pipeline**: Manages GPU configurations and handles:
    
    1. Enabling debug support.
    2. Creating a `D3D12Device`.
    3. Setting up a DXGI factory and swap chain.
    4. Creating descriptor heaps (RTV, DSV).
    5. Acquiring buffers from the swap chain and attaching them to the RTV.
    6. Creating depth-stencil buffers and storing them in the DSV.
    7. Allocating command lists.
- **Assets**: Include geometry, shaders, and other resources necessary for rendering. The process involves:
    
    1. Creating an empty root signature.
    2. Setting up a pipeline state object (PSO) with shaders and input layouts.
    3. Initializing a command list and recording buffer views and PSOs.
    4. Creating fences for synchronization.

---

#### **OnRender: Executing the Render Loop**

Rendering involves recording GPU commands, executing them, and synchronizing CPU and GPU operations:

1. **PopulateCommandList**:
    
    - Resets the command allocator and command list.
    - Records graphics commands:
        - Setting the root signature, viewports, scissor rectangles, and render targets.
        - Clearing the render target.
        - Specifying vertex buffers, primitive topology, and drawing commands.
        - Closing the command list after recording.
2. **ExecuteCommandList**: Sends the recorded commands to the GPU for execution.
    
3. **WaitForPreviousFrame**: Ensures all GPU tasks are complete before proceeding. This step switches the back buffer to the front buffer.
    

---

#### **OnDestroy: Cleaning Up**

Before releasing resources, the framework ensures that all GPU operations are complete. Once verified, all created resources are destroyed.

---

### Conclusion

This framework provides a structured approach to setting up and rendering with DX12. By dividing tasks into `OnInit`, `OnUpdate`, `OnRender`, and `OnDestroy`, we achieve modularity and clarity. The process involves initializing pipelines and assets, recording and executing rendering commands, and cleaning up resources responsibly. This foundational understanding prepares us for building more advanced DX12 applications.
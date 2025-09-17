---
date: 24-February-2024
Links: https://www.braynzarsoft.net/viewtutorial/q16390-directx-12-depth-testing
Code: BryanZar Tutorial 07
---

# Introduction
When a pixel fragment makes it out of the pixel shader, the OM (Output Merger) compares the z value (depth value) of that pixel fragment with the z value of the pixel currently on the render target.

A pixel fragment is a pixel that makes it to the pixel shader. Not all pixels that make it to the pixel shader will be the final pixel color on the render target. The final pixel color on the render target depends on depth/stencil testing as well as blending (pixels shaders can actually stop a pixel fragment from making it to the OM by using the HLSL clip function, which we will have a quick tutorial on later).

Depth testing will cause objects that are closer to the camera to show up in front of objects that are further away from the camera, even when the objects that are further away are drawn after the closer object. Without depth testing, whatever is drawn last will always overwrite anything that was drawn previous to it.

Depth is stored in a buffer called the depth/stencil buffer. The depth stencil buffer has a format of D32, where 24 bits are for the depth value, and 8 bits are for the stencil value. I will talk about stencil testing in a later tutorial.

The depth/stencil buffer has the same width and height as the render target, so that every pixel on the render target has a depth value which is stored in the depth/stencil buffer.

Depth testing is a pretty simple idea, and the above basically covers it all, so lets get into the code.

# Overview
1. InitD3D
2. Render
3. Cleanup

# 1. InitD3D
## Functional Overview
1. Enumerate Adapters and Create D3D12 Device
2. Create Direct Command Queue
3. Create Swap Chain
4. Create Back Buffers (Render Target Views) and its Descriptor Heap
5. Create Command Allocators
6. Create Command List
7. Create Fence and Fence Event
8. Create Root Signature
9. Create Vertex and Pixel Shaders
10. Create Input Layout
11. Create Pipeline State Object (PSO)
12. Create Vertex Buffer
13. Create Index Buffer
14. Create Depth and Stencil Buffer and Views
15. Execute the commandList to Upload Initial Assets
16. Increment the Fence Values to signal fence as Buffers get uploaded
17. Create Buffer Views
18. Fill out ViewPort
19. Fill out a Scissor Rect
## Data Structures Involved
### 1. InitD3D
```cpp
//global Data
// direct3d stuff
const int frameBufferCount = 3; // number of buffers we want, 2 for double buffering, 3 for tripple buffering
ID3D12Device* device; // direct3d device
IDXGISwapChain3* swapChain; // swapchain used to switch between render targets
ID3D12CommandQueue* commandQueue; // container for command lists
ID3D12DescriptorHeap* rtvDescriptorHeap; // a descriptor heap to hold resources like the render targets
ID3D12Resource* renderTargets[frameBufferCount]; // number of render targets equal to buffer count
ID3D12CommandAllocator* commandAllocator[frameBufferCount]; // we want enough allocators for each buffer * number of threads (we only have one thread)
ID3D12GraphicsCommandList* commandList; // a command list we can record commands into, then execute them to render the frame
ID3D12Fence* fence[frameBufferCount];    // an object that is locked while our command list is being executed by the gpu. We need as many 
                                         //as we have allocators (more if we want to know when the gpu is finished with an asset)

HANDLE fenceEvent; // a handle to an event when our fence is unlocked by the gpu
UINT64 fenceValue[frameBufferCount]; // this value is incremented each frame. each fence will have its own value

int frameIndex; // current rtv we are on
int rtvDescriptorSize; // size of the rtv descriptor on the device (all front and back buffers will be the same size)
                       // function declarations

ID3D12PipelineState* pipelineStateObject; // pso containing a pipeline state
ID3D12RootSignature* rootSignature; // root signature defines data shaders will access

D3D12_VIEWPORT viewport; // area that output from rasterizer will be stretched to.
D3D12_RECT scissorRect; // the area to draw in. pixels outside that area will not be drawn onto

ID3D12Resource* vertexBuffer; // a default buffer in GPU memory that we will load vertex data for our triangle into
ID3D12Resource* indexBuffer; // a default buffer in GPU memory that we will load index data for our triangle into

D3D12_VERTEX_BUFFER_VIEW vertexBufferView; // a structure containing a pointer to the vertex data in gpu memory
                                           // the total size of the buffer, and the size of each element (vertex)
D3D12_INDEX_BUFFER_VIEW indexBufferView; // a structure holding information about the index buffer

ID3D12Resource* depthStencilBuffer; // This is the memory for our depth buffer. it will also be used for a stencil buffer in a later tutorial
ID3D12DescriptorHeap* dsDescriptorHeap; // This is a heap for our depth/stencil buffer descriptor
```

## Code 
### 1. InitD3D() function
#### 1. Create D3D12 Device
##### 0. Vertex Structure
```cpp
struct Vertex {
    Vertex(float x, float y, float z, float r, float g, float b, float a) : pos(x, y, z), color(r, g, b, z) {}
    XMFLOAT3 pos;
    XMFLOAT4 color;
};
```
##### a. Find Suitable Adapter
```cpp
	IDXGIFactory4* dxgiFactory;
    hr = CreateDXGIFactory1(IID_PPV_ARGS(&dxgiFactory));
    if (FAILED(hr))
    {
        return false;
    }

    IDXGIAdapter1* adapter; // adapters are the graphics card (this includes the embedded graphics on the motherboard)

    int adapterIndex = 0; // we'll start looking for directx 12  compatible graphics devices starting at index 0

    bool adapterFound = false; // set this to true when a good one was found

                               // find first hardware gpu that supports d3d 12
    while (dxgiFactory->EnumAdapters1(adapterIndex, &adapter) != DXGI_ERROR_NOT_FOUND)
    {
        DXGI_ADAPTER_DESC1 desc;
        adapter->GetDesc1(&desc);

        if (desc.Flags & DXGI_ADAPTER_FLAG_SOFTWARE)
        {
            // we dont want a software device
            continue;
        }

        // we want a device that is compatible with direct3d 12 (feature level 11 or higher)
        hr = D3D12CreateDevice(adapter, D3D_FEATURE_LEVEL_11_0, _uuidof(ID3D12Device), nullptr);
        if (SUCCEEDED(hr))
        {
            adapterFound = true;
            break;
        }

        adapterIndex++;
    }

    if (!adapterFound)
    {
        return false;
    }

```
##### b. Create The Device
```cpp
// Create the device
    hr = D3D12CreateDevice(
        adapter,
        D3D_FEATURE_LEVEL_11_0,
        IID_PPV_ARGS(&device)
        );
    if (FAILED(hr))
    {
        return false;
    }
```

#### 2. Create Direct Command Queue
```cpp
// -- Create a direct command queue -- //

    D3D12_COMMAND_QUEUE_DESC cqDesc = {};
    cqDesc.Flags = D3D12_COMMAND_QUEUE_FLAG_NONE;
    cqDesc.Type = D3D12_COMMAND_LIST_TYPE_DIRECT; // direct means the gpu can directly execute this command queue

    hr = device->CreateCommandQueue(&cqDesc, IID_PPV_ARGS(&commandQueue)); // create the command queue
    if (FAILED(hr))
    {
        return false;
    }

```
#### 3. Create Swap Chain
##### a. Create Swap Chain
```cpp
// -- Create the Swap Chain (double/tripple buffering) -- //

    DXGI_MODE_DESC backBufferDesc = {}; // this is to describe our display mode
    backBufferDesc.Width = Width; // buffer width
    backBufferDesc.Height = Height; // buffer height
    backBufferDesc.Format = DXGI_FORMAT_R8G8B8A8_UNORM; // format of the buffer (rgba 32 bits, 8 bits for each chanel)

                                                    // describe our multi-sampling. We are not multi-sampling, so we set the count to 1 (we need at least one sample of course)
    DXGI_SAMPLE_DESC sampleDesc = {};
    sampleDesc.Count = 1; // multisample count (no multisampling, so we just put 1, since we still need 1 sample)

                          // Describe and create the swap chain.
    DXGI_SWAP_CHAIN_DESC swapChainDesc = {};
    swapChainDesc.BufferCount = frameBufferCount; // number of buffers we have
    swapChainDesc.BufferDesc = backBufferDesc; // our back buffer description
    swapChainDesc.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT; // this says the pipeline will render to this swap chain
    swapChainDesc.SwapEffect = DXGI_SWAP_EFFECT_FLIP_DISCARD; // dxgi will discard the buffer (data) after we call present
    swapChainDesc.OutputWindow = hwnd; // handle to our window
    swapChainDesc.SampleDesc = sampleDesc; // our multi-sampling description
    swapChainDesc.Windowed = !FullScreen; // set to true, then if in fullscreen must call SetFullScreenState with true for full screen to get uncapped fps

    IDXGISwapChain* tempSwapChain;

    dxgiFactory->CreateSwapChain(
        commandQueue, // the queue will be flushed once the swap chain is created
        &swapChainDesc, // give it the swap chain description we created above
        &tempSwapChain // store the created swap chain in a temp IDXGISwapChain interface
        );

    swapChain = static_cast<IDXGISwapChain3*>(tempSwapChain);

```
##### b. Create Frame Index
```cpp

frameIndex = swapChain->GetCurrentBackBufferIndex();

```

#### 4. Create Back Buffers (Render Target Views) and its Descriptor Heap
##### a. Create RTV Descriptor Heap
```cpp
// -- Create the Back Buffers (render target views) Descriptor Heap -- //

    // describe an rtv descriptor heap and create
    D3D12_DESCRIPTOR_HEAP_DESC rtvHeapDesc = {};
    rtvHeapDesc.NumDescriptors = frameBufferCount; // number of descriptors for this heap.
    rtvHeapDesc.Type = D3D12_DESCRIPTOR_HEAP_TYPE_RTV; // this heap is a render target view heap

                                            // This heap will not be directly referenced by the shaders (not shader visible), as this will store the output from the pipeline
                                            // otherwise we would set the heap's flag to D3D12_DESCRIPTOR_HEAP_FLAG_SHADER_VISIBLE
    rtvHeapDesc.Flags = D3D12_DESCRIPTOR_HEAP_FLAG_NONE;
    hr = device->CreateDescriptorHeap(&rtvHeapDesc, IID_PPV_ARGS(&rtvDescriptorHeap));
    if (FAILED(hr))
    {
        return false;
    }
```
##### b. Get Descriptor Size and CPU Descriptor Handle
```cpp
    // get the size of a descriptor in this heap (this is a rtv heap, so only rtv descriptors should be stored in it.
    // descriptor sizes may vary from device to device, which is why there is no set size and we must ask the 
    // device to give us the size. we will use this size to increment a descriptor handle offset
    rtvDescriptorSize = device->GetDescriptorHandleIncrementSize(D3D12_DESCRIPTOR_HEAP_TYPE_RTV);

    // get a handle to the first descriptor in the descriptor heap. a handle is basically a pointer,
    // but we cannot literally use it like a c++ pointer.
    CD3DX12_CPU_DESCRIPTOR_HANDLE rtvHandle(rtvDescriptorHeap->GetCPUDescriptorHandleForHeapStart());

```

##### c. Get Buffer(Resource) from SwapChain and Create RenderTargetView for each
```cpp
// Create a RTV for each buffer (double buffering is two buffers, tripple buffering is 3).
    for (int i = 0; i < frameBufferCount; i++)
    {
        // first we get the n'th buffer in the swap chain and store it in the n'th
        // position of our ID3D12Resource array
        hr = swapChain->GetBuffer(i, IID_PPV_ARGS(&renderTargets[i]));
        if (FAILED(hr))
        {
            return false;
        }

        // the we "create" a render target view which binds the swap chain buffer (ID3D12Resource[n]) to the rtv handle
        device->CreateRenderTargetView(renderTargets[i], nullptr, rtvHandle);

        // we increment the rtv handle by the rtv descriptor size we got above
        rtvHandle.Offset(1, rtvDescriptorSize);
    }
```

#### 5. Create Command Allocators

```cpp
    // -- Create the Command Allocators -- //

    for (int i = 0; i < frameBufferCount; i++)
    {
        hr = device->CreateCommandAllocator(D3D12_COMMAND_LIST_TYPE_DIRECT, IID_PPV_ARGS(&commandAllocator[i]));
        if (FAILED(hr))
        {
            return false;
        }
    }
```

#### 6. Create Command List
```cpp
// -- Create a Command List -- //

    // create the command list with the first allocator
    hr = device->CreateCommandList(0, D3D12_COMMAND_LIST_TYPE_DIRECT, commandAllocator[frameIndex], NULL, IID_PPV_ARGS(&commandList));
    if (FAILED(hr))
    {
        return false;
    }
```

#### 7. Create Fence and Fence Event
```cpp
    // -- Create a Fence & Fence Event -- //

    // create the fences
    for (int i = 0; i < frameBufferCount; i++)
    {
        hr = device->CreateFence(0, D3D12_FENCE_FLAG_NONE, IID_PPV_ARGS(&fence[i]));
        if (FAILED(hr))
        {
            return false;
        }
        fenceValue[i] = 0; // set the initial fence value to 0
    }

    // create a handle to a fence event
    fenceEvent = CreateEvent(nullptr, FALSE, FALSE, nullptr);
    if (fenceEvent == nullptr)
    {
        return false;
    }
```
#### 8. Create Root Signature
```cpp
    // create root signature

    CD3DX12_ROOT_SIGNATURE_DESC rootSignatureDesc;
    rootSignatureDesc.Init(0, nullptr, 0, nullptr, D3D12_ROOT_SIGNATURE_FLAG_ALLOW_INPUT_ASSEMBLER_INPUT_LAYOUT);

    ID3DBlob* signature;
    hr = D3D12SerializeRootSignature(&rootSignatureDesc, D3D_ROOT_SIGNATURE_VERSION_1, &signature, nullptr);
    if (FAILED(hr))
    {
        return false;
    }

    hr = device->CreateRootSignature(0, signature->GetBufferPointer(), signature->GetBufferSize(), IID_PPV_ARGS(&rootSignature));
    if (FAILED(hr))
    {
        return false;
    }
```

#### 9. Create Vertex and Pixel Shaders
```cpp
// create vertex and pixel shaders

    // when debugging, we can compile the shader files at runtime.
    // but for release versions, we can compile the hlsl shaders
    // with fxc.exe to create .cso files, which contain the shader
    // bytecode. We can load the .cso files at runtime to get the
    // shader bytecode, which of course is faster than compiling
    // them at runtime

    // compile vertex shader
    ID3DBlob* vertexShader; // d3d blob for holding vertex shader bytecode
    ID3DBlob* errorBuff; // a buffer holding the error data if any
    hr = D3DCompileFromFile(L"VertexShader.hlsl",
        nullptr,
        nullptr,
        "main",
        "vs_5_0",
        D3DCOMPILE_DEBUG | D3DCOMPILE_SKIP_OPTIMIZATION,
        0,
        &vertexShader,
        &errorBuff);
    if (FAILED(hr))
    {
        OutputDebugStringA((char*)errorBuff->GetBufferPointer());
        return false;
    }

    // fill out a shader bytecode structure, which is basically just a pointer
    // to the shader bytecode and the size of the shader bytecode
    D3D12_SHADER_BYTECODE vertexShaderBytecode = {};
    vertexShaderBytecode.BytecodeLength = vertexShader->GetBufferSize();
    vertexShaderBytecode.pShaderBytecode = vertexShader->GetBufferPointer();

    // compile pixel shader
    ID3DBlob* pixelShader;
    hr = D3DCompileFromFile(L"PixelShader.hlsl",
        nullptr,
        nullptr,
        "main",
        "ps_5_0",
        D3DCOMPILE_DEBUG | D3DCOMPILE_SKIP_OPTIMIZATION,
        0,
        &pixelShader,
        &errorBuff);
    if (FAILED(hr))
    {
        OutputDebugStringA((char*)errorBuff->GetBufferPointer());
        return false;
    }

    // fill out shader bytecode structure for pixel shader
    D3D12_SHADER_BYTECODE pixelShaderBytecode = {};
    pixelShaderBytecode.BytecodeLength = pixelShader->GetBufferSize();
    pixelShaderBytecode.pShaderBytecode = pixelShader->GetBufferPointer();
```

#### 10. Create Input Layout
```cpp
    // create input layout

    // The input layout is used by the Input Assembler so that it knows
    // how to read the vertex data bound to it.

    D3D12_INPUT_ELEMENT_DESC inputLayout[] =
    {
        { "POSITION", 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, 0, D3D12_INPUT_CLASSIFICATION_PER_VERTEX_DATA, 0 },
        { "COLOR", 0, DXGI_FORMAT_R32G32B32A32_FLOAT, 0, 12, D3D12_INPUT_CLASSIFICATION_PER_VERTEX_DATA, 0 }
    };

    // fill out an input layout description structure
    D3D12_INPUT_LAYOUT_DESC inputLayoutDesc = {};

    // we can get the number of elements in an array by "sizeof(array) / sizeof(arrayElementType)"
    inputLayoutDesc.NumElements = sizeof(inputLayout) / sizeof(D3D12_INPUT_ELEMENT_DESC);
    inputLayoutDesc.pInputElementDescs = inputLayout;


```
#### 11. Create Pipeline State Objects
```cpp
// create a pipeline state object (PSO)

    // In a real application, you will have many pso's. for each different shader
    // or different combinations of shaders, different blend states or different rasterizer states,
    // different topology types (point, line, triangle, patch), or a different number
    // of render targets you will need a pso

    // VS is the only required shader for a pso. You might be wondering when a case would be where
    // you only set the VS. It's possible that you have a pso that only outputs data with the stream
    // output, and not on a render target, which means you would not need anything after the stream
    // output.

    D3D12_GRAPHICS_PIPELINE_STATE_DESC psoDesc = {}; // a structure to define a pso
    psoDesc.InputLayout = inputLayoutDesc; // the structure describing our input layout
    psoDesc.pRootSignature = rootSignature; // the root signature that describes the input data this pso needs
    psoDesc.VS = vertexShaderBytecode; // structure describing where to find the vertex shader bytecode and how large it is
    psoDesc.PS = pixelShaderBytecode; // same as VS but for pixel shader
    psoDesc.PrimitiveTopologyType = D3D12_PRIMITIVE_TOPOLOGY_TYPE_TRIANGLE; // type of topology we are drawing
    psoDesc.RTVFormats[0] = DXGI_FORMAT_R8G8B8A8_UNORM; // format of the render target
    psoDesc.SampleDesc = sampleDesc; // must be the same sample description as the swapchain and depth/stencil buffer
    psoDesc.SampleMask = 0xffffffff; // sample mask has to do with multi-sampling. 0xffffffff means point sampling is done
    psoDesc.RasterizerState = CD3DX12_RASTERIZER_DESC(D3D12_DEFAULT); // a default rasterizer state.
    psoDesc.BlendState = CD3DX12_BLEND_DESC(D3D12_DEFAULT); // a default blent state.
    psoDesc.NumRenderTargets = 1; // we are only binding one render target
    psoDesc.DepthStencilState = CD3DX12_DEPTH_STENCIL_DESC(D3D12_DEFAULT); // a default depth stencil state

    // create the pso
    hr = device->CreateGraphicsPipelineState(&psoDesc, IID_PPV_ARGS(&pipelineStateObject));
    if (FAILED(hr))
    {
        return false;
    }

```
#### 12. Create Vertex Buffer
```cpp
// Create vertex buffer

    // a triangle
    Vertex vList[] = {
        // first quad (closer to camera, blue)
        { -0.5f,  0.5f, 0.5f, 0.0f, 0.0f, 1.0f, 1.0f },
        {  0.5f, -0.5f, 0.5f, 0.0f, 0.0f, 1.0f, 1.0f },
        { -0.5f, -0.5f, 0.5f, 0.0f, 0.0f, 1.0f, 1.0f },
        {  0.5f,  0.5f, 0.5f, 0.0f, 0.0f, 1.0f, 1.0f },

        // second quad (further from camera, green)
        { -0.75f,  0.75f,  0.7f, 0.0f, 1.0f, 0.0f, 1.0f },
        {   0.0f,  0.0f, 0.7f, 0.0f, 1.0f, 0.0f, 1.0f },
        { -0.75f,  0.0f, 0.7f, 0.0f, 1.0f, 0.0f, 1.0f },
        {   0.0f,  0.75f,  0.7f, 0.0f, 1.0f, 0.0f, 1.0f }
    };

    int vBufferSize = sizeof(vList);

    // create default heap
    // default heap is memory on the GPU. Only the GPU has access to this memory
    // To get data into this heap, we will have to upload the data using
    // an upload heap
    device->CreateCommittedResource(
        &CD3DX12_HEAP_PROPERTIES(D3D12_HEAP_TYPE_DEFAULT), // a default heap
        D3D12_HEAP_FLAG_NONE, // no flags
        &CD3DX12_RESOURCE_DESC::Buffer(vBufferSize), // resource description for a buffer
        D3D12_RESOURCE_STATE_COPY_DEST, // we will start this heap in the copy destination state since we will copy data
                                        // from the upload heap to this heap
        nullptr, // optimized clear value must be null for this type of resource. used for render targets and depth/stencil buffers
        IID_PPV_ARGS(&vertexBuffer));

    // we can give resource heaps a name so when we debug with the graphics debugger we know what resource we are looking at
    vertexBuffer->SetName(L"Vertex Buffer Resource Heap");

    // create upload heap
    // upload heaps are used to upload data to the GPU. CPU can write to it, GPU can read from it
    // We will upload the vertex buffer using this heap to the default heap
    ID3D12Resource* vBufferUploadHeap;
    device->CreateCommittedResource(
        &CD3DX12_HEAP_PROPERTIES(D3D12_HEAP_TYPE_UPLOAD), // upload heap
        D3D12_HEAP_FLAG_NONE, // no flags
        &CD3DX12_RESOURCE_DESC::Buffer(vBufferSize), // resource description for a buffer
        D3D12_RESOURCE_STATE_GENERIC_READ, // GPU will read from this buffer and copy its contents to the default heap
        nullptr,
        IID_PPV_ARGS(&vBufferUploadHeap));
    vBufferUploadHeap->SetName(L"Vertex Buffer Upload Resource Heap");

    // store vertex buffer in upload heap
    D3D12_SUBRESOURCE_DATA vertexData = {};
    vertexData.pData = reinterpret_cast<BYTE*>(vList); // pointer to our vertex array
    vertexData.RowPitch = vBufferSize; // size of all our triangle vertex data
    vertexData.SlicePitch = vBufferSize; // also the size of our triangle vertex data

    // we are now creating a command with the command list to copy the data from
    // the upload heap to the default heap
    UpdateSubresources(commandList, vertexBuffer, vBufferUploadHeap, 0, 0, 1, &vertexData);

    // transition the vertex buffer data from copy destination state to vertex buffer state
    commandList->ResourceBarrier(1, &CD3DX12_RESOURCE_BARRIER::Transition(vertexBuffer, D3D12_RESOURCE_STATE_COPY_DEST, D3D12_RESOURCE_STATE_VERTEX_AND_CONSTANT_BUFFER));

```
#### 13. Create Index Buffer
```cpp
 // Create index buffer

    // a quad (2 triangles)
    DWORD iList[] = {
        // first quad (blue)
        0, 1, 2, // first triangle
        0, 3, 1, // second triangle
    };

    int iBufferSize = sizeof(iList);

    // create default heap to hold index buffer
    device->CreateCommittedResource(
        &CD3DX12_HEAP_PROPERTIES(D3D12_HEAP_TYPE_DEFAULT), // a default heap
        D3D12_HEAP_FLAG_NONE, // no flags
        &CD3DX12_RESOURCE_DESC::Buffer(iBufferSize), // resource description for a buffer
        D3D12_RESOURCE_STATE_COPY_DEST, // start in the copy destination state
        nullptr, // optimized clear value must be null for this type of resource
        IID_PPV_ARGS(&indexBuffer));

    // we can give resource heaps a name so when we debug with the graphics debugger we know what resource we are looking at
    vertexBuffer->SetName(L"Index Buffer Resource Heap");

    // create upload heap to upload index buffer
    ID3D12Resource* iBufferUploadHeap;
    device->CreateCommittedResource(
        &CD3DX12_HEAP_PROPERTIES(D3D12_HEAP_TYPE_UPLOAD), // upload heap
        D3D12_HEAP_FLAG_NONE, // no flags
        &CD3DX12_RESOURCE_DESC::Buffer(vBufferSize), // resource description for a buffer
        D3D12_RESOURCE_STATE_GENERIC_READ, // GPU will read from this buffer and copy its contents to the default heap
        nullptr,
        IID_PPV_ARGS(&iBufferUploadHeap));
    vBufferUploadHeap->SetName(L"Index Buffer Upload Resource Heap");

    // store vertex buffer in upload heap
    D3D12_SUBRESOURCE_DATA indexData = {};
    indexData.pData = reinterpret_cast<BYTE*>(iList); // pointer to our index array
    indexData.RowPitch = iBufferSize; // size of all our index buffer
    indexData.SlicePitch = iBufferSize; // also the size of our index buffer

    // we are now creating a command with the command list to copy the data from
    // the upload heap to the default heap
    UpdateSubresources(commandList, indexBuffer, iBufferUploadHeap, 0, 0, 1, &indexData);

    // transition the vertex buffer data from copy destination state to vertex buffer state
    commandList->ResourceBarrier(1, &CD3DX12_RESOURCE_BARRIER::Transition(indexBuffer, D3D12_RESOURCE_STATE_COPY_DEST, D3D12_RESOURCE_STATE_VERTEX_AND_CONSTANT_BUFFER));


```
#### 14. Create Depth and Stencil Buffer and Views
```cpp
// Create the depth/stencil buffer

    // create a depth stencil descriptor heap so we can get a pointer to the depth stencil buffer
    D3D12_DESCRIPTOR_HEAP_DESC dsvHeapDesc = {};
    dsvHeapDesc.NumDescriptors = 1;
    dsvHeapDesc.Type = D3D12_DESCRIPTOR_HEAP_TYPE_DSV;
    dsvHeapDesc.Flags = D3D12_DESCRIPTOR_HEAP_FLAG_NONE;
    hr = device->CreateDescriptorHeap(&dsvHeapDesc, IID_PPV_ARGS(&dsDescriptorHeap));
    if (FAILED(hr))
    {
        Running = false;
    }

    D3D12_DEPTH_STENCIL_VIEW_DESC depthStencilDesc = {};
    depthStencilDesc.Format = DXGI_FORMAT_D32_FLOAT;
    depthStencilDesc.ViewDimension = D3D12_DSV_DIMENSION_TEXTURE2D;
    depthStencilDesc.Flags = D3D12_DSV_FLAG_NONE;

    D3D12_CLEAR_VALUE depthOptimizedClearValue = {};
    depthOptimizedClearValue.Format = DXGI_FORMAT_D32_FLOAT;
    depthOptimizedClearValue.DepthStencil.Depth = 1.0f;
    depthOptimizedClearValue.DepthStencil.Stencil = 0;

    device->CreateCommittedResource(
        &CD3DX12_HEAP_PROPERTIES(D3D12_HEAP_TYPE_DEFAULT),
        D3D12_HEAP_FLAG_NONE,
        &CD3DX12_RESOURCE_DESC::Tex2D(DXGI_FORMAT_D32_FLOAT, Width, Height, 1, 0, 1, 0, D3D12_RESOURCE_FLAG_ALLOW_DEPTH_STENCIL),
        D3D12_RESOURCE_STATE_DEPTH_WRITE,
        &depthOptimizedClearValue,
        IID_PPV_ARGS(&depthStencilBuffer)
        );
    hr = device->CreateDescriptorHeap(&dsvHeapDesc, IID_PPV_ARGS(&dsDescriptorHeap));
    if (FAILED(hr))
    {
        Running = false;
    }
    dsDescriptorHeap->SetName(L"Depth/Stencil Resource Heap");

    device->CreateDepthStencilView(depthStencilBuffer, &depthStencilDesc, dsDescriptorHeap->GetCPUDescriptorHandleForHeapStart());
```

#### 15. Execute CommandLists to Upload Initial Assets (Triangle data)
```cpp
// Now we execute the command list to upload the initial assets (triangle data)
    commandList->Close();
    ID3D12CommandList* ppCommandLists[] = { commandList };
    commandQueue->ExecuteCommandLists(_countof(ppCommandLists), ppCommandLists);
```
#### 16. Increment the Fence Values to signal fence as Buffers get uploaded
```cpp
   // increment the fence value now, otherwise the buffer might not be uploaded by the time we start drawing
    fenceValue[frameIndex]++;
    hr = commandQueue->Signal(fence[frameIndex], fenceValue[frameIndex]);
    if (FAILED(hr))
    {
        Running = false;
    }
```
#### 17. Create Buffer Views
```cpp
// create a vertex buffer view for the triangle. We get the GPU memory address to the vertex pointer using the GetGPUVirtualAddress() method
    vertexBufferView.BufferLocation = vertexBuffer->GetGPUVirtualAddress();
    vertexBufferView.StrideInBytes = sizeof(Vertex);
    vertexBufferView.SizeInBytes = vBufferSize;

    // create a vertex buffer view for the triangle. We get the GPU memory address to the vertex pointer using the GetGPUVirtualAddress() method
    indexBufferView.BufferLocation = indexBuffer->GetGPUVirtualAddress();
    indexBufferView.Format = DXGI_FORMAT_R32_UINT; // 32-bit unsigned integer (this is what a dword is, double word, a word is 2 bytes)
    indexBufferView.SizeInBytes = iBufferSize;

```
#### 18. Fill out the ViewPort
```cpp
 // Fill out the Viewport
    viewport.TopLeftX = 0;
    viewport.TopLeftY = 0;
    viewport.Width = Width;
    viewport.Height = Height;
    viewport.MinDepth = 0.0f;
    viewport.MaxDepth = 1.0f;
```
#### 19. Fill out the Scissor Rect
```cpp
    // Fill out a scissor rect
    scissorRect.left = 0;
    scissorRect.top = 0;
    scissorRect.right = Width;
    scissorRect.bottom = Height;
```

# 2. Render
## Functional Overview
1. Wait For Previous Frame to be completed 
2. Update Pipeline (Record Command And SetPipeline)
3. Render (Execute Command Lists and Signal Fence and Present)
## Data Structures Involved
All Are Created on InitD3D so We use it here
## Code
### 1. WaitForPreviousFrame
```cpp
void WaitForPreviousFrame()
{
    HRESULT hr;

    // swap the current rtv buffer index so we draw on the correct buffer
    frameIndex = swapChain->GetCurrentBackBufferIndex();

    // if the current fence value is still less than "fenceValue", then we know the GPU has not finished executing
    // the command queue since it has not reached the "commandQueue->Signal(fence, fenceValue)" command
    if (fence[frameIndex]->GetCompletedValue() < fenceValue[frameIndex])
    {
        // we have the fence create an event which is signaled once the fence's current value is "fenceValue"
        hr = fence[frameIndex]->SetEventOnCompletion(fenceValue[frameIndex], fenceEvent);
        if (FAILED(hr))
        {
            Running = false;
        }

        // We will wait until the fence has triggered the event that it's current value has reached "fenceValue". once it's value
        // has reached "fenceValue", we know the command queue has finished executing
        WaitForSingleObject(fenceEvent, INFINITE);
    }

    // increment fenceValue for next frame
    fenceValue[frameIndex]++;
}
```

### 2. UpdatePipeLine()
```cpp
void UpdatePipeline()
{
    HRESULT hr;

    // We have to wait for the gpu to finish with the command allocator before we reset it
    WaitForPreviousFrame();

    // we can only reset an allocator once the gpu is done with it
    // resetting an allocator frees the memory that the command list was stored in
    hr = commandAllocator[frameIndex]->Reset();
    if (FAILED(hr))
    {
        Running = false;
    }

    // reset the command list. by resetting the command list we are putting it into
    // a recording state so we can start recording commands into the command allocator.
    // the command allocator that we reference here may have multiple command lists
    // associated with it, but only one can be recording at any time. Make sure
    // that any other command lists associated to this command allocator are in
    // the closed state (not recording).
    // Here you will pass an initial pipeline state object as the second parameter,
    // but in this tutorial we are only clearing the rtv, and do not actually need
    // anything but an initial default pipeline, which is what we get by setting
    // the second parameter to NULL
    hr = commandList->Reset(commandAllocator[frameIndex], pipelineStateObject);
    if (FAILED(hr))
    {
        Running = false;
    }

    // here we start recording commands into the commandList (which all the commands will be stored in the commandAllocator)

    // transition the "frameIndex" render target from the present state to the render target state so the command list draws to it starting from here
    commandList->ResourceBarrier(1, &CD3DX12_RESOURCE_BARRIER::Transition(renderTargets[frameIndex], D3D12_RESOURCE_STATE_PRESENT, D3D12_RESOURCE_STATE_RENDER_TARGET));

    // here we again get the handle to our current render target view so we can set it as the render target in the output merger stage of the pipeline
    CD3DX12_CPU_DESCRIPTOR_HANDLE rtvHandle(rtvDescriptorHeap->GetCPUDescriptorHandleForHeapStart(), frameIndex, rtvDescriptorSize);

    // get a handle to the depth/stencil buffer
    CD3DX12_CPU_DESCRIPTOR_HANDLE dsvHandle(dsDescriptorHeap->GetCPUDescriptorHandleForHeapStart());

    // set the render target for the output merger stage (the output of the pipeline)
    commandList->OMSetRenderTargets(1, &rtvHandle, FALSE, &dsvHandle);

    // Clear the render target by using the ClearRenderTargetView command
    const float clearColor[] = { 0.0f, 0.2f, 0.4f, 1.0f };
    commandList->ClearRenderTargetView(rtvHandle, clearColor, 0, nullptr);

    // clear the depth/stencil buffer
    commandList->ClearDepthStencilView(dsDescriptorHeap->GetCPUDescriptorHandleForHeapStart(), D3D12_CLEAR_FLAG_DEPTH, 1.0f, 0, 0, nullptr);

    // draw triangle
    commandList->SetGraphicsRootSignature(rootSignature); // set the root signature
    commandList->RSSetViewports(1, &viewport); // set the viewports
    commandList->RSSetScissorRects(1, &scissorRect); // set the scissor rects
    commandList->IASetPrimitiveTopology(D3D_PRIMITIVE_TOPOLOGY_TRIANGLELIST); // set the primitive topology
    commandList->IASetVertexBuffers(0, 1, &vertexBufferView); // set the vertex buffer (using the vertex buffer view)
    commandList->IASetIndexBuffer(&indexBufferView);
    commandList->DrawIndexedInstanced(6, 1, 0, 0, 0); // draw first quad
    commandList->DrawIndexedInstanced(6, 1, 0, 4, 0); // draw second quad

    // transition the "frameIndex" render target from the render target state to the present state. If the debug layer is enabled, you will receive a
    // warning if present is called on the render target when it's not in the present state
    commandList->ResourceBarrier(1, &CD3DX12_RESOURCE_BARRIER::Transition(renderTargets[frameIndex], D3D12_RESOURCE_STATE_RENDER_TARGET, D3D12_RESOURCE_STATE_PRESENT));

    hr = commandList->Close();
    if (FAILED(hr))
    {
        Running = false;
    }
}
```

### 3. Render()
```cpp
void Render()
{
    HRESULT hr;

    UpdatePipeline(); // update the pipeline by sending commands to the commandqueue

    // create an array of command lists (only one command list here)
    ID3D12CommandList* ppCommandLists[] = { commandList };

    // execute the array of command lists
    commandQueue->ExecuteCommandLists(_countof(ppCommandLists), ppCommandLists);

    // this command goes in at the end of our command queue. we will know when our command queue 
    // has finished because the fence value will be set to "fenceValue" from the GPU since the command
    // queue is being executed on the GPU
    hr = commandQueue->Signal(fence[frameIndex], fenceValue[frameIndex]);
    if (FAILED(hr))
    {
        Running = false;
    }

    // present the current backbuffer
    hr = swapChain->Present(0, 0);
    if (FAILED(hr))
    {
        Running = false;
    }
}
```
# 3. Cleanup

```cpp
void Cleanup()
{
    // wait for the gpu to finish all frames
    for (int i = 0; i < frameBufferCount; ++i)
    {
        frameIndex = i;
        WaitForPreviousFrame();
    }

    // get swapchain out of full screen before exiting
    BOOL fs = false;
    if (swapChain->GetFullscreenState(&fs, NULL))
        swapChain->SetFullscreenState(false, NULL);

    SAFE_RELEASE(device);
    SAFE_RELEASE(swapChain);
    SAFE_RELEASE(commandQueue);
    SAFE_RELEASE(rtvDescriptorHeap);
    SAFE_RELEASE(commandList);

    for (int i = 0; i < frameBufferCount; ++i)
    {
        SAFE_RELEASE(renderTargets[i]);
        SAFE_RELEASE(commandAllocator[i]);
        SAFE_RELEASE(fence[i]);
    };

    SAFE_RELEASE(pipelineStateObject);
    SAFE_RELEASE(rootSignature);
    SAFE_RELEASE(vertexBuffer);
    SAFE_RELEASE(indexBuffer);

    SAFE_RELEASE(depthStencilBuffer);
    SAFE_RELEASE(dsDescriptorHeap);
}
```

# Shaders
## Vertex
```hlsl
struct VS_INPUT
{
    float3 pos : POSITION;
    float4 color: COLOR;
};

struct VS_OUTPUT
{
    float4 pos: SV_POSITION;
    float4 color: COLOR;
};

VS_OUTPUT main(VS_INPUT input)
{
    VS_OUTPUT output;
    output.pos = float4(input.pos, 1.0f);
    output.color = input.color;
    return output;
}
```

## Pixel shader
```hlsl
struct VS_OUTPUT
{
    float4 pos: SV_POSITION;
    float4 color: COLOR;
};

float4 main(VS_OUTPUT input) : SV_TARGET
{
    // return interpolated color
    return input.color;
}
```

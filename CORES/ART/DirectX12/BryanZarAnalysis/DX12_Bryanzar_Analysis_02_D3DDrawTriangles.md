---
date: 18-February-2024
Links: https://www.braynzarsoft.net/viewtutorial/q16390-04-direct3d-12-drawing
Code: BryanZar Tutorial 02
---

# Overview
1. InitD3D
2. Render
3. Cleanup

# Concepts
## Buffer and BufferViews
Buffers are ID3D12Resources. contain data/textures.

Views are predfined usage of Resources. Below are the types of views
1. Constant Buffer View (CBV)
2. Unordered Access view (UAV)
3. Shader Resource View (SRV)
4. Samplers
5. Render Target Views (RTV)
6. Depth Stencil View (DSV)
7. Index Buffer view (IBV)
8. Vertex Buffer View (VBV)
9. Stream Output View (SOV)

## Descriptor and Descriptor Table and Descritor Heaps and its relation to resource binding
### Descriptor
Descriptor are a structure which tells Shaders where to find resource and how to interpret the data in the resources.  

Descriptors only Placed in Descriptor Heaps.

### Descriptor Handles
a descriptor Handle is the unique address of the descritor. its similar to pointer.

```cpp
D3D12_CPU_DESCRIPTOR_HANDLE h = ID3D12DescriptorHeap::GetCPUDescriptorHandleForHeapStart();
D3D12_GPU_DESCRIPTOR_HANDLE h = ID3D12DescriptorHeap::GetGPUDescriptorHandleForHeapStart();
```
Size of descriptor varies by hardware. To get increment between each descriptor in a heap use 
```cpp
int incrementSize = - ID3D12Device::GetDescriptorHandleIncrementSize(SpecifyHeapType);
```

To get nth CPU Descriptor we use 
```cpp
 D3D12_GPU_DESCRIPTOR_HANDLE nth =  h + incrementSize;
```

We can use helpers from d3dx12.h
```cpp
CD3DX12_CPU_DESCRIPTOR_HANDLE
CD3DX12_GPU_DESCRIPTOR_HANDLE
```
### Descriptor Table
Descriptor Tables are an array of Descriptors inside descriptor heap.


```cpp
DescriptorHeap hp = {Desc1,Desc2,Desc3,Desc4,Desc5,Desc6...}

struct DescriptorTable {
  int Offset;
  int size;
};

DescriptorTable tbl = {Offset: 2, size: 3};
//So from tbl we get Desc3,Desc4,Desc5 3 Descriptors
```

a descriptor Table is actually just a sub-range of a descriptor heeap.

Shaders can access descriptors in a descriptor heap through Root Signature's descriptor tables by index. 
### Descriptor Heaps

Descriptor Heaps in GPU can be categorized into 3 types
1. Shader Visible Descriptor Heaps
	1. couple of flavors One type being (D3D12_SRV_UAV_CBV_DESCRIPTOR_HEAP) stores SRV,UAV and CBV all Intermeixed
	2. D3D12_DESCRIPTOR_HEAP_TYPE_SAMPLER  only stores Samplers
2. Non Shader Visible Descriptor Heaps
	1. Render Target Views (RTVs)
	2. Depth Stencil Views (DSVs)
3. Index Buffer Views (IBV) and Vertex Buffer Views (VBVs) and Stream Output views (SOVs) are passed directly to API methods and don't have Heaps

|               | Shader visible, CPU write only | Non-shader visible, CPU read/write |     |
| ------------- | ------------------------------ | ---------------------------------- | --- |
| CBV, SRV, UAV | yes                            | yes                                |     |
| SAMPLER       | yes                            | yes                                |     |
| RTV           | no                             | yes                                |     |
| DSV           | no                             | yes                                |     |
|               |                                |                                    |     |
|               |                                |                                    |     |
|               |                                |                                    |     | 
### Creating Descriptor Heaps
```cpp
typedef enum D3D12_DESCRIPTOR_HEAP_TYPE
{
    D3D12_DESCRIPTOR_HEAP_TYPE_CBV_SRV_UAV,    // Constant buffer/Shader resource/Unordered access views
    D3D12_DESCRIPTOR_HEAP_TYPE_SAMPLER,        // Samplers
    D3D12_DESCRIPTOR_HEAP_TYPE_RTV,            // Render target view
    D3D12_DESCRIPTOR_HEAP_TYPE_DSV,            // Depth stencil view
    D3D12_DESCRIPTOR_HEAP_TYPE_NUM_TYPES       // Simply the number of descriptor heap types
} D3D12_DESCRIPTOR_HEAP_TYPE;

// Describe and create a sampler descriptor heap.
D3D12_DESCRIPTOR_HEAP_DESC samplerHeapDesc = {};
samplerHeapDesc.NumDescriptors = 1;
samplerHeapDesc.Type = D3D12_DESCRIPTOR_HEAP_TYPE_SAMPLER;
samplerHeapDesc.Flags = D3D12_DESCRIPTOR_HEAP_FLAG_SHADER_VISIBLE;
ThrowIfFailed(m_device->CreateDescriptorHeap(&samplerHeapDesc, IID_PPV_ARGS(&m_samplerHeap)))

// Describe and create a shader resource view (SRV) and unordered
// access view (UAV) descriptor heap.
D3D12_DESCRIPTOR_HEAP_DESC srvUavHeapDesc = {};
srvUavHeapDesc.NumDescriptors = DescriptorCount;
srvUavHeapDesc.Type = D3D12_DESCRIPTOR_HEAP_TYPE_CBV_SRV_UAV;
srvUavHeapDesc.Flags = D3D12_DESCRIPTOR_HEAP_FLAG_SHADER_VISIBLE;
ThrowIfFailed(m_device->CreateDescriptorHeap(&srvUavHeapDesc, IID_PPV_ARGS(&m_srvUavHeap)));

m_rtvDescriptorSize = m_device->GetDescriptorHandleIncrementSize(D3D12_DESCRIPTOR_HEAP_TYPE_RTV);
m_srvUavDescriptorSize = m_device->GetDescriptorHandleIncrementSize(D3D12_DESCRIPTOR_HEAP_TYPE_CBV_SRV_UAV);
```
### Resource Bindings 
Descriptor tables, each identifying a range in a descriptor heap, are bound at slots defined by the current root signature on a command list.

The following resource references can share the same descriptor table and heap:

- Shader resource views
- Unordered access views
- Constant buffer views

The following resource references must be in their own descriptor heap:

- Samplers

The following resources are not placed in descriptor tables or heaps, but are bound directly using command lists:

- Index buffers
- Vertex buffers
- Stream output buffers
- Render targets
- Depth stencil views

# 1. InitD3D
## Functional Overview
1. Create D3D12 Device
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
13. Fill out ViewPort
14. Fill out a Scissor Rect
## Data Structures Involved
### 1. InitD3D
```cpp
//global Data
const int frameBufferCount = 3; 
ID3D12Device* device; 
IDXGISwapChain3* swapChain; 
ID3D12CommandQueue* commandQueue; 
ID3D12DescriptorHeap* rtvDescriptorHeap; 
ID3D12Resource* renderTargets[frameBufferCount]; 
ID3D12CommandAllocator* commandAllocator[frameBufferCount]; 
ID3D12GraphicsCommandList* commandList; 
ID3D12Fence* fence[frameBufferCount];  
HANDLE fenceEvent; 
UINT64 fenceValue[frameBufferCount]; 

int frameIndex;
int rtvDescriptorSize; 

ID3D12PipelineState* pipelineStateObject; // pso containing a pipeline state
ID3D12RootSignature* rootSignature; // root signature defines data shaders will access
D3D12_VIEWPORT viewport; // area that output from rasterizer will be stretched to.
D3D12_RECT scissorRect; // the area to draw in. pixels outside that area will not be drawn onto
ID3D12Resource* vertexBuffer; // a default buffer in GPU memory that we will load vertex data for our triangle into
D3D12_VERTEX_BUFFER_VIEW vertexBufferView; // a structure containing a pointer to the vertex data in gpu memory the total size of the buffer, and the size of each element (vertex)

```

## Code 
### 1. InitD3D() function
#### 1. Create D3D12 Device
##### a. Find Suitable Adapter
```cpp
IDXGIFactory4* dxgiFactory;
hr = CreateDXGIFactory1(IID_PPV_ARGS(&dxgiFactory));
if (FAILED(hr))
{
	return false;
}

//Find Best Suitable Adapter 
IDXGIAdapter1* adapter;
int adapterIndex = 0; 
bool adapterFound = false; 
while (dxgiFactory->EnumAdapters1(adapterIndex, &adapter) != DXGI_ERROR_NOT_FOUND)
{
	DXGI_ADAPTER_DESC1 desc;
	adapter->GetDesc1(&desc);
	if (desc.Flags & DXGI_ADAPTER_FLAG_SOFTWARE)
	{
		// we dont want a software device
		continue;
	}
	//we call D3D12CreateDevice() with a NULL fourth parameter. this is so we do not create a device quite yet, because we want to make sure that this method succeeds before we create the device. if it succeeds, we know we have an adapter (GPU) that supports feature level 11.
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
DXGI_MODE_DESC backBufferDesc = {}; 
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

// command lists are created in the recording state. our main loop will set it up for recording again so close it now
commandList->Close();
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
	{ "POSITION", 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, 0, D3D12_INPUT_CLASSIFICATION_PER_VERTEX_DATA, 0 }
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

// create the pso
hr = device->CreateGraphicsPipelineState(&psoDesc, IID_PPV_ARGS(&pipelineStateObject));
if (FAILED(hr))
{
	return false;
}

```
#### 12. Create Vertex Buffer
##### 12.1 Create Vertex Buffer
```cpp
// Create vertex buffer

// a triangle
Vertex vList[] = {
	{ { 0.0f, 0.5f, 0.5f } },
	{ { 0.5f, -0.5f, 0.5f } },
	{ { -0.5f, -0.5f, 0.5f } },
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
	D3D12_RESOURCE_STATE_COPY_DEST, // we will start this heap in the copy destination state since we will copy data from the upload heap to this heap
	nullptr, // optimized clear value must be null for this type of resource. used for render targets and depth/stencil buffers
	IID_PPV_ARGS(&vertexBuffer));

// we can give resource heaps a name so when we debug with the graphics debugger we know what resource we are looking at
vertexBuffer->SetName(L"Vertex Buffer Resource Heap");
```
##### 12.2 Create Upload Heap
```cpp
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
```
##### 12.3 Store Vertex buffer in Upload Heap

###### 12.3.1 Create and Update Sub resources
```cpp
// store vertex buffer in upload heap
D3D12_SUBRESOURCE_DATA vertexData = {};
vertexData.pData = reinterpret_cast<BYTE*>(vList); // pointer to our vertex array
vertexData.RowPitch = vBufferSize; // size of all our triangle vertex data
vertexData.SlicePitch = vBufferSize; // also the size of our triangle vertex data

```
###### 12.3.2 Create Barrier and execute command List for buffer
```cpp
// we are now creating a command with the command list to copy the data from
// the upload heap to the default heap
UpdateSubresources(commandList, vertexBuffer, vBufferUploadHeap, 0, 0, 1, &vertexData);
// transition the vertex buffer data from copy destination state to vertex buffer state
commandList->ResourceBarrier(1, &CD3DX12_RESOURCE_BARRIER::Transition(vertexBuffer, D3D12_RESOURCE_STATE_COPY_DEST, D3D12_RESOURCE_STATE_VERTEX_AND_CONSTANT_BUFFER));

// Now we execute the command list to upload the initial assets (triangle data)
commandList->Close();
ID3D12CommandList* ppCommandLists[] = { commandList };
commandQueue->ExecuteCommandLists(_countof(ppCommandLists), ppCommandLists);
```
###### 12.3.3 Update Fence As we executed Command List
```cpp
// increment the fence value now, otherwise the buffer might not be uploaded by the time we start drawing
fenceValue[frameIndex]++;
hr = commandQueue->Signal(fence[frameIndex], fenceValue[frameIndex]);
if (FAILED(hr))
{
	Running = false;
}
```

###### 12.3.4 Update Buffer View
```cpp
// create a vertex buffer view for the triangle. We get the GPU memory address to the vertex pointer using the GetGPUVirtualAddress() method
vertexBufferView.BufferLocation = vertexBuffer->GetGPUVirtualAddress();
vertexBufferView.StrideInBytes = sizeof(Vertex);
vertexBufferView.SizeInBytes = vBufferSize;
```
#### 13. Fill out the ViewPort
```cpp
// Fill out the Viewport
viewport.TopLeftX = 0;
viewport.TopLeftY = 0;
viewport.Width = Width;
viewport.Height = Height;
viewport.MinDepth = 0.0f;
viewport.MaxDepth = 1.0f;
```
#### 14. Fill out the Scissor Rect
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

	// set the render target for the output merger stage (the output of the pipeline)
	commandList->OMSetRenderTargets(1, &rtvHandle, FALSE, nullptr);

	// Clear the render target by using the ClearRenderTargetView command
	const float clearColor[] = { 0.0f, 0.2f, 0.4f, 1.0f };
	commandList->ClearRenderTargetView(rtvHandle, clearColor, 0, nullptr);

	// draw triangle
	commandList->SetGraphicsRootSignature(rootSignature); // set the root signature
	commandList->RSSetViewports(1, &viewport); // set the viewports
	commandList->RSSetScissorRects(1, &scissorRect); // set the scissor rects
	commandList->IASetPrimitiveTopology(D3D_PRIMITIVE_TOPOLOGY_TRIANGLELIST); // set the primitive topology
	commandList->IASetVertexBuffers(0, 1, &vertexBufferView); // set the vertex buffer (using the vertex buffer view)
	commandList->DrawInstanced(3, 1, 0, 0); // finally draw 3 vertices (draw the triangle)

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
}
```
---
date: 17-February-2024
Links: https://www.braynzarsoft.net/viewtutorial/q16390-03-initializing-directx-12
Code: BryanZar Tutorial 01
---

# Overview
1. InitD3D
2. Render
3. Cleanup
	
# 1. InitD3D
## Functional Overview
1. Create D3D12 Device
2. Create Direct Command Queue
3. Create Swap Chain
4. Create Back Buffers (Render Target Views) and its Descriptor Heap
5. Create Command Allocators
6. Create Command List
7. Create Fence and Fence Event
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

//Temporary Data
IDXGIFactory4* dxgiFactory;
IDXGIAdapter1* adapter;
IDXGISwapChain* tempSwapChain;

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
hr = device->CreateCommandList(0, D3D12_COMMAND_LIST_TYPE_DIRECT, commandAllocator[0], NULL, IID_PPV_ARGS(&commandList));
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

	// swap the current rtv buffer index so we draw on the correct buffer
	frameIndex = swapChain->GetCurrentBackBufferIndex();
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
	hr = commandList->Reset(commandAllocator[frameIndex], NULL);
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
## Code
### 1. Cleanup All The resources
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
}
```
---
date: 17-April-2024
---

# How do we create Descriptors and Access it

## Resources and Descriptors and its Binding

In DX12 There are 2 Concepts 
1. Resources (Buffers, Textures etc..) All are ID3D12Resources now in DX12. 
2. Resource View aka. Descriptors. (Mention how to interpret and use resources)

Resource Binding is Activity on Managing Resource vs Descriptors

Now we have questions 

### 1. What is Descriptors

Descriptors or views (64bit)(Normally) is a structure contains information about Resources and its interpretation. Its seperate object. So GPU can easily interpret and use Resources.

### 2. Where does Descriptor Live (Heap) and why do we put it there.

Descriptor lives in Heap. The Heap is called Descriptor Heap. Either we place descriptor directly in heap or we have CopyDescriptor functionality.

### 3. What is Descriptor Heap Types

we can Categorize into based on Shader can View it or Not 
1. **Shader Visibile Descriptor Heaps (its single heap contain these views)
	1. UnOrdered Access View (UAV)
	2. Shader Resource View (SRV)
	3. Constant Buffer View (CBV)
2. **Non Shader Visible Descriptor Heaps
	1. Render Target View Heap (RTV)
	2. Depth Stencil View Heap (DSV)
3. **Heapless Descriptors / Transparent Descriptors / No Heaps
	1. VBV (Vertex Buffer View)
	2. IBV (Index Buffer View)
	3. SOV (Stream Output View)
	4. Descriptors directly allocated on RootSignature/Root Parametes.

### 4. How do we create Descriptors
1. We Create Resources / Get Resources from Somewhere
2. Create Views using Create_View functions which sometimes it directly allocates to Heap. Sometimes you do it manually etc.. it Depends

### 5. How do we use Descriptors 

Each DescriptorHeaps have method
1. GetCPUDescriptorHandleForHeapStart
2. GetGPUDescriptorHandleForHeapStart
from that we can use Index which is got by GetDescriptorHandleIncrementSize Method.

With these 2 information we can access direct Resource Descriptors in CPU.


Each Descriptors have its own Size we can get by 
```cpp
mDescriptorSize = md3dDevice->GetDescriptorHandleIncrementSize(D3D12_DESCRIPTOR_HEAP_TYPE_);
```

Create Descriptors Handle from Queue. (Sample RTV) almost same for others we use d3dx12.h utils
```cpp
	CD3DX12_CPU_DESCRIPTOR_HANDLE rtvHeapHandle(mRtvHeap->GetCPUDescriptorHandleForHeapStart());
	for (UINT i = 0; i < SwapChainBufferCount; i++)
	{
		ThrowIfFailed(mSwapChain->GetBuffer(i, IID_PPV_ARGS(&mSwapChainBuffer[i])));
		md3dDevice->CreateRenderTargetView(mSwapChainBuffer[i].Get(), nullptr, rtvHeapHandle);
		rtvHeapHandle.Offset(1, mRtvDescriptorSize);
	}
```

This Get Buffer Resource from SwapChain and Creates RTV Descriptors and Allocates to RTV Heap.

Below gives example on Depth Stencil View 
```cpp
 ThrowIfFailed(md3dDevice->CreateCommittedResource(
     &CD3DX12_HEAP_PROPERTIES(D3D12_HEAP_TYPE_DEFAULT),
		D3D12_HEAP_FLAG_NONE,
     &depthStencilDesc,
		D3D12_RESOURCE_STATE_COMMON,
     &optClear,
     IID_PPV_ARGS(mDepthStencilBuffer.GetAddressOf())));

 // Create descriptor to mip level 0 of entire resource using the format of the resource.
	D3D12_DEPTH_STENCIL_VIEW_DESC dsvDesc;
	dsvDesc.Flags = D3D12_DSV_FLAG_NONE;
	dsvDesc.ViewDimension = D3D12_DSV_DIMENSION_TEXTURE2D;
	dsvDesc.Format = mDepthStencilFormat;
	dsvDesc.Texture2D.MipSlice = 0;
 md3dDevice->CreateDepthStencilView(mDepthStencilBuffer.Get(), &dsvDesc, DepthStencilView());
```
```cpp
D3D12_CPU_DESCRIPTOR_HANDLE D3DApp::DepthStencilView()const
{
	return mDsvHeap->GetCPUDescriptorHandleForHeapStart();
}
```


# Summary
1. Create Resources (Buffers, Constants, Textures ) etc..
2. Create Respective Descriptors (RTV, CBV, VBV,DSV)
3. Allocate in Respective Heaps ({rtv: RTV, cbv: SRV, UAV, CBV, noheap: VBV})
4. Create Root Signature where we collect descriptors in (DescriptorTables, Directly)
5. Build PSO with rootSignature
6. In Pipeline set Heaps/RootSignature again
7. Apply Resource Barriers for Resources (not Descriptors)
8. Draw
9. ReSet Barriers
10. Set Fence to identify work are done in Queue.
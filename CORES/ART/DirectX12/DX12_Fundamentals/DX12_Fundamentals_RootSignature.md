# What is root Signature and whats its significance

Root Signature is called Application Binding Area. Here we bind Descriptors which is involved on Application.

So We Create RootSignature with list of Root Parameters 

Root Parameters contains either
1. Descriptor Table (Range in Descriptor Heap) (UAV/SRV/CBV)
2. Descriptors Directly
3. Small Root constants 

This is bound in 
1. Pipeline State object 
```cpp
D3D12_GRAPHICS_PIPELINE_STATE_DESC psoDesc;
psoDesc.pRootSignature = mRootSignature.Get();
```
2. In Direct Pipeline itself using (SetGraphicsRootSignature)

```cpp
  ID3D12DescriptorHeap* descriptorHeaps[] = { mCbvHeap.Get() };
  mCommandList->SetDescriptorHeaps(_countof(descriptorHeaps), descriptorHeaps); 
  mCommandList->SetGraphicsRootSignature(mRootSignature.Get());
```

### 1. Why RootSignature is Set 2 times
We use 2 times so dx can verify as well. SetGraphicsRootSignature is final effect even we set different in PSO. (dont do that unless required)

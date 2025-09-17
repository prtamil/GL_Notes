---
date: 8-February-2024
---

# DataStructure Overview

## 1. Device and Device Contexts
ID3D11Device1* d3d11Device;   (living through out program)
ID3D11DeviceContext1* d3d11DeviceContext; (living through out program)
## 2. Debug Devices
ID3D11Debug* d3dDebug; (shortly lived)
ID3D11InfoQueue* d3dInfoQueue; (shortly lived)

## 3. SwapChain
IDXGISwapChain1* d3d11SwapChain; (living through out program)
IDXGIFactory2* dxgiFactory;  (Released after creating d3d11SwapChain)
IDXGIAdapter* dxgiAdapter;   (Released after creating d3d11SwapChain)

## 4. Framebuffer RenderTarget
ID3D11RenderTargetView* d3d11FrameBufferView; (living through out program)
ID3D11Texture2D* d3d11FrameBuffer; (releases shortly after creating framebufferview)

## 5. Vertex Shader and Pixel Shaders
ID3DBlob* vsBlob;  (temp)
ID3D11VertexShader* vertexShader; (living through out program)
ID3DBlob* shaderCompileErrorsBlob; (temp)

ID3D11PixelShader* pixelShader; (living through out program)
ID3DBlob* psBlob;(temp)
## 6. Input LayOut and Vertex Buffers
ID3D11InputLayout* inputLayout; (living through out program)
ID3D11Buffer* vertexBuffer; (living through out program)

# Code Overview
## 1. Code for Device and DeviceContext
```cpp
// Create D3D11 Device and Context
ID3D11Device1* d3d11Device;
ID3D11DeviceContext1* d3d11DeviceContext;
{
    ID3D11Device* baseDevice;
    ID3D11DeviceContext* baseDeviceContext;
    D3D_FEATURE_LEVEL featureLevels[] = { D3D_FEATURE_LEVEL_11_0 };
    UINT creationFlags = D3D11_CREATE_DEVICE_BGRA_SUPPORT;
    #if defined(DEBUG_BUILD)
    creationFlags |= D3D11_CREATE_DEVICE_DEBUG;
    #endif

    HRESULT hResult = D3D11CreateDevice(0, D3D_DRIVER_TYPE_HARDWARE, 
                                        0, creationFlags, 
                                        featureLevels, ARRAYSIZE(featureLevels), 
                                        D3D11_SDK_VERSION, &baseDevice, 
                                        0, &baseDeviceContext);
    if(FAILED(hResult)){
        MessageBoxA(0, "D3D11CreateDevice() failed", "Fatal Error", MB_OK);
        return GetLastError();
    }
    
    // Get 1.1 interface of D3D11 Device and Context
    //create D3D11CreateDevice gives ID3D11Device to get DX11.1 device query from it to get ID3D11Device1
    //Same for Context
    hResult = baseDevice->QueryInterface(__uuidof(ID3D11Device1), (void**)&d3d11Device);
    assert(SUCCEEDED(hResult));
    baseDevice->Release();

    hResult = baseDeviceContext->QueryInterface(__uuidof(ID3D11DeviceContext1), (void**)&d3d11DeviceContext);
    assert(SUCCEEDED(hResult));
    baseDeviceContext->Release();
}
```



### D3D11CreateDevice function
```cpp
HRESULT D3D11CreateDevice(
  [in, optional]  IDXGIAdapter            *pAdapter,
                  D3D_DRIVER_TYPE         DriverType,
                  HMODULE                 Software,
                  UINT                    Flags,
  [in, optional]  const D3D_FEATURE_LEVEL *pFeatureLevels,
                  UINT                    FeatureLevels,
                  UINT                    SDKVersion,  //D3D11_SDK_VERSION
  [out, optional] ID3D11Device            **ppDevice,
  [out, optional] D3D_FEATURE_LEVEL       *pFeatureLevel,
  [out, optional] ID3D11DeviceContext     **ppImmediateContext
);
```

#### D3D_DRIVER_TYPE 
```cpp
typedef enum D3D_DRIVER_TYPE {
  D3D_DRIVER_TYPE_UNKNOWN = 0,
  D3D_DRIVER_TYPE_HARDWARE,
  D3D_DRIVER_TYPE_REFERENCE,
  D3D_DRIVER_TYPE_NULL,
  D3D_DRIVER_TYPE_SOFTWARE,
  D3D_DRIVER_TYPE_WARP
} ;
```
#### UINT flags

```cpp
typedef enum D3D11_CREATE_DEVICE_FLAG {
  D3D11_CREATE_DEVICE_SINGLETHREADED = 0x1,
  D3D11_CREATE_DEVICE_DEBUG = 0x2,
  D3D11_CREATE_DEVICE_SWITCH_TO_REF = 0x4,
  D3D11_CREATE_DEVICE_PREVENT_INTERNAL_THREADING_OPTIMIZATIONS = 0x8,
  D3D11_CREATE_DEVICE_BGRA_SUPPORT = 0x20,
  D3D11_CREATE_DEVICE_DEBUGGABLE = 0x40,
  D3D11_CREATE_DEVICE_PREVENT_ALTERING_LAYER_SETTINGS_FROM_REGISTRY = 0x80,
  D3D11_CREATE_DEVICE_DISABLE_GPU_TIMEOUT = 0x100,
  D3D11_CREATE_DEVICE_VIDEO_SUPPORT = 0x800
} ;


```

#### D3D_FEATURE_LEVEL
```cpp
typedef enum D3D_FEATURE_LEVEL {
  D3D_FEATURE_LEVEL_1_0_GENERIC,
  D3D_FEATURE_LEVEL_1_0_CORE,
  D3D_FEATURE_LEVEL_9_1,
  D3D_FEATURE_LEVEL_9_2,
  D3D_FEATURE_LEVEL_9_3,
  D3D_FEATURE_LEVEL_10_0,
  D3D_FEATURE_LEVEL_10_1,
  D3D_FEATURE_LEVEL_11_0,
  D3D_FEATURE_LEVEL_11_1,
  D3D_FEATURE_LEVEL_12_0,
  D3D_FEATURE_LEVEL_12_1,
  D3D_FEATURE_LEVEL_12_2
} ;
```

## 2. Code for Debug Devices
```cpp
#ifdef DEBUG_BUILD
    // Set up debug layer to break on D3D11 errors
    ID3D11Debug *d3dDebug = nullptr;
    d3d11Device->QueryInterface(__uuidof(ID3D11Debug), (void**)&d3dDebug);
    if (d3dDebug)
    {
        ID3D11InfoQueue *d3dInfoQueue = nullptr;
        if (SUCCEEDED(d3dDebug->QueryInterface(__uuidof(ID3D11InfoQueue), (void**)&d3dInfoQueue)))
        {
            d3dInfoQueue->SetBreakOnSeverity(D3D11_MESSAGE_SEVERITY_CORRUPTION, true);
            d3dInfoQueue->SetBreakOnSeverity(D3D11_MESSAGE_SEVERITY_ERROR, true);
            d3dInfoQueue->Release();
        }
        d3dDebug->Release();
    }
#endif

```

## 3. Code for Swap Chain
```cpp
// Create Swap Chain
IDXGISwapChain1* d3d11SwapChain;
{
    // Get DXGI Factory (needed to create Swap Chain)
    IDXGIFactory2* dxgiFactory;
    {
        IDXGIDevice1* dxgiDevice;
        HRESULT hResult = d3d11Device->QueryInterface(__uuidof(IDXGIDevice1), (void**)&dxgiDevice);
        assert(SUCCEEDED(hResult));

        IDXGIAdapter* dxgiAdapter;
        hResult = dxgiDevice->GetAdapter(&dxgiAdapter);
        assert(SUCCEEDED(hResult));
        dxgiDevice->Release();

        DXGI_ADAPTER_DESC adapterDesc;
        dxgiAdapter->GetDesc(&adapterDesc);

        OutputDebugStringA("Graphics Device: ");
        OutputDebugStringW(adapterDesc.Description);

        hResult = dxgiAdapter->GetParent(__uuidof(IDXGIFactory2), (void**)&dxgiFactory);
        assert(SUCCEEDED(hResult));
        dxgiAdapter->Release();
    }
    
    DXGI_SWAP_CHAIN_DESC1 d3d11SwapChainDesc = {};
    d3d11SwapChainDesc.Width = 0; // use window width
    d3d11SwapChainDesc.Height = 0; // use window height
    d3d11SwapChainDesc.Format = DXGI_FORMAT_B8G8R8A8_UNORM_SRGB;
    d3d11SwapChainDesc.SampleDesc.Count = 1;
    d3d11SwapChainDesc.SampleDesc.Quality = 0;
    d3d11SwapChainDesc.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT;
    d3d11SwapChainDesc.BufferCount = 2;
    d3d11SwapChainDesc.Scaling = DXGI_SCALING_STRETCH;
    d3d11SwapChainDesc.SwapEffect = DXGI_SWAP_EFFECT_DISCARD;
    d3d11SwapChainDesc.AlphaMode = DXGI_ALPHA_MODE_UNSPECIFIED;
    d3d11SwapChainDesc.Flags = 0;

    HRESULT hResult = dxgiFactory->CreateSwapChainForHwnd(d3d11Device, hwnd, &d3d11SwapChainDesc, 0, 0, &d3d11SwapChain);
    assert(SUCCEEDED(hResult));

    dxgiFactory->Release();
}
```

### CreateSwapChainForHwnd
```cpp
HRESULT CreateSwapChainForHwnd(
  [in]           IUnknown                              *pDevice,
  [in]           HWND                                  hWnd,
  [in]           const DXGI_SWAP_CHAIN_DESC1           *pDesc,
  [in, optional] const DXGI_SWAP_CHAIN_FULLSCREEN_DESC *pFullscreenDesc,
  [in, optional] IDXGIOutput                           *pRestrictToOutput,
  [out]          IDXGISwapChain1                       **ppSwapChain
);
```

### DXGI_SWAP_CHAIN_DESC
![[dxgi_swap_chain.png]]
### DXGI_SWAP_CHAIN_FULLSCREEN_DESC
```cpp
typedef struct DXGI_SWAP_CHAIN_FULLSCREEN_DESC {
  DXGI_RATIONAL            RefreshRate;
  DXGI_MODE_SCANLINE_ORDER ScanlineOrdering;
  DXGI_MODE_SCALING        Scaling;
  BOOL                     Windowed;
} DXGI_SWAP_CHAIN_FULLSCREEN_DESC;
```

## 4. Code for Create Render Target / Frame Buffer
   ```cpp
      // Create Framebuffer Render Target
   ID3D11RenderTargetView* d3d11FrameBufferView;
   {
       ID3D11Texture2D* d3d11FrameBuffer;
       HRESULT hResult = d3d11SwapChain->GetBuffer(0, __uuidof(ID3D11Texture2D), (void**)&d3d11FrameBuffer);
       assert(SUCCEEDED(hResult));

       hResult = d3d11Device->CreateRenderTargetView(d3d11FrameBuffer, 0, &d3d11FrameBufferView);
       assert(SUCCEEDED(hResult));
       d3d11FrameBuffer->Release();
   }
```
### CreateRenderTargetView
```cpp
HRESULT CreateRenderTargetView(
  [in]            ID3D11Resource                      *pResource,
  [in, optional]  const D3D11_RENDER_TARGET_VIEW_DESC *pDesc,
  [out, optional] ID3D11RenderTargetView              **ppRTView
);
```

### D3D11_RENDER_TARGET_VIEW_DESC
```cpp
typedef struct D3D11_RENDER_TARGET_VIEW_DESC {
  DXGI_FORMAT         Format;
  D3D11_RTV_DIMENSION ViewDimension;
  union {
    D3D11_BUFFER_RTV        Buffer;
    D3D11_TEX1D_RTV         Texture1D;
    D3D11_TEX1D_ARRAY_RTV   Texture1DArray;
    D3D11_TEX2D_RTV         Texture2D;
    D3D11_TEX2D_ARRAY_RTV   Texture2DArray;
    D3D11_TEX2DMS_RTV       Texture2DMS;
    D3D11_TEX2DMS_ARRAY_RTV Texture2DMSArray;
    D3D11_TEX3D_RTV         Texture3D;
  };
} D3D11_RENDER_TARGET_VIEW_DESC;
```
## 5. Code for Creating Vertex and Pixel Shaders
```cpp
// Create Vertex Shader
ID3DBlob* vsBlob;
ID3D11VertexShader* vertexShader;
{
    ID3DBlob* shaderCompileErrorsBlob;
    HRESULT hResult = D3DCompileFromFile(L"shaders.hlsl", nullptr, nullptr, "vs_main", "vs_5_0", 0, 0, &vsBlob, &shaderCompileErrorsBlob);
    if(FAILED(hResult))
    {
        const char* errorString = NULL;
        if(hResult == HRESULT_FROM_WIN32(ERROR_FILE_NOT_FOUND))
            errorString = "Could not compile shader; file not found";
        else if(shaderCompileErrorsBlob){
            errorString = (const char*)shaderCompileErrorsBlob->GetBufferPointer();
            shaderCompileErrorsBlob->Release();
        }
        MessageBoxA(0, errorString, "Shader Compiler Error", MB_ICONERROR | MB_OK);
        return 1;
    }

    hResult = d3d11Device->CreateVertexShader(vsBlob->GetBufferPointer(), vsBlob->GetBufferSize(), nullptr, &vertexShader);
    assert(SUCCEEDED(hResult));
}

// Create Pixel Shader
ID3D11PixelShader* pixelShader;
{
    ID3DBlob* psBlob;
    ID3DBlob* shaderCompileErrorsBlob;
    HRESULT hResult = D3DCompileFromFile(L"shaders.hlsl", nullptr, nullptr, "ps_main", "ps_5_0", 0, 0, &psBlob, &shaderCompileErrorsBlob);
    if(FAILED(hResult))
    {
        const char* errorString = NULL;
        if(hResult == HRESULT_FROM_WIN32(ERROR_FILE_NOT_FOUND))
            errorString = "Could not compile shader; file not found";
        else if(shaderCompileErrorsBlob){
            errorString = (const char*)shaderCompileErrorsBlob->GetBufferPointer();
            shaderCompileErrorsBlob->Release();
        }
        MessageBoxA(0, errorString, "Shader Compiler Error", MB_ICONERROR | MB_OK);
        return 1;
    }

    hResult = d3d11Device->CreatePixelShader(psBlob->GetBufferPointer(), psBlob->GetBufferSize(), nullptr, &pixelShader);
    assert(SUCCEEDED(hResult));
    psBlob->Release();
}
```
## 6. Code for Input Layout and Vertex Buffers
```cpp
// Create Input Layout
ID3D11InputLayout* inputLayout;
{
    D3D11_INPUT_ELEMENT_DESC inputElementDesc[] =
    {
        { "POS", 0, DXGI_FORMAT_R32G32_FLOAT, 0, 0, D3D11_INPUT_PER_VERTEX_DATA, 0 },
        { "COL", 0, DXGI_FORMAT_R32G32B32A32_FLOAT, 0, D3D11_APPEND_ALIGNED_ELEMENT, D3D11_INPUT_PER_VERTEX_DATA, 0 }
    };

    HRESULT hResult = d3d11Device->CreateInputLayout(inputElementDesc, ARRAYSIZE(inputElementDesc), vsBlob->GetBufferPointer(), vsBlob->GetBufferSize(), &inputLayout);
    assert(SUCCEEDED(hResult));
    vsBlob->Release();
}

// Create Vertex Buffer
ID3D11Buffer* vertexBuffer;
UINT numVerts;
UINT stride;
UINT offset;
{
    float vertexData[] = { // x, y, r, g, b, a
        0.0f,  0.5f, 0.f, 1.f, 0.f, 1.f,
        0.5f, -0.5f, 1.f, 0.f, 0.f, 1.f,
        -0.5f, -0.5f, 0.f, 0.f, 1.f, 1.f
    };
    stride = 6 * sizeof(float);
    numVerts = sizeof(vertexData) / stride;
    offset = 0;

    D3D11_BUFFER_DESC vertexBufferDesc = {};
    vertexBufferDesc.ByteWidth = sizeof(vertexData);
    vertexBufferDesc.Usage     = D3D11_USAGE_IMMUTABLE;
    vertexBufferDesc.BindFlags = D3D11_BIND_VERTEX_BUFFER;

    D3D11_SUBRESOURCE_DATA vertexSubresourceData = { vertexData };

    HRESULT hResult = d3d11Device->CreateBuffer(&vertexBufferDesc, &vertexSubresourceData, &vertexBuffer);
    assert(SUCCEEDED(hResult));
}
```

### D3D11_INPUT_ELEMENT_DESC
```cpp
typedef struct D3D11_INPUT_ELEMENT_DESC {
  LPCSTR                     SemanticName;
  UINT                       SemanticIndex;
  DXGI_FORMAT                Format;
  UINT                       InputSlot;
  UINT                       AlignedByteOffset;
  D3D11_INPUT_CLASSIFICATION InputSlotClass;
  UINT                       InstanceDataStepRate;
} D3D11_INPUT_ELEMENT_DESC;
```

### D3D11_BUFFER_DESC
```cpp
typedef struct D3D11_BUFFER_DESC {
  UINT        ByteWidth;
  D3D11_USAGE Usage;
  UINT        BindFlags;
  UINT        CPUAccessFlags;
  UINT        MiscFlags;
  UINT        StructureByteStride;
} D3D11_BUFFER_DESC;
```

### D3D11_SUBRESOURCE_DATA
```cpp
typedef struct D3D11_SUBRESOURCE_DATA {
  const void *pSysMem;
  UINT       SysMemPitch;
  UINT       SysMemSlicePitch;
} D3D11_SUBRESOURCE_DATA;
```
## 7. Code for MainLoop and Putting All Resources to USE.
```cpp
// Main Loop
bool isRunning = true;
while(isRunning)
{
    MSG msg = {};
    while(PeekMessageW(&msg, 0, 0, 0, PM_REMOVE))
    {
        if(msg.message == WM_QUIT)
            isRunning = false;
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
    }

    if(global_windowDidResize)
    {
        d3d11DeviceContext->OMSetRenderTargets(0, 0, 0);
        d3d11FrameBufferView->Release();

        HRESULT res = d3d11SwapChain->ResizeBuffers(0, 0, 0, DXGI_FORMAT_UNKNOWN, 0);
        assert(SUCCEEDED(res));
        
        ID3D11Texture2D* d3d11FrameBuffer;
        res = d3d11SwapChain->GetBuffer(0, __uuidof(ID3D11Texture2D), (void**)&d3d11FrameBuffer);
        assert(SUCCEEDED(res));

        res = d3d11Device->CreateRenderTargetView(d3d11FrameBuffer, NULL,
                                                 &d3d11FrameBufferView);
        assert(SUCCEEDED(res));
        d3d11FrameBuffer->Release();

        global_windowDidResize = false;
    }

    FLOAT backgroundColor[4] = { 0.1f, 0.2f, 0.6f, 1.0f };
    d3d11DeviceContext->ClearRenderTargetView(d3d11FrameBufferView, backgroundColor);

    RECT winRect;
    GetClientRect(hwnd, &winRect);
    D3D11_VIEWPORT viewport = { 0.0f, 0.0f, (FLOAT)(winRect.right - winRect.left), (FLOAT)(winRect.bottom - winRect.top), 0.0f, 1.0f };
    d3d11DeviceContext->RSSetViewports(1, &viewport);

    d3d11DeviceContext->OMSetRenderTargets(1, &d3d11FrameBufferView, nullptr);

    d3d11DeviceContext->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
    d3d11DeviceContext->IASetInputLayout(inputLayout);
    d3d11DeviceContext->IASetVertexBuffers(0, 1, &vertexBuffer, &stride, &offset);

    d3d11DeviceContext->VSSetShader(vertexShader, nullptr, 0);
    d3d11DeviceContext->PSSetShader(pixelShader, nullptr, 0);


    d3d11DeviceContext->Draw(numVerts, 0);
    
    d3d11SwapChain->Present(1, 0);
}
```
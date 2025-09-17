---
date: 8-February-2024
---

```cpp
#include <d3d11.h>
#include <iostream>

// Define your texture dimensions
const int textureWidth = 256;
const int textureHeight = 256;

int main() {
    // Initialize DirectX objects
    ID3D11Device* device; // Assume this is initialized elsewhere
    ID3D11DeviceContext* deviceContext; // Assume this is initialized elsewhere
    
    // Create texture data (in this example, a simple 2D checkerboard pattern)
    unsigned char* textureData = new unsigned char[textureWidth * textureHeight * 4]; // RGBA format
    
    for (int y = 0; y < textureHeight; y++) {
        for (int x = 0; x < textureWidth; x++) {
            unsigned char color = ((x / 32 + y / 32) % 2) * 255; // Simple checkerboard pattern
            textureData[(y * textureWidth + x) * 4 + 0] = color; // R
            textureData[(y * textureWidth + x) * 4 + 1] = color; // G
            textureData[(y * textureWidth + x) * 4 + 2] = color; // B
            textureData[(y * textureWidth + x) * 4 + 3] = 255;   // A
        }
    }

    // Create texture description
    D3D11_TEXTURE2D_DESC textureDesc;
    ZeroMemory(&textureDesc, sizeof(textureDesc));
    textureDesc.Width = textureWidth;
    textureDesc.Height = textureHeight;
    textureDesc.MipLevels = 1;
    textureDesc.ArraySize = 1;
    textureDesc.Format = DXGI_FORMAT_R8G8B8A8_UNORM; // RGBA format
    textureDesc.SampleDesc.Count = 1;
    textureDesc.Usage = D3D11_USAGE_DEFAULT;
    textureDesc.BindFlags = D3D11_BIND_SHADER_RESOURCE;
    textureDesc.CPUAccessFlags = 0;
    textureDesc.MiscFlags = 0;

    // Create texture data
    D3D11_SUBRESOURCE_DATA initData;
    ZeroMemory(&initData, sizeof(initData));
    initData.pSysMem = textureData;
    initData.SysMemPitch = textureWidth * 4; // 4 bytes per pixel

    // Create texture
    ID3D11Texture2D* texture;
    HRESULT hr = device->CreateTexture2D(&textureDesc, &initData, &texture);
    if (FAILED(hr)) {
        std::cerr << "Failed to create texture" << std::endl;
        return 1;
    }

    // Create shader resource view description
    D3D11_SHADER_RESOURCE_VIEW_DESC srvDesc;
    ZeroMemory(&srvDesc, sizeof(srvDesc));
    srvDesc.Format = textureDesc.Format;
    srvDesc.ViewDimension = D3D11_SRV_DIMENSION_TEXTURE2D;
    srvDesc.Texture2D.MipLevels = 1;

    // Create shader resource view
    ID3D11ShaderResourceView* srv;
    hr = device->CreateShaderResourceView(texture, &srvDesc, &srv);
    if (FAILED(hr)) {
        std::cerr << "Failed to create shader resource view" << std::endl;
        return 1;
    }

    // Now you can use 'srv' in shaders for texture sampling

    // Don't forget to release resources when done
    srv->Release();
    texture->Release();
    delete[] textureData;

    return 0;
}

```

```hlsl
// Define a texture variable using the appropriate texture type
Texture2D myTexture;

// Define the sampler state
SamplerState mySamplerState {
    Filter = MIN_MAG_MIP_LINEAR;
    AddressU = Wrap;
    AddressV = Wrap;
};

// Define the input struct for the vertex shader
struct VSInput {
    float3 position : POSITION;
    float2 texCoord : TEXCOORD0;
};

// Define the output struct for the vertex shader
struct VSOutput {
    float4 position : SV_POSITION;
    float2 texCoord : TEXCOORD0;
};

// Vertex shader function
VSOutput VSMain(VSInput input) {
    VSOutput output;
    output.position = float4(input.position, 1.0);
    output.texCoord = input.texCoord;
    return output;
}

// Pixel shader function
float4 PSMain(VSOutput input) : SV_Target {
    // Sample the texture using the shader resource view (SRV)
    return myTexture.Sample(mySamplerState, input.texCoord);
}

```
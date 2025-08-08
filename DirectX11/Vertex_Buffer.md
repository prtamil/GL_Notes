---
date: 8-February-2024
---

```c
#include <d3d11.h>
#include <iostream>

// Define your vertex struct
struct Vertex {
    float x, y, z;
};

int main() {
    // Initialize DirectX objects
    ID3D11Device* device; // Assume this is initialized elsewhere
    ID3D11DeviceContext* deviceContext; // Assume this is initialized elsewhere
    
    // Create vertex data
    Vertex vertices[] = {
        {0.0f, 0.0f, 0.0f},
        {1.0f, 0.0f, 0.0f},
        {0.0f, 1.0f, 0.0f}
    };
    int numVertices = sizeof(vertices) / sizeof(Vertex);

    // Create a buffer description
    D3D11_BUFFER_DESC bufferDesc;
    ZeroMemory(&bufferDesc, sizeof(bufferDesc));
    bufferDesc.Usage = D3D11_USAGE_DEFAULT;
    bufferDesc.ByteWidth = sizeof(Vertex) * numVertices;
    bufferDesc.BindFlags = D3D11_BIND_VERTEX_BUFFER;
    bufferDesc.CPUAccessFlags = 0;
    bufferDesc.MiscFlags = 0;

    // Create a subresource data structure
    D3D11_SUBRESOURCE_DATA initData;
    ZeroMemory(&initData, sizeof(initData));
    initData.pSysMem = vertices;

    // Create the buffer
    ID3D11Buffer* vertexBuffer;
    HRESULT hr = device->CreateBuffer(&bufferDesc, &initData, &vertexBuffer);
    if (FAILED(hr)) {
        std::cerr << "Failed to create vertex buffer" << std::endl;
        return 1;
    }

    // Now you can use vertexBuffer in rendering

    // Don't forget to release the resources when done
    vertexBuffer->Release();
    
    return 0;
}

```
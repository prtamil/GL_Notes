```cpp
#pragma once
#include <GL/glew.h>
#include <iostream>

class FBOManager {
public:
    GLuint fbo = 0;
    GLuint colorTex = 0;
    GLuint depthRbo = 0;
    GLuint depthStencilRbo = 0;

    int width = 0;
    int height = 0;

    enum AttachmentType {
        COLOR_DEPTH,
        COLOR_DEPTH_STENCIL
    };

    bool setup(int w, int h, AttachmentType type) {
        width = w;
        height = h;

        glGenFramebuffers(1, &fbo);
        glBindFramebuffer(GL_FRAMEBUFFER, fbo);

        // --- Color Texture ---
        glGenTextures(1, &colorTex);
        glBindTexture(GL_TEXTURE_2D, colorTex);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, colorTex, 0);

        // --- Depth or Depth+Stencil Renderbuffer ---
        if (type == COLOR_DEPTH) {
            glGenRenderbuffers(1, &depthRbo);
            glBindRenderbuffer(GL_RENDERBUFFER, depthRbo);
            glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, width, height);
            glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depthRbo);
        }
        else if (type == COLOR_DEPTH_STENCIL) {
            glGenRenderbuffers(1, &depthStencilRbo);
            glBindRenderbuffer(GL_RENDERBUFFER, depthStencilRbo);
            glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, width, height);
            glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, depthStencilRbo);
        }

        // Check FBO completeness
        if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) {
            std::cerr << "[FBOManager] Framebuffer is not complete!" << std::endl;
            return false;
        }

        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        return true;
    }

    void bind() {
        glBindFramebuffer(GL_FRAMEBUFFER, fbo);
        glViewport(0, 0, width, height);
    }

    void unbind() {
        glBindFramebuffer(GL_FRAMEBUFFER, 0);
    }

    void clear(bool useStencil = false) {
        if (useStencil)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT);
        else
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    }

    void destroy() {
        if (colorTex) glDeleteTextures(1, &colorTex);
        if (depthRbo) glDeleteRenderbuffers(1, &depthRbo);
        if (depthStencilRbo) glDeleteRenderbuffers(1, &depthStencilRbo);
        if (fbo) glDeleteFramebuffers(1, &fbo);

        colorTex = 0;
        depthRbo = 0;
        depthStencilRbo = 0;
        fbo = 0;
    }
};

```

🧪 Usage Example in Your App

```cpp
FBOManager fboMain;

void setup() {
    glewInit(); // if needed
    fboMain.setup(800, 600, FBOManager::COLOR_DEPTH_STENCIL);  // Or COLOR_DEPTH
}

void draw() {
    fboMain.bind();
    fboMain.clear(true); // true = stencil also

    // Draw your scene here...

    fboMain.unbind();
}

```
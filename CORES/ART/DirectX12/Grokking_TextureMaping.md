
# Texture Pipeline
1. Object space location + {Projector Functions} => Texture Coordinates (UV)
2. Texture Coordinates + {Corresponder Functions (Wrap,border etc..)} => Texture Space
3. Texture Space + {Obtain value from Texture,(Filtering, Linear, Cubic, Anisotropic etc..)} => Texture Value 
4. Texture Value + {Value Transform Function} => Transformed Texture Value (Actual color etc..)

As Per DirectX11 We have following abstractions 

1. Texture Resource 
2. Sampler (Filtering, Corresponder Functions)
3. Shader Resource View (SRV)(read Texture/Buffer in Shaders)
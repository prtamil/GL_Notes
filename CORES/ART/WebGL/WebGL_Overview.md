# Objects in WebGL
## Types of Object in WebGL
Standard Objects
1. Buffer
2. Texture
3. RenderBuffer
4. Sampler
5. Query
Containers
1. VertexArray
2. FrameBuffer
3. TransformFeedBack
## Object Manipulation
Using Objects 
1. CreateObj
	1. createBuffer
	2. createTexture
	3. createRenderBuffer
	4. createSampler
	5. createVertexArray
	6. createQuery
	7. createFrameBuffer
	8. createTransformFeedback
2. Bind Obj
	1. bindBuffer
	2. bindTexture
	3. bindRenderBuffer
	4. bindSampler
	5. bindVertexArray
	6. bindFramebuffer
	7. bindTransformFeedback 
	8. (no bindQuery)
3. Delete Object

# How to send data to shaders
1. uniform => const buffer
2. attribute => Varying data

Set Attributes
gl.vertexAttrib*(attribLoc,values) //Directly Set Attrib on location
gl.VertexAttribPointer //How to read attrib from buffer

Set Uniform
gl.uniform* //Set uniform

# How WebGL programs work
Process
1. Compile Shaders and Make Program
2. Get location of attribute/uniform from shaders
3. use location and create buffers and textures 
4. bind objects and set data
5. Render it






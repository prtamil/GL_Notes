## Overview of Texture
```js
//ps
fragColor = texture(sampler, texCoord);
```
texture has 2 params
1. sampler
	1. intelligent wrapper for images
	2. decides on the color found at exact coordinate
	3. blends pixel colors if necessary
	4. your GPU can store lots of samples
	5. your shader can use several samplers at once

2. texcoord
	1. an xy point in image
	2. coordinates are named u and v (xy=uv=st)

## How to use UV coordinates
1. Measured in floating point numbers which is not pixels
2. between 0 and 1
3. [0,0] <- Bottom Left
4. [0.5, 0.5] <- Center
5. [1,1] <- Top Right
## How to Create Texture Objects Full Code
```js
const vertexShaderSrc = `#version 300 es
#pragma vscode_glsllint_stage: vert

layout(location=0) in vec4 aPosition;
layout(location=1) in vec2 aTexCoord;

out vec2 vTexCoord;
void main()
{
	vTexCoord = aTexCoord;
    gl_Position = aPosition;
}`;

const fragmentShaderSrc = `#version 300 es
#pragma vscode_glsllint_stage: frag

precision mediump float;

in vec2 vTexCoord;

uniform sampler2D uSampler;

out vec4 fragColor;

void main()
{
    fragColor = texture(uSampler, vTexCoord);
}`;

const gl = document.querySelector('canvas').getContext('webgl2');

const program = gl.createProgram();
{
	const vertexShader = gl.createShader(gl.VERTEX_SHADER);
	gl.shaderSource(vertexShader, vertexShaderSrc);
	gl.compileShader(vertexShader);
	gl.attachShader(program, vertexShader);

	const fragmentShader = gl.createShader(gl.FRAGMENT_SHADER);
	gl.shaderSource(fragmentShader, fragmentShaderSrc);
	gl.compileShader(fragmentShader);
	gl.attachShader(program, fragmentShader);

	gl.linkProgram(program);

	if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
		console.log(gl.getShaderInfoLog(vertexShader));
		console.log(gl.getShaderInfoLog(fragmentShader));
	}
}
gl.useProgram(program);

const vertexBufferData = new Float32Array([
	-.9,.9,
	-.9,-.9,
	.9,.9,
	.9,-.9,
]);

const texCoordBufferData = new Float32Array([
	0,1,
	0,0,
	1,1,
	1,0,
]);

const pixels = new Uint8Array([
	255,255,255,		230,25,75,			60,180,75,			255,225,25,
	67,99,216,			245,130,49,			145,30,180,			70,240,240,
	240,50,230,			188,246,12,			250,190,190,		0,128,128,
	230,190,255,		154,99,36,			255,250,200,		0,0,0,
]);

const pixelBuffer = gl.createBuffer();
gl.bindBuffer(gl.PIXEL_UNPACK_BUFFER, pixelBuffer);
gl.bufferData(gl.PIXEL_UNPACK_BUFFER, pixels, gl.STATIC_DRAW);

const vertexBuffer = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, vertexBuffer);
gl.bufferData(gl.ARRAY_BUFFER, vertexBufferData, gl.STATIC_DRAW);
gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
gl.enableVertexAttribArray(0);

const texCoordBuffer = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, texCoordBuffer);
gl.bufferData(gl.ARRAY_BUFFER, texCoordBufferData, gl.STATIC_DRAW);
gl.vertexAttribPointer(1, 2, gl.FLOAT, false, 0,0);
gl.enableVertexAttribArray(1);

const loadImage = () => new Promise(resolve => {
	const image = new Image();
	image.addEventListener('load', () => resolve(image));
	image.src = './image.png';
});

const run = async () => {
	const image = await loadImage();

	// gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);

	const textureSlot = 1;
	gl.activeTexture(gl.TEXTURE0 + textureSlot);
	gl.uniform1i(gl.getUniformLocation(program, 'uSampler'), textureSlot);

	const texture = gl.createTexture();
	gl.bindTexture(gl.TEXTURE_2D, texture);
	// gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, 500,300, 0, gl.RGB, gl.UNSIGNED_BYTE, image);
	// gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, 4,4, 0, gl.RGB, gl.UNSIGNED_BYTE, pixels);
	gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, 4,4, 0, gl.RGB, gl.UNSIGNED_BYTE, 0);

	gl.generateMipmap(gl.TEXTURE_2D);
	gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
	gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
	gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.MIRRORED_REPEAT);
	gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.MIRRORED_REPEAT);

	gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
};

run();
```

## What's Code Overview of Texture mapping in WebGL

```js
 const pixelTexture = gl.createTexture();
  gl.activeTexture(gl.TEXTURE0 + pixelTextureUnit); // Activate texture #0 (Sampler)
  gl.bindTexture(gl.TEXTURE_2D, pixelTexture);
  gl.texImage2D(
    gl.TEXTURE_2D,
    0,
    gl.RGB,
    4,
    4,
    0,
    gl.RGB,
    gl.UNSIGNED_BYTE,
    pixels
  );
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
```
## How does mipmap work
By Default webGL expects you to use mipmaps
We have two choices
1. set default mip map
```js
gl.generateMipmap(gl.TEXTURE_2D);
```
2. Override the default Settings so mipmaps aren't needed
```js
gl.generateMipmap(gl.TEXTURE_2D);
gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST)
gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR)
```

## What's image flip issue
JPG,PNG,GIF, WebP => Origin is at top
WEBGL Texture => Origin is at bottom

So we could flip things so jpg image could be in sync with WEBGL Texture
```js
gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true) 
//flips pixel y upside down so JPG could be sync with WEBGL Texure
```


## gl.texImage2D function detail
```js
texImage2D(
	target,  gl.TEXTURE_2D
	level,   0 (Level of mipmap)
	internalFormat,  gl.RGB  (colors of texture, used by fragment shader)
	width,    4   (source image)(provide pixel data yourself with array)
	height,   4
	border,   0
	format,   gl.RGB
	type,  gl.UNSIGNED_BYTE
	source
)
```

### Width and Height
1. Smaller than source image -> WebGL will trim pixels furtheest from origin
2. Bigger than source image -> texImage2D will fail and no texture will be updated.

### Sources
1. HTMLImageElement -> ```<img> or new Image```
2. HTMLVideoElement -> ```<video>```
3. HTMLCanvasElement -> ```<canvas>```
4. BitmapImage -> ```createImageBitmap()```
5. ImageData -> Canvas area contents
6. Pixel data -> typed Array
7. Pixel Buffer 

### Sources Pixel Data
#### Pixel Data => Data stored in arrays 
1. new Uint8Array
2. new Uint16Array
3. new Uint32Array
4. new Float32Array
```js
const pixels = new Uint8Array([
	255,255,255,		230,25,75,			60,180,75,			255,225,25,
	67,99,216,			245,130,49,			145,30,180,			70,240,240,
	240,50,230,			188,246,12,			250,190,190,		0,128,128,
	230,190,255,		154,99,36,			255,250,200,		0,0,0,
]);
//4x4 pixel data (src = pixels) Direct uint8Array
gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, 4,4, 0, gl.RGB, gl.UNSIGNED_BYTE, pixels);
```
#### Pixel Buffers using PIXEL_UNPACK_BUFFER
```js
const pixels = new Uint8Array([
	255,255,255,		230,25,75,			60,180,75,			255,225,25,
	67,99,216,			245,130,49,			145,30,180,			70,240,240,
	240,50,230,			188,246,12,			250,190,190,		0,128,128,
	230,190,255,		154,99,36,			255,250,200,		0,0,0,
]);


const pixelBuffer = gl.createBuffer();
gl.bindBuffer(gl.PIXEL_UNPACK_BUFFER, pixelBuffer);
gl.bufferData(gl.PIXEL_UNPACK_BUFFER, pixels, gl.STATIC_DRAW);
...
gl.texImage2D(
	gl.TEXTURE_2D,
	0,
	gl.RGB,
	256, //Width
	256, //Height
	0,
	gl.RGB,
	gl.UNSIGNED_BYTE, //Buffer Type
	0 //Pixel buffer offset
)

```

## What is pixel Buffer is it CPU or GPU

a Pixel Unpack Buffer (PUB) resides in GPU memory. It serves as a buffer object on the GPU side that allows efficient transfer of pixel data from the CPU to the GPU.

When you create and bind a Pixel Unpack Buffer, you're essentially allocating memory on the GPU where you can store pixel data. This data can then be efficiently accessed by the GPU when performing operations such as transferring data to textures using functions like glTexSubImage2D or glTexImage2D.

Using Pixel Unpack Buffers can help optimize data transfer between the CPU and GPU by decoupling the data upload from other OpenGL commands, allowing for asynchronous transfers and potentially better parallelization of tasks.

## What is sampler2D default value
its texture0.  

## What is texture Units and How to set Sampler2D/Texture Unit from JS Code 

its WebGL way to keep multiple textures 
texture unit is texture processor in GPU

Limitations
 1. webgl can use 32 textures  (MAX_COMBINED_TEXTURE_IMAGE_UNITS)
 2. upto 16 per fragment shader (MAX_TEXTURE_IMAGE_UNITS)


//Multi Texturing Shaders
```glsl
uniform sampler2D one; //TEXTURE0
uniform sampler2D two; //TEXTURE5

in vec2 vTexOne;
in vec2 vTexTwo;

void main() {
  fragColor = texture(one, vTexOne) * texture(two, vTexTwo);
}
```

```js
const oneSlot = 1;
const fiveSlot = 5;
gl.activeTexture(gl.TEXTURE0 + oneSlot);
gl.uniform1i(gl.getUniformLocation(program, 'one'), oneSlot);
gl.activeTexture(gl.TEXTURE0 + fiveSlot);
gl.uniform1i(gl.getUniformLocation(program, 'two'), fiveSlot);
```

Sampler get ActiveTexture Slot as input (TEXTURE0...TEXTURE15)
This can be used for multiple textures.
## What is relation between pixel unpack buffer and texture 
 Let's illustrate the relation between the pixel unpack buffer and textures in WebGL2 with some sample code.

1. **Creating and Using Pixel Unpack Buffer**:

```javascript
// Create and initialize a pixel unpack buffer
const pixelUnpackBuffer = gl.createBuffer();
gl.bindBuffer(gl.PIXEL_UNPACK_BUFFER, pixelUnpackBuffer);
const imageData = new Uint8Array([ /* pixel data */ ]);
gl.bufferData(gl.PIXEL_UNPACK_BUFFER, imageData, gl.STATIC_DRAW);

// Create and bind a texture
const texture = gl.createTexture();
gl.bindTexture(gl.TEXTURE_2D, texture);

// Set texture parameters and specify pixel data from the pixel unpack buffer
gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, width, height, 0, gl.RGBA, gl.UNSIGNED_BYTE, 0); // 0 specifies data comes from a buffer bound to PIXEL_UNPACK_BUFFER
```

we create a pixel unpack buffer, fill it with pixel data, then bind it when specifying pixel data for the texture using `texImage2D()`. This way, the data from the pixel unpack buffer is transferred to the texture.

2. **Directly Specifying Pixel Data into a Texture**:

```javascript
// Create and bind a texture
const texture = gl.createTexture();
gl.bindTexture(gl.TEXTURE_2D, texture);

// Set texture parameters and specify pixel data directly
gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
const imageData = new Uint8Array([ /* pixel data */ ]);
gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, width, height, 0, gl.RGBA, gl.UNSIGNED_BYTE, imageData);
```

we directly specify pixel data into the texture without using a pixel unpack buffer. This method is straightforward when you have the pixel data readily available.

Both methods achieve the same result of loading pixel data into a texture, but the first one utilizes a pixel unpack buffer for efficient data transfer and manipulation, while the second one directly specifies the pixel data.

## Example MultiTexture Code and Explain
```js
const vertexShaderSrc = `#version 300 es
#pragma vscode_glsllint_stage: vert

layout(location=0) in vec4 aPosition;
layout(location=1) in vec2 aTexCoord;

out vec2 vTexCoord;

void main()
{
	vTexCoord = aTexCoord;
    gl_Position = aPosition;
}`;

const fragmentShaderSrc = `#version 300 es
#pragma vscode_glsllint_stage: frag

precision mediump float;

in vec2 vTexCoord;

uniform sampler2D uPixelSampler;  //Texture Unit 1
uniform sampler2D uKittenSampler;  //Texture Unit 5

out vec4 fragColor;

void main()
{
    fragColor = texture(uPixelSampler, vTexCoord) * texture(uKittenSampler, vTexCoord);
}`;

const gl = document.querySelector("canvas").getContext("webgl2");

const program = gl.createProgram();
{
  const vertexShader = gl.createShader(gl.VERTEX_SHADER);
  gl.shaderSource(vertexShader, vertexShaderSrc);
  gl.compileShader(vertexShader);
  gl.attachShader(program, vertexShader);

  const fragmentShader = gl.createShader(gl.FRAGMENT_SHADER);
  gl.shaderSource(fragmentShader, fragmentShaderSrc);
  gl.compileShader(fragmentShader);
  gl.attachShader(program, fragmentShader);

  gl.linkProgram(program);

  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    console.log(gl.getShaderInfoLog(vertexShader));
    console.log(gl.getShaderInfoLog(fragmentShader));
  }
}
gl.useProgram(program);

const vertexBufferData = new Float32Array([-0.9, -0.9, 0.9, -0.9, 0, 0.9]);

const texCoordBufferData = new Float32Array([0, 0, 1, 0, 0.5, 1]);

const pixels = new Uint8Array([
  255, 255, 255, 230, 25, 75, 60, 180, 75, 255, 225, 25, 67, 99, 216, 245, 130,
  49, 145, 30, 180, 70, 240, 240, 240, 50, 230, 188, 246, 12, 250, 190, 190, 0,
  128, 128, 230, 190, 255, 154, 99, 36, 255, 250, 200, 0, 0, 0,
]);

const vertexBuffer = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, vertexBuffer);
gl.bufferData(gl.ARRAY_BUFFER, vertexBufferData, gl.STATIC_DRAW);
gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
gl.enableVertexAttribArray(0);

const texCoordBuffer = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, texCoordBuffer);
gl.bufferData(gl.ARRAY_BUFFER, texCoordBufferData, gl.STATIC_DRAW);
gl.vertexAttribPointer(1, 2, gl.FLOAT, false, 0, 0);
gl.enableVertexAttribArray(1);

// Note: In my video, the next 5 statements were in the `run()` function.
// For clarity, these really have nothing to do with the image and can be
// done any time after the WebGL program creation and before the draw call.
gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);

const pixelTextureUnit = 0;
const kittenTextureUnit = 5;

gl.uniform1i(gl.getUniformLocation(program, "uPixelSampler"), pixelTextureUnit);
gl.uniform1i(
  gl.getUniformLocation(program, "uKittenSampler"),
  kittenTextureUnit
);

const loadImage = () =>
  new Promise((resolve) => {
    const image = new Image();
    image.addEventListener("load", () => resolve(image));
    image.src = "./assets/kitten.jpg";
  });

const run = async () => {
  const image = await loadImage();

  const pixelTexture = gl.createTexture();
  gl.activeTexture(gl.TEXTURE0 + pixelTextureUnit); // Activate texture #0
  gl.bindTexture(gl.TEXTURE_2D, pixelTexture);
  gl.texImage2D(
    gl.TEXTURE_2D,
    0,
    gl.RGB,
    4,
    4,
    0,
    gl.RGB,
    gl.UNSIGNED_BYTE,
    pixels
  );
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);

  const kittenTexture = gl.createTexture();
  gl.activeTexture(gl.TEXTURE0 + kittenTextureUnit); // Activate texture #5
  // gl.activeTexture(gl.TEXTURE5);                   // Same value is activated
  gl.bindTexture(gl.TEXTURE_2D, kittenTexture);
  gl.texImage2D(
    gl.TEXTURE_2D,
    0,
    gl.RGBA,
    500,
    300,
    0,
    gl.RGBA,
    gl.UNSIGNED_BYTE,
    image
  );
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);

  gl.drawArrays(gl.TRIANGLES, 0, 3);
};

run();
```
## How to set Attributes
Set Attributes
gl.vertexAttrib*(attribLoc,values) //Directly Set Attrib on location
gl.VertexAttribPointer //How to read attrib from buffer

## How to Set Uniform
Set Uniform
gl.uniform* //Set uniform

## What if we dont set uniform in JS and declare it on shader
1. it still gets a default value.
2. ex: uniform vec4 color => (0,0,0,1)

What happens for sampler2D 
it will take texture0
## How Create Buffer and Bind it and use it 

```js
//We use Element Buffer as Example
let abuff = gl.createBuffer()
gl.bindBuffer(gl.ARRAY_BUFFER, abuff);
gl.bufferData(gl.ARRAY_BUFFER, vertData, gl.STATIC_DRAW)

let ebuff = gl.createBuffer()
gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, ebuff);
gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, elemData, gl.STATIC_DRAW)

gl.vertexAttribPointer(0) <- uses binded buffer, 
gl.vertexAttribPointer(1) <- uses binded buffer, 
gl.enableVertexAttribArray(0)
gl.enableVertexAttribArray(1)
gl.drawElements()
```

Object Create complete code 
```js
const vertexBuffer = gl.createBuffer()
gl.bindBuffer(gl.ARRAY_BUFFER, vertexBuffer);
gl.bufferData(gl.ARRAY_BUFFER, vertexBufferData, gl.STATIC_DRAW)
gl.vertexAttribPointer(0,2, gl.FLOAT, false,0,0)
gl.enableVertexAttribArray(0)
```


## How does vertex Array Object VAO work.

VAO changes when below changes
1. vertexAttribPointer
2. enableVertexAttribArray
3. disableVertexAttribArray
4. vertexAttribDivisor
5. bindBuffer(ELEMENTS_ARRAY_BUFFER)

VAO
1. Create update and Store a snapshot of vertex attribute Settings 
2. Snapshot of Views (Descriptors in DX12)
3. Saves Snapshot of our vertex settings and Restore snapshot at draw line
4. used in render loop
5. Saves from creating Same setttings for every draw call
6. Optional

with VAO what will be the initial state 
1. VAOs are created Empty
2. Attribures are disabled by default
3. Need to call enableVertexAttribArray everytime
4. We need to create complete VAO

Steps for Creating VAO
1. Fist bind current buffer So we can take snapshot of its attributes
2. Create and Bind VAO
3. declare vertexAttribPointer
4. Enable Vertex Attrib Array
5. Clear VAO by Unbinding by setting to null

Code for Creating VAO and binding attributes
```js

gl.bindBuffer(gl.ARRAY_BUFFER, buffer1);  //1. Fist bind current buffer 
const vao1 = gl.createVertexArray();      //2. Create and Bind VAO
gl.bindVertexArray(vao1);

gl.vertexAttribPointer(0, 1, gl.FLOAT, false, 24, 20);  //3. declare vertexAttribPointer
gl.vertexAttribPointer(1, 2, gl.FLOAT, false, 24, 0);
gl.vertexAttribPointer(2, 3, gl.FLOAT, false, 24, 8);

gl.enableVertexAttribArray(0);   //4. Enable Vertex Attrib Array
gl.enableVertexAttribArray(1);
gl.enableVertexAttribArray(2);

gl.bindVertexArray(null);  //5. Clear VAO by Unbinding by setting to null
```


Code for Using VAO in renderLoop
```js
	gl.bindVertexArray(vao1);
    gl.drawArrays(gl.POINTS, 0, 4);
    gl.bindVertexArray(vao2);
    gl.drawArrays(gl.POINTS, 0, 4);
    gl.bindVertexArray(null);
```

## VAO Sample Code 
```js
const vss1 = `#version 300 es
#pragma vscode_glsllint_stage: vert

layout(location=0) in float aPointSize;
layout(location=1) in vec2 aPosition;
layout(location=2) in vec3 aColor;

out vec3 vColor;

void main()
{
    vColor = aColor;
    gl_PointSize = aPointSize;
    gl_Position = vec4(aPosition, 0.0, 1.0);
}`;

const fss1 = `#version 300 es
#pragma vscode_glsllint_stage: frag

precision mediump float;

in vec3 vColor;

out vec4 fragColor;

void main()
{
    fragColor = vec4(vColor, 1.0);
}`;

const gl = document.querySelector('canvas').getContext('webgl2');

const program = gl.createProgram();

const vertexShader = gl.createShader(gl.VERTEX_SHADER);
gl.shaderSource(vertexShader, vss1);
gl.compileShader(vertexShader);
gl.attachShader(program, vertexShader);

const fragmentShader = gl.createShader(gl.FRAGMENT_SHADER);
gl.shaderSource(fragmentShader, fss1);
gl.compileShader(fragmentShader);
gl.attachShader(program, fragmentShader);

gl.linkProgram(program);

if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    console.log(gl.getShaderInfoLog(vertexShader));
    console.log(gl.getShaderInfoLog(fragmentShader));
    console.log(gl.getProgramInfoLog(program));
    throw new Error('failed to link');
}

gl.useProgram(program);

const data1 = new Float32Array([
    -.8,.6,         1,.75,.75,    125,
    -.3,.6,         0,.75,1,      32,
    .3,.6,          .5,1,.75,     75,
    .8,.6,          0,.75,.75,    9,
]);
const buffer1 = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, buffer1);
gl.bufferData(gl.ARRAY_BUFFER, data1, gl.STATIC_DRAW);

const vao1 = gl.createVertexArray();
gl.bindVertexArray(vao1);

gl.vertexAttribPointer(0, 1, gl.FLOAT, false, 24, 20);
gl.vertexAttribPointer(1, 2, gl.FLOAT, false, 24, 0);
gl.vertexAttribPointer(2, 3, gl.FLOAT, false, 24, 8);

gl.enableVertexAttribArray(0);
gl.enableVertexAttribArray(1);
gl.enableVertexAttribArray(2);

gl.bindVertexArray(null);

const data2 = new Float32Array([
    -.8,-.6,        .25,0,0,      25,
    -.3,-.6,        0,0,.25,      132,
    .3,-.6,         0,.25,0,      105,
    .6,-.6,         .25,0,.25,    90,
]);
const buffer2 = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, buffer2);
gl.bufferData(gl.ARRAY_BUFFER, data2, gl.STATIC_DRAW);

const vao2 = gl.createVertexArray();
gl.bindVertexArray(vao2);

gl.vertexAttribPointer(0, 1, gl.FLOAT, false, 24, 20);
gl.vertexAttribPointer(1, 2, gl.FLOAT, false, 24, 0);
gl.vertexAttribPointer(2, 3, gl.FLOAT, false, 24, 8);

gl.enableVertexAttribArray(0);
gl.enableVertexAttribArray(1);
gl.enableVertexAttribArray(2);

gl.bindVertexArray(null);

const draw = () => {
    gl.bindVertexArray(vao1);
    gl.drawArrays(gl.POINTS, 0, 4);
    gl.bindVertexArray(vao2);
    gl.drawArrays(gl.POINTS, 0, 4);
    gl.bindVertexArray(null);

    requestAnimationFrame(draw);
};

draw();
```

## Do i need to rebind a VAO to change my data
1. VAOs keeps reference to its buffers not data itself
2. They care where your buffers are 
3. Not what's in them
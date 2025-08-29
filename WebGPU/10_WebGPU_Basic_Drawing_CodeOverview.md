# WebGPU Code Overview
##   0. Start with Canvas
```html
<!doctype html>
<html>  
	<head>    
		<meta charset="utf-8">    
		<title>WebGPU Life</title>  
	</head>  
	<body>    
		<canvas width="512" height="512"></canvas>    
		<script type="module">      
			const canvas = document.querySelector("canvas");      // Your WebGPU code will begin here!    
		</script>  
	</body>
</html>
```
##  1. Get Device and Configure Canvas
```js
	 const canvas = document.querySelector("canvas");

      // WebGPU device initialization
      if (!navigator.gpu) {
        throw new Error("WebGPU not supported on this browser.");
      }
      //GPUAdapter
      const adapter = await navigator.gpu.requestAdapter();
      if (!adapter) {
        throw new Error("No appropriate GPUAdapter found.");
      }
      //GPUDevice
      const device = await adapter.requestDevice();

      // Canvas configuration
      //GPUCanvasContext
      const context = canvas.getContext("webgpu");
      const canvasFormat = navigator.gpu.getPreferredCanvasFormat();
      context.configure({
          device: device,
          format: canvasFormat,
      });
```
## 2.  Geometry
```js
	// Create a buffer with the vertices for a single cell.
      const vertices = new Float32Array([
      //   X,    Y
        -0.8, -0.8, // Triangle 1
         0.8, -0.8,
         0.8,  0.8,

        -0.8, -0.8, // Triangle 2
         0.8,  0.8,
        -0.8,  0.8,
      ]);
      //GPUBuffer
      const vertexBuffer = device.createBuffer({
        label: "Cell vertices",
        size: vertices.byteLength,
        usage: GPUBufferUsage.VERTEX | GPUBufferUsage.COPY_DST,
      });
      device.queue.writeBuffer(vertexBuffer, 0, vertices);
      
      //GPUVertexBufferLayout
      const vertexBufferLayout = {
        arrayStride: 8,
        attributes: [{
          format: "float32x2",
          offset: 0,
          shaderLocation: 0, // Position. Matches @location(0) in the @vertex shader.
        }],
      };
```
## 3. Create Shader Module
```js
	// Create the shader that will render the cells.
	  //GPUShaderModule
      const cellShaderModule = device.createShaderModule({
        label: "Cell shader",
        code: `
          @vertex
          fn vertexMain(@location(0) position: vec2f)
            -> @builtin(position) vec4f {
            return vec4f(position, 0, 1);
          }

          @fragment
          fn fragmentMain() -> @location(0) vec4f {
            return vec4f(1, 0, 0, 1);
          }
        `
      });
```
## 4. Create Render Pipeline
```js
// Create a pipeline that renders the cell.
     //GPURenderPipeline
      const cellPipeline = device.createRenderPipeline({
        label: "Cell pipeline",
        layout: "auto", //GPUPipelineLayout
        vertex: {
          module: cellShaderModule,
          entryPoint: "vertexMain",
          buffers: [vertexBufferLayout]
        },
        fragment: {
          module: cellShaderModule,
          entryPoint: "fragmentMain",
          targets: [{
            format: canvasFormat
          }]
        }
      });
```
## 5. Create Command Encoder with Render Pass
```js
	// Clear the canvas with a render pass
	 //GPUCommandEncoder
      const encoder = device.createCommandEncoder();
      //GPURenderPassEncoder
      const pass = encoder.beginRenderPass({
        colorAttachments: [{
          view: context.getCurrentTexture().createView(),
          loadOp: "clear",
          clearValue: { r: 0, g: 0, b: 0.4, a: 1.0 },
          storeOp: "store",
        }]
      });

      // Draw the square.
      pass.setPipeline(cellPipeline);
      pass.setVertexBuffer(0, vertexBuffer);
      pass.draw(vertices.length / 2);

      pass.end();
```
## 6. Submit Command to Queue
```js
        //GPUCommandBuffer  <- encoder.finish();
		device.queue.submit([encoder.finish()]);
```
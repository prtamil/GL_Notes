# Setting Normalized Coordinates and Fix Aspect Ratio.
## 1. Normalize FragCoordinates from 800x600 to 0 to 1
  ```cpp
  float2 uv = fragCoordinates/iResoultion.xy 
  //Main purpose is to convert from in 800w600h we need to convert to 0 to 1 on both side.
  //After this we will be using 0to1. 

/*
     (0,1)                 (1,1)    
      ┌─────────────────────┐       
      │                     │       
      │                     │       
      │                     │       
      │                     │       
      │         (0.5)       │       
      │                     │       
      │                     │       
      │                     │       
      │                     │       
      └─────────────────────┘       
    (0,0)                   (1,0)   
 
*/
```

## 2. Now center is 0.5 it is not good for calculation we need to recenter to (0,0) .
```cpp
//We can do this by 2 operation.
 //1. 
 uv = uv - 0.5; //(Shift 0.0 to center)(-0.5 to 0.5)
 //2. 
 uv = uv * 2.0;// (will get -1 to 1)
/*after that we will get below coordinates

  (1,-1)                (1,1)   
   ┌─────────────────────┐      
   │                     │      
   │                     │      
   │                     │      
   │                     │      
   │         (0,0)       │      
   │                     │      
   │                     │      
   │                     │      
   │                     │      
   └─────────────────────┘      
 (-1,-1)                 (-1,1) 

We can Shorthand this 2 steps into two steps */*
  float2 uv = fragCoordinates/iResoultion.xy ;
  uv = (uv - 0.5) * 2.0;;

//Again we further reduce to single step 

float2 uv = fragCoord/iResoultion.xy * 2.0 - 1.0;
   
```

## 3. Fix Aspect Ratio Issues So that image will look in same for different resolution
```cpp
//it can be done by multiplying uv.x into iResoulution ratio

uv.x *= (float)iResoulution.x / (float)iResolution.y;
//if not float integer will mess u up. HLSL will be integer, GLSL will be float. IDK

//Again we further reduce to single step
float2 uv = (fragCoord * 2.0 - iResoulution.xy) / iResoulution.y;

```

## 4. Proper 4 Steps deeply explained with Readable Code
```cpp
  float2 uv = fragCoordinates/iResoultion.xy 
  float aspect = (float)iResoulution.x / (float)iResolution.y;
  uv = uv - 0.5;  //Make 0 center
  uv = uv * 2.0;  //Make -1 to 1 on height and width;
  uv.x *= aspect;  //fix Aspect ratio. 
```
## 5. Shortcut and Optimized Code for Aspect ratio and -1 to 1 coordinates
```cpp
//1.
float2 uv = (fragCoord * 2.0 - iResoulution.xy) / iResoulution.y;
//2.
float2 uv = fragCoord - iResolution.xy*0.5;
         uv /= iResolution.y;

```
## 6. Below are list shortcuts to fix aspect ratio
```cpp
// Copyleft (C) 2021 Michaelangel007 aka Michael Pohoreski
//
// LESSON on apply aspect ratio to draw a circle without distortion with any resolution of canvas
// 0 Naive Draw circle at bottom left of canvas
// 1 Naive Draw circle at center
// 2 Naive Draw circle at center with correct aspect ratio so top/bottom touches canvas edge
// 3 Naive Draw circle at center with correct aspect ratio so left/right touches canvas edge
// 4 Naive Same as 2 but can hold left mouse down and scrub to change quantization level
// 5 Optimized Same as 2 but simpler and faster
// 6 Optimized Same as 3 but simpler and faster
#define LESSON 5

// How NOT to do aspect ratio correction
// * https://stackoverflow.com/questions/67039308/how-to-draw-a-circle-instead-of-an-ellipse-when-your-monitor-screen-resolution-i

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2  uv = fragCoord     / iResolution.xy;
    float AR = iResolution.x / iResolution.y;

#if LESSON == 1
    uv -= 0.5; // Move to center of canvas
#endif

#if LESSON == 2
    uv -= 0.5;
    uv.x *= AR; // Top/Bottom touch canvas edge
#endif

#if LESSON == 3
    uv -= 0.5;
    uv.y *= 1.0/AR; // Left/Right touch canvas edge (clipping is normal if width > height)
#endif

#if LESSON == 4 // quantize resolution
    float SCALE = (iMouse.z > 0.5) && (iMouse.x >= 0.0)
                ? 1.0 + floor(512.0 * iMouse.x / iResolution.x)
                : 0.5;
    fragCoord = round(fragCoord / SCALE) * SCALE;
    uv = fragCoord/iResolution.xy;
    uv -= 0.5;
    uv.x *= AR; // Top/Bottom touch canvas edge
#endif

#if LESSON == 5 // Simpler and Faster with correct aspect ratio so top/bottom touches canvas edge
    uv = fragCoord - iResolution.xy*0.5;
    uv /= iResolution.y;
#endif

#if LESSON == 6 // Simpler and Faster with correct aspect ratio so left/right touches canvas edge
    uv = fragCoord - iResolution.xy*0.5;
    uv /= iResolution.x;
#endif


    float g = dot(uv,uv);
    g = (g < 0.25)
      ? 1.0
      : 0.0;

    vec3 fg = vec3(0.0, 0.5, 1.0); // sky blue
    vec3 bg = vec3(1.0, 1.0, 1.0); // white
    fragColor = vec4( mix(bg,fg,g), 1.0);
}
```


ASCII graphics becomes powerful when you realize **characters themselves are pixels with different brightness**.  
Demo-scene programmers learned how to use this to fake **lighting, depth, and smooth gradients** even in very limited terminals.

Here are the **8 classic shading tricks** used in ASCII renderers, raymarchers, and terminal demos.

---

# 1. Brightness Gradient (Character Density)

Characters have **different ink density**.  
Some fill more pixels → appear darker.

Example gradient:

```
 .:-=+*#%@
```

Left → light  
Right → dark

Example shading:

```
     ....
   ..::::..
  .::----::.
  :--====--:
  -==++++==-
  ==++++++==
  +++****+++
  **######**
```

How renderers use it:

```
brightness = clamp(light, 0..1)

index = brightness * (len(shades)-1)
char  = shades[index]
```

Used in:

- raymarching
    
- sphere shading
    
- terrain rendering
    

This is **the most important ASCII shading trick**.

---

# 2. ASCII Dithering

Dithering simulates **intermediate brightness levels**.

Example:

```
50% gray:

# #
 # 
# #
 # 
```

Instead of one character, you alternate pixels.

Example:

```
light  = .
medium = .:
dark   = :#
```

Checkerboard patterns smooth gradients.

Classic dithering pattern:

```
. . .
 . .
. . .
```

Used when:

```
terminal colors are limited
```

Very common in **old-school demos**.

---

# 3. Subpixel Shading

Some characters represent **half blocks**.

Example Unicode blocks:

```
█  full
▄  bottom half
▀  top half
▌  left half
▐  right half
```

This effectively **doubles vertical resolution**.

Example:

```
██
▀█
▄█
```

Many ASCII engines use this trick to create **smooth curves**.

---

# 4. Directional Characters

Some characters imply **surface direction**.

Example set:

```
/  \
|  -
```

Used to approximate slopes.

Example sphere:

```
   /----\
  /      \
 |        |
  \      /
   \----/
```

Directional characters can fake **surface normals**.

Demo-scene raymarchers sometimes map:

```
normal.x → /
normal.y → |
normal.z → -
```

---

# 5. ASCII Lighting Model

Many ASCII renderers simulate **Lambert lighting**.

Normal lighting equation:

```
brightness = dot(normal, light_dir)
```

Then convert brightness → character.

Example:

```
shades = " .:-=+*#%@"
```

Full pipeline:

```
raymarch
compute normal
dot(normal, light)
convert brightness to character
print
```

This produces **real 3D shading in ASCII**.

---

# 6. Distance Fog

Objects farther away appear lighter.

Example:

```
near = #
mid  = +
far  = :
very far = .
```

Distance attenuation:

```
brightness *= 1 / (1 + distance)
```

Example scene:

```
#####++++
###++++::
##++::::.
```

This adds **depth perception**.

Used heavily in:

- ASCII raymarching
    
- terrain renderers
    
- dungeon engines
    

---

# 7. Temporal Dithering (Frame Flicker)

Instead of spatial dithering, alternate characters between frames.

Frame 1:

```
.....
```

Frame 2:

```
:::::
```

The eye averages them.

Result:

```
mid gray
```

Used in:

```
old CRT demos
low resolution displays
```

Very effective in **fast ASCII animations**.

---

# 8. Color + Character Combination

Modern terminals support **256 colors**.

So shading becomes:

```
character density
+
color brightness
```

Example:

```
dark green  = .
green       = :
bright green= *
white       = @
```

Used in Matrix rain style effects.

Example gradient:

```
. : * # @
```

This gives **two dimensions of shading**.

---

# Classic ASCII Shading String

Most ASCII renderers use something like:

```
" .'`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
```

Characters sorted by **pixel density**.

Simple version:

```
" .:-=+*#%@"
```

---

# Example: ASCII Sphere Renderer

Simple shading idea:

```
brightness = dot(normal, light)

char = shades[int(brightness * len(shades))]
```

Output might look like:

```
       ....
     ..::::..
    .::----::.
   .:--====--:.
   :-==++++==-:
   -==++++++==-
   ==++****++==
   +***####***+
   **######****
```

That is **true lighting in ASCII**.

---

# Why Demo Scene Programmers Loved ASCII

Because with only:

```
text characters
a few colors
very slow hardware
```

they could still create:

```
3D scenes
raymarchers
fractals
fluid effects
```

Purely with clever tricks.

---

# For Your Raymarching Terminal Project

The best combo is:

```
1. Lambert lighting
2. character density gradient
3. distance fog
4. optional dithering
```

That combination produces **surprisingly good ASCII 3D rendering**.

---

If you'd like, I can also show you something that will help your projects a lot:

**The 10 classic ASCII simulations programmers build when learning graphics**  
(including some extremely cool ones beyond fluids and raymarching).
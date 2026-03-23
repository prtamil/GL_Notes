The timing loop you’re studying is one of the **core patterns of real-time simulation**. It didn’t come from a single inventor; it evolved in the **game development community and simulation research** over decades. But one person is most closely associated with explaining and popularizing the exact form you’re learning.

---

# Who Popularized This Technique

The modern explanation of this loop is strongly associated with  
Glenn Fiedler.

In 2004 he wrote the famous article:

Fix Your Timestep!

That article clearly explained the **fixed timestep + accumulator loop**, which is essentially the same system you’re studying.

Before that article, many engines already used similar ideas internally, but the article made it **standard knowledge across the game industry**.

---

# Where This System Is Used

This loop appears in almost every **real-time simulation system**.

### Game Engines

Examples include systems inside engines like:

- Unity
    
- Unreal Engine
    
- Godot
    

In these engines:

- physics runs at fixed rates (30–120 Hz)
    
- rendering runs independently (60–240 Hz)
    

---

### Physics Engines

Physics libraries rely heavily on fixed timesteps:

- Box2D
    
- Bullet Physics
    

Physics solvers require **stable dt values** to avoid numerical instability.

---

### Simulators

Used in:

- robotics simulators
    
- flight simulators
    
- vehicle dynamics simulators
    

Because real-world physics must remain **deterministic and reproducible**.

---

### Terminal / ASCII Simulations

Even your **terminal graphics experiments** (Matrix rain, SPH fluids, fireworks) benefit from it.

Without this loop:

- motion becomes inconsistent
    
- animations depend on CPU speed
    
- slow frames break the simulation
    

---

# Why This System Became Standard

It solves three critical problems simultaneously.

---

## 1. Deterministic Physics

Physics always runs with:

```text
dt = constant
```

Example:

```text
0.0333 seconds
```

Benefits:

- stable simulations
    
- consistent results
    
- easier debugging
    

This is extremely important for physics solvers.

---

## 2. Hardware Independence

The simulation speed becomes **independent of hardware**.

Example:

|Machine|Render FPS|Physics|
|---|---|---|
|slow laptop|30|30|
|gaming PC|240|30|

Both produce **identical simulation results**.

---

## 3. CPU Efficiency

The **frame budget bank** prevents the program from burning CPU.

Without sleep:

```
render loop ≈ 2000 FPS
```

With frame cap:

```
render loop ≈ 60 FPS
```

CPU usage drops dramatically.

---

## 4. Robust Against Pauses

If the program stalls (window move, debugger pause):

The **dt clamp** prevents massive catch-up work.

Without clamp:

```
dt = 2000ms
```

Physics would attempt **60+ updates instantly**.

With clamp:

```
dt = 100ms
```

Only a few ticks occur.

---

# Benefits of the Two-Bank Model

### Stable Physics

Physics runs at **exactly the designed rate**.

---

### Smooth Rendering

Rendering can happen faster than physics.

Example:

```
physics = 30 Hz
render  = 144 Hz
```

---

### Efficient CPU Usage

Frame budget bank ensures unused time is returned to the OS.

---

### Easy Scaling

You can change physics rate easily:

```
30 Hz
60 Hz
120 Hz
```

Without rewriting the simulation.

---

# Drawbacks of This System

Despite its elegance, it is not perfect.

---

## 1. Visual Stutter Without Interpolation

If physics runs at 30 Hz but rendering at 144 Hz, the object position updates only every 33ms.

Result:

```
visible stepping
```

Modern engines solve this with **render interpolation**.

---

## 2. Physics Can Lag on Very Slow Machines

If a machine cannot keep up:

```
dt > physics_step repeatedly
```

The loop runs multiple physics ticks per frame.

Eventually the program may still fall behind.

---

## 3. Clamp Loses Time

When a stall occurs:

```
dt = 2000ms
clamped to 100ms
```

You effectively **discard 1900ms of simulation time**.

This slightly breaks physical accuracy.

But it prevents the spiral-of-death problem.

---

## 4. Complexity

Compared to the naive loop:

```
update()
draw()
sleep()
```

The accumulator model is more complex to understand.

But once learned, it becomes a **standard mental tool**.

---

# Why This Pattern Matters for You

Since you're building **ASCII simulations in C**, this timing model is actually the **same architecture used in real engines**.

Your experiments (Matrix rain, fluids, fireworks, raymarching) are essentially **mini game engines**.

Learning this loop gives you the same conceptual foundation used by professional graphics programmers.

---

✅ **One interesting historical note**

Many famous engines used variations of this loop internally, including early engines from developers like  
John Carmack, who emphasized deterministic timing and fixed physics steps in engine design.

---

If you'd like, I can also show you something fascinating:

**How this loop evolved into the architecture used by modern engines** — the **three-loop model** used today:

```
input loop
simulation loop
render loop
```

Understanding that structure explains **how engines like Unreal and Unity scale to hundreds of systems.**
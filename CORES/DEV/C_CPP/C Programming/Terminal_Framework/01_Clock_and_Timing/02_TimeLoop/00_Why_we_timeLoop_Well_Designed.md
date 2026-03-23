When people first write animation or simulation loops, they usually start with something simple. But small timing mistakes quickly cause strange behaviour: animations that run too fast, physics that explodes, or programs that consume 100% CPU.

The architecture you learned (the **two-bank loop with fixed simulation steps**) prevents most of these issues. Below are the **five timing bugs beginners almost always encounter**, and how the architecture avoids them.

---

# 1. Frame-Rate Dependent Physics

## The Bug

A beginner often writes physics like this:

```c
while (running) {
    update();   // physics
    render();
}
```

Inside `update()` they do something like:

```c
position += velocity;
```

The problem is that `update()` runs **once per frame**. If a machine renders twice as many frames, physics also runs twice as often.

Example:

|Computer|FPS|Movement Speed|
|---|---|---|
|slow laptop|30|normal|
|gaming PC|240|8× faster|

Objects move faster on faster machines.

---

## How the Bank Model Fixes It

The simulation loop always uses a **fixed timestep**:

```
physics_step = constant
```

Physics updates are triggered only when the **physics bank** contains enough time:

```
while sim_bank >= physics_step
```

So physics runs at exactly the same rate regardless of rendering speed.

---

# 2. Using Variable `dt` Directly in Physics

## The Bug

Some beginners attempt to fix frame-rate dependency by using measured time:

```c
dt = current_time - previous_time;
position += velocity * dt;
```

This seems correct, but it creates a new problem.

Frame times vary because of:

- OS scheduling
    
- GPU work
    
- background tasks
    

So `dt` may jump like:

```
8 ms
17 ms
12 ms
40 ms
9 ms
```

Physics solvers hate inconsistent time steps. Collisions and integration become unstable.

---

## How the Bank Model Fixes It

The loop **never sends the raw `dt` to physics**.

Instead physics always receives:

```
dt_fixed = physics_step
```

Example:

```
0.0333 seconds every tick
```

This produces stable numerical integration.

---

# 3. The Spiral of Death

## The Bug

If the program stalls (window drag, debugger pause), the next frame sees a huge `dt`.

Example:

```
dt = 2000 ms
```

If physics tries to catch up:

```
2000 / 33 = 60 physics ticks
```

Each physics tick takes time, making the next frame even slower. The loop gets trapped in a feedback loop called the **spiral of death**.

---

## How the Bank Model Fixes It

The loop clamps the time deposit:

```
if dt > 100ms
    dt = 100ms
```

This prevents large bursts of physics updates.

Instead of trying to simulate two seconds instantly, the system performs only a few safe ticks.

---

# 4. Busy Loop CPU Burn

## The Bug

Without a frame cap, a render loop may look like this:

```c
while (running) {
    update();
    render();
}
```

On a fast CPU this might run:

```
2000+ FPS
```

Even if nothing changes visually.

Result:

- CPU usage = 100%
    
- laptop fans spin
    
- battery drains quickly
    

---

## How the Architecture Fixes It

The loop introduces a **frame budget bank**.

Example:

```
frame_budget = 16.6 ms  (60 FPS)
```

After work finishes:

```
sleep(frame_budget - elapsed)
```

Unused time is returned to the operating system, keeping CPU usage low.

---

# 5. Physics Jitter or Visual Stutter

## The Bug

If physics runs at a lower frequency than rendering, objects appear to jump.

Example:

|System|Frequency|
|---|---|
|physics|30 Hz|
|render|144 Hz|

The object’s position updates only every 33 ms, so rendering repeats the same position several frames.

This produces visible stepping.

---

## How Modern Engines Solve It

Engines interpolate between physics states using the **remaining fraction of the physics bank**.

Example idea:

```
alpha = sim_bank / physics_step
```

Rendering blends between the previous and next simulation state.

This technique was popularized by  
Glenn Fiedler in the article  
Fix Your Timestep!.

Interpolation allows physics at 30 Hz to appear perfectly smooth even when rendering at 144 Hz.

---

# Why These Bugs Matter

The problems above appear in nearly every beginner animation loop:

1. Frame-rate dependent motion
    
2. Unstable physics
    
3. Spiral-of-death freezes
    
4. 100% CPU usage
    
5. Visual stutter
    

The **two-bank architecture** solves most of them simultaneously.

That’s why similar designs exist inside engines like:

- Unity
    
- Unreal Engine
    
- Godot
    

Even your **terminal ASCII simulations** benefit from exactly the same timing model.

---

If you want to go deeper, the next concept that makes this architecture truly powerful is:

**the interpolation factor (`alpha = sim_bank / physics_step`)**, which lets rendering predict positions between physics ticks. It’s one of the small tricks that separates **toy render loops from professional engine loops.**
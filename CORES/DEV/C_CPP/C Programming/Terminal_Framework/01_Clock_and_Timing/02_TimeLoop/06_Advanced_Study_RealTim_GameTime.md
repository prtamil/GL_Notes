Now we extend the model one more step.  
Everything you learned so far assumed **only one timeline**. But real engines actually run **two different clocks**.

This concept is subtle, but once you see it, a lot of engine features suddenly make sense.

---

# Why One Clock Is Not Enough

So far your loop measures **real-world time**:

```text
real_dt = now - previous_time
```

This represents **physical wall-clock time** — the time the computer experiences.

But many game features require **controlling time itself**.

Examples:

|Feature|What it means|
|---|---|
|Pause|simulation time stops|
|Slow motion|simulation runs slower|
|Fast-forward|simulation runs faster|
|Replay systems|time can move backward or forward|
|Deterministic multiplayer|simulation must run exactly the same everywhere|

These features cannot be implemented if physics always uses **real time directly**.

So engines introduce another concept:

> **Game Time**

---

# Two Clocks in an Engine

A real-time engine usually maintains two clocks.

### 1. Real Time

This is the **actual clock of the computer**.

Measured with functions like:

```text
clock_gettime(CLOCK_MONOTONIC)
```

Real time:

- always moves forward
    
- cannot be paused
    
- reflects the real world
    

Example:

```text
real_time = 10.25 seconds since program start
```

---

### 2. Game Time

Game time is a **virtual timeline controlled by the engine**.

Example:

```text
game_time += dt
```

But the engine can modify this value.

Example:

```text
game_time += dt * time_scale
```

Now time becomes adjustable.

---

# The Time Scale

A single variable often controls game time speed.

```text
time_scale
```

Examples:

|time_scale|Effect|
|---|---|
|1.0|normal speed|
|0.5|half speed|
|2.0|double speed|
|0.0|pause|

Physics uses **scaled time**, not raw time.

Example:

```text
game_dt = real_dt * time_scale
```

Now the engine can slow or pause the simulation without touching the real clock.

---

# Where the Bank Model Fits

The bank architecture still works exactly the same.

The only difference is **which time gets deposited**.

Instead of:

```text
sim_bank += real_dt
```

the engine deposits **scaled time**:

```text
sim_bank += game_dt
```

This allows the simulation to obey time scaling.

---

# Example Scenario: Slow Motion

Suppose:

```text
real_dt = 16 ms
time_scale = 0.25
```

Then:

```text
game_dt = 4 ms
```

Only 4 ms enters the simulation bank.

Physics now advances **four times slower**.

Rendering still happens normally.

---

# Example Scenario: Pause

Pause simply sets:

```text
time_scale = 0
```

Now:

```text
game_dt = 0
```

So the bank receives **no time**.

Physics stops.

But the engine can still:

- render frames
    
- animate UI
    
- process input
    

Everything else continues normally.

---

# The Three Time Domains

At this point the engine effectively manages **three different time domains**.

|Time Domain|Purpose|
|---|---|
|Real Time|wall clock|
|Game Time|simulation timeline|
|Frame Budget|render pacing|

Each one controls a different subsystem.

---

# Updated Loop With Dual Clocks

Here is the architecture including the **game-time layer**.

```c
int64_t physics_step = 33 * NS_PER_MS;
int64_t frame_budget = 16 * NS_PER_MS;

double time_scale = 1.0;

int64_t previous_time = clock_ns();
int64_t sim_bank = 0;

while (!quit)
{
    int64_t frame_start = clock_ns();

    process_input();

    int64_t now = clock_ns();
    int64_t real_dt = now - previous_time;
    previous_time = now;

    if (real_dt > 100 * NS_PER_MS)
        real_dt = 100 * NS_PER_MS;

    int64_t game_dt = real_dt * time_scale;

    sim_bank += game_dt;

    while (sim_bank >= physics_step)
    {
        previous_state = current_state;

        simulate_world(current_state, physics_step);

        sim_bank -= physics_step;
    }

    double alpha = (double)sim_bank / physics_step;

    State render_state =
        current_state * alpha +
        previous_state * (1.0 - alpha);

    draw_frame(render_state);

    int64_t elapsed = clock_ns() - frame_start;

    clock_sleep_ns(frame_budget - elapsed);
}
```

---

# Why This Design Is So Powerful

Adding a second clock unlocks many features.

### Pause

Physics halts without freezing rendering.

---

### Slow motion

Simulation slows while UI and rendering remain smooth.

---

### Replay systems

Recorded inputs can be replayed exactly.

---

### Deterministic networking

Multiplayer engines synchronize **game time**, not real time.

---

# The Complete Mental Model

When you think about real-time loops, remember these layers.

### 1. Real Clock

Measures what the computer experiences.

### 2. Time Scaling

Transforms real time into simulation time.

### 3. Simulation Bank

Accumulates time until physics steps occur.

### 4. Interpolation

Smooths rendering between physics states.

### 5. Frame Budget

Limits rendering speed and saves CPU.

Together they form a **robust timing architecture** used in many engines such as:

- Unity
    
- Unreal Engine
    
- Godot
    

---

# Final Insight

Once you understand this architecture, something interesting happens:

You realize **almost every real-time system follows the same pattern**:

- game engines
    
- physics simulators
    
- robotics control loops
    
- audio engines
    
- networking tick systems
    

They all solve the same problem:

> **convert messy real-world time into stable deterministic simulation time**

And the **bank model with fixed steps** is one of the cleanest solutions ever discovered.

---

If you'd like, I can also show you a fascinating historical detail:

**why early engines like Quake and Doom used a completely different timing model — and how that shaped the evolution of modern game loops.**
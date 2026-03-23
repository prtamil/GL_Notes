Below is a **conclusive mental model essay** that ties together everything you’ve been studying: clocks, simulation banks, frame budgets, interpolation, and the loop from **Fix Your Timestep! by Glenn Fiedler**.

I’ll keep the structure simple so you can **revisit it months later and still understand the whole system immediately.**

---

# The Time Loop: A Practical Mental Model for Real-Time Simulation

Every real-time simulation — games, physics demos, visual effects, or even terminal graphics — must solve one fundamental problem:

**Real time is messy, but simulation math requires consistency.**

The operating system schedules programs unpredictably. Frames may arrive at irregular intervals:

```
7 ms
16 ms
12 ms
33 ms
9 ms
```

But physics engines require **stable, evenly spaced time steps** to produce correct results. If simulation time fluctuates, physics becomes unstable, motion becomes inconsistent, and the program behaves differently on different machines.

The solution used in modern engines is a timing architecture built around a simple but powerful idea:

> **Treat time like money in a bank.**

Instead of spending time immediately when it arrives, we **deposit time into banks** and spend it in controlled amounts.

This architecture solves several classic problems simultaneously:

- frame-rate dependent physics
    
- unstable simulation steps
    
- runaway update loops
    
- CPU overuse
    
- visual stuttering
    

Understanding this system means you understand **the core timing architecture used by most real-time engines**.

---

# The Core Idea: Time as Currency

Each frame the program measures how much **real time passed**.

This time is deposited into a **simulation bank**.

Physics does not run immediately.  
Instead, physics waits until the bank contains enough time to purchase a **fixed simulation step**.

Example:

```
physics_step = 33 ms
```

If the bank contains:

```
40 ms
```

Then physics can run **one step**:

```
bank after step = 7 ms
```

That leftover time remains in the bank for the next frame.

This mechanism keeps physics running at a **perfectly stable rate**, regardless of how irregular frame timing becomes.

---

# The Two Time Banks

A well-designed real-time loop usually maintains **two separate banks**.

### 1. The Simulation Bank

This bank stores accumulated real time until enough exists to run a simulation step.

```
sim_bank += dt
```

When sufficient time is available:

```
while sim_bank >= physics_step
    simulate()
    sim_bank -= physics_step
```

This guarantees physics always advances using **identical time increments**.

---

### 2. The Frame Budget Bank

Rendering does not need to run infinitely fast.

If a display refreshes at 60 Hz, one frame should take about:

```
frame_budget = 16.6 ms
```

After completing the frame's work, the program calculates remaining time:

```
remaining = frame_budget − elapsed
```

If time remains, the program sleeps briefly.

This prevents the program from burning 100% CPU when nothing needs to be drawn.

---

# Why Fixed Simulation Steps Matter

Physics algorithms rely on **numerical integration**.

If time steps fluctuate like:

```
5 ms
30 ms
10 ms
40 ms
```

results become unstable:

- collisions break
    
- objects penetrate surfaces
    
- forces behave unpredictably
    

Using a constant step such as:

```
dt = 33 ms
```

ensures stable physics and deterministic results.

---

# The Spiral of Death

Another critical protection is **time clamping**.

If a program freezes momentarily (for example during window movement or debugging), the next frame might measure a large time jump.

Example:

```
frame_time = 2 seconds
```

Without protection, the simulation loop would attempt dozens of physics updates to catch up.

This can cause a catastrophic feedback loop known as the **spiral of death**.

To prevent this, the loop caps the amount of time deposited:

```
if dt > 100 ms
    dt = 100 ms
```

Instead of attempting to simulate two seconds instantly, the engine simply drops excess time.

The simulation stays stable rather than collapsing.

---

# Interpolation: Making Motion Smooth

Even with fixed physics updates, another problem appears.

Suppose physics runs at:

```
30 Hz
```

But rendering occurs at:

```
144 Hz
```

That means several render frames appear between physics updates.

Without correction, objects appear to **jump between positions**.

Interpolation solves this.

The leftover fraction of the simulation bank indicates how far the next step has progressed.

```
alpha = sim_bank / physics_step
```

Rendering blends between the previous and current physics states:

```
interpolated_state =
      previous_state * (1 - alpha)
    + current_state  * alpha
```

This produces smooth motion even when physics runs slower than rendering.

---

# The Final Mental Model

Think of the engine as operating three systems simultaneously:

### Real Time Measurement

The program measures how much time actually passed.

### Simulation Bank

Time accumulates until enough exists to run fixed physics steps.

### Frame Budget

Rendering runs up to a target frame rate and sleeps when finished early.

Interpolation then smooths visual output between physics updates.

Together these ideas create a **stable, efficient, and smooth real-time loop**.

---

# Final Consolidated Pseudocode

Below is the fully integrated loop, rewritten using the variables from your previous essays and including every major concept.

```c
int64_t physics_step = 33 * NS_PER_MS;      // 30 Hz simulation
int64_t frame_budget = 16 * NS_PER_MS;      // ~60 FPS render cap

int64_t previous_time = clock_ns();
int64_t sim_bank = 0;

State previous_state;
State current_state;

while (!quit)
{
    int64_t frame_start = clock_ns();

    process_input();

    int64_t now = clock_ns();
    int64_t dt  = now - previous_time;
    previous_time = now;

    if (dt > 100 * NS_PER_MS)
        dt = 100 * NS_PER_MS;

    sim_bank += dt;

    while (sim_bank >= physics_step)
    {
        previous_state = current_state;

        simulate_world(current_state, physics_step);

        sim_bank -= physics_step;
    }

    double alpha = (double)sim_bank / (double)physics_step;

    State render_state =
        current_state * alpha +
        previous_state * (1.0 - alpha);

    draw_frame(render_state);

    int64_t elapsed = clock_ns() - frame_start;

    int64_t sleep_ns = frame_budget - elapsed;

    clock_sleep_ns(sleep_ns);
}
```

---

# Key Points to Remember

When revisiting this architecture, keep these ideas in mind:

1. **Time is deposited into a bank**
    
2. **Physics only spends fixed amounts**
    
3. **Frame budget prevents CPU waste**
    
4. **Time clamping prevents spiral-of-death**
    
5. **Interpolation smooths rendering**
    

These five ideas together form the **foundation of real-time simulation timing**.

---

If you'd like, I can also show you something very interesting next:

**Why some high-end engines actually run TWO separate clocks (real time vs game time)** — a trick used for pause systems, slow motion, and deterministic replays.
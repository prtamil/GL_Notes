# The Rendering Framework: A Complete Technical Explanation

## Overview

The framework is built around one central idea: **separate what the program knows from what it does, and separate when things happen from how fast the hardware runs.** Every piece exists to enforce one of those two separations.

---

## §2 Clock — The Foundation of Everything

```c
static int64_t clock_ns(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (int64_t)t.tv_sec * NS_PER_SEC + t.tv_nsec;
}
```

### Why nanoseconds, not milliseconds?

A terminal frame at 60 fps takes 16,666,666 nanoseconds. Milliseconds give you 16 ms — you lose 666 microseconds of precision every frame. Over a minute that accumulates to 40ms of timing drift. Nanoseconds eliminate this entirely. The int64_t holds nanoseconds for over 292 years before overflowing.

### Why CLOCK_MONOTONIC, not time() or gettimeofday()?

There are three clocks available to a C program:

**`time()`** — resolution is 1 whole second. Useless for animation.

**`CLOCK_REALTIME`** — tracks wall-clock time. The problem: it can jump. When the system adjusts for NTP drift, or the user changes the timezone, this clock can jump backward or forward by arbitrary amounts. If your loop sees dt suddenly become -500ms or +10 seconds, the simulation either runs backward or tries to simulate 300 ticks in one frame.

**`CLOCK_MONOTONIC`** — guaranteed to never go backward. It counts from an arbitrary fixed point (usually system boot) and only ever increases. This is the only correct clock for measuring elapsed time in a real-time loop.

### clock_sleep_ns

```c
static void clock_sleep_ns(int64_t ns)
{
    if (ns <= 0) return;
    struct timespec req = { ns / NS_PER_SEC, ns % NS_PER_SEC };
    nanosleep(&req, NULL);
}
```

`nanosleep` is used instead of `usleep` for two reasons. First, `usleep` is deprecated in POSIX 2008 and absent in C11 strict mode. Second, `nanosleep` takes a `timespec` which can express both seconds and nanoseconds in one call. The `if (ns <= 0) return` guard prevents passing negative values — if the frame took longer than the budget, we skip sleeping entirely rather than passing a negative to nanosleep which would be undefined behavior.

---

## §9 Screen — The Double Buffer System

### Why two windows?

A terminal is not like a GPU framebuffer. When you call `wrefresh()`, ncurses walks through every character in the window that changed since the last refresh and sends escape sequences to the terminal to update those cells. This takes real time — on a 200×50 terminal repainting every cell can take 5–10ms. During that time, if you are writing new content into the same window you just started refreshing, you get **tearing**: the user sees a mix of old and new content on screen simultaneously.

The double buffer solution:

```c
typedef struct {
    WINDOW *back;    /* you draw here — invisible to the user */
    WINDOW *front;   /* ncurses refreshes this to the terminal */
    WINDOW *hud_win; /* separate overlay, always on top */
    int     cols, rows;
} Screen;
```

Every frame:

1. `werase(back)` — wipe the back window clean
2. Draw your scene into `back`
3. `screen_swap(s)` — exchange the two pointers
4. `wrefresh(front)` — push the now-complete frame to the terminal

The user only ever sees complete, fully-drawn frames. The in-progress drawing is always happening in the invisible `back` window.

### screen_swap — O(1) pointer exchange

```c
static void screen_swap(Screen *s)
{
    WINDOW *tmp = s->front;
    s->front    = s->back;
    s->back     = tmp;
}
```

This is three pointer assignments. It does not copy any data. A 200×50 terminal has 10,000 cells; copying them would take ~40 microseconds. The swap takes ~1 nanosecond. This is why we swap pointers instead of copying content.

### The HUD window — why separate?

```c
s->hud_win = newwin(1, HUD_COLS, 0, s->cols - HUD_COLS);
```

ncurses renders windows in the order they are refreshed. If you refresh `front` and then refresh `hud_win`, the HUD is guaranteed to appear on top of the rain/wireframe/whatever. If the HUD were part of the main window, clearing the main window each frame would wipe the HUD too, causing it to flicker. By keeping it separate, the HUD is updated independently on its own slower timer (every 500ms) and is never cleared by the main render cycle.

### screen_resize — the correct ncurses resize sequence

```c
static void screen_resize(Screen *s)
{
    delwin(s->hud_win);
    delwin(s->back);
    delwin(s->front);
    endwin();
    refresh();                  /* re-reads terminal dimensions */
    screen_build_windows(s);
}
```

This is a specific sequence that matters. `endwin()` puts the terminal back into a clean state and flushes ncurses' internal representation. `refresh()` on `stdscr` after `endwin()` forces ncurses to re-read `LINES` and `COLS` from the terminal. Only after `refresh()` does `getmaxyx(stdscr, rows, cols)` return the new dimensions. If you skip `endwin()+refresh()` and just delete/recreate windows, `getmaxyx` still returns the old size and your new windows are the wrong dimensions.

---

## The dt Loop — Fixed Timestep with Variable Render Rate

This is the most important design in the whole framework. Understanding it requires understanding two problems it solves simultaneously.

### Problem 1: simulation speed depends on CPU speed

Naive loop:

```c
while (running) {
    scene_tick(&scene);   // advance physics
    render(&scene);       // draw
    usleep(30000);        // wait 30ms
}
```

On a slow machine, `render()` takes 25ms, so each tick fires every 55ms. On a fast machine it takes 2ms, so each tick fires every 32ms. The simulation runs at different speeds on different machines. A spinning cube spins 70% faster on a fast machine than on a slow one.

### Problem 2: stall recovery

If the process is paused (you switch windows, the OS suspends it, a debugger attaches), then resumes, a naive dt loop will try to "catch up" by running hundreds of ticks in one frame. The cube teleports to a completely different angle.

### The solution: fixed timestep accumulator

```c
int64_t frame_time = clock_ns();
int64_t sim_accum  = 0;

while (running) {
    int64_t now = clock_ns();
    int64_t dt  = now - frame_time;
    frame_time  = now;

    /* Clamp: if we stalled >100ms, pretend only 100ms passed */
    if (dt > 100 * NS_PER_MS) dt = 100 * NS_PER_MS;

    /* Bank the elapsed time */
    sim_accum += dt;

    /* Consume it in fixed steps */
    int64_t tick_ns = TICK_NS(app->sim_fps);
    while (sim_accum >= tick_ns) {
        scene_tick(&scene, dt_sec);   /* always called with the same dt */
        sim_accum -= tick_ns;
    }

    render(&scene);
}
```

**What this achieves:**

`scene_tick` is always called with exactly `dt_sec = tick_ns / NS_PER_SEC`. This value never changes. The cube always rotates `rot_speed * dt_sec` radians per tick. The visual speed in radians per second is therefore exactly `rot_speed` — identical on every machine, at every frame rate.

If the machine is fast and renders 120fps but the sim runs at 30fps, `sim_accum` often doesn't reach `tick_ns` when checked, so `scene_tick` is skipped — the sim idles. The render still runs, showing the same frame twice (smooth, no tearing).

If the machine is slow and renders at 20fps against a 30fps sim, `sim_accum` exceeds `tick_ns` after two render frames and `scene_tick` is called once, catching up exactly. The visual speed stays correct.

The 100ms clamp prevents the "spiral of death": if paused for 10 seconds, without the clamp `sim_accum` would hold 10,000ms and the while loop would fire 300 ticks in one frame. With the clamp, we simply throw away all time beyond 100ms. The cube jumps slightly but doesn't teleport.

### dt_sec — the physics time unit

```c
float dt_sec = (float)tick_ns / (float)NS_PER_SEC;
```

This converts the fixed tick length from nanoseconds to seconds. Physics quantities are expressed in real-world units per second: `rot_speed = 0.9` means 0.9 radians per second. `scene_tick` multiplies by `dt_sec` to get the per-tick increment:

```c
s->rx += s->rot_x * dt_sec;   /* angle += rad/sec * sec = radians */
```

This is why changing `sim_fps` with `]`/`[` changes smoothness but not visual speed: `dt_sec` decreases proportionally as `sim_fps` increases, so `rot_speed * dt_sec` stays constant per second of real time.

---

## FPS Counter — Measurement, Not Calculation

```c
int64_t fps_accum   = 0;
int     frame_count = 0;
double  fps_display = 0.0;

/* Inside the loop: */
frame_count++;
fps_accum += dt;
if (fps_accum >= FPS_UPDATE_MS * NS_PER_MS) {
    fps_display = (double)frame_count
                / ((double)fps_accum / NS_PER_SEC);
    frame_count = 0;
    fps_accum   = 0;
}
```

This measures actual frames delivered to the user, not theoretical frame rate. It counts every time `screen_present()` is called (a real frame swap), accumulates the real elapsed time, and computes the ratio every 500ms. The 500ms window is chosen deliberately: shorter windows (50ms) cause the number to fluctuate wildly because frame timing has natural jitter. Longer windows (2000ms) feel unresponsive. 500ms gives stable, readable numbers that update twice per second.

The formula `frame_count / (fps_accum / NS_PER_SEC)` is frames per second measured empirically. If 15 frames rendered in 500ms, fps = 15 / 0.5 = 30.0. This accounts for real scheduling jitter, sleep overshoot, and OS preemption — it shows you what the user actually experienced, not what the math predicted.

---

## App — The Single Owner

```c
typedef struct {
    Scene                 scene;
    Screen                screen;
    int                   sim_fps;
    volatile sig_atomic_t running;
    volatile sig_atomic_t need_resize;
} App;

static App g_app;
```

### Why one global

Signal handlers cannot receive parameters. `SIGINT` (Ctrl-C) and `SIGWINCH` (resize) are delivered asynchronously by the OS and can only reach global or static data. The entire program state lives in one struct so the signal handlers can set `running = 0` or `need_resize = 1` without any other mechanism.

```c
static void on_exit_signal(int sig)   { (void)sig; g_app.running = 0;     }
static void on_resize_signal(int sig) { (void)sig; g_app.need_resize = 1; }
```

### volatile sig_atomic_t — not just volatile

`volatile` alone tells the compiler "don't cache this in a register, re-read from memory every time." That prevents the optimizer from turning `while (running)` into `while (true)` because it sees no code that changes `running` in the loop body.

But `volatile` alone doesn't prevent the CPU from reordering the write. On some architectures a signal handler could write `running = 0` and the main thread could see a stale cached value for several cycles.

`sig_atomic_t` is defined by the C standard as the integer type whose read and write are guaranteed to be atomic on the target architecture — they complete without interruption. Combined with `volatile`, this is the only fully correct way to communicate from a signal handler to the main loop in standard C without locks.

### need_resize — deferred handling

```c
if (app->need_resize) {
    app_do_resize(app);
    frame_time = clock_ns();
    sim_accum  = 0;
}
```

The resize is handled at the top of the main loop, not inside the signal handler. Signal handlers are severely restricted — calling `malloc`, `free`, ncurses functions, or anything that takes locks from a signal handler causes undefined behavior. The signal handler only sets a flag; the main loop does the actual work on the next iteration.

After `app_do_resize`, `frame_time` is reset and `sim_accum` is cleared. The resize operation (deleting windows, creating new ones) takes 5–20ms. Without resetting these, the accumulator would contain that 20ms and fire extra sim ticks to compensate — the shape would visibly jump after every resize. Resetting makes the loop treat the resize as a clean start.

---

## The Complete Frame Cycle

One iteration of the main loop, annotated:

```c
while (app->running) {

    // 1. Handle deferred resize before anything reads screen dimensions
    if (app->need_resize) { app_do_resize(app); ... }

    // 2. Measure real elapsed time since last frame
    int64_t now = clock_ns();
    int64_t dt  = now - frame_time;   // nanoseconds since last frame
    frame_time  = now;
    if (dt > 100 * NS_PER_MS) dt = 100 * NS_PER_MS;  // stall clamp

    // 3. Advance simulation in fixed steps
    sim_accum += dt;
    while (sim_accum >= tick_ns) {
        scene_tick(&app->scene, dt_sec);  // always same dt_sec
        sim_accum -= tick_ns;
    }

    // 4. Render current state (may be between two sim ticks)
    scene_render(&app->scene);         // compute geometry
    screen_draw_scene(&app->screen, &app->scene);  // werase + draw
    screen_present(&app->screen);      // swap + wrefresh

    // 5. Update FPS display every 500ms
    frame_count++;
    fps_accum += dt;
    if (fps_accum >= 500 * NS_PER_MS) { compute fps; reset; }
    screen_draw_hud(...);              // refresh overlay window

    // 6. Non-blocking input
    int ch = getch();                  // returns ERR immediately if no key
    if (ch != ERR) app_handle_key(app, ch);

    // 7. Sleep the remainder of the frame budget
    int64_t elapsed = clock_ns() - frame_time + dt;
    clock_sleep_ns(NS_PER_SEC / 60 - elapsed);  // yield unused CPU
}
```

Step 7 is subtle. `NS_PER_SEC / 60` is 16,666,666 ns — one frame at 60fps. `elapsed` is how long this iteration actually took. The sleep is `budget - elapsed`. If the frame took 8ms, we sleep 8ms. If it took 20ms (over budget), `elapsed > budget`, the sleep gets a negative value, `clock_sleep_ns` returns immediately, and we start the next frame immediately — the frame cap never blocks us from catching up.

This gives you 60fps maximum render rate with minimal CPU usage. Without it, the loop would spin at 10,000fps burning a full CPU core doing redundant redraws of an animation that only changes at 30Hz.

---

## Summary: The Four Guarantees

| Guarantee                                 | Mechanism                                                |
| ----------------------------------------- | -------------------------------------------------------- |
| Simulation speed constant across hardware | Fixed-timestep accumulator with constant `dt_sec`        |
| No tearing or half-drawn frames           | Double WINDOW buffer, swap then refresh                  |
| Terminal always restored on any exit      | `atexit(cleanup)` + `endwin()` idempotent                |
| Correct resize on any terminal            | SIGWINCH → flag → deferred `app_do_resize` with dt reset |
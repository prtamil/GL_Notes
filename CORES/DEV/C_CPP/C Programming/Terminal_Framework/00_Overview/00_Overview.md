# The Framework: A Study in Layered Abstraction for Terminal Animation

## Preface

Over the course of building matrix_rain, fireworks, kaboom, blast_bomb, and burst, a consistent framework emerged organically. It was never designed upfront — it crystallized through iteration, each program teaching the next what the right boundaries were. This essay explains what the framework is, why each layer exists, and what design philosophy holds it together.

---

## The Central Problem

Writing animation in a terminal is deceptively difficult. You are working with a display technology from the 1970s — a grid of characters, refreshed by a library (ncurses) that was designed for static forms, not moving pictures. Three fundamental tensions make this hard:

**Speed vs. correctness.** Redrawing every cell every frame is simple but causes flicker. Drawing only changed cells is fast but requires tracking state across frames — and that state can go stale.

**Simulation vs. rendering.** The physics of a particle explosion has nothing to do with how ncurses draws characters. Mixing them produces code that is impossible to change without breaking everything.

**Platform vs. portability.** Terminal colors, resize signals, and input handling are platform-specific details. Scattering them through the code makes every program fragile.

The framework resolves all three tensions through a single principle: **one layer, one responsibility, one direction of dependency.**

---

## The Eight Sections

Every program in the series follows the same section structure. Reading the header comment of any file tells you the whole architecture before you read a single function.

### §1 Config — The Single Source of Truth

```c
enum {
    SIM_FPS_DEFAULT  = 24,
    BURSTS_DEFAULT   =  5,
    PARTICLES        = 48,
    BURST_TICKS      = 22,
};
```

Every magic number lives here and nowhere else. This is not merely stylistic tidiness — it is a discipline that makes the code _readable as documentation_. When you want to know how fast the simulation runs, you read one line. When you want to change it, you change one line. No hunting, no grep, no surprises.

The use of anonymous `enum` rather than `#define` is deliberate. Enum constants have types, appear in debugger symbols, and participate in compiler warnings. A `#define` is a textual substitution that evaporates before the compiler sees it. For constants that represent counts and rates — things that should behave like integers — the enum is the correct C tool.

Runtime-mutable state (current speed, current burst count) is kept separately in the `App` struct. The distinction matters: config is what the _program_ knows at compile time; app state is what the _user_ has changed at runtime. Conflating them is the source of many subtle bugs.

---

### §2 Clock — Physics Divorced from Hardware

```c
static int64_t clock_ns(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (int64_t)t.tv_sec * NS_PER_SEC + t.tv_nsec;
}
```

The clock section is small — two functions — but its consequences are large. `clock_ns()` wraps `CLOCK_MONOTONIC`, which never jumps backward. This is the only correct clock for a game loop. `CLOCK_REALTIME` can jump when the system clock is adjusted; using it for delta-time produces a single catastrophic frame that appears to advance the simulation by hours.

`clock_sleep_ns()` uses `nanosleep()` rather than `usleep()`. The difference is that `nanosleep()` is POSIX-correct and handles interruption by signals without discarding the remaining sleep time.

The dt (delta-time) accumulator pattern built on top of this clock is the real contribution of §2:

```c
sim_accum += dt;
while (sim_accum >= tick_ns) {
    field_tick(&app->field);
    sim_accum -= tick_ns;
}
```

This is a fixed-timestep simulation with a variable render rate. The simulation advances in exact, equal steps regardless of how fast or slow the computer is. A slow machine simply skips render frames; a fast machine renders the same frame multiple times. The physics — particle positions, burst radii, fade curves — are identical on every machine because they never see a variable dt. This is the gold standard for real-time simulation, described by Glenn Fiedler's canonical essay "Fix Your Timestep" and used in every serious game engine.

The clamping line:

```c
if (dt > 100 * NS_PER_MS) dt = 100 * NS_PER_MS;
```

prevents the "spiral of death" — if the process is paused (switched away, debugged, system load spike), the accumulated dt would try to catch up by running hundreds of ticks in one frame, which looks like an explosion teleporting across the screen. The clamp says: if we have been away for more than 100ms, pretend only 100ms passed.

---

### §3 Color — Isolation of Platform Specifics

ncurses color pairs are a platform detail. The number 196 (xterm bright red) means nothing to a particle simulation. The name `C_RED` means everything. §3 creates a named vocabulary:

```c
typedef enum {
    C_RED = 1, C_ORANGE = 2, C_YELLOW = 3,
    C_GREEN = 4, C_CYAN = 5, C_BLUE = 6, C_MAGENTA = 7,
} Hue;
```

Everything above §3 speaks in `Hue` values. The ncurses `COLOR_PAIR()` call appears only in `particle_draw()` and `screen_draw_hud()` — never in the physics or simulation code.

The 256-color / 8-color runtime fallback:

```c
if (COLORS >= 256) {
    init_pair(C_RED, 196, COLOR_BLACK);
} else {
    init_pair(C_RED, COLOR_RED, COLOR_BLACK);
}
```

means the same binary runs correctly in a modern xterm with vivid colors and in tmux without 256-color configured. The simulation code never knows which path was taken. This is the _open/closed principle_ in C: the rendering is open to extension (new color schemes) but the simulation is closed to modification.

The `COLOR_BLACK` explicit background — rather than `-1` with `use_default_colors()` — is the key to the "characters appear on black background" aesthetic. With `-1`, tmux frequently maps the background to monochrome. With `COLOR_BLACK`, it works everywhere.

---

### §4 The Atomic Unit — Cell, Particle, Blob, Debris

Each program defines its smallest visual unit in §4. This is the atom of the simulation — the thing that has a position, a character, a color, and a lifetime. The exact structure varies by program, but the contract is the same:

- It knows only its own state
- It has a `spawn/init` function that fully initialises it
- It has a `tick` function that advances one simulation step
- It has a `draw` function that writes one character into a WINDOW

The `Particle` in burst is the clearest expression of this:

```c
typedef struct {
    float cx, cy;    /* birth centre                   */
    float rx, ry;    /* offset in circle space         */
    float vx, vy;    /* velocity in circle space       */
    float life;      /* 1.0 → 0.0                      */
    float decay;
    int   delay;     /* ticks before movement begins   */
    char  sym;
    Hue   hue;
    bool  alive;
} Particle;
```

Notice what is absent: no pointer to its parent burst, no knowledge of the screen dimensions (passed as parameters to `tick` and `draw`), no ncurses types. It is a pure value type. You could serialise it, copy it, move it between arrays — it has no hidden dependencies.

The `delay` field is an example of encoding _temporal behavior_ directly in the data rather than in control flow. Instead of a separate "launch wave" loop in the simulation, each particle carries its own countdown. The simulation tick is a single uniform loop: `for each particle, tick it`. The staggered launch behavior emerges from the data without any special-case code.

The circle-space physics with aspect correction at draw time deserves special attention:

```c
/* Physics: uniform in all directions */
p->vx *= 0.82f;
p->vy *= 0.82f;
p->rx += p->vx;
p->ry += p->vy;

/* Draw: squash horizontal to match terminal cell proportions */
int x = (int)(p->cx + p->rx * ASPECT);
int y = (int)(p->cy + p->ry);
```

This is the separation of _logical space_ from _screen space_. The simulation computes in a mathematically clean coordinate system where circles are circles. The renderer transforms to the distorted screen coordinate system where a terminal's cells are twice as tall as they are wide. Conflating these two spaces — as the original `blast_bomb.c` did with `vx *= 0.5` — produces subtle errors that accumulate over time and produce ellipses instead of circles. Keeping them separate eliminates the error class entirely.

---

### §5 The Entity — Column, Rocket, Burst, Bomb

§5 owns a collection of §4 atoms and a state machine that governs their lifecycle. This is where the visual effect actually lives.

The state machine is the most important structural decision in the whole framework. Every entity in every program is modeled as a finite automaton:

```
matrix_rain Column:  ACTIVE → (scrolls off bottom) → INACTIVE → (random chance) → ACTIVE

fireworks Rocket:    IDLE → RISING → EXPLODED → IDLE

burst Burst:         IDLE → FLASH → LIVE → IDLE
```

The state machine externalizes the "what phase am I in?" question from a tangle of if-statements into a named, enumerable type. Reading `b->state == BS_FLASH` is unambiguous. Reading the equivalent pile of `if (b->ticks > 3 && b->ticks < 7 && b->flash_done)` is archaeology.

Each state transition is a single assignment. Each state's behavior is a single `case` in a `switch`. New states can be added without modifying existing cases. The entire lifecycle of a visual effect is visible on one screen.

The callback pattern for cross-layer communication:

```c
static void burst_tick(Burst *b, int cols, int rows,
                       void (*scorch_cb)(int x, int y, void *ud), void *ud)
```

is the framework's solution to the dependency inversion problem. `Burst` needs to notify the `Field` when it dies, but it must not depend on `Field` — that would be a circular dependency (§5 depending on §6). Instead, `burst_tick` accepts a function pointer. The field passes `field_scorch_cb` downward; the burst calls it upward without knowing who it is. This is the observer pattern in its purest C form: no virtual tables, no heap allocation, just a function pointer and a void pointer for context.

---

### §6 The Simulation — Rain, Show, Field

§6 owns the entity pool and the shared state that persists across entity lifetimes. In matrix_rain this is the column array and the canvas. In burst it is the burst array and the scorch layer.

The scorch layer in burst and blast_bomb is a pedagogically interesting design. It is a `char[cols × rows]` array that accumulates marks from finished bursts. It outlives individual bursts, it is drawn before live bursts (so live bursts render on top), and it is cleared only on an explicit user command.

This demonstrates a principle about persistence: not everything should be reset every frame. The scorch layer gives the animation a _memory_ — the field looks increasingly battle-worn as bursts accumulate. This historical layering is impossible if you model everything as stateless per-frame rendering.

The separation between `field_tick()` and `field_draw()` is a hard rule of the framework. Tick advances the simulation; draw reads it. They are never combined. This matters because:

1. The simulation might tick multiple times between renders (fixed-timestep accumulator catching up)
2. The renderer needs a stable snapshot to read from
3. Testing the simulation does not require a display

`field_draw()` is always preceded by `werase(back)` — the full-window clear that became the solution to the "junk characters" problem. The lesson from that debugging session was that a diff renderer (drawing only changed cells) fails with double buffering because the `back` window carries content from two frames ago, not one. A full clear before each repaint is the only correct approach when you swap window pointers rather than copy window contents.

---

### §7 Screen — The Display Layer

§7 is the entire ncurses interface. Everything ncurses-specific lives here: `initscr`, `newwin`, `wrefresh`, `delwin`, `endwin`, `wattron`, `wattroff`, `mvwaddch`.

The double-buffer design has three windows:

```
back     ← painted this frame (werase + draw)
front    ← currently visible on the terminal
hud_win  ← narrow overlay, refreshed last (stays on top)
```

`screen_swap()` is a pointer exchange:

```c
WINDOW *tmp = s->front;
s->front    = s->back;
s->back     = tmp;
```

Three assignments. No data copied. O(1) regardless of terminal size. `wrefresh(front)` sends the newly painted window to the terminal in a single burst. Because ncurses batches all the character changes since the last refresh into one write, the user never sees a half-drawn frame — the swap is atomic from the user's perspective.

The HUD is a separate window that is refreshed _after_ `wrefresh(front)`. ncurses renders windows in refresh order; refreshing hud_win last ensures it overlays the main window cleanly without being overwritten by it.

`screen_resize()` is the resize handler:

```c
static void screen_resize(Screen *s)
{
    delwin(s->hud_win);
    delwin(s->back);
    delwin(s->front);
    endwin();
    refresh();          /* re-probes LINES and COLS from the terminal */
    screen_build_windows(s);
}
```

`endwin()` + `refresh()` is the canonical ncurses resize sequence. `endwin` flushes the terminal to a clean state; `refresh` re-reads the terminal dimensions into ncurses' `LINES` and `COLS` globals. Only after this can `getmaxyx(stdscr, ...)` return correct values.

---

### §8 App — The Orchestrator

§8 owns everything. It contains the simulation state, the screen state, the runtime-mutable settings, and the signal flags. It is the only global in the program — a single `static App g_app` — and it is global for one reason only: signal handlers cannot receive arguments.

```c
static void on_exit_signal(int sig)   { (void)sig; g_app.running = 0;     }
static void on_resize_signal(int sig) { (void)sig; g_app.need_resize = 1; }
```

Both flags are `volatile sig_atomic_t` — the only type the C standard guarantees can be written safely from a signal handler. `volatile` prevents the compiler from caching the value in a register across loop iterations. `sig_atomic_t` is an integer type whose reads and writes are atomic on the target architecture. Using plain `int` or `bool` here is a data race.

The `atexit(cleanup)` pattern:

```c
static void cleanup(void) { endwin(); }
```

registers `endwin()` to be called on every exit path: normal return, `exit()`, `abort()`, and signal-induced termination. Without this, a crash leaves the terminal in raw ncurses mode — invisible cursor, no echo, broken input — requiring the user to type `reset` blindly. The `atexit` registration costs one line and eliminates an entire class of user-visible failures.

The main loop has exactly five responsibilities, in exactly this order, every frame:

1. **Resize check** — handle SIGWINCH before anything else so the first post-resize frame uses correct dimensions
2. **dt measurement** — record elapsed time, clamp to 100ms
3. **Simulation accumulator** — advance physics in fixed steps
4. **Render** — paint to back window, swap, refresh
5. **Input** — non-blocking `getch()`, dispatch to key handler

The frame cap at the end:

```c
int64_t elapsed = clock_ns() - frame_time + dt;
clock_sleep_ns(NS_PER_SEC / 60 - elapsed);
```

limits the loop to 60 renders per second. Without it, the loop would spin at thousands of frames per second, burning 100% of a CPU core doing redundant redraws of an animation that changes at 24 Hz. The sleep returns unused CPU budget to the operating system.

---

## What the Framework Achieves

Looking across all five programs, the framework achieves four things that are genuinely difficult to achieve simultaneously in C:

**Correctness across conditions.** Terminal resizes, signal interruption, tmux, 8-color terminals, fast machines, slow machines — the same binary handles all of them correctly because each concern is isolated to one layer that handles it completely.

**Readability by layer.** You can read §4 and understand the physics of a particle without knowing anything about ncurses. You can read §7 and understand the double-buffer mechanism without knowing what a burst is. Each section is a complete, comprehensible unit. A new contributor can be onboarded to one section at a time.

**Extensibility without modification.** Adding a new color theme requires changing only `color_init()`. Adding a new particle behavior requires changing only `particle_tick()`. The callback pattern means `burst_tick()` can notify `field_scorch_cb` without depending on `Field`. Each layer is extended by writing new code, not by modifying existing code.

**Zero hidden state.** There are no static variables in simulation code (the one exception is `kaboom_prng` which is a deliberate port of the original's algorithm). Every function receives what it needs as parameters. Every struct contains everything it needs. You can snapshot the entire simulation state by copying the `App` struct — no hidden global tables, no thread-local storage, no malloc'd singletons.

---

## The Deeper Principle

The framework is ultimately an argument that **the structure of C programs should reflect the structure of the problem, not the structure of the language**.

C gives you structs, functions, enums, and pointers. It does not give you classes, inheritance, interfaces, or modules. The temptation is to compensate for these absences by reaching for complexity — void pointer vtables simulating polymorphism, global arrays simulating object pools, preprocessor macros simulating generics.

This framework does none of that. It uses the simplest possible tool for each job: an enum for named constants, a struct for grouped state, a function pointer for a callback, a switch for a state machine. The power comes not from any individual technique but from applying each technique consistently, at the right boundary, in the right direction.

The result is code that any C programmer can read, modify, and extend — not because it avoids interesting ideas, but because every interesting idea is expressed in the clearest possible way.
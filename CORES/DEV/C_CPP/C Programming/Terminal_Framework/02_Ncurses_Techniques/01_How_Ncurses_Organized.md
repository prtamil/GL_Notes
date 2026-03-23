Got it — you want a **clean skeleton** that shows _only how ncurses is structured and used_, with everything else stripped out.

I’ll keep the exact architecture from your `bounce.c`, but replace physics/scene with placeholders so you can clearly see the **rendering framework**.

---

# 🧱 Minimal ncurses Framework Skeleton

```c
/*
 * ncurses_framework.c
 *
 * Focus: ONLY ncurses usage + frame pipeline
 * Physics / simulation replaced with placeholders
 */

#include <ncurses.h>
#include <stdbool.h>
#include <stdlib.h>

/* ================================================================ */
/* §1 Screen (ncurses layer)                                        */
/* ================================================================ */

typedef struct {
    int cols;
    int rows;
} Screen;

static void color_init(void)
{
    start_color();
    init_pair(1, COLOR_GREEN, COLOR_BLACK);
    init_pair(2, COLOR_YELLOW, COLOR_BLACK);
}

/* Initialize ncurses */
static void screen_init(Screen *s)
{
    initscr();              // start ncurses
    noecho();               // no key echo
    cbreak();               // instant key input
    curs_set(0);            // hide cursor

    nodelay(stdscr, TRUE);  // non-blocking input
    keypad(stdscr, TRUE);   // arrow keys support
    typeahead(-1);          // avoid output interruption

    color_init();

    getmaxyx(stdscr, s->rows, s->cols);
}

/* Cleanup */
static void screen_free(void)
{
    endwin();               // restore terminal
}

/* Handle resize */
static void screen_resize(Screen *s)
{
    endwin();
    refresh();
    getmaxyx(stdscr, s->rows, s->cols);
}

/* ================================================================ */
/* §2 Scene (PLACEHOLDER — no real logic)                            */
/* ================================================================ */

typedef struct {
    int dummy;  // placeholder
} Scene;

static void scene_init(Scene *s)
{
    (void)s;
}

/* Update simulation (placeholder) */
static void scene_tick(Scene *s)
{
    (void)s;
}

/* Draw simulation (THIS is where ncurses draw happens) */
static void scene_draw(const Scene *s, int cols, int rows)
{
    (void)s;

    // Example: draw a simple character in center
    int cx = cols / 2;
    int cy = rows / 2;

    attron(COLOR_PAIR(1) | A_BOLD);
    mvaddch(cy, cx, 'O');
    attroff(COLOR_PAIR(1) | A_BOLD);
}

/* ================================================================ */
/* §3 Frame Build + Present                                         */
/* ================================================================ */

/* Build frame (writes to ncurses buffer, NOT terminal) */
static void screen_draw(Screen *s, const Scene *sc)
{
    erase();   // clear "next frame"

    // draw scene
    scene_draw(sc, s->cols, s->rows);

    // draw HUD (example)
    attron(COLOR_PAIR(2) | A_BOLD);
    mvprintw(0, 2, "ncurses framework demo");
    attroff(COLOR_PAIR(2) | A_BOLD);
}

/* Present frame (ONLY place that touches terminal) */
static void screen_present(void)
{
    wnoutrefresh(stdscr);  // prepare frame
    doupdate();            // flush diff to terminal
}

/* ================================================================ */
/* §4 Input                                                         */
/* ================================================================ */

static bool handle_input(int ch)
{
    switch (ch) {
    case 'q':
    case 27:   // ESC
        return false;
    default:
        return true;
    }
}

/* ================================================================ */
/* §5 App Loop                                                      */
/* ================================================================ */

int main(void)
{
    Screen screen;
    Scene  scene;

    screen_init(&screen);
    scene_init(&scene);

    bool running = true;

    while (running) {

        /* ── update (placeholder) ── */
        scene_tick(&scene);

        /* ── build frame ── */
        screen_draw(&screen, &scene);

        /* ── present frame ── */
        screen_present();

        /* ── input ── */
        int ch = getch();
        if (ch != ERR && !handle_input(ch))
            running = false;
    }

    screen_free();
    return 0;
}
```

---

# 🧠 What this shows clearly

## 🔑 The ncurses structure in isolation

### 1. Init phase

```c
initscr();
...
getmaxyx();
```

---

### 2. Frame loop (THIS is the core)

```c
while (running) {
    scene_tick();     // your logic (independent)

    screen_draw();    // write into buffer
    screen_present(); // flush once

    getch();          // input
}
```

---

### 3. The rendering pipeline (exact pattern)

```c
erase();             // clear next frame
mvaddch()/mvprintw()// draw into buffer
wnoutrefresh();      // finalize
doupdate();          // show frame
```

---

# 🎯 Key takeaway

This skeleton isolates the **true ncurses contract**:

```text
ncurses is only responsible for:

1. Managing a virtual screen (buffer)
2. Letting you draw into it
3. Efficiently flushing it to terminal
```

---

# 🧩 If you study just this

Ignore everything else and focus on:

```c
erase();
draw();
wnoutrefresh();
doupdate();
```

That’s the **entire rendering engine**.

---

If you want next step, I can:

- strip it down EVEN more (like 50-line minimal engine)
    
- or show a **multi-window version** (where wnoutrefresh becomes critical)
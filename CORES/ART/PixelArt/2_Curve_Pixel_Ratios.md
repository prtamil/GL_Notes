| **Pattern Name**  | **Steps**            | **Shape Description**                         |
| ----------------- | -------------------- | --------------------------------------------- |
| **Mini Arc**      | `1H, 1D, 1V`         | Very tight curve (3 pixels)                   |
| **Small Arc**     | `2H, 1D, 2V`         | Compact, well-balanced arc                    |
| **Wide Arc**      | `3H, 1D, 3V`         | Bigger curve, gentle roundness                |
| **Smooth Arc**    | `2H, 2D, 2V`         | Very smooth; good for natural round corners   |
| **Sharp Slope**   | `1H, 1V`             | Sharp L-corner                                |
| **45° Diagonal**  | `1D, 1D, 1D`         | Perfect slope                                 |
| **Steep Curve**   | `2H, 3D, 2V`         | Rounded drop; more angled                     |
| **Flat-Top Arc**  | `2H, 1D, 1V, 1D, 2V` | Curve with a flat middle                      |
| **Shallow Curve** | `1H, 2D, 1V`         | Flatter, good for wide curves in small space  |
| **Ellipse Slice** | `3H, 2D, 1V`         | Mimics ellipse edge                           |
| **Smooth Drop**   | `1H, 1D, 1D, 1V`     | Gently curving into vertical                  |
| **Bullet Tip**    | `1V, 1D, 1H, 1D, 1V` | Good for top or bottom point (like a capsule) |
| **Dome Top**      | `2H, 1D, 1H, 1D, 2V` | Curves over with a dome                       |
| **Corner Bubble** | `1V, 1D, 1H, 1D, 1V` | U-turn arc; bubble shape                      |
| **Wavy Segment**  | `1H, 1D, 1V, 1D, 1H` | S-curve feel in tiny space                    |

```py
# We'll generate grid diagrams for each pattern in a 7x7 grid (for visibility).
# Each pattern is a list of steps with a starting point at (0, 0)

import numpy as np
import matplotlib.pyplot as plt

# Define directions
directions = {
    "H": (0, 1),   # Horizontal: same row, next column
    "V": (1, 0),   # Vertical: next row, same column
    "D": (1, 1),   # Diagonal: next row, next column
}

# Parse step string like '2H' into individual moves
def parse_steps(step_string):
    steps = []
    for part in step_string.split(", "):
        count = int(part[:-1])
        direction = part[-1]
        steps.extend([direction] * count)
    return steps

# Generate grid for a given pattern
def generate_grid(steps, size=7):
    grid = np.full((size, size), '.', dtype=str)
    r, c = 0, 0
    grid[r, c] = '■'
    for step in steps:
        dr, dc = directions[step]
        r += dr
        c += dc
        if 0 <= r < size and 0 <= c < size:
            grid[r, c] = '■'
    return grid

# Pattern table
patterns = {
    "Mini Arc": "1H, 1D, 1V",
    "Small Arc": "2H, 1D, 2V",
    "Wide Arc": "3H, 1D, 3V",
    "Smooth Arc": "2H, 2D, 2V",
    "Sharp Slope": "1H, 1V",
    "45° Diagonal": "1D, 1D, 1D",
    "Steep Curve": "2H, 3D, 2V",
    "Flat-Top Arc": "2H, 1D, 1V, 1D, 2V",
    "Shallow Curve": "1H, 2D, 1V",
    "Ellipse Slice": "3H, 2D, 1V",
    "Smooth Drop": "1H, 1D, 1D, 1V",
    "Bullet Tip": "1V, 1D, 1H, 1D, 1V",
    "Dome Top": "2H, 1D, 1H, 1D, 2V",
    "Corner Bubble": "1V, 1D, 1H, 1D, 1V",
    "Wavy Segment": "1H, 1D, 1V, 1D, 1H",
}

# Plot all patterns in a grid
fig, axes = plt.subplots(nrows=5, ncols=3, figsize=(12, 18))
axes = axes.flatten()

for ax, (name, step_str) in zip(axes, patterns.items()):
    steps = parse_steps(step_str)
    grid = generate_grid(steps, size=7)
    ax.set_title(name, fontsize=9)
    ax.imshow(grid == '■', cmap='Greys', vmin=0, vmax=1)
    ax.set_xticks(range(7))
    ax.set_yticks(range(7))
    ax.set_xticklabels(range(7))
    ax.set_yticklabels(range(7))
    ax.grid(True, color='lightgray')
    for r in range(7):
        for c in range(7):
            if grid[r, c] == '■':
                ax.text(c, r, '■', va='center', ha='center', fontsize=9)
    ax.invert_yaxis()

plt.tight_layout()
plt.show()

```
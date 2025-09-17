# 📦 Circular Placement of Objects Along a Ring

When designing visual elements, data points, or decorative patterns that follow a circular path, a common task is to place multiple objects evenly around the circumference of a circle (or ring).

This note explores the **mathematical foundation**, explains why we do certain calculations, and provides step-by-step reasoning both **with and without spacing** between the objects.

---

## 🧭 Problem Statement

**Given:**

- $R$: radius of the main ring (the big circle)
- $(c_x, c_y)$: center point of the ring
- $r$: radius of each small circle to place along the ring

**Goal:**

- Find where to place these small circles so that:
  - They are evenly spaced around the ring.
  - Optionally, add spacing $s$ between them.
- Return a list of positions and sizes for these circles.

---

## ✅ Step-by-Step Process

### 1️⃣ Define the ring

The ring is a circle with circumference:

$$
C = 2\pi R
$$

---

### 2️⃣ Decide how many objects, $N$, to place

#### **Case A: No spacing (tight packing)**

Circles just touch each other.

- The straight-line distance between centers of adjacent circles (chord length):

$$
2r
$$

- This chord must match the distance between adjacent points on the ring:

$$
2r = 2R \cdot \sin\left(\frac{\pi}{N}\right)
$$

Which gives:

$$
r = R \cdot \sin\left(\frac{\pi}{N}\right)
$$

- Rearranged to compute $N$ given $r$:

$$
N = \left\lfloor \frac{\pi}{\arcsin\left(\frac{r}{R}\right)} \right\rfloor
$$

This gives the **maximum number of small circles** that fit on the ring without overlapping.

---

#### **Case B: With spacing $s$**

Now, between adjacent circles, there is an arc distance $s$ (between their edges).

- The arc distance between centers is:

$$
2r + s
$$

- Number of objects:

$$
N = \left\lfloor \frac{C}{2r + s} \right\rfloor
$$

or equivalently:

$$
N = \left\lfloor \frac{2\pi R}{2r + s} \right\rfloor
$$

---

### 3️⃣ Calculate angular step

A full circle has $2\pi$ radians.

$$
\theta_{\text{step}} = \frac{2\pi}{N}
$$

This is the angle between adjacent objects from the center of the ring.

---

### 4️⃣ Find the position of each object

Loop over $i = 0, 1, 2, \ldots, N-1$:

$$
\theta_i = \theta_{\text{step}} \cdot i = \frac{2\pi}{N} \cdot i
$$

Then compute the Cartesian coordinates:

$$
x_i = c_x + R \cdot \cos(\theta_i)
$$

$$
y_i = c_y + R \cdot \sin(\theta_i)
$$

Each $(x_i, y_i)$ is the center of a small circle.

---

### 5️⃣ Set radius of each small circle

- In tight packing:

$$
r = R \cdot \sin\left(\frac{\pi}{N}\right)
$$

- In manual spacing:  
  $r$ is chosen by you; spacing $s$ controls the gaps.

---

## 🧠 Why $\theta_i = \frac{2\pi}{N} \cdot i$?

- $i$ is just an index (0, 1, 2, …)
- $\frac{2\pi}{N}$ is the fixed angular step to place points evenly.
- Multiplying gives the actual angle in radians.

This covers the entire circle from angle $0$ up to just below $2\pi$.

---

## ✏️ Summary Table

| Step | Purpose | Formula |
|-----|--------|--------|
| Find number of objects $N$ | Without spacing | $$N = \left\lfloor \frac{\pi}{\arcsin\left(\frac{r}{R}\right)} \right\rfloor$$ |
| | With spacing | $$N = \left\lfloor \frac{2\pi R}{2r + s} \right\rfloor$$ |
| Angular step | Angle between objects | $$\theta_{\text{step}} = \frac{2\pi}{N}$$ |
| Position of each object | $(x_i, y_i)$ | $$x_i = c_x + R \cdot \cos(\theta_i)$$ <br> $$y_i = c_y + R \cdot \sin(\theta_i)$$ |
| Object radius in tight packing |  | $$r = R \cdot \sin\left(\frac{\pi}{N}\right)$$ |

---

## ✨ Why spacing?

Spacing $s$ lets you add gaps between objects to make them less crowded.

If spacing isn't needed, tight packing uses pure geometry.

---

## ✅ Practical uses

- Visual patterns
- Radial menus
- LEDs along a ring
- Clock dials
- Circular text or decorations

---

## ✅ Conclusion

To place objects evenly around a ring:

1. Start with ring center and radius.
2. Decide spacing (or not).
3. Compute how many objects fit.
4. Use angular step and trigonometry to compute positions.

This method ensures **evenly spaced, beautiful circular layouts**, whether tightly packed or with deliberate gaps.


# Code 
```java
// === Ring and circle parameters ===
float ringRadius = 150;   // radius of the main ring
float smallCircleRadius = 15; // radius for the interactive ring (blue)
float spacing = 10;          // spacing between small circles in the interactive ring

// === Fixed tight-packing ring parameters ===
float fixedCircleRadius = 20; // small circle radius for tight packing ring (red)

void setup() {
  size(500, 500);
}

void draw() {
  background(255);
  float centerX = width / 2;
  float centerY = height / 2;

  // --- Draw fixed tight-packing ring ---
  drawTightPackingRing(centerX, centerY);

  // --- Draw interactive ring with spacing ---
  drawSpacingRing(centerX, centerY);

  // --- Draw info text ---
  drawInfoText();
}

// ------------------------------------------------------------
// Draws the tight-packing ring where circles just touch
void drawTightPackingRing(float cx, float cy) {
  // Compute how many circles can fit
  int numCircles = (int)floor(PI / asin(fixedCircleRadius / ringRadius));
  // Compute actual radius to fit perfectly
  float actualRadius = ringRadius * sin(PI / numCircles);
  
  drawRing(cx, cy, ringRadius, numCircles, actualRadius, color(200, 100, 100));
}

// ------------------------------------------------------------
// Draws the interactive ring where user controls circle radius and spacing
void drawSpacingRing(float cx, float cy) {
  // Compute number of circles based on spacing and desired small circle radius
  float perimeter = TWO_PI * ringRadius;
  float arcPerCircle = 2 * smallCircleRadius + spacing;
  int numCircles = (int)floor(perimeter / arcPerCircle);

  drawRing(cx, cy, ringRadius, numCircles, smallCircleRadius, color(100, 150, 250));
}

// ------------------------------------------------------------
// Draws a ring of N circles with given radius and color
void drawRing(float cx, float cy, float R, int N, float circleRadius, color col) {
  float angleStep = TWO_PI / N;

  fill(col);
  noStroke();

  for (int i = 0; i < N; i++) {
    float angle = angleStep * i;
    float x = cx + R * cos(angle);
    float y = cy + R * sin(angle);
    ellipse(x, y, 2 * circleRadius, 2 * circleRadius);
  }
}

// ------------------------------------------------------------
// Displays current interactive parameters on screen
void drawInfoText() {
  fill(0);
  textSize(14);
  textAlign(LEFT);

  text("Interactive Ring Controls:", 10, height - 60);
  text("r2 (radius): " + nf(smallCircleRadius, 1, 1) + "    [+ / - to adjust]", 10, height - 40);
  text("s (spacing): " + nf(spacing, 1, 1) + "    [ ] / [ to adjust]", 10, height - 20);
}

// ------------------------------------------------------------
// Handle key presses to adjust parameters
void keyPressed() {
  if (key == '+') {
    smallCircleRadius += 1;
  } else if (key == '-') {
    smallCircleRadius = max(1, smallCircleRadius - 1);
  } else if (key == ']') {
    spacing += 2;
  } else if (key == '[') {
    spacing = max(0, spacing - 2);
  }
}


```
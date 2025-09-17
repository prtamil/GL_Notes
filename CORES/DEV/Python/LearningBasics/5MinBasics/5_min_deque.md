### **5-Minute Python `deque` (Double-Ended Queue) Cheat Sheet** ⏳🚀

💡 `deque` (from `collections`) is a **fast, flexible list-like** data structure optimized for **fast appends and pops** from both ends.

---

### 🔹 **Import & Create**

```py
from collections import deque

d = deque([1, 2, 3, 4, 5])  # Create a deque
d = deque()                 # Create an empty deque
d = deque("hello")          # Create deque from a string → deque(['h', 'e', 'l', 'l', 'o'])

```
---

### 🔄 **Adding Elements**

```py
d.append(6)        # Add to right → deque([1, 2, 3, 4, 5, 6])
d.appendleft(0)    # Add to left → deque([0, 1, 2, 3, 4, 5, 6])
d.extend([7, 8])   # Extend right → deque([0, 1, 2, 3, 4, 5, 6, 7, 8])
d.extendleft([-2, -1]) # Extend left (reversed order) → deque([-1, -2, 0, 1, 2, 3, 4, 5, 6, 7, 8])

```
---

### ❌ **Removing Elements**

```py
d.pop()            # Remove from right → returns 8
d.popleft()        # Remove from left → returns -1
d.remove(3)        # Remove first occurrence of 3
d.clear()          # Empty the deque → deque([])

```
---

### 🔄 **Rotating & Reversing**

```py
d.rotate(2)        # Rotate right by 2 → deque([4, 5, 6, 7, 8, -2, 0, 1, 2])
d.rotate(-2)       # Rotate left by 2 → deque([-2, 0, 1, 2, 4, 5, 6, 7, 8])
d.reverse()        # Reverse deque

```

---

### 🔍 **Checking & Converting**

```py
len(d)             # Get size of deque
list(d)            # Convert deque to list
"hello" in d       # Check if element exists → True/False

```

---

### 🏆 **Most Used `deque` One-Liners**

```py
deque(maxlen=5)     # Create a deque with max length (auto removes old elements)
d.count(2)          # Count occurrences of 2
d[0]                # Access first element
d[-1]               # Access last element


```

---

🔥 **Master these in 5 minutes, and you’ve got Python `deque` covered!** 🚀 Let me know if you need more! 😊
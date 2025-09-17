### **5-Minute Python Slicing Cheat Sheet** ⏳🚀

💡 **Slicing Syntax:**



`sequence[start:stop:step]`

- `start`: Starting index (inclusive)
- `stop`: Ending index (exclusive)
- `step`: Step size (default is `1`)

Works on **lists, tuples, strings, and ranges**!

---

### 🔹 **Basic Slicing**

```py
lst = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

lst[2:5]      # Slice from index 2 to 4 → [2, 3, 4]
lst[:5]       # First 5 elements → [0, 1, 2, 3, 4]
lst[5:]       # From index 5 to end → [5, 6, 7, 8, 9]
lst[:]        # Copy entire list → [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

```

---

### 🔥 **Using Step**

```py
lst[::2]      # Every second element → [0, 2, 4, 6, 8]
lst[1::2]     # Every second element, starting from index 1 → [1, 3, 5, 7, 9]
lst[::-1]     # Reverse the list → [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
lst[::-2]     # Reverse with step 2 → [9, 7, 5, 3, 1]

```
---

### 🔍 **String Slicing**

```py
s = "hello world"

s[:5]         # First 5 characters → 'hello'
s[-5:]        # Last 5 characters → 'world'
s[::2]        # Every second character → 'hlowrd'
s[::-1]       # Reverse string → 'dlrow olleh'

```

---

### 🔢 **Tuple & Range Slicing**

```py
t = (10, 20, 30, 40, 50)

t[1:4]        # Slice from index 1 to 3 → (20, 30, 40)

r = range(10)
list(r[2:7])  # Convert sliced range to list → [2, 3, 4, 5, 6]

```
---

### 🏆 **Most Used Slicing One-Liners**

```py
lst[:3]        # First 3 elements
lst[-3:]       # Last 3 elements
lst[1:-1]      # Remove first & last element
lst[::3]       # Every third element
lst[::-1]      # Reverse list
s[:3] + s[-3:] # First & last 3 chars of string

```

---

🔥 **Master these in 5 minutes, and you’ve got Python slicing covered!** 🚀 Let me know if you need more! 😊


```py
# Basic slicing
lst = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# 1. Get first N elements
first_n = lst[:3]  # [0, 1, 2]

# 2. Get last N elements
last_n = lst[-3:]  # [7, 8, 9]

# 3. Reverse a list
reversed_lst = lst[::-1]  # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]

# 4. Get every Nth element
every_second = lst[::2]  # [0, 2, 4, 6, 8]

# 5. Remove first N elements
skip_n = lst[3:]  # [3, 4, 5, 6, 7, 8, 9]

# 6. Remove last N elements
skip_last_n = lst[:-3]  # [0, 1, 2, 3, 4, 5, 6]

# 7. Get elements from index N to M (exclusive)
sublist = lst[2:6]  # [2, 3, 4, 5]

# 8. Get elements from index N to M with step K
step_slice = lst[1:8:2]  # [1, 3, 5, 7]

# 9. Copy a list
copied_lst = lst[:]  # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# 10. Trim first and last N elements
trimmed_lst = lst[2:-2]  # [2, 3, 4, 5, 6, 7]

# 11. Get middle element(s)
middle = lst[len(lst)//2] if len(lst) % 2 else lst[len(lst)//2-1 : len(lst)//2+1]

# 12. Flatten a list of lists (using sum trick)
nested = [[1, 2], [3, 4], [5, 6]]
flattened = sum(nested, [])  # [1, 2, 3, 4, 5, 6]

# 13. Remove first and last elements
inner = lst[1:-1]  # [1, 2, 3, 4, 5, 6, 7, 8]

# 14. Rotate list left by N places
rotate_left = lst[3:] + lst[:3]  # [3, 4, 5, 6, 7, 8, 9, 0, 1, 2]

# 15. Rotate list right by N places
rotate_right = lst[-3:] + lst[:-3]  # [7, 8, 9, 0, 1, 2, 3, 4, 5, 6]

```
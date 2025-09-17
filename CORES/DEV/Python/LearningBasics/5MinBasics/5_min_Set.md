### **5-Minute Python Set Methods Cheat Sheet** ⏳🚀

---

### 🔹 **Creating & Basics**

```py
s = {1, 2, 3, 4, 5}     # Define a set
s = set([1, 2, 3, 3, 4]) # Remove duplicates → {1, 2, 3, 4}

```
---

### 🔄 **Adding & Removing Elements**

```py
s.add(6)           # Add a single element → {1, 2, 3, 4, 5, 6}
s.update([7, 8])   # Add multiple elements → {1, 2, 3, 4, 5, 6, 7, 8}
s.remove(3)        # Remove element (error if not found)
s.discard(10)      # Remove element safely (no error)
s.pop()            # Remove and return a random element
s.clear()          # Empty the set

```
---

### 🔍 **Set Operations**

```py
a = {1, 2, 3}
b = {3, 4, 5}

a | b   # Union → {1, 2, 3, 4, 5}
a & b   # Intersection → {3}
a - b   # Difference → {1, 2} (in a but not in b)
b - a   # Difference → {4, 5}
a ^ b   # Symmetric Difference → {1, 2, 4, 5} (elements in either but not both)

```

---

### 🔥 **Checking & Comparing**

```py
3 in s          # Check if element exists → True
a.issubset(b)   # Check if a is subset of b
b.issuperset(a) # Check if b is superset of a
a.isdisjoint(b) # Check if no common elements → False


```

---

### 🔄 **Copying & Converting**

```py
s2 = s.copy()           # Copy set
lst = list(s)           # Convert set to list
s = set(lst)            # Convert list to set (remove duplicates)

```
---

### 🏆 **Most Used Set One-Liners**

```py
len(s)                # Get size of set
max(s)                # Get max element
min(s)                # Get min element
set("hello")          # Convert string to set → {'h', 'e', 'l', 'o'}

```

---

🔥 **Master these in 5 minutes, and you’ve got Python sets covered!** 🚀 Let me know if you need more! 😊
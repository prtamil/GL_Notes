Here’s a **5-minute Python List Methods Cheat Sheet** ⏳🚀

---

### 🔹 **Basic List Methods**

```py
lst = [1, 2, 3, 4, 5]
lst.append(6)      # Add single element → [1, 2, 3, 4, 5, 6]
lst.extend([7, 8]) # Add multiple elements → [1, 2, 3, 4, 5, 6, 7, 8]
lst.insert(2, 99)  # Insert 99 at index 2 → [1, 2, 99, 3, 4, 5, 6, 7, 8]

```

---

### 🔥 **Removing Elements**

```py
lst.pop()          # Remove last item → [1, 2, 99, 3, 4, 5, 6, 7] (returns 8)
lst.pop(2)         # Remove item at index 2 → [1, 2, 3, 4, 5, 6, 7] (returns 99)
lst.remove(4)      # Remove first occurrence of 4 → [1, 2, 3, 5, 6, 7]
del lst[1]         # Delete element at index 1 → [1, 3, 5, 6, 7]
lst.clear()        # Empty the list → []

```
---

### 🔄 **Sorting & Reversing**

```py
lst = [3, 1, 4, 1, 5, 9]
lst.sort()         # Sort in ascending order → [1, 1, 3, 4, 5, 9]
lst.sort(reverse=True) # Descending order → [9, 5, 4, 3, 1, 1]
lst.reverse()      # Reverse list → [1, 1, 3, 4, 5, 9]
sorted(lst)        # Get sorted copy without modifying → [1, 1, 3, 4, 5, 9]

```

---

### 🔍 **Finding & Counting**

```py
lst = [10, 20, 30, 40, 50, 20]
lst.index(20)      # Get index of first occurrence → 1
lst.count(20)      # Count occurrences of 20 → 2
min(lst)           # Get min value → 10
max(lst)           # Get max value → 50
sum(lst)           # Sum of all elements → 170
len(lst)           # Length of list → 6

```

---

### 🔀 **Copying & Duplicates**

```py
copy_lst = lst.copy()   # Create a copy of the list
unique_lst = list(set(lst))  # Remove duplicates → [10, 20, 30, 40, 50]

```

---

### 🔥 **Most Used List One-Liners**

```py
lst[-1]          # Get last element
lst[:3]          # First 3 elements
lst[-3:]         # Last 3 elements
lst[::-1]        # Reverse list
lst[::2]         # Every second element

```

---

🔥 **Master these in 5 minutes, and you’ve got Python lists covered!** 🚀 Let me know if you need more!
### **5-Minute Python Dictionary Methods Cheat Sheet** ⏳🚀

---

### 🔹 **Creating & Accessing Dictionary**

```py
d = {"name": "Alice", "age": 25, "city": "New York"}
d["name"]         # Access value → 'Alice'
d.get("age")      # Get value safely → 25
d.get("salary", 0)# Default if key not found → 0

```
---

### 🔄 **Adding & Updating**

```py
d["age"] = 26     # Update value
d["gender"] = "F" # Add new key-value pair
d.update({"job": "Engineer", "age": 27}) # Update multiple keys

```

---

### ❌ **Removing Elements**

```py
d.pop("city")     # Remove key and return value → 'New York'
del d["age"]      # Delete key-value pair
d.popitem()       # Remove and return last item (Python 3.7+)
d.clear()         # Empty the dictionary

```

---

### 🔍 **Checking Keys & Values**

```py
"name" in d       # Check if key exists → True/False
d.keys()          # Get all keys → dict_keys(['name', 'gender', 'job'])
d.values()        # Get all values → dict_values(['Alice', 'F', 'Engineer'])
d.items()         # Get all key-value pairs → dict_items([('name', 'Alice'), ...])

```

---

### 🔄 **Looping Over Dictionary**

```py
for k, v in d.items():  # Iterate over key-value pairs
    print(k, v)

for key in d:           # Iterate over keys
    print(key, d[key])

```

---

### 🔥 **Copying & Merging**

```py
d2 = d.copy()           # Create a copy
d3 = {**d, "salary": 5000}  # Merge dictionaries
d.update({"salary": 5000})  # Merge & update

```

---

### 🏆 **Most Used Dictionary One-Liners**

```py
len(d)             # Get dictionary size
list(d.keys())     # Get list of keys
list(d.values())   # Get list of values
list(d.items())    # Get list of key-value pairs
dict.fromkeys(["a", "b", "c"], 0)  # Create dict with default values

```

---

🔥 **Master these in 5 minutes, and you’ve got Python dictionaries covered!** 🚀 Let me know if you need more! 😊
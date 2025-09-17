### **5-Minute Python String Methods Cheat Sheet** ⏳🚀

---

### 🔹 **Basic String Methods**

```py
s = "hello world"
s.upper()         # Convert to uppercase → 'HELLO WORLD'
s.lower()         # Convert to lowercase → 'hello world'
s.title()         # Title case → 'Hello World'
s.capitalize()    # Capitalize first letter → 'Hello world'
s.swapcase()      # Swap case → 'HELLO WORLD'

```

---

### 🔍 **Searching & Checking**

```py
s.find("o")       # First occurrence index → 4
s.rfind("o")      # Last occurrence index → 7
s.count("l")      # Count occurrences of 'l' → 3
"hello" in s      # Check if "hello" exists → True
s.startswith("he")# Check prefix → True
s.endswith("ld")  # Check suffix → True

```

---

### ✂️ **Slicing & Substrings**

```py
s[0]             # First character → 'h'
s[-1]            # Last character → 'd'
s[:5]            # First 5 chars → 'hello'
s[-5:]           # Last 5 chars → 'world'
s[::2]           # Every second character → 'hlowrd'
s[::-1]          # Reverse string → 'dlrow olleh'

```

---

### 🛠 **Modifying & Cleaning**

```py
s.strip()        # Remove leading/trailing spaces
s.replace("world", "Python") # Replace substring → 'hello Python'
s.split()        # Split into words → ['hello', 'world']
"-".join(["hello", "world"]) # Join list into string → 'hello-world'
s.center(20, "*") # Center align → '****hello world****'

```

---

### 🔢 **Character & Encoding**

```py
ord('A')         # Get ASCII value → 65
chr(65)          # Get character from ASCII → 'A'
s.encode()       # Convert to bytes
b'hello'.decode()# Convert bytes to string

```

---

### ✅ **Checking Characters**

```py
s.isalpha()      # Check if all chars are alphabets
s.isdigit()      # Check if all chars are digits
s.isalnum()      # Check if alphanumeric
s.isspace()      # Check if whitespace only
s.islower()      # Check if all lowercase
s.isupper()      # Check if all uppercase

```

---

### 🔥 **Most Used String One-Liners**

```py
s[-1]           # Get last character
s[:3]           # First 3 characters
s[-3:]          # Last 3 characters
s[::2]          # Every second character
s[::-1]         # Reverse string
"".join(reversed(s))  # Another way to reverse
len(s)          # String length

```

---

🔥 **Master these in 5 minutes, and you’ve got Python strings covered!** 🚀 Let me know if you need more! 😊
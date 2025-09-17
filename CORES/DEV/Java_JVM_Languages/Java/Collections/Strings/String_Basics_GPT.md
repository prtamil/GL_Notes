# Basic 
Here are the essential Java string processing methods for your tasks, written in a simple and memorable way:

### **1. Split string into characters, words, sentences**

```java
String str = "Hello, world! Java is fun.";

// Split into characters
char[] chars = str.toCharArray();

// Split into words
String[] words = str.split("\\s+");

// Split into sentences
String[] sentences = str.split("[.!?]\\s*"); 

```

---

### **2. Join characters, words, sentences back**

```java
// Join characters
String joinedChars = String.valueOf(chars);

// Join words
String joinedWords = String.join(" ", words);

// Join sentences
String joinedSentences = String.join(". ", sentences) + ".";

```

---

### **3. Convert String to Set, List**

```java
import java.util.*;

List<String> wordList = Arrays.asList(words); // String to List
Set<String> wordSet = new HashSet<>(wordList); // String to Set

```

---

### **4. Convert Set, List to String**

```java
String listToString = String.join(", ", wordList); // List to String
String setToString = String.join(", ", wordSet); // Set to String

```

---

### **5. Reverse a String**


```java
String reversed = new StringBuilder(str).reverse().toString();

```
---

### **6. Split by index**

```java
String part1 = str.substring(0, 5);
String part2 = str.substring(5);

```

---

### **7. Transform characters in a string**


```java
String upperCaseStr = str.toUpperCase();
String lowerCaseStr = str.toLowerCase();

// Replace vowels with '*'
String replaced = str.replaceAll("[aeiouAEIOU]", "*");

```
---

### **8. Format a string (printf style)**

```java
String name = "Alice";
int age = 25;
String formatted = String.format("Name: %s, Age: %d", name, age);

```

---

This covers all the cases concisely
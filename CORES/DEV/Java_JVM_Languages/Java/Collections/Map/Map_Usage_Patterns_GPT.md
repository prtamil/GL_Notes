Here are foundational usage patterns for the `Map` interface in modern Java. I'll use `HashMap` as an example implementation.

---

### **1. Create Frequencies of Characters from a String**

```java
import java.util.*;

public class CharFrequency {
    public static void main(String[] args) {
        String str = "hello world";
        Map<Character, Integer> freqMap = new HashMap<>();

        for (char c : str.toCharArray()) {
            freqMap.put(c, freqMap.getOrDefault(c, 0) + 1);
        }

        System.out.println(freqMap);
    }
}

```

> **Key Concepts**: `getOrDefault()`, counting frequencies.

---

### **2. Create Frequencies of Items from List/Set**

```java
import java.util.*;

public class ListSetFrequency {
    public static void main(String[] args) {
        List<String> items = List.of("apple", "banana", "apple", "orange", "banana", "banana");
        Map<String, Integer> freqMap = new HashMap<>();

        for (String item : items) {
            freqMap.put(item, freqMap.getOrDefault(item, 0) + 1);
        }

        System.out.println(freqMap);
    }
}

```

> **Key Concepts**: `getOrDefault()`, iterable collections.

---

### **3. Values in Map are Lists (Appending Values for a Key)**

```java
import java.util.*;

public class MultiValueMap {
    public static void main(String[] args) {
        Map<String, List<String>> multiValueMap = new HashMap<>();

        multiValueMap.computeIfAbsent("fruit", k -> new ArrayList<>()).add("apple");
        multiValueMap.computeIfAbsent("fruit", k -> new ArrayList<>()).add("banana");
        multiValueMap.computeIfAbsent("vegetable", k -> new ArrayList<>()).add("carrot");

        System.out.println(multiValueMap);
    }
}

```

> **Key Concepts**: `computeIfAbsent()`, appending to a list.

---

### **4. Iterate Over Key-Value Pairs, Keys, and Values**

```java
import java.util.*;

public class IterateMap {
    public static void main(String[] args) {
        Map<String, Integer> map = Map.of("A", 1, "B", 2, "C", 3);

        // Iterate over key-value pairs
        for (Map.Entry<String, Integer> entry : map.entrySet()) {
            System.out.println(entry.getKey() + " -> " + entry.getValue());
        }

        // Iterate over keys
        for (String key : map.keySet()) {
            System.out.println("Key: " + key);
        }

        // Iterate over values
        for (Integer value : map.values()) {
            System.out.println("Value: " + value);
        }
    }
}

```

> **Key Concepts**: `entrySet()`, `keySet()`, `values()`.

---

### **5. Map Function Over Key-Value Pairs**

```java
import java.util.*;

public class MapFunction {
    public static void main(String[] args) {
        Map<String, Integer> map = Map.of("A", 1, "B", 2, "C", 3);

        map.forEach((key, value) -> System.out.println(key + " -> " + (value * 2)));
    }
}

```

> **Key Concepts**: `forEach()`, lambda expressions.

---

### **6. Filter Function for Selecting Keys and Values**

```java
import java.util.*;
import java.util.stream.Collectors;

public class FilterMap {
    public static void main(String[] args) {
        Map<String, Integer> map = Map.of("A", 5, "B", 10, "C", 15);

        // Filter keys starting with "A"
        Map<String, Integer> filteredKeys = map.entrySet().stream()
            .filter(e -> e.getKey().startsWith("A"))
            .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));

        // Filter values greater than 8
        Map<String, Integer> filteredValues = map.entrySet().stream()
            .filter(e -> e.getValue() > 8)
            .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));

        System.out.println("Filtered by Key: " + filteredKeys);
        System.out.println("Filtered by Value: " + filteredValues);
    }
}

```

> **Key Concepts**: `stream()`, `filter()`, `collect()`.

---

### **7. Reduce Map Items into a Singular Item**

```java
import java.util.*;

public class ReduceMap {
    public static void main(String[] args) {
        Map<String, Integer> map = Map.of("A", 1, "B", 2, "C", 3);

        int sum = map.values().stream().reduce(0, Integer::sum);
        System.out.println("Sum of values: " + sum);
    }
}

```

> **Key Concepts**: `reduce()`, `stream()`.

---

### **8. Get Top K Max Frequencies in a Frequency Map**

```java
import java.util.*;
import java.util.stream.Collectors;

public class TopKFrequent {
    public static void main(String[] args) {
        String str = "hello world";
        Map<Character, Integer> freqMap = new HashMap<>();

        for (char c : str.toCharArray()) {
            freqMap.put(c, freqMap.getOrDefault(c, 0) + 1);
        }

        int k = 3;
        List<Map.Entry<Character, Integer>> topK = freqMap.entrySet().stream()
            .sorted((a, b) -> b.getValue().compareTo(a.getValue())) // Descending order
            .limit(k)
            .collect(Collectors.toList());

        System.out.println("Top " + k + " most frequent: " + topK);
    }
}

```

> **Key Concepts**: `sorted()`, `limit()`, `collect()`.

---

### **9. Convert Key to Value and Value to Key (Handling Duplicates)**

```java
import java.util.*;

public class ReverseMap {
    public static void main(String[] args) {
        Map<String, String> original = Map.of("A", "1", "B", "2", "C", "1");
        Map<String, List<String>> reversed = new HashMap<>();

        for (Map.Entry<String, String> entry : original.entrySet()) {
            reversed.computeIfAbsent(entry.getValue(), k -> new ArrayList<>()).add(entry.getKey());
        }

        System.out.println(reversed);
    }
}

```

> **Key Concepts**: `computeIfAbsent()`, handling duplicate values.

---

### **10. Merge Two Maps with Summed Values**

```java
import java.util.*;

public class MergeMaps {
    public static void main(String[] args) {
        Map<String, Integer> map1 = Map.of("A", 1, "B", 2);
        Map<String, Integer> map2 = Map.of("A", 3, "C", 4);

        Map<String, Integer> merged = new HashMap<>(map1);
        map2.forEach((key, value) -> merged.merge(key, value, Integer::sum));

        System.out.println("Merged Map: " + merged);
    }
}

```

> **Key Concepts**: `merge()`, handling existing keys.

---

### **11. Replace All Values in Map**

```java
import java.util.*;

public class ReplaceValues {
    public static void main(String[] args) {
        Map<String, Integer> map = new HashMap<>(Map.of("A", 1, "B", 2, "C", 3));

        map.replaceAll((key, value) -> value * 2);
        System.out.println("Updated Map: " + map);
    }
}

```

> **Key Concepts**: `replaceAll()`.

---

These fundamental patterns will help you use `Map` efficiently in **modern Java** with functional programming features. Let me know if you want more patterns!
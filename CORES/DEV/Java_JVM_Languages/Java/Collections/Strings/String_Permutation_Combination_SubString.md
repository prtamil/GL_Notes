Here are the modified methods for **permutations**, **combinations**, and **subsets** that return a `List<String>` instead of printing them.

---

## **1. Permutations (All Possible Arrangements)**

### **Mental Model**: Arranging letters in all possible ways.

- The number of **permutations** for a string of length `N` is **N! (factorial)**.

```java
import java.util.*;

public class StringPermutations {
    public static List<String> getPermutations(String str) {
        List<String> result = new ArrayList<>();
        permute(str, "", result);
        return result;
    }

    private static void permute(String str, String chosen, List<String> result) {
        if (str.isEmpty()) {
            result.add(chosen);
            return;
        }

        for (int i = 0; i < str.length(); i++) {
            char ch = str.charAt(i);
            String remaining = str.substring(0, i) + str.substring(i + 1);
            permute(remaining, chosen + ch, result);
        }
    }

    public static void main(String[] args) {
        System.out.println(getPermutations("ABC"));
    }
}

```

### **Example Output for `"ABC"`**

plaintext



`[ABC, ACB, BAC, BCA, CAB, CBA]`

---

## **2. Combinations (Picking Characters, Order Doesn't Matter)**

### **Mental Model**: Picking people for a team.

- Unlike permutations, **order does not matter** in combinations.
- There are **2ⁿ - 1 combinations** (excluding the empty set).

```java
import java.util.*;

public class StringCombinations {
    public static List<String> getCombinations(String str) {
        List<String> result = new ArrayList<>();
        combine(str, "", 0, result);
        return result;
    }

    private static void combine(String str, String chosen, int index, List<String> result) {
        if (index == str.length()) {
            if (!chosen.isEmpty()) result.add(chosen); // Skip empty combination
            return;
        }

        // Include the current character
        combine(str, chosen + str.charAt(index), index + 1, result);
        
        // Exclude the current character
        combine(str, chosen, index + 1, result);
    }

    public static void main(String[] args) {
        System.out.println(getCombinations("ABC"));
    }
}

```

### **Example Output for `"ABC"`**

plaintext



`[A, AB, ABC, AC, B, BC, C]`

---

## **3. Subsets (Power Set, Includes Empty Set)**

### **Mental Model**: Generating all subsets (power set).

- **Includes the empty set**.
- The number of **subsets** for `N` characters is `2ⁿ` (Power Set).

```java
import java.util.*;

public class StringSubsets {
    public static List<String> getSubsets(String str) {
        List<String> result = new ArrayList<>();
        subset(str, "", 0, result);
        return result;
    }

    private static void subset(String str, String chosen, int index, List<String> result) {
        if (index == str.length()) {
            result.add(chosen); // Add all subsets, including the empty set
            return;
        }

        // Include the current character
        subset(str, chosen + str.charAt(index), index + 1, result);
        
        // Exclude the current character
        subset(str, chosen, index + 1, result);
    }

    public static void main(String[] args) {
        System.out.println(getSubsets("ABC"));
    }
}

```

### **Example Output for `"ABC"`**



CopyEdit

`["", "A", "AB", "ABC", "AC", "B", "BC", "C"]`

---

### **Quick Summary**

| Method           | Order Matters? | Includes Empty Set? | Output Example for `"ABC"`                     |
| ---------------- | -------------- | ------------------- | ---------------------------------------------- |
| **Permutations** | ✅ Yes          | ❌ No                | `["ABC", "ACB", "BAC", "BCA", "CAB", "CBA"]`   |
| **Combinations** | ❌ No           | ❌ No                | `["A", "AB", "ABC", "AC", "B", "BC", "C"]`     |
| **Subsets**      | ❌ No           | ✅ Yes               | `["", "A", "AB", "ABC", "AC", "B", "BC", "C"]` |

---

Now you have **optimized** and **easy-to-use** functions that return `List<String>` instead of printing the results.
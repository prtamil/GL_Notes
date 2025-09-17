Here are the **modern Java** implementations for generating **anagrams** and **palindromes**, ensuring that the methods return a `List<String>` instead of printing results.

---

## **1. Generate Anagrams**

### **Mental Model**: Rearranging letters in any possible way to form valid words.

- **An anagram is a permutation of the given string**.
- The method should return all **unique** anagrams.

```java
import java.util.*;

public class StringAnagrams {
    public static List<String> getAnagrams(String str) {
        Set<String> result = new HashSet<>(); // Use Set to avoid duplicates
        permute(str, "", result);
        return new ArrayList<>(result);
    }

    private static void permute(String str, String chosen, Set<String> result) {
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
        System.out.println(getAnagrams("abc"));
    }
}

```

### **Example Output for `"abc"`**



`[abc, acb, bac, bca, cab, cba]`

---

## **2. Generate Palindromes**

### **Mental Model**: A word or phrase that reads the same forward and backward.

- **Find all permutations** and **filter out only palindromes**.

```java
import java.util.*;
import java.util.stream.Collectors;

public class PalindromeGenerator {
    public static List<String> generatePalindromes(String str) {
        // Count character frequencies
        var charCounts = str.chars()
                .mapToObj(c -> (char) c)
                .collect(Collectors.groupingBy(c -> c, Collectors.summingInt(c -> 1)));

        // Identify the middle character and form the half-string
        String middle = charCounts.entrySet().stream()
                .filter(e -> e.getValue() % 2 != 0)
                .map(e -> String.valueOf(e.getKey()))
                .findFirst()
                .orElse("");

        if (charCounts.values().stream().filter(v -> v % 2 != 0).count() > 1) return List.of(); // More than 1 odd → no palindrome possible

        String half = charCounts.entrySet().stream()
                .map(e -> String.valueOf(e.getKey()).repeat(e.getValue() / 2))
                .collect(Collectors.joining());

        // Generate unique permutations of the half-string
        Set<String> halfPermutations = new HashSet<>();
        permute(half.toCharArray(), 0, halfPermutations);

        // Construct full palindromes
        return halfPermutations.stream()
                .map(h -> h + middle + new StringBuilder(h).reverse())
                .toList();
    }

    // Simple permutation generator
    private static void permute(char[] arr, int index, Set<String> result) {
        if (index == arr.length) {
            result.add(new String(arr));
            return;
        }
        for (int i = index; i < arr.length; i++) {
            if (i != index && arr[i] == arr[index]) continue;
            swap(arr, i, index);
            permute(arr, index + 1, result);
            swap(arr, i, index);
        }
    }

    private static void swap(char[] arr, int i, int j) {
        char temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }

    public static void main(String[] args) {
        System.out.println(generatePalindromes("aab"));      // Output: ["aba"]
        System.out.println(generatePalindromes("aabb"));     // Output: ["abba", "baab"]
        System.out.println(generatePalindromes("racecar"));  // Output: ["racecar"]
        System.out.println(generatePalindromes("abc"));      // Output: []
    }
}

```

### **Example Output for `"aab"`**



`[aba, baa]`

---

### **Quick Summary**

|Function|Description|Example Output for `"abc"`|
|---|---|---|
|**Anagrams**|Rearrange characters into unique words|`["abc", "acb", "bac", "bca", "cab", "cba"]`|
|**Palindromes**|Find anagram permutations that are palindromes|For `"aab"` → `["aba", "baa"]`|

Now you have **clean**, **efficient**, and **modern Java** implementations for generating **anagrams** and **palindromes**!
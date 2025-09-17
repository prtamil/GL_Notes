```java
import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;

public class HashMapExamples {
    
    // 1. Find frequencies of characters in a string
    public static Map<Character, Long> charFrequencies(String s) {
        return s.chars().mapToObj(c -> (char) c)
                .collect(Collectors.groupingBy(Function.identity(), Collectors.counting()));
    }

    // 2. Reverse key-value pairs in a map
    public static <K, V> Map<V, K> reverseMap(Map<K, V> map) {
        return map.entrySet().stream()
                .collect(Collectors.toMap(Map.Entry::getValue, Map.Entry::getKey));
    }

    // 3. Find top K most frequent letters in a string
    public static List<Map.Entry<Character, Long>> topKFrequentLetters(String s, int k) {
        return charFrequencies(s).entrySet().stream()
                .sorted((a, b) -> Long.compare(b.getValue(), a.getValue()))
                .limit(k)
                .collect(Collectors.toList());
    }

    // 4. Implement groupBy using HashMap
    public static <T, K> Map<K, List<T>> groupBy(List<T> items, Function<T, K> classifier) {
        return items.stream().collect(Collectors.groupingBy(classifier));
    }

    // 5. Easiest way to find key-value
    public static <K, V> void printMap(Map<K, V> map) {
        map.forEach((key, value) -> System.out.println(key + " -> " + value));
    }

    // 6. Hashtable with key and values as a List
    public static <K, V> Map<K, List<V>> createHashTable() {
        return new Hashtable<>();
    }

    // 7. Map, Reduce, Filter on HashMap
    public static int sumOfValues(Map<String, Integer> map) {
        return map.values().stream().reduce(0, Integer::sum);
    }

    public static Map<String, Integer> filterByValue(Map<String, Integer> map, int threshold) {
        return map.entrySet().stream()
                .filter(e -> e.getValue() > threshold)
                .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
    }

    public static void main(String[] args) {
        String text = "hello world";
        System.out.println("Character Frequencies: " + charFrequencies(text));

        Map<Integer, String> map = Map.of(1, "A", 2, "B", 3, "C");
        System.out.println("Reversed Map: " + reverseMap(map));

        System.out.println("Top 2 frequent letters: " + topKFrequentLetters(text, 2));

        List<String> items = Arrays.asList("apple", "banana", "cherry", "apple", "banana");
        System.out.println("Grouped by first letter: " + groupBy(items, s -> s.charAt(0)));

        Map<String, Integer> numMap = Map.of("a", 10, "b", 20, "c", 30);
        System.out.println("Sum of Values: " + sumOfValues(numMap));
        System.out.println("Filtered Map: " + filterByValue(numMap, 15));
    }
}

```

You're referring to using `map`, `reduce`, and `filter` with a `Map` (such as `HashMap`). Here's how you can use these operations with a `Map` in modern Java:

### 1. **map**:

In the context of `Map`, the `map` operation is typically used to transform keys or values. You can use `Map`'s `entrySet()` to apply transformations on the key-value pairs.

Example: **Transforming values in a `Map`:**

```java
Map<String, Integer> map = new HashMap<>();
map.put("a", 1);
map.put("b", 2);
map.put("c", 3);

// Use map() to apply a transformation to the values
Map<String, Integer> transformedMap = map.entrySet()
    .stream()
    .collect(Collectors.toMap(
        Map.Entry::getKey, // Keep the key the same
        entry -> entry.getValue() * 2 // Multiply values by 2
    ));

System.out.println(transformedMap); // Output: {a=2, b=4, c=6}

```


### 2. **filter**:

You can filter entries based on certain conditions using the `filter` method, and only keep the entries that match your criteria.

Example: **Filtering entries based on values in a `Map`:**

```java
Map<String, Integer> map = new HashMap<>();
map.put("a", 1);
map.put("b", 2);
map.put("c", 3);

// Use filter() to retain only the entries where the value is greater than 1
Map<String, Integer> filteredMap = map.entrySet()
    .stream()
    .filter(entry -> entry.getValue() > 1)
    .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));

System.out.println(filteredMap); // Output: {b=2, c=3}

```

### 3. **reduce**:

The `reduce` method can be used to aggregate values in the `Map`. For example, you might want to reduce the values in the `Map` into a single result.

Example: **Reducing values in a `Map` to their sum:**

```java
Map<String, Integer> map = new HashMap<>();
map.put("a", 1);
map.put("b", 2);
map.put("c", 3);

// Use reduce() to sum the values
int sum = map.values()
    .stream()
    .reduce(0, Integer::sum); // Start with 0, sum up the values

System.out.println(sum); // Output: 6

```

These methods allow you to process and manipulate `Map` objects using the modern `Stream` API in Java.
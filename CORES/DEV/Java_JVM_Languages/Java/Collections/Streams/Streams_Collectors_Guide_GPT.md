
java streams collect explained. how to use collectors. stringbuilders, how to write custom collectors

###### ChatGPT said:

Java Streams' `collect()` method is used to accumulate elements from a stream into a collection, a single value, or another data structure. The `Collectors` utility class provides built-in collectors for common operations.

---

## 1. **Basic `collect()` Usage**

The `collect()` method in Java Streams takes a `Collector` and accumulates elements from the stream.

Example: Convert a list of strings to a `List<String>` using `Collectors.toList()`

```java
import java.util.*;
import java.util.stream.Collectors;

public class Main {
    public static void main(String[] args) {
        List<String> names = Arrays.asList("Alice", "Bob", "Charlie");

        List<String> collectedNames = names.stream()
                                           .collect(Collectors.toList());

        System.out.println(collectedNames); // Output: [Alice, Bob, Charlie]
    }
}

```

---

## 2. **Common `Collectors` Methods**

### `Collectors.toList()`

Collects elements into a `List`.

```java
List<Integer> numbers = List.of(1, 2, 3, 4, 5);
List<Integer> list = numbers.stream().collect(Collectors.toList());

```

### `Collectors.toSet()`

Collects elements into a `Set`.

```java
Set<String> set = names.stream().collect(Collectors.toSet());

```

### `Collectors.toMap()`

Collects elements into a `Map`.

```java
Map<Integer, String> map = names.stream()
    .collect(Collectors.toMap(String::length, name -> name, (existing, replacement) -> existing));

```

### `Collectors.joining()`

Joins elements into a single string.

```java
String result = names.stream().collect(Collectors.joining(", "));
System.out.println(result); // Output: Alice, Bob, Charlie

```

---

## 3. **Using `StringBuilder` in Streams**

If you want to concatenate strings efficiently, using `StringBuilder` within `collect()` is a good choice.

Example: Concatenating strings using `StringBuilder`

```java
StringBuilder sb = names.stream()
    .collect(StringBuilder::new, StringBuilder::append, StringBuilder::append);
System.out.println(sb.toString()); // Output: AliceBobCharlie

```

Explanation:

- `StringBuilder::new` → Creates a new `StringBuilder`
- `StringBuilder::append` (accumulator) → Appends each element
- `StringBuilder::append` (combiner) → Merges partial results (useful in parallel streams)

---

## 4. **Writing Custom Collectors**

If built-in collectors don't meet your needs, you can write a custom `Collector`.

### **Custom Collector Example: Collecting into a StringBuilder**

```java
import java.util.*;
import java.util.stream.Collector;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class CustomCollectorExample {
    public static void main(String[] args) {
        List<String> words = Arrays.asList("Hello", "World", "Streams");

        StringBuilder result = words.stream()
                .collect(new StringBuilderCollector());

        System.out.println(result.toString()); // Output: HelloWorldStreams
    }

    public static class StringBuilderCollector implements Collector<String, StringBuilder, StringBuilder> {
        @Override
        public Supplier<StringBuilder> supplier() {
            return StringBuilder::new;
        }

        @Override
        public BiConsumer<StringBuilder, String> accumulator() {
            return StringBuilder::append;
        }

        @Override
        public BinaryOperator<StringBuilder> combiner() {
            return StringBuilder::append;
        }

        @Override
        public Function<StringBuilder, StringBuilder> finisher() {
            return sb -> sb;
        }

        @Override
        public Set<Characteristics> characteristics() {
            return Set.of(Characteristics.IDENTITY_FINISH);
        }
    }
}

```

### **Explanation of Custom Collector Components**

1. **`supplier()`** → Creates the container (`StringBuilder`).
2. **`accumulator()`** → Defines how elements are added (`append` to `StringBuilder`).
3. **`combiner()`** → Merges two `StringBuilder` objects (useful in parallel streams).
4. **`finisher()`** → Transforms the accumulated result (not needed for `StringBuilder`).
5. **`characteristics()`** → Defines behavior (`IDENTITY_FINISH` means no transformation is needed).

---

## 5. **When to Use Custom Collectors**

- When built-in collectors don’t meet your requirements.
- When you need better performance, e.g., using `StringBuilder` instead of `joining()`.
- When you need a completely different output format.

---

### **Summary**

|Collector|Purpose|
|---|---|
|`toList()`|Collects elements into a `List`|
|`toSet()`|Collects elements into a `Set`|
|`toMap()`|Collects elements into a `Map`|
|`joining()`|Concatenates elements into a single `String`|
|`reducing()`|Reduces elements to a single value|
|**Custom Collector**|Collects elements using a custom strategy|

---

Would you like an example of a custom collector for something else, like computing statistics? 🚀
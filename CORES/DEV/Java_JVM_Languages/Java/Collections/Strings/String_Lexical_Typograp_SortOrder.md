### **Sorting Strings in Modern Java (Java 21)**

Sorting a string can be done in **two ways**:

1. **Lexicographical Order** (Dictionary Order)
2. **Typographical Order** (Natural Order, Case-Insensitive)

---

### **1️⃣ Lexicographical Order (Default Sort)**

- Sorts characters **by ASCII value**
- `"A" < "B" < "Z" < "a" < "b" < "z"`
- Case-sensitive

#### **Code:**

```java
import java.util.Arrays;

public class StringSorting {
    public static String sortLexicographically(String str) {
        char[] chars = str.toCharArray();
        Arrays.sort(chars); // Default lexicographic sort
        return new String(chars);
    }

    public static void main(String[] args) {
        System.out.println(sortLexicographically("HelloWorld")); // "HWdellloor"
    }
}

```
---

### **2️⃣ Typographical Order (Natural Case-Insensitive Order)**

- **Ignores case** (Sorts `"A"` and `"a"` together)
- `"A" == "a" < "B" == "b" < "C" == "c"`
- More human-readable order

#### **Code:**

```java
import java.util.stream.Collectors;

public class StringSorting {
    public static String sortTypographically(String str) {
        return str.chars()
                .mapToObj(c -> (char) c)
                .sorted(String.CASE_INSENSITIVE_ORDER)
                .map(String::valueOf)
                .collect(Collectors.joining());
    }

    public static void main(String[] args) {
        System.out.println(sortTypographically("HelloWorld")); // "deHllloorW"
    }
}

```
---

### **💡 Key Differences**

|**Method**|**Sorting Order**|**Example Input**|**Sorted Output**|
|---|---|---|---|
|**Lexicographical**|ASCII-based (A-Z then a-z)|`"HelloWorld"`|`"HWdellloor"`|
|**Typographical**|Case-insensitive natural order|`"HelloWorld"`|`"deHllloorW"`|

---

### **🚀 Modern Java Features Used**

✅ **Streams (`str.chars().mapToObj(...)`)** for character sorting  
✅ **`String.CASE_INSENSITIVE_ORDER`** for natural sorting  
✅ **Functional programming (`Collectors.joining()`)** for clean processing

This makes the code **modern, concise, and easy to understand**!
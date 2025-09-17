what is static keyword in java can you list various ways we use static in java interms of latest java 21 lts.

In Java, the `static` keyword is used to define members (variables, methods, blocks, and nested classes) that belong to the class itself rather than to any specific instance of the class. This means that `static` members are shared across all instances of the class and can be accessed without creating an object of the class.

As of **Java 21 LTS**, the `static` keyword continues to be used in the same ways as in previous versions, but with some enhancements and best practices. Below are the various ways the `static` keyword is used in Java:

---

### 1. **Static Variables**

A `static` variable (also called a class variable) is shared among all instances of a class. It is initialized only once, at the start of the program execution, and is stored in a fixed memory location.

**Example:**

```java


class Counter {
    static int count = 0; // Static variable

    Counter() {
        count++; // Incremented for every object creation
    }
}

public class Main {
    public static void main(String[] args) {
        Counter c1 = new Counter();
        Counter c2 = new Counter();
        System.out.println("Total objects created: " + Counter.count); // Output: 2
    }
}
```

**Use Case:**

- To maintain a shared state across all instances of a class (e.g., counting the number of objects created).
    

---

### 2. **Static Methods**

A `static` method belongs to the class rather than any specific instance. It can be called directly using the class name without creating an object.

**Example:**

```java
class MathUtils {
    static int add(int a, int b) {
        return a + b;
    }
}

public class Main {
    public static void main(String[] args) {
        int result = MathUtils.add(5, 10); // Calling static method
        System.out.println("Result: " + result); // Output: 15
    }
}

```

**Use Case:**

- For utility methods that do not depend on instance variables (e.g., `Math.sqrt()`, `Collections.sort()`).
    
- Factory methods for creating objects.
    

---

### 3. **Static Block**

A `static` block is used to initialize static variables or perform one-time setup operations for the class. It is executed when the class is loaded into memory.

**Example:**

```java

class Database {
    static String connection;

    static {
        // Static block to initialize static variable
        connection = "Database connected";
        System.out.println(connection);
    }
}

public class Main {
    public static void main(String[] args) {
        // No need to create an object, static block is executed automatically
    }
}
```
**Use Case:**

- To initialize static variables or resources (e.g., database connections, configuration files).
    

---

### 4. **Static Nested Class**

A `static` nested class is a class defined inside another class with the `static` keyword. It does not have access to the instance variables and methods of the outer class.

**Example:**

```java


class Outer {
    static class Inner {
        void display() {
            System.out.println("Inside static nested class");
        }
    }
}

public class Main {
    public static void main(String[] args) {
        Outer.Inner inner = new Outer.Inner(); // Create object of static nested class
        inner.display();
    }
}
```


**Use Case:**

- To logically group classes that are only used in one place.
    
- To avoid unnecessary coupling between classes.
    

---

### 5. **Static Imports (Java 5+)**

Static imports allow you to access static members (variables and methods) of a class directly without qualifying them with the class name.

**Example:**

```java


import static java.lang.Math.*;

public class Main {
    public static void main(String[] args) {
        double result = sqrt(25) + pow(2, 3); // Directly using Math methods
        System.out.println("Result: " + result); // Output: 13.0
    }
}

```


**Use Case:**

- To improve code readability by reducing verbosity (e.g., using `sqrt()` instead of `Math.sqrt()`).
    

---

### 6. **Static Variables in Interfaces (Java 8+)**

Starting from Java 8, interfaces can have `static` variables and methods. These are implicitly `public`, `final`, and `static`.

**Example:**

```java


interface Constants {
    static final double PI = 3.14159; // Static variable in interface
    static void printMessage() {      // Static method in interface
        System.out.println("Hello from interface");
    }
}

public class Main {
    public static void main(String[] args) {
        System.out.println("PI: " + Constants.PI); // Accessing static variable
        Constants.printMessage(); // Calling static method
    }
}
```


**Use Case:**

- To define constants or utility methods in interfaces.
    

---

### 7. **Static Methods in Interfaces (Java 8+)**

Java 8 introduced `static` methods in interfaces, which can be used to define utility methods.

**Example:**

```java

interface MathOperations {
    static int add(int a, int b) {
        return a + b;
    }
}

public class Main {
    public static void main(String[] args) {
        int result = MathOperations.add(5, 10); // Calling static method in interface
        System.out.println("Result: " + result); // Output: 15
    }
}
```

**Use Case:**

- To provide utility methods that are related to the interface but do not depend on instance-specific data.
    

---

### 8. **Static Factory Methods (Java 9+)**

Java 9 introduced the ability to create private `static` methods in interfaces, which can be used as helper methods for `static` factory methods.

**Example:**


```java


interface Vehicle {
    static Vehicle createCar() {
        return new Car();
    }

    static Vehicle createBike() {
        return new Bike();
    }

    private static void logCreation(String type) {
        System.out.println("Creating a " + type);
    }

    class Car implements Vehicle {
        Car() {
            logCreation("Car");
        }
    }

    class Bike implements Vehicle {
        Bike() {
            logCreation("Bike");
        }
    }
}

public class Main {
    public static void main(String[] args) {
        Vehicle car = Vehicle.createCar();
        Vehicle bike = Vehicle.createBike();
    }
}

```

**Use Case:**

- To encapsulate object creation logic and provide a clean API for creating objects.
    

---

### Summary of Uses of `static` Keyword:

|**Context**|**Description**|
|---|---|
|**Static Variables**|Shared across all instances of a class.|
|**Static Methods**|Belong to the class and can be called without creating an object.|
|**Static Block**|Used for one-time initialization of static variables.|
|**Static Nested Class**|A nested class that does not have access to instance members of the outer class.|
|**Static Imports**|Allows direct access to static members without qualifying with the class name.|
|**Static in Interfaces**|Defines constants and utility methods in interfaces.|
|**Static Factory Methods**|Encapsulates object creation logic in interfaces or classes.|

---

### Key Points:

- `static` members are associated with the class rather than instances.
    
- They are loaded into memory when the class is loaded.
    
- Overuse of `static` can lead to tight coupling and make testing harder, so use it judiciously.
    
- Java 21 continues to support all these features, with no significant changes to the `static` keyword itself.
    



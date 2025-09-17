what is final class in java. can you list various ways we use final keyword in java and explain it

In Java, the `final` keyword is used to restrict the user from modifying certain elements of the code. It can be applied to variables, methods, and classes. Below is an explanation of the various ways the `final` keyword is used in Java:

---

### 1. **Final Class**

A `final` class is a class that cannot be extended (inherited). If you declare a class as `final`, no other class can inherit from it.

**Example:**

```java

final class FinalClass {
    // Class implementation
}

// This will cause a compilation error
// class SubClass extends FinalClass { }
```

**Use Case:**

- To prevent inheritance when you want to ensure that the class's behavior cannot be altered by subclasses.
    
- Commonly used for immutable classes like `String` in Java.
    

---

### 2. **Final Method**

A `final` method is a method that cannot be overridden by subclasses. If a method is declared as `final`, it ensures that the method's implementation remains unchanged in any subclass.

**Example:**

```java

class Parent {
    final void display() {
        System.out.println("This is a final method.");
    }
}

class Child extends Parent {
    // This will cause a compilation error
    // void display() { }
}
```


**Use Case:**

- To prevent subclasses from changing the behavior of critical methods.
    
- Often used in frameworks or libraries to ensure consistent behavior.
    

---

### 3. **Final Variable**

A `final` variable is a variable whose value cannot be changed once it is initialized. It acts as a constant.

**Example:**

```java

class Example {
    final int MAX_VALUE = 100;

    void modifyValue() {
        // This will cause a compilation error
        // MAX_VALUE = 200;
    }
}
```


**Use Case:**

- To define constants (e.g., `PI = 3.14`).
    
- To ensure that a variable's value remains unchanged throughout the program.
    

---

### 4. **Final Parameter**

A `final` parameter is a method parameter that cannot be modified inside the method.

**Example:**

```

void printMessage(final String message) {
    // This will cause a compilation error
    // message = "New Message";
    System.out.println(message);
}
```


**Use Case:**

- To prevent accidental modification of method parameters.
    
- Useful in lambda expressions and anonymous classes.
    

---

### 5. **Final with Static**

When `final` is used with `static`, it creates a constant that belongs to the class rather than an instance of the class.

**Example:**

```java

class Constants {
    static final double PI = 3.14159;
}
```


**Use Case:**

- To define global constants that are shared across all instances of a class.
    
- Commonly used in utility classes.
    

---

### Summary of Uses of `final` Keyword:

| **Context**         | **Description**                                                              |
| ------------------- | ---------------------------------------------------------------------------- |
| **Final Class**     | Prevents inheritance. No subclass can extend a final class.                  |
| **Final Method**    | Prevents method overriding in subclasses.                                    |
| **Final Variable**  | Makes a variable constant. Its value cannot be changed after initialization. |
| **Final Parameter** | Prevents modification of method parameters.                                  |
| **Static Final**    | Defines a class-level constant that cannot be changed.                       |

---

### Key Points:

- The `final` keyword ensures immutability, security, and consistency in your code.
    
- It is widely used in designing robust and maintainable applications.
    
- Overusing `final` can restrict flexibility, so use it judiciously.

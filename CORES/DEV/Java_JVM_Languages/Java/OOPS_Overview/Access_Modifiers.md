### **Access Modifiers in Java**

Access modifiers in Java define the **visibility (or scope) of variables, methods, and classes**. Java provides four access modifiers:

1. **public** – Accessible from anywhere.
2. **private** – Accessible only within the same class.
3. **protected** – Accessible within the same package and subclasses.
4. **default (package-private)** – Accessible only within the same package (when no modifier is specified).

---

## **1. `public` Access Modifier**

- **Scope**: Can be accessed **from anywhere** (inside the same class, same package, different package, or subclasses).
- **Use case**: Use `public` when you want a class, method, or variable to be accessible globally.

### **Example of `public`**

```java
package mypackage;

public class PublicExample {
    public String name = "Java";

    public void display() {
        System.out.println("Public Method: Hello, " + name);
    }
}

// Accessing it from another package
package anotherpackage;

import mypackage.PublicExample;

public class TestPublic {
    public static void main(String[] args) {
        PublicExample obj = new PublicExample();
        System.out.println(obj.name);  // Allowed
        obj.display();  // Allowed
    }
}

```

✅ The `PublicExample` class and its members are accessible **anywhere**.

---

## **2. `private` Access Modifier**

- **Scope**: Accessible **only within the same class**.
- **Use case**: Used to implement **Encapsulation** (restricting access to internal details).

### **Example of `private`**

```java
package mypackage;

public class PrivateExample {
    private String secret = "Top Secret Data";

    private void showSecret() {
        System.out.println("Private Method: " + secret);
    }

    public void accessSecret() {
        showSecret();  // Allowed inside the same class
    }
}

public class TestPrivate {
    public static void main(String[] args) {
        PrivateExample obj = new PrivateExample();
        // System.out.println(obj.secret);  // ❌ ERROR: secret is private
        // obj.showSecret();  // ❌ ERROR: private method cannot be accessed

        obj.accessSecret(); // ✅ Indirect access via a public method
    }
}

```

❌ `secret` and `showSecret()` cannot be accessed outside **PrivateExample**.  
✅ You can access them **indirectly** through a **public method (`accessSecret()`)**.

---

## **3. `protected` Access Modifier**

- **Scope**:
    - Accessible within the **same package**.
    - Accessible in **subclasses** (even if they are in a different package).
- **Use case**: Used when designing **inheritance**, allowing subclasses to access certain members while restricting them from the general public.

### **Example of `protected`**

```java
package mypackage;

public class ProtectedExample {
    protected String info = "Protected Data";

    protected void showInfo() {
        System.out.println("Protected Method: " + info);
    }
}

// Accessing it from the same package
package mypackage;

public class TestProtected {
    public static void main(String[] args) {
        ProtectedExample obj = new ProtectedExample();
        System.out.println(obj.info);  // ✅ Allowed (same package)
        obj.showInfo();  // ✅ Allowed (same package)
    }
}

// Accessing it from a different package using inheritance
package anotherpackage;

import mypackage.ProtectedExample;

public class SubClass extends ProtectedExample {
    public void display() {
        System.out.println(info);  // ✅ Allowed (via inheritance)
        showInfo();  // ✅ Allowed (via inheritance)
    }
}

public class TestProtectedInheritance {
    public static void main(String[] args) {
        SubClass obj = new SubClass();
        obj.display();

        // ProtectedExample obj2 = new ProtectedExample();  
        // ❌ ERROR: Cannot access directly from another package
    }
}

```

✅ `info` and `showInfo()` are **accessible in subclasses**, even in a different package.  
❌ But `ProtectedExample` members **cannot be accessed directly** from another package.

---

## **4. `default` (Package-Private) Access Modifier**

- **Scope**: Accessible **only within the same package**.
- **Use case**: Useful when you want to **restrict access** to package members without exposing them globally.

### **Example of `default` (no modifier)**

```java
package mypackage;

class DefaultExample {  // No modifier, so package-private
    String message = "Default Access";

    void showMessage() {
        System.out.println("Default Method: " + message);
    }
}

// Accessing it from the same package
package mypackage;

public class TestDefault {
    public static void main(String[] args) {
        DefaultExample obj = new DefaultExample();
        System.out.println(obj.message);  // ✅ Allowed (same package)
        obj.showMessage();  // ✅ Allowed (same package)
    }
}

// Trying to access from a different package (Will cause error)
package anotherpackage;

import mypackage.DefaultExample;  // ❌ ERROR: Cannot be accessed

public class TestDefaultOutside {
    public static void main(String[] args) {
        // DefaultExample obj = new DefaultExample();  // ❌ ERROR
    }
}

```

❌ `DefaultExample` and its members are **not accessible outside the package**.

---

## **Comparison Table**

|Modifier|Same Class|Same Package|Subclass (Different Package)|Other Packages|
|---|---|---|---|---|
|**public**|✅ Yes|✅ Yes|✅ Yes|✅ Yes|
|**private**|✅ Yes|❌ No|❌ No|❌ No|
|**protected**|✅ Yes|✅ Yes|✅ Yes|❌ No|
|**default**|✅ Yes|✅ Yes|❌ No|❌ No|

---

## **When to Use Each Access Modifier?**

|Modifier|When to Use?|
|---|---|
|**public**|Use when a class, method, or field should be accessible everywhere.|
|**private**|Use when you want to hide implementation details from outside classes (Encapsulation).|
|**protected**|Use in inheritance when subclasses should access a member but not unrelated classes.|
|**default**|Use when you want to restrict access to the same package only (useful for modular design).|

---

## **Final Thoughts**

Understanding access modifiers helps in **designing secure, maintainable, and modular** applications.

- Use `private` for **encapsulation**.
- Use `public` **sparingly**, only when necessary.
- Use `protected` in **inheritance**.
- Use `default` for **package encapsulation**.

Do you want me to provide **real-world examples** (like a Bank Account or Employee system) using these concepts?
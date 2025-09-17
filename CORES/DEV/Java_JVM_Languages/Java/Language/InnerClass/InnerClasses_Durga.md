# Inner Class

## Purpose

Without exist on one type of object if there is no chance of existing another type of object then use innerclass.

without University object exist Department object should not exist.

Interface Entry is defined inside Interface Map.

Relation between outer class and inner class is "has-a" (Composition/Aggregation)

## Modifiers applied for OuterClass and InnerClass

OuterClass [5] 

	1.  public
	2.  <default>
	3.  final
	4.  abstract
	5.  strictfp


InnerClass  Additional to Outerclass modifiers [8] 

	1. private
	2. protected
	3. static


## Types of InnerClass
 
	
based on position , Declaration, Position of Declaration (inside class, method) we have 4 tpes

1. Normal or Regular inner class
2. Method local inner class
3. anonymous inner class
4. Static Nested classes.

### Normal or Regular inner Class

```java
class Outer {
    class Inner {

    }
}
```

```bash
=> Outer.class, Outer$Inner.java.
> javac Outer.java  //Compile
> java Outer // Execute Outer
> java 'Outer$Inner' // Execute innerclass
java 17 innerclass can have main method.

```

```
//Static methods cant declate in innerclass //before 16
//Static methods are valid in innerclass //after 16
```

**Accessing Inner Class from Static Area of OuterClass / Outside OuterClass**

```java
OuterClass o = new OuterClass();
OuterClass.InnerClass i = o.new Inner();
i.meth();
```

```java
OuterClass.InnerClass i = new OuterClass().new InnerClass();
i.method();
```

```java
new OuterClass().new InnerClass().method();
```

**Accessing Inner Class from Instance Area of outer class**

```java
class Outer {
    class Inner{
        public void init(){
            System.out.println("INNER");
        }
    }
    public void m1(){
        Inner i = new Inner();
        i.init();
    }
    public static void main() {
        Outer o = new Outer();
        o.m1();
    }
}

```

**Variable Scopes with InnerClass**

```java
class Outer {
    int x = 10;
    class Inner {
       int x = 100;
       public void m1(){
           int x = 1000;
           System.out.println(x); //1000
           System.out.println(this.x); //100
           System.out.println(Outer.this.x); //10
       }
    }
}
```

### Method local inner class.

Can declare innerclass inside method. is called method local inner class.

```java
void method(){
    class Inner{

    }
    Inner i = new Inner();
    i.meth();
}
```

```java
//Java 16+
void method(){
    interface Biter {
        void bite();
    }
    Biter b = () -> {System.out.println("Biteme")};
    b.bite();
}
```

```java
//from jdk8 Innerclass mehtod can access local variable as well
class Outer {
    int x = 1;
    int z = 20;
void meth(){
    int x = 10;
    final int y = 20;
    class Inner {
        void m1(){
            System.out.println(x); //Error cannot access local variable JDk7,
            System.out.println(x); //JDK8+ its accessible.
            System.out.println(y); //Can access local variable only if its final.
            System.out.println(Outer.this.x); //Can access outer class instance var
            System.out.println(z); //Can access
        }
    }
    Inner i = new Inner();
    i.m1();
}

```
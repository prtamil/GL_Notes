# Super

1. Super can be used to refer immediate parent class instance variable.
2. Super can be used to invoke immediate parent class method.
3. super() can be used to invoke immediate parent class constructor.

TIPS:

1. Call to super() must be first statement in Subclass Constructor
2. If a constructor does not explicitly invoke a superclass constructor, the Java compiler
   automatically inserts a call to the no-argument constructor of the superclass.
   if superclass does not have a no-argument constructor you will get compile-time error.
   Object does have such a constructur. os if Object is the only superclass there is no problem.

3. constructor chaining => subclass constructor invokes a constructor of it superclass either
   explicitly or implicitly whole chain of constructor is called all the way to constructor of Object.

# Constructor Chaining.

1. with same class => this()
2. From base class => super()

# this()

1. this() expression should always be the first line of the constructor.
2. There should be atleast be one constructor without this() keyword.
3. Constructor chainning can be achieved in any order.

# super()

1. Call to super() must be first statement in Subclass Constructor
2. If a constructor does not explicitly invoke a superclass constructor, the Java compiler
   automatically inserts a call to the no-argument constructor of the superclass.
   if superclass does not have a no-argument constructor you will get compile-time error.
   Object does have such a constructur. os if Object is the only superclass there is no problem.

# init block

Init block is always executed before any constructor whenever a constructor is used
for creating a new object.

if more than one blocks they are executed in the order in which they are defined
within the same class.

```java
class Temp {
    {
        System.out.println("InitBlock");
    }
    Temp(){
        System.out.println("NOARG C");
    }
    Temp(int n){
        System out.println("ONEARG C");
    }
}

class Main {
    public static void main(String[] args){
        new Temp();
        new Temp(5);
    }
}
//Output
// InitBlock
// NOARG C
// InitBlock
// ONEARG C
```

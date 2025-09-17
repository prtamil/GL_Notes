# Default Methods in Java 8

Before Java8 interfaces could only have abstract methods.
Java8 provides default methods so that we dont need to declare class to provide implementation

```java
interface Test {
    public void square(int a);
    default void show(){
        System.out.println("Default Method);
    }
}
class TestImpl implements Test {
    public void square(int a){
        System.out.println("Impl");
    }
}
class Main {
    public static void main(String[] args){
        TestImpl t = new TestImpl();
        t.square(10);
        t.show(); //Default method //Only on Implmented class object.
    }
}


```

1. Defualt method were introduced to provide backward compaitablity so existing interface can use lambda expressions without reimplementing them.
2. default method are also known as defender methods or virtualextension methods.

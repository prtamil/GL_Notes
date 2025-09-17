# Switch Expresssion
```java
String mess = switch(i){
case 10,15 -> "i is 10 or 15";
case 20 -> "i is 20";
default -> throw new RuntimeException("noooo");
}
```

# ForEach

for(Type elem: collction){
//dosomething
}

# Default Value

1. Class Fields have default Value [Null or 0]
2. Local variable will never have default value ; throws compiler Error.

# Order of Method inside class

1. does not matter.
2. as long as inside class its ok.

# Lambda

Function require

1. Name
2. parameters
3. body
4. return

lambda requires only

1. parameters
2. body

**_ Tips _**

1. Lambda expressions should be glue code. Two lines may be too many.

# Iterators

External Iterators => Forloop
Internal Iterators => forEach

# :: double colon -> Method References

```java
List<Integer> li = Arrays.asList(1,2,3,4,5,8,6);
li.forEach((Integer val) -> System.out.println(val));
li.forEach((val)->System.out.println(val)) //TypeInference for Lambda only
li.forEach(val->System.out.println(val)) //No parens for single params
li.forEach(System.out::println) //No params, Double colon for method reference.
```

:: double colon => method reference

1. Static method => list.forEach(Class::staticMethod)
2. an instance method => list.forEach(object::instanceMethod), list.forEach((new Class())::instanceMethod)
3. super => super::print
4. Instance method of arbitrary object of pparticular type => list.forEach(Class::someinstanceMethod)
5. Constructor => list.forEach(ArrayList::new);

**_ Usage _**
-> Passthru. Passing as lambda functions , simple arguments passthru use it
-> pass what yoou receive

# Map 
1. AbstractMap  => Implements most of Map interface
2. EnumMap  => Use of Enum keys
3. HashMap  => Random Order
4. TreeMap  => Sorted Order 
5. WeakHashMap => Hash table with weak keys
6. LinkedHashMap => Insertion Order
7. IdentityHashMap => for Reference Equality

## Retrieval and Updation
put,get, remove, getOrDefault, compute, computeIfAbsent, computeIfPresent
entrySet, keySet, values,

## containment
containsKey,containsValue

## iteration

```java 
for(HashMap.Entry<String,Integer> m : map.entrySet()) {
	sout("Key "+ m.getKey());
	sout("Value" + m.getValue());
}
```

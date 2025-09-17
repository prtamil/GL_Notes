# Want to statically initialize objects

## Using Of [Convince Factor method of collections]
```java
List<String> s1 = List.of("Tamil", "Papps", "Yuva");  //Immutable Collections Cannot modify 
List<String> s2 = new ArrayList<>(List.of("Tamil","Papa")) //Mutable Collection Can modify
	
s1.add("Err because its imutable");
s2.add("Ok its because its mutable")

```
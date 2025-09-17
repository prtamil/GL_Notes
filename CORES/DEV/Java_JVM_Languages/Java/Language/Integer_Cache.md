# Integer Cache 

Java provides Integer cache for same identiy within value of -128 to 128. 
After that each value contains different identity.

This Integer Cache works only on autoboxing which means Conversion from a primitive type to an object reference is called autoboxing.

Integer Cache available to (Byte,Short,Long)

```java

Integer a = 127;
Integer b = 127;  
//a==b => True (Identity same)
Integer a = 230;
Integer b = 230;
//a==b => False (Diffrent identity)

```

```java
// A program demonstrate IntegerCache
// implementation in Java.
 
// This is how IntegerCache class works.
private static class IntegerCache {
 
     // Method and variable declaration.
    static final int low = -128;
    static final int high;
    static final Integer[] cache;
    private IntegerCache() {}
 
    static
    {
        // Range value from -128 to 127
        int var0 = 127;
        String var1 = VM.getSavedProperty(
            "java.lang.Integer.IntegerCache.high");
        int var2;
        
       // Check if var1 value is null or not.
        if (var1 != null) {
            
          // For exception case
           try {
                var2 = Integer.parseInt(var1);
                var2 = Math.max(var2, 127);
                var0 = Math.min(var2, 2147483518);
            }
            catch (NumberFormatException var4) {
            }
        }
 
        high = var0;
        
       // High range for IntegerCache
        cache = new Integer[high - -128 + 1];
        var2 = -128;
       
       // defining var3 values using loop.
        for (int var3 = 0; var3 < cache.length; ++var3) {
            cache[var3] = new Integer(var2++);
        }
        assert high >= 127;
    }
}
```
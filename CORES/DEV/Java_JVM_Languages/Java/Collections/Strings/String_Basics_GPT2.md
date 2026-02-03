Here's a comprehensive guide to foundational string processing methods in modern Java, covering the topics you've listed:

1. **String to Char Array and Char Array to String**
    
    _String to Char Array:_
    ```java
	String str = "Hello, World!";
	char[] charArray = str.toCharArray();

	```
    
    
    _Char Array to String:_
    ```java
	char[] charArray = {'H', 'e', 'l', 'l', 'o'};
	String str = new String(charArray);

	```
    
    
2. **String to Integer, Float and Float/Integer to String**
    
    _String to Integer:_
    ```java
	String numberStr = "123";
	int number = Integer.parseInt(numberStr);

	```
    
    
    _String to Float:_
    ```java
	String floatStr = "123.45";
	float number = Float.parseFloat(floatStr);

	```
    
    
    _Integer to String:_
    ```java
	int number = 123;
	String numberStr = Integer.toString(number);

	```
    
    
    _Float to String:_
    
    ```java
	float number = 123.45f;
	String floatStr = Float.toString(number);

	```
    
3. **Split String to Characters, Words, Sentences**
    
    _Split String to Characters:_
    
    ```java
	String str = "Hello";
	String[] characters = str.split("");

	```
    
    _Split String to Words:_
    
    ```java
	String sentence = "This is a sample sentence.";
	String[] words = sentence.split("\\s+");

	```
    
    _Split String to Sentences:_
    
    ```java
	String paragraph = "This is the first sentence. This is the second sentence!";
	String[] sentences = paragraph.split("[.!?]\\s*");

	```
    
4. **Join Character Collections (List/Set/Deque) back to String**
    
    ```java
	List<Character> charList = Arrays.asList('H', 'e', 'l', 'l', 'o');
	StringBuilder sb = new StringBuilder();
	for (char ch : charList) {
	    sb.append(ch);
	}
	String str = sb.toString();

	```
    
5. **Sort String, Reverse String, Sort in Lexical Order**
    
    _Sort String:_
    
    ```java
	String str = "dcba";
	char[] charArray = str.toCharArray();
	Arrays.sort(charArray);
	String sortedStr = new String(charArray);

	```
    
    _Reverse String:_
    
    ```java
	String str = "Hello";
	String reversedStr = new StringBuilder(str).reverse().toString();

	```
    
    _Sort in Lexical Order:_
    
    ```java
	 List<String> words = Arrays.asList("apple", "banana", "cherry");
	 Collections.sort(words);

	```
    
6. **Map, Filter, Reduce for String**
    
    _Map (Convert to Uppercase):_
    
    ```java
	String str = "hello";
	String upperStr = str.chars()
                     .mapToObj(c -> (char) c)
                     .map(Character::toUpperCase)
                     .collect(StringBuilder::new, StringBuilder::append, StringBuilder::append)
                     .toString();

	```
    
    _Filter (Remove Non-Alphabetic Characters):_
    
    ```java
	String str = "H3ll0 W0rld!";
	String filteredStr = str.chars()
                        .filter(Character::isLetter)
                        .mapToObj(c -> (char) c)
                        .collect(StringBuilder::new, StringBuilder::append, StringBuilder::append)
                        .toString();

	```
    
    _Reduce (Concatenate with Separator):_
    
    ```java
	String[] words = {"Hello", "World"};
	String result = Arrays.stream(words)
                      .reduce((a, b) -> a + ", " + b)
                      .orElse("");

	```
    
7. **Tokenize String**
    
```java
	String str = "This is a sample sentence.";
	StringTokenizer tokenizer = new StringTokenizer(str);
	while (tokenizer.hasMoreTokens()) {
	    String token = tokenizer.nextToken();
	    // Process token
	}

```
	
    
8. **Build String using StringBuilder vs StringBuffer**
    
    _Using StringBuilder:_
    
    ```java
	StringBuilder sb = new StringBuilder();
	sb.append("Hello");
	sb.append(" ");
	sb.append("World");
	String result = sb.toString();

	```
    
    _Using StringBuffer:_
    
    ```java
	StringBuffer sb = new StringBuffer();
	sb.append("Hello");
	sb.append(" ");
	sb.append("World");
	String result = sb.toString();


	```
    
    _Note:_ `StringBuilder` is faster and suitable for single-threaded contexts, while `StringBuffer` is thread-safe and suitable for multi-threaded contexts.
    
9. **Format 2 Decimal Points on String for Float and Double**
    
    ```java
	float number = 123.4567f;
	String formatted = String.format("%.2f", number);

	```
    
10. **String Search Substring, Single Character, Search Occurrences**
    
    _Search Substring:_
    
    ```java
	String str = "Hello, World!";
	boolean contains = str.contains("World");

	```
    
    _Search Single Character:_
    
    ```java
	String str = "Hello";
	int index = str.indexOf('e');

	```
    
    _Search Occurrences:_
    
    ```java
	String str = "banana";
	int count = str.length() - str.replace("a", "").length();

	```
    
11. **Group by Character in Given String**
    
    ```java
	String str = "banana";
	Map<Character, Long> frequency = str.chars()
                                    .mapToObj(c -> (char) c)
                                    .collect(Collectors.groupingBy(c -> c, Collectors.counting()));

	```
    
12. **Permutation of Given String**
    
    ```java
	public static void permute(String str, String result) {
	    if (str.length() == 0) {
	        System.out.println(result);
	        return;
	    }
	    for (int i = 0; i < str.length(); i++) {
	        char ch = str.charAt(i);
	        String ros = str.substring(0, i) + str.substring(i + 1);
	        permute(ros, result + ch);
	    }
}

	```
    
13. **Combination of Given String**
    
```java
	public static void combine(String str) {
	    int n = str.length();
	    for (int i = 0; i < (1 << n); i++) {
	        StringBuilder combination = new StringBuilder();
	        for (int j = 0; j < n; j++) {
	            if ((i & (1 << j)) > 0) {
	                combination.append(str.charAt(j));
	            }
	        }
	        System.out.println(combination.toString());
	    }
}

```
    

These examples cover foundational string processing methods in modern Java. For more advanced string manipulations, you might consider using third-party libraries like Apache Commons Lang or Google's Guava, which offer additional utilities to simplify complex string operations.
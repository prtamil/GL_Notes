#### Chap 3 fundamental types
1. References
	1. &T, &mut T
	2. single Writer, multiple reader
2. Integer overflow
	1. checked (option), wrapped , saturated (min,max range), overflow (value,bool)
3. Arrays
	1. declare let x = [true;1000] ([V;N]) Value,N->Len 
	2. slices has methods but it will work on arrays as its passed as ref of array to methods. ref of array is slice
	3. default value. cannot create without default value
4. Vec
	1. in heap
		1. vec![1,2,3,4,5]  ,`vec![0;rows*cols] (array literals)` 
	2. let mut x = Vec::with_capacity(100) (reserve capacity no much relocation)
	3. v.len(), v.capacity()
	4. push, pop, insert, remove
5. Slice
	1. Fn takes argument as slice we can pass both vec and array 
	2. reference is non owning pointer to value
6. String
	1. r"xxx" -> Raw String literals string with no escape sequence r ``"c:\Program files\"``
	2. b"xxx" -> Byte string u8 array, cannot contain unicode, can contain ascii and ctrl codes
	3. String is similar to `Vec<u8>`
7. String slice (&str)
	1. &str is string slice. 
	2. &str is fat ptr, contains length and ref it is equivalent to `&[u8]`
	3. String literal `let s = "test"` is stored in readonly memory. 
	4. &str is immutable its impossible to modify 
	5. &mut str also only `.make_ascii_uppercase, make_ascii_lowercase` only works
	6. String.len gives byte count.  string.chars().count -> gives char count
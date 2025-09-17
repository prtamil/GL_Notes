# Learning Notes CSharp and dotNet
## dotNet 
1. CLS 
	1. Common Lang Specification
	2. MSIL Msft Intermediate Language
2. CTS
	1. Common Type System (Types and its sizes (int 32 bit))
3. BCL
4. CLR or VES
## CSharp
### types
	1. value types
	2. reference types
	3. Generic type parameters
	4. Pointer Types
### Value Types vs Reference Types
Value Types
1. Enumerations (define your own)
2. tuples
3. structs  (define your own)
4. char
5. bool
6. Ints
7. floats
Reference Types
1. Classes (define your own)
2. arrays
3. string
4. Interfaces (define your own)
5. object
6. Records (define your own)
7. Delegates (define your own)
8. dynamic
Pointer types
1. pointer
### NumericSuffixes
```c#
float x = 3.5f;  bydefault 3.5 infer to Double 
decimal y = 1.34M; bydefault 1.34 infer to double will get error
int x = 0b1111_1000_1010;
int x = 1_000_000;
1.GetType() => Int32 (int)
0xF000_0000.GetType() => UInt32 (uint)
0x1000000000.GetType() => Int64 (long)

```
```txt
F (float) 
D (double)
M (decimal)
U (uint)
L (long)
UL (ulong)


```
| C# Type  | System Type | Suffix  | Size      |                              |
| -------- | ----------- | ------- | --------- | ---------------------------- |
| sbyte    | sbyte       |         | 8bits     |                              |
| short    | Int16       |         | 16bits    |                              |
| int      | Int32       |         | 32bits    |                              |
| long     | Int64       |         | 64bits    |                              |
| nint     | IntPtr      |         | 32-64bits | Low Level Interlop Scenarios |
|          |             |         |           |                              |
| Unsigned |             |         |           |                              |
| -----    | ------      | ------  | --------  |                              |
| byte     | Byte        |         | 8bits     |                              |
| ushort   | UInt16      |         | 16bits    |                              |
| uint     | UInt32      | U       | 32bits    |                              |
| ulong    | UInt64      | UL      | 64bits    |                              |
| uint     | UIntPtr     |         | 32-64Bits | Low Level Interlop Scenarios |
|          |             |         |           |                              |
| Real     |             |         |           |                              |
| ------   | -------     | ------- | --------  |                              |
| float    | Single      | F       | 32bits    |                              |
| double   | Double      | D       | 64bits    |                              |
| decimal  | Decimal     | M       | 128bits   |                              |
|          |             |         |           |                              |

### Conversions
```txt
Conversions
1. Implicit  (lossless) No need specify (long a = intB)
2. Explicit   (loss) need to specify  (int a = (int)longA;)

System.Convert  have all the methods for Conversions 
```
### Overflow
```txt
1. checked
2. unchecked
```
### Floating point const
```c#
double.NaN, double.PositiveInfinity, double.NegativeInfinity
float.NaN, float.PositiveInfinity, float.NegativeInfinity

```

### String Type
1. String is Reference type 
2. == (Equality operator operates like value type)
3. verbatim (Word for Word) escape escape sequences (@). Can contains multiple Lines 
4. @$ -> Multiline string interpolated Lines
5. const string interpolations C# 10. as long as interpolated values are also constant
6. $ -> String Interpolation
7. @ -> Verbatim Identifier
8. """ -> raw string literal
```

# Copy Constructor
## When does it gets called
In C++, a Copy Constructor may be called in the following cases: 

-   When an object of the class is returned by value. 
-   When an object of the class is passed (to a function) by value as an argument. 
-   When an object is constructed based on another object of the same class. 
-   When the compiler generates a temporary object.

It is, however, not guaranteed that a copy constructor will be called in all these cases, because the C++ Standard allows the compiler to optimize the copy away in certain cases, one example is the **return value optimization** (sometimes referred to as RVO).

#### Code Example

```cpp
class a {
public:
    a() {
        printf("constructor called\n");
    };  
    a(const a& other) { 
        printf("copy constructor called\n");
    };    
    a& operator=(const a& other) {
        printf("copy assignment operator called\n");
        return *this; 
    };
};
```

So then this code:

```cpp
a b; //constructor
a c; //constructor
b = c; //copy assignment
c = a(b); //copy constructor, then copy assignment
```

produces this as the result:

```cpp
constructor called
constructor called
copy assignment operator called
copy constructor called
copy assignment operator called
```

Another interesting thing, say you have the following code:

```cpp
a* b = new a(); //constructor called
a* c; //nothing is called
c = b; //still nothing is called
c = new a(*b); //copy constructor is called
```

This occurs because when you when you assign a pointer, that does nothing to the actual object.
```cpp
a c = b;
```
 also calls copy constructor

https://stackoverflow.com/questions/21206359/in-which-situations-is-the-c-copy-constructor-called

## Syntax of Copy Constructor
```cpp
class Test {
 public:
 Test(int x){
 m = x;
 }
 Test& Test(const Test& t1){
    m = t1.m;
 }
 int m;
}

Test t(20);
Test s(t);

```

## Why Parameter of Copy Constructor is Const reference 
1. it is reference because passing argument by value will initiate copy constructor tends to recursive callback
2. const
	1. because should copy not change the object to be copied. logically one should not mutate original one. it not right.
	2. compiler created temporary objects cannot be bound to non-const references 
		```cpp
		  Test t,t1 ;
		  Test t2(t+t1);  //t+t1 => Temporary Rvalue 
		  //RValue will be captured only by const references 
		  const Test &r = t+t1; //Only const reference capture rvalue 
		  Test &r = t+t1; //Will throw error. because rvalue will be assigned 
		  Test &&r = t+t1; //ok rvalue reference
		  const Test &r = t+t1 //ok const reference capture rvalue 
		  //const reference will create temp and assign temp.
		  Test _compiler_generated_tmp = t+t1;
		  const Test &r = _compiler_generated_tmp; 
		``` 
		 1. only const reference capture rvalue (tempory objects). non const throws error.
## Difference between Copy Constructor and Assignment Operator

```cpp
Test t;
Test t1(t);   //Copy Constructor    ; by default its default copy constructor.
Test t1 = t;  //Copy Constructor
Test t2;
t2 = t;      //Assignment Operator  ; by default its bitwise copy
```

```cpp
class Test {
  Test();
  Test(const Test& t1); //Cpy Ctr
  //assignment operator
  Test& operator=(const Test& t1){
	  //After Copy operation
	  this->x = t1.x;
	  return *this;
  }
  int x;
}
```


| Cpy Ctr                                             | Assignment Operator                                        |
| --------------------------------------------------- | ---------------------------------------------------------- |
| Called when new object created from existing object | already initialized object assignment from existing object |
| overloaded constructor                              | bitwise operator                                           |
| implicitly provided when not overloaded             | bitwise copy gets created when not overloaded              |
| creates seprate memory block for new object         | does not create seprate memory block or new memory space                                                           |
## Copy elision
Copy elision (Copy omission) is a compiler optimization technique that avoids unnecessary copying of objects

according to theory 
```cpp
  B ob = "copy me"; 
```

should be broken down by the compiler as
```cpp
B ob = B("copy me");
```
and should call Copy Constructor of B. 

But 

The modern compilers break down the statement
```cpp
B ob = "copy me"; //copy initialization
```
 
as
```cpp
B ob("copy me"); //direct initialization
```
and thus eliding call to copy constructor.

If 
```cpp
“-fno-elide-constructors” 
```

option is used, first default constructor is called to create a temporary object, then copy constructor is called to copy the temporary object to ob.
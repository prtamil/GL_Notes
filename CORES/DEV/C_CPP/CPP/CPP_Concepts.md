# September-2022
C++
///
1. Initialization (20 types) 
	1. default initialization
	2. aggregate initialization
	3. value initialization 
	4. ... [3 is major we have endless listing of other types]
2. nvro, rvo
3. C++17 fold Expressions. 
5. Layout (POD, trivial, standard) ```cpp std::is_trivial<Employee> == true ```
6. Pointer Declaration Syntax 
```c
int (*p)[5]; //ptr to array
int *p[5]  //array of pointers
```
7. lambda basics 
 ```cpp
 [Capture](Parameter)->ReturnType{Body};
 []()->int{}; //[Capture](Parameter)->Return{Body}
 [&capturedVariableByRef](float p1, float p2)->int{ 
   int res; 
   res = capturedVariableByRef + p1 + p2;
   return res; //Bug int to float lost precision
 }
 [&](){}; //Captures all variables as reference
 [=](){}; //Captures all variables as copy
```
8. lvalue vs rvalue (https://www.internalpointers.com/post/understanding-meaning-lvalues-and-rvalues-c)
9. c++ namespace private members (https://www.internalpointers.com/post/c-namespaces-private-members)
10. lvalue, rvalue, xvalue, glvalue, prvalue
11. Copy elision

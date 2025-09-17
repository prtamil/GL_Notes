# Abstract classes

1. An instance of an abstract class can not be created.
2. Constructors are allowed.
3. We can have an abstract class without any abstract method.
4. Abstract classes can have final methods also useless [final method you cannot override, abstract designed to override.]
5. We are not allowed to create object for any abstract class.
6. we can define static methods in an abstract class.

[https://www.geeksforgeeks.org/abstract-classes-in-java/]

## diff between interface and abstract class

### Class vs Interface

interface can only have abstract methods
abstract class can have

1. abstract methods
2. non-abstract methods
3. default methods
4. static methods.

### Final variables

1. variables defined in interface are default final.
2. abstract class may contain non-final variables.

### Type of variables

Abstract class can have

1. non-final,
2. final
3. static
4. non-static

variables

Interface have

1. static
2. final

variables.

### Implementation

Abstract class => Can provide impl
Interface => only signature

### Multiple Implementations

Interface => Only extend other interface
Abstract Class => Extend class/implent interface

### Accessibility of Data Members

Interface => Members public by default
Abstract class => Private/protected/public etc..

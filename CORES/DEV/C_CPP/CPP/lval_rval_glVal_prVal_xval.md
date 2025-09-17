# LValue and RValue Overview

lvalue vs rvalue (https://www.internalpointers.com/post/understanding-meaning-lvalues-and-rvalues-c) 
This clearly explains what lvalue and rvalue is


## Important Observations
1. & operator requires lvalue
# Core Concept to understand mynotes  (https://www.stroustrup.com/terminology.pdf)
1. Identity  (i)
2. Movable

 all this confusion happen because of move (m)
  
iM, Im, m, im,

i -> identifiable
m -> movable
I -> not identifiable
M -> not movable

WShaped Structure below
.......................

iM    im    Im
\\     |    /
   i    m

W Shaped  category

Less formal definition
1. lessFormal  (iM/i => lvalues, m/Im => rvalues)


Proper definition
iM => classical lValue
m => classical rValue

i => generalized Lvalue (glvalue)
Im => pure rValue = (prValue)

im => xvalue (experx only, xrated, ) expiring value

LVALUES
1. iM -> lValue
2. i -> glValue
RVALUES
1. m -> rValue
2. Im -> prValue

iM => xValue  

IM -> No such category. Useless also
# Easy Understanding

I have struggled with this for a long time, until I came across the cppreference.com explanation of the [value categories](http://en.cppreference.com/w/cpp/language/value_category).

It is actually rather simple, but I find that it is often explained in a way that's hard to memorize. Here it is explained very schematically. I'll quote some parts of the page:

> ### Primary categories
> 
> The primary value categories correspond to two properties of expressions:
> 
> - _has identity_: it's possible to determine whether the expression refers to the same entity as another expression, such as by comparing addresses of the objects or the functions they identify (obtained directly or indirectly);
>     
> - _can be moved from_: move constructor, move assignment operator, or another function overload that implements move semantics can bind to the expression.
>     
> 
> Expressions that:
> 
> - have identity and cannot be moved from are called _lvalue expressions_;
> - have identity and can be moved from are called _xvalue expressions_;
> - do not have identity and can be moved from are called _prvalue expressions_;
> - do not have identity and cannot be moved from are not used.
> 
> ### lvalue
> 
> An lvalue ("left value") expression is an expression that _has identity_ and _cannot be moved from_.
> 
> ### rvalue (until C++11), prvalue (since C++11)
> 
> A prvalue ("pure rvalue") expression is an expression that _does not have identity_ and _can be moved from_.
> 
> ### xvalue
> 
> An xvalue ("expiring value") expression is an expression that _has identity_ and _can be moved from_.
> 
> ### glvalue
> 
> A glvalue ("generalized lvalue") expression is an expression that is either an lvalue or an xvalue. It _has identity_. It may or may not be moved from.
> 
> ### rvalue (since C++11)
> 
> An rvalue ("right value") expression is an expression that is either a prvalue or an xvalue. It _can be moved from_. It may or may not have identity.

## So let's put that into a table:

|                              | Can be moved from (= rvalue) | Cannot be moved from |
| ---------------------------- | ---------------------------- | -------------------- |
| **Has identity (= glvalue)** | xvalue                       | lvalue               |
| **No identity**              | prvalue                      | not used             |
|                              |                              |                                                                           |                      |
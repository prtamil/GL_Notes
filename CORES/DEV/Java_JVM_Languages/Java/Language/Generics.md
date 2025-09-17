# Generics Concepts

- Only on compile time not runtime.
- after compilation as last step generics sytax will be removed.
- jvm generics will not be available.

At compile time

1. compile code normally by considering generic syntax
2. remove generic syntax
3. compile code again with removed syntax.

# Generics class

```java
class Bound <T>  //Unbounded Type parameter
class Bound <T extends Number>  //Bounded Type Parameter
class Bound <T extends A>  //A Class
class Bound <T extends A & B &C &D>  //A Class, B,C,D => Interfaces , Multiple Bounds
class Bound <T extends B & A & C>  //error A Class, B,C => Interface //Error First Should be Class
class Bound <T extends B> // Ok , B can be Interfaces
class Bound <T implements C> // Error , no implementss only extends even for interface
class Bound <T super C> //Error implements,super not applicable only extends
class Bound <T extends X> //if X= class,  X or its Child can be passed.
class Bound <T extends X> //if X = interface , Interface or Implementation canbe passes.
class Bound <T extends X & Y> //error. if X,Y both Class Java not support multiple inheritance for class.
```

# variables

```java
List<?> x = new List<String>() => Valid
List<?> x = new List<?> => Error ? belong to left hand side.  // Without Bounds Error
List<?> x = new List<? extends String> => Error ? belong to left side. //Without Bounds Error
```

# Generic methods `<?>`

```java
public void method(ArrayList<? extends A> a);
public void method(ArrayList<? super C> a) //Class
public void method(ArrayList<?> a) //a.add(null) => allowed, rest error a.add(10.5),a.add("STR") are error.
                                   //Null is valid for anytype.
                                   //These type of operation best suitable for ReadOnly operation.
                                   //You can read but cannot write.
```

# PECS (Producer Extends Consumer Super)

1. Pulling from Collection => Producer => `<? extends X> => Generic Method
2. Stuffing in Collection => Consumer => `<? super X> => Generic Method.

```java
void method (ArrayList<? extends Number>) => { a.get(i)} //add only null.
void method (ArrayList<? super Number>) => {a.add(10)}  //
```

# Covariance, Contravariance, InVariance => Applies generic method

CoVariance => ? extends MyClass => List`<? extends MyClass> => Producer => Pull
ContraVariance => ? super MyClass => List`<? super MyClass> => Consumer => Stuff
InVariance/NonVariance => MyClass => List`<MyClass> => Do both Pull/Push and anything

# Generic Area / Non Generic Area

- Generic Collections pass to non generic object => Will work => -Xlint:unchecked
- `ArrayList<String> o => fn(ArrayList a)` => Yes //backward compaitablity pre j7

```java
  ArrayList<String> s = new ArrayList<>();
  s.add("eee") //ok
  s.add(10) //compile err
  function(s); //Ok

  function(ArrayList s){
      s.add(10)  //ok   jdk7 arraylist is dynamic backwards compaitabily
      s.add(20)  //ok   //-Xlint:unchecker will find error else its valid.
  }
```

- Non Generic area from Generic Area

```java
ArrayList l = new ArrayList<String>();  //Generic to NonGeric var
l.add("str") //ok
l.add(10) //Warning but ok. as l is nongeneric

ArrayList<String> l = new ArrayList();
l.add("SSS") //ok
l.add(10) //Error typechecked.
```

```java
import java.util.*;
public class tst {
    public void m1(ArrayList<String> l) {}
    public void m1(ArrayList<Integer> l) {}

    public static void main(String[] args) {
    }
}
//ERROR
//m1<string>, m1<Integer> have same type erasure.
```

At compile time

3. compile code normally by considering generic syntax
4. remove generic syntax
5. compile code again with removed syntax.

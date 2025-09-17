## C#

1. foreach
2. top level statements
3. [attribute]
4. [Operator Overloading, TypeConversion, (OperatorOverloading public,static)]
5. static methods. invocation and creation.
6. Timer/TimerCallback as GameLoop for Terminal Graphics
7. switch/pattern matching
   > public State getCurrent(State val) => val switch {
   > "RUN" => 1,
   > "START" => 2,
   > "SLEEP" => 3,
   > };
   > var = getCurrent(val);
8. Linq
   > String s = "this is sparta and tonight we dine in hell";
   > s.GroupBy(c => c).
   > Select(c => new { c.Key, Count = c.Count() }).
   > ToList().
   > ForEach(l => Console.WriteLine($"{l.Key} -> {l.Count}"));
   >s.GroupBy(c => c).ToList().ForEach(l => Console.WriteLine($"SS {l.Key} -> {l.Count()}"));

> var lst = new List<int> { 1, 2, 3, 4, 5, 6, 6, 7, 8, 8, 9 };
> lst.Select(x => x \* x).
> Where(x => x > 20).
> ToList().
> ForEach(x => Console.Write($"{x}, "));

9. test

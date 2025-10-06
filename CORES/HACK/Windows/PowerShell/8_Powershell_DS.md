# 📝 PowerShell Data Structures Cheat Sheet

## 1. **PowerShell-native (dynamic, flexible, human-friendly)**

|Structure|Syntax|Best Use-Case|Notes|
|---|---|---|---|
|**Scalar**|`$x = 42`|Single values|Strings, ints, bools, etc.|
|**Array**|`$a = 1,2,3` or `@(1,2,3)`|Fixed-length sequences|Adding creates new array → not efficient for big changes|
|**Range**|`1..10`|Simple sequential arrays|Inclusive|
|**Hashtable**|`$h = @{Key="Value"}`|Key/value lookups, configs|Keys not strongly typed|
|**Ordered Hashtable**|`$h = [ordered]@{}`|Ordered configs (INI, JSON-like)|Preserves insertion order|
|**PSCustomObject**|`[PSCustomObject]@{Name="Bob"; Age=30}`|Tabular data, clean output, CSV/JSON export|Best for pipeline friendliness|
|**String**|`"hello"`|Text manipulation|Can be treated as `char[]`|

---

## 2. **.NET Collections (typed, efficient, algorithmic use)**

|Structure|Example|Best Use-Case|Notes|
|---|---|---|---|
|**ArrayList**|`$al = [System.Collections.ArrayList]::new()`|Dynamic array (legacy)|Slower, not strongly typed|
|**List<T>**|`$list = [System.Collections.Generic.List[int]]::new()`|Dynamic arrays with fast add/remove|Strongly typed, preferred over ArrayList|
|**Dictionary<TKey,TValue>**|`$d = [System.Collections.Generic.Dictionary[string,int]]::new()`|Strongly typed hashtable|O(1) lookups|
|**SortedDictionary<TKey,TValue>**|`$sd = [System.Collections.Generic.SortedDictionary[string,int]]::new()`|Sorted key/value|Slower than dictionary|
|**Queue<T>**|`$q = [System.Collections.Generic.Queue[int]]::new()`|FIFO processing|`Enqueue()`, `Dequeue()`|
|**Stack<T>**|`$s = [System.Collections.Generic.Stack[int]]::new()`|LIFO processing|`Push()`, `Pop()`|
|**HashSet<T>**|`$set = [System.Collections.Generic.HashSet[int]]::new()`|Set ops (union, diff, intersect)|Eliminates duplicates automatically|
|**LinkedList<T>**|`[System.Collections.Generic.LinkedList[int]]::new()`|Insert/remove in middle|Rare in scripting|
|**BitArray**|`[System.Collections.BitArray]::new(8)`|Compact binary flags|Useful in networking/low-level ops|
|**ConcurrentDictionary<TKey,TValue>**|`[System.Collections.Concurrent.ConcurrentDictionary[string,int]]::new()`|Thread-safe dictionary|For parallel jobs|

---

## 3. **Mental Model: When to Use**

- **Use PowerShell-native** if:
    
    - You care about **simplicity**, quick scripts, configs, or human readability.
        
    - You need **nice console output** (tables, CSV, JSON).
        
    - Example: `PSCustomObject` is perfect for building a row of structured data.
        
- **Use .NET types** if:
    
    - You need **performance** or **typed data**.
        
    - You’re doing **algorithmic work** (queues, stacks, sets, large collections).
        
    - You want to avoid PowerShell array resizing overhead.
        

---

## 4. Quick Example: Side by Side

```psh
# Native Array (easy, but not efficient for big add/remove)
$a = 1,2,3
$a += 4    # Creates a new array

# .NET List<T> (efficient for add/remove)
$list = [System.Collections.Generic.List[int]]::new()
$list.Add(1)
$list.Add(2)
$list.Add(3)
$list.Add(4)   # no array copy overhead

```

---

⚡ **Rule of Thumb**:

- Use **Arrays, Hashtables, PSCustomObjects** for **day-to-day scripting**.
    
- Use **List<T>, Dictionary<,>, HashSet<T>, Queue<T>, Stack<T>** when you’re writing something closer to an **algorithm** or handling **large datasets**.
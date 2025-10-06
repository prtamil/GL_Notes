# Sort-Object — deep dive (syntax, behavior, examples — no links)

`Sort-Object` sorts objects that come through the pipeline. It’s one of the most-used cmdlets for ordering data (numbers, strings, dates, or objects by one/more properties). Below you’ll find syntax, a clear explanation of parameters and behavior, lots of practical examples, patterns, and gotchas — ready to paste into Obsidian.

---

## Syntax (concise)

```psh
Sort-Object [[-Property] <Object[]>] [-Descending] [-Unique] [-CaseSensitive]
            [-Culture <String>] [-InputObject <PSObject>] [<CommonParameters>]

```

You can pass property names or scriptblocks to `-Property`. If you don’t supply `-Property`, the cmdlet sorts the objects themselves.

---

## What it returns

- A sequence of the input objects sorted according to the key(s) you specify.
- If you sort objects, you get the original objects back (not transformed copies) but in sorted order.
- With `-Unique`, duplicates are removed from the sorted results (behavior explained below).
    

---

## Key parameters — explained

- `-Property <name|scriptblock|expression[]>`  
    Specify one or more properties or scriptblocks that produce the sort key(s). Examples: `-Property Name`, `-Property Length, CreationTime`, or `-Property { $_.Name.Length }`.
    
- `-Descending`  
    Reverse sort order. Applies to the overall sort (i.e., it applies to the full sort operation).
    
- `-Unique`  
    Remove duplicate results from the sorted output. If you provided `-Property`, uniqueness is determined by the property value(s) used for sorting.
    
- `-CaseSensitive`  
    Perform case-sensitive string comparison when sorting string keys.
    
- `-Culture <string>`  
    Specifies the culture used for string comparisons (affects collation of characters like accented letters). Uses current culture by default.
    
- `-InputObject <object>`  
    Accept a value via parameter rather than via pipeline. Note: passing a collection here treats it as _one_ object — usually you want to pipe elements into Sort-Object.
    

---

## Behavior notes & important mental models

- **Sort-Object collects input**: it must see all input values before it can produce the sorted output. That means it buffers the whole collection in memory — be careful with very large streams.
    
- **Multiple properties**: pass multiple property names to sort hierarchically (primary, then secondary, etc.):
    
    `Get-ChildItem | Sort-Object -Property Extension, Name`
    
- **Scriptblock keys**: you can compute a key on the fly:
    
    `Get-ChildItem | Sort-Object -Property { $_.LastWriteTime.Date }`
    
- **-Unique vs Select-Object -Unique**:
    
    - `Sort-Object -Unique` returns **sorted unique** results (duplicates removed after sorting).
        
    - `Select-Object -Unique` returns the **first occurrence** of each distinct item in the _original_ order (no sorting).  
        Example:
        
    
    `# sorted unique 3,1,2,3 | Sort-Object -Unique    # -> 1,2,3  # first-occurrence unique (keeps original order) 3,1,2,3 | Select-Object -Unique  # -> 3,1,2`
    
- **Null / missing property values**: objects that don’t have the property or have $null will be compared as nulls. Their relative position depends on how .NET comparison treats nulls; test for your dataset if null ordering matters.
    
- **String comparisons**: by default, culture & case rules follow the current culture and are usually case-insensitive; use `-CaseSensitive` or `-Culture` to change that.
    

---

## Examples (practical, explained)

### 1) Sort numbers (ascending / descending)

```psh
1,5,2,10 | Sort-Object
# -> 1,2,5,10

1,5,2,10 | Sort-Object -Descending
# -> 10,5,2,1

```

### 2) Sort strings (case-insensitive vs case-sensitive)

```psh
"apple","Banana","apple" | Sort-Object
# default: sorts with culture rules (case-insensitive in many locales)

"apple","Banana","apple" | Sort-Object -CaseSensitive
# forces case-sensitive sort

```


### 3) Sort files by size (largest first)

```psh
Get-ChildItem -File | Sort-Object -Property Length -Descending | Select-Object -First 10
# top 10 largest files

```


### 4) Sort objects by multiple properties

```psh
Import-Csv employees.csv | Sort-Object -Property Department,LastName,FirstName
# sorts by Department (primary), then LastName, then FirstName

```


### 5) Sort by a computed value (scriptblock)

```psh
# sort by the date only (ignore time)
Get-ChildItem | Sort-Object -Property { $_.LastWriteTime.Date }

```


### 6) Sorted unique values (unique property values)

```psh
Get-ChildItem | Sort-Object -Property Extension -Unique
# returns each extension once, sorted

```


### 7) Sorting text lines

```psh
Get-Content file.txt | Sort-Object | Set-Content file.sorted.txt
# lexical sorting of lines

```


### 8) Case with culture (accented characters)

```psh
# Use a specific culture for sort comparisons
"é","e","É","E" | Sort-Object -Culture "fr-FR"

```


### 9) Sort with scriptblock that returns different types

```psh
# sort by length of name, numeric key
Get-ChildItem | Sort-Object -Property { $_.Name.Length } -Descending

```


### 10) Two-step (secondary then primary) sort pattern

If you need complex mixed-direction sorting (descending by one property, ascending by another), one approach is a two-step sort: sort by the secondary key first, then the primary key. This works in practice because equal-key ordering is commonly preserved; for guaranteed behavior build a composite key instead.

```psh
# example idea (secondary then primary):
$data | Sort-Object SecondaryKey | Sort-Object PrimaryKey -Descending

```


(If you need strict guarantees across environments, compute a single composite key via a scriptblock and sort on that.)

---

## Common patterns / recipes

- **Top N by property**:
    

`Get-ChildItem -File | Sort-Object -Property Length -Descending | Select-Object -First 5`

- **Unique sorted list of values**:
    

`$data | Sort-Object -Property SomeProperty -Unique | Select-Object -ExpandProperty SomeProperty`

- **Stable-looking multi-key sorting (simple)**:
    

`# sort by last name then by first name 
`$people | Sort-Object -Property LastName, FirstName`

- **Sort and then group (e.g., list sorted then group)**:
    

`$items | Sort-Object Category, Name | Group-Object Category`

---

## Performance tips & gotchas

- **Memory**: `Sort-Object` buffers all input. For very large datasets consider:
    - Using more memory-efficient .NET sorting on arrays (e.g., `[array]::Sort($arr)` for primitive arrays).
    - Streaming approaches (pre-aggregate, filter early, or use stronger-typed collections).
        
- **InputObject**: don’t pass a collection via `-InputObject` if you intend to sort its elements — that will treat the collection as a single object. Pipe elements into `Sort-Object` instead.
- **Unique semantics**: `-Unique` removes duplicates after sort. If you want to preserve the first occurrence, use `Select-Object -Unique` instead.
- **Comparisons and culture**: string ordering can change with `-Culture` and whether `-CaseSensitive` is used. If consistent ordering across systems is required, specify `-Culture`.
    

---

## Quick cheat sheet (one-liners)

- Sort ascending:

`$items | Sort-Object`

- Sort by property descending:

`$items | Sort-Object -Property Score -Descending`

- Sort by scriptblock:

`$items | Sort-Object { $_.Name.Length }`

- Unique sorted values:

`$items | Sort-Object -Property Category -Unique`

- Top N:

`$items | Sort-Object -Property Value -Descending | Select-Object -First 10`
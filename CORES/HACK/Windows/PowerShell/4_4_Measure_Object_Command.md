# Measure-Object — deep dive (syntax, behavior, examples)

Great — `Measure-Object` is the little Swiss Army knife for counting and basic stats in PowerShell. It works on _collections_ (objects piped in) and on _strings_ (lines/words/characters), and can produce Count, Sum, Average, Min/Max, Standard Deviation and more. 

---

## Quick summary

- **What it does:** counts objects and computes numeric stats (Sum, Average, Minimum, Maximum, StandardDeviation) for a property, and (for text) counts lines/words/characters. 
    
- **Typical result:** a single object (a measurement object) with properties like `Count`, `Sum`, `Average`, `Maximum`, `Minimum`, `StandardDeviation`, and `Property` (text measurements show `Lines`, `Words`, `Characters`)
    

---

## Syntax (two main "modes")

**Generic numeric/statistics mode**

```psh
Measure-Object [[-Property] <PSPropertyExpression[]>] 
               [-InputObject <PSObject>] 
               [-StandardDeviation] [-AllStats] 
               [-Sum] [-Average] [-Maximum] [-Minimum] 
               [<CommonParameters>]

```

**Text mode (counts)**

```psh
Measure-Object [[-Property] <PSPropertyExpression[]>] 
               [-InputObject <PSObject>] 
               [-Line] [-Word] [-Character] [-IgnoreWhiteSpace] 
               [<CommonParameters>]

```

(official syntax: see Microsoft docs).

---

## Important parameter notes

- `-Property <name or scriptblock>` — which property (or scriptblock) of each input object to measure. If omitted, `Measure-Object` counts input objects
- `-Sum`, `-Average`, `-Minimum`, `-Maximum`, `-StandardDeviation` — calculate the named stat for the property values.
- `-AllStats` — return all stats at once (Count, Average, Sum, Max, Min, StandardDeviation). (Added in PS6+). 
- `-Line`, `-Word`, `-Character`, `-IgnoreWhiteSpace` — text-mode switches to count lines/words/characters (and optionally ignore whitespace). Useful with `Get-Content` or string input
- `-InputObject` — you can pass an object directly via this parameter, but note that when you use `-InputObject`, the value is treated as **one** input object (so prefer piping when you want to measure each element in a collection)
    

---

## What `Measure-Object` returns

A single _measurement object_. Example properties you can read:

- `.Count` — number of input objects measured (or number of lines when using text mode on collections of lines).
- `.Sum`, `.Average`, `.Minimum`, `.Maximum`, `.StandardDeviation` — numeric stats (present only if requested or via `-AllStats`).
- For text-mode: `.Lines`, `.Words`, `.Characters` (the output table shows these headings).
    

You typically extract numbers like:

```psh
(1..5 | Measure-Object -Sum).Sum        # → 15
(1..5 | Measure-Object).Count           # → 5

```

---

## Practical examples (with explanations)

### 1) Count files & folders in current folder

```psh
Get-ChildItem | Measure-Object # then: (Get-ChildItem | Measure-Object).Count
```


This simply counts how many objects `Get-ChildItem` emitted.

---

### 2) Sum / Average / Min / Max of file sizes

```psh
$m = Get-ChildItem -File | Measure-Object -Property Length -Minimum -Maximum -Sum -Average
$m.Sum       # total bytes
$m.Average   # average file size (bytes)
$m.Maximum   # largest file (bytes)
$m.Minimum   # smallest file (bytes)

```

Classic usage: measure a numeric property (`Length`).

---

### 3) Count lines / words / characters in a text file

```psh
# simple: Get-Content returns an array of lines, so Count gives the line count:
(Get-Content C:\Temp\tmp.txt).Count

# OR use Measure-Object text switches:
Get-Content C:\Temp\tmp.txt | Measure-Object -Line -Word -Character
# Output columns: Lines  Words  Characters

```

If you use `Get-Content -Raw` (single string), `Measure-Object -Line` will count newline-separated lines inside that single string. See docs for differences.

---

### 4) All stats at once

```psh
1..5 | Measure-Object -AllStats
# returns Count, Average, Sum, Maximum, Minimum, StandardDeviation, Property

```

`-AllStats` is convenient for quick summaries. 

---

### 5) Measure using a calculated/scriptblock property

```psh
# total size in MB (scriptblock property)
Get-ChildItem | Measure-Object -Sum { $_.Length / 1MB }
# (.Sum will be in MB)

```

`Measure-Object` accepts a scriptblock for property — handy for on-the-fly calculations. [Microsoft Learn](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/measure-object?view=powershell-7.5)

---

### 6) Measure boolean incidence (true = 1, false = 0)

```psh
# count how many directories (PSIsContainer is boolean)
Get-ChildItem | Measure-Object -Property PSIsContainer -Sum -Average -Maximum -Minimum
# .Sum gives number of folders (because True is treated as 1)

```

Useful when properties are booleans — `Sum` acts like counting True values. [Microsoft Learn](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/measure-object?view=powershell-7.5)

---

### 7) Measure hashtables or custom objects

```psh
@{num=3}, @{num=4}, @{num=5} | Measure-Object -Maximum num
# .Maximum → 5

```

`Measure-Object` can inspect hashtables / PSCustomObjects (PS6+ enhancements). [Microsoft Learn](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/measure-object?view=powershell-7.5)

---

### 8) Wildcard property names

```psh
Get-Process | Measure-Object -Maximum *paged*memory*size

```

You can target properties using wildcards (useful for similarly-named properties). [Microsoft Learn](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/measure-object?view=powershell-7.5)

---

### 9) Standard deviation

```psh
Get-Process | Measure-Object -Average -StandardDeviation CPU
# returns Average and StandardDeviation of CPU usage across processes

```

`-StandardDeviation` is supported (PS6+). [Microsoft Learn](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/measure-object?view=powershell-7.5)

---

### 10) Watch out for InputObject vs pipeline

```psh
# This treats the whole collection as a single input object:
Measure-Object -InputObject (Get-ChildItem)

# Prefer piping to measure each element:
Get-ChildItem | Measure-Object

```

`-InputObject` treats the argument as one object; piping enumerates items so they are counted individually. Use piping unless you intentionally want single-object behavior. [Microsoft Learn](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/measure-object?view=powershell-7.5)

---

## Common patterns / one-liners (cheat sheet)

```psh
# sum of numeric array
(1,2,3,4,5 | Measure-Object -Sum).Sum

# average of file lengths
(Get-ChildItem -File | Measure-Object -Property Length -Average).Average

# lines, words, characters in file
Get-Content file.txt | Measure-Object -Line -Word -Character

# all stats for a CSV column
Import-Csv employees.csv | Measure-Object -Property Years -AllStats

```

---

## Tips, gotchas & best practices

- If you want **all stats** at once use `-AllStats`. Good for quick summaries. 
- If you need to treat booleans as counts (True = 1), `-Sum` works (see PSIsContainer example).
- Use **scriptblock property** to measure derived values (e.g., convert bytes→MB)
- If a property is missing on some objects, older PS versions might error; recent PS (7.3+) no longer errors unless you run in StrictMode. (Docs note this behavior change.) 
- For counting lines in files, `Get-Content` without `-Raw` returns an array of lines — `.Count` is an easy way to get line count. If you use `-Raw` (one big string), use `Measure-Object -Line`. 
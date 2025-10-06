# Group-Object — deep dive (syntax, behavior, and examples)

`Group-Object` is one of the most powerful cmdlets for categorizing pipeline data. It groups pipeline objects by one or more property values (or by a scriptblock). It returns a `GroupInfo` object (Count, Name, Group) — or a `Hashtable` when you use `-AsHashTable`.

---

## Syntax (concise)

```txt
Group-Object [[-Property] <Object[]>] [-NoElement] [-AsHashTable] [-AsString]
             [-InputObject <PSObject>] [-Culture <String>] [-CaseSensitive]
             [<CommonParameters>]

```

---

## What `Group-Object` returns

- **Default:** objects of type `GroupInfo` with useful properties:
    
    - `.Name` — the group key (value used for grouping)
    - `.Count` — number of items in the group
    - `.Group` — the array of objects that belong to that group
        
- **With `-AsHashTable`:** returns a `Hashtable` where each key is the group name and each value is the group elements.
    

---

## Important parameters — explained

- **`-Property`** — group by one or more properties (name, scriptblock, or calculated).
- **`-NoElement`** — omit the members of each group from the output (just counts).
- **`-AsHashTable` / `-AsString`** — return groups as a hashtable; `-AsString` makes keys string-friendly.
- **`-CaseSensitive` / `-Culture`** — control case sensitivity and culture-based comparisons.
- **`-InputObject`** — note: if you pass a collection here, it is treated as one object. Use pipeline for per-item grouping.
    

---

## Behavior notes

- Output is sorted ascending by group name by default.
- Items inside each group remain in the order they were received.
- Objects missing the property go into a group named `AutomationNull.Value`.
- If property values differ in type, PowerShell uses the first item’s type for conversions.
    

---

## Examples

### 1. Basic grouping

`1,1,2,3,3,3 | Group-Object`

Output:

```txt
Count Name Group
----- ---- -----
    2 1    {1,1}
    1 2    {2}
    3 3    {3,3,3}

```

---

### 2. Group files by extension

```psh
Get-ChildItem -File |
  Group-Object -Property Extension -NoElement |
  Sort-Object -Property Count -Descending |
  Select-Object -First 10

```

---

### 3. Group by scriptblock

`1..10 | Group-Object { $_ % 2 }`

Groups into `0` (even) and `1` (odd).

---

### 4. Group processes by priority

`Get-Process | Group-Object -Property PriorityClass -NoElement`

---

### 5. Group then aggregate

```psh
$data | Group-Object Id | ForEach-Object {
  [PSCustomObject]@{
    Id  = $_.Name
    Sum = ($_.Group | Measure-Object Price -Sum).Sum
  }
}

```

---

### 6. Return a hashtable of groups

```psh
$A = Get-Command Get-*,Set-* -CommandType Cmdlet |
     Group-Object Verb -AsHashTable -AsString

$A.Get   # cmdlets with Verb 'Get'

```

---

### 7. Case-sensitive grouping

```psh
$hash = Get-ChildItem |
        Group-Object Extension -CaseSensitive -AsHashTable

```

---

### 8. Group by multiple properties

```psh
$employees | Group-Object Department,City

```

---

### 9. InputObject vs pipeline

```psh
Group-Object -InputObject (Get-ChildItem)   # one group only
Get-ChildItem | Group-Object               # groups each item

```

---

## Common recipes

- **Top N groups by count**
    

```psh
Get-ChildItem | Group-Object Extension -NoElement |
  Sort-Object Count -Desc | Select-Object -First 10

```

- **Counts as hashtable**
    

```psh
$counts = Get-ChildItem |
          Group-Object Extension -NoElement -AsHashTable -AsString
$counts['.txt']

```

- **Summary objects**
    

```psh
Get-Process |
  Group-Object Name |
  ForEach-Object { [PSCustomObject]@{ Name=$_.Name; Count=$_.Count } } |
  Sort-Object Count -Descending

```

---

## Tips & best practices

- Use `-NoElement` if you only need counts (saves memory).
- Default output is sorted by group name.
- Groups retain the original input order inside `.Group`.
- Missing properties → `AutomationNull.Value`.
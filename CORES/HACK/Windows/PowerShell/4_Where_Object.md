`Where-Object` is **one of the most powerful and commonly used cmdlets** in PowerShell, but its mental model can be tricky at first. Let’s break it down step by step.

---

## **1️⃣ Mental Model of `Where-Object`**

Think of `Where-Object` as a **filter**:

- You have a **collection of objects** (output from any cmdlet).
- You want **only some objects** based on a condition.
- `Where-Object` lets you define that **condition**, returning only objects that match.
    

**Flow:**

`Input objects → Where-Object { condition } → Output filtered objects`

---

## **2️⃣ Basic Syntax**

**Old style (pre-PowerShell 3.0)**

`Get-Process | Where-Object {$_.CPU -gt 100}`

- `$_` → represents the **current object in the pipeline**
- `.Property` → property of the object
- `-gt, -lt, -eq` etc → comparison operators
    

**New simplified style (PowerShell 3.0+)**

`Get-Process | Where-Object CPU -gt 100`

- `Where-Object` automatically treats the first argument as property name.
    

---

## **3️⃣ Top 10 Common Usages**

### 1. Filter numeric property

`Get-Process | Where-Object CPU -gt 100`

- Returns processes using more than 100 CPU units.
    

---

### 2. Filter string property (equals)

`Get-Service | Where-Object Status -eq "Running"`

- Only running services.
    

---

### 3. Filter string property (not equals)

`Get-Service | Where-Object DisplayName -ne "Windows Update"`

- Excludes Windows Update service.
    

---

### 4. Filter string contains / matches

`Get-Process | Where-Object Name -like "*chrome*"`

- Returns processes whose name contains "chrome".
    
- Other wildcards: `*` (any), `?` (single char)
    

---

### 5. Multiple conditions (AND)

`Get-Process | Where-Object { $_.CPU -gt 50 -and $_.Handles -gt 500 }`

- Both conditions must be true.
    

---

### 6. Multiple conditions (OR)

`Get-Service | Where-Object { $_.Status -eq "Running" -or $_.StartType -eq "Manual" }`

- Either condition true.
    

---

### 7. Filter with Not

`Get-Process | Where-Object { -not ($_.Name -like "*svchost*") }`

- Excludes processes containing "svchost".
    

---

### 8. Filter using a script block with method

`Get-ChildItem | Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-7) }`

- Returns files modified in the last 7 days.
    

---

### 9. Using property with array

`Get-Service | Where-Object Status -in "Running","Paused"`

- Filters services whose status is either Running or Paused.
    

---

### 10. Filter by object type

`Get-ChildItem | Where-Object { $_ -is [System.IO.DirectoryInfo] }`

- Returns only directories (ignores files).
    

---

## **4️⃣ Key Mental Model Tips**

1. **Pipeline-based filtering** → always comes **after `|`**.
2. **`$_` is your current object** → use it when you need custom logic.
3. **Comparison operators**:
    

|Operator|Meaning|
|---|---|
|`-eq`|equals|
|`-ne`|not equal|
|`-gt`|greater than|
|`-lt`|less than|
|`-ge`|greater or equal|
|`-le`|less or equal|
|`-like`|wildcard match|
|`-notlike`|wildcard not match|
|`-in`|value in array|

4. **Script block `{}` vs simplified property syntax**
    
    - Script block `{}` → full flexibility (`-and`, `-or`, methods).
        
    - Simplified → `Property -operator value` (PowerShell 3.0+).
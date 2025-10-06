---



---
## *1. Syntax*
```psh
ForEach-Object [-Process] <ScriptBlock>
               [-Begin <ScriptBlock>]
               [-End <ScriptBlock>]
               [<CommonParameters>]

```
## **2. How it Works**

`ForEach-Object` is used in the **pipeline**. It lets you run a block of code for **each item** that flows through.

It has **three script blocks** you can use:

- **`-Begin { ... }`**  
    Runs **once at the start** of the pipeline (before processing items). Good for setup, initialization.
    
- **`-Process { ... }`** _(default if you don’t specify)_  
    Runs **once for each item** coming through the pipeline.  
    Inside here:
    
    - `$_` → refers to the current pipeline object.
        
    - `$PSItem` → same as `$_` (just a more explicit alias).
        
- **`-End { ... }`**  
    Runs **once at the end**, after all items are processed. Good for cleanup or summary.
    

---

## **3. Examples**

### Example 1: Simple usage

`1..5 | ForEach-Object { $_ * 2 }`

**Output**:

`2 4 6 8 10`

👉 Each number in `1..5` is doubled.

---

### Example 2: Printing file names

`Get-ChildItem | ForEach-Object { $_.Name }`

Shows only the **file names** from the directory.

---

### Example 3: Using `-Begin`, `-Process`, `-End`

``1..3 | ForEach-Object `   -Begin   { "Starting..." } `   -Process { "Processing $_" } `   -End     { "Finished!" }``

**Output**:

`Starting... Processing 1 Processing 2 Processing 3 Finished!`

---

### Example 4: Multiple actions inside

`1..3 | ForEach-Object {     $square = $_ * $_     "Number: $_, Square: $square" }`

**Output**:

`Number: 1, Square: 1 Number: 2, Square: 4 Number: 3, Square: 9`

---

### Example 5: Short alias `%`

`1..4 | % { $_ + 10 }`

**Output**:

`11 12 13 14`

---

### Example 6: Complex object example

`Get-Process | ForEach-Object {     "Process: $($_.ProcessName) | ID: $($_.Id)" }`

Outputs a custom string for every process.

---

## **4. Mental Model**

- Think of `ForEach-Object` as a **custom worker** in the pipeline.
    
- Every object flows through the pipe → lands in `$_` → you do something → pass result onward.
    
- Use `-Begin` to prepare, `-Process` to handle each item, and `-End` to wrap up.
    

---

Would you like me to also make a **side-by-side comparison** between `ForEach-Object` (pipeline style) and
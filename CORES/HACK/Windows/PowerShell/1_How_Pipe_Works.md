Let’s break down **how the pipeline actually works** and what kind of “objects” flow through it:

---

## ⚙️ 1. The Pipe = Stream of Objects

- In Unix shells, the pipe (`|`) sends **raw text** from stdout of one command to stdin of the next.
- In PowerShell, the pipe sends **.NET objects**.
    
- Example:
    
`Get-Process | Where-Object CPU -gt 100`

- `Get-Process` outputs `System.Diagnostics.Process` objects.
- Those are passed into `Where-Object`, which checks their `CPU` property.
    

---

## ⚙️ 2. Are These Objects "Generic"?

- **No single generic structure.**
    
- Each cmdlet produces **typed objects** — sometimes built-in .NET classes, sometimes custom ones.
    

Examples:

- `Get-Process` → `System.Diagnostics.Process`
- `Get-Service` → `System.ServiceProcess.ServiceController`
- `Get-ChildItem` → `System.IO.FileInfo` or `System.IO.DirectoryInfo`
    

So the pipeline can carry **any type** of object.

---

## ⚙️ 3. How Does the Next Cmdlet Consume Objects?

- The pipeline engine tries three strategies, in this order:
    

1. **ByValue binding** → If the input object type matches a parameter type directly, it passes the whole object.
    
    `Get-Process | Stop-Process`
    Here `Stop-Process` has a `-InputObject` parameter that accepts `System.Diagnostics.Process`. The match works, so the object flows directly.
    
2. **ByPropertyName binding** → If the input object has a property name matching a parameter, it maps it.
    
    `Get-Process | Select-Object Name | Stop-Process`
    - `Select-Object Name` outputs a generic object with a `Name` property.
    - `Stop-Process` has a `-Name` parameter.
    - Pipeline auto-binds the property `Name` → parameter `-Name`.
        
3. **Fallback to string** → If neither works, the object is converted to its string representation.
    
    - Example: piping to `Out-File` or to external commands like `sort.exe`.
        

---

## ⚙️ 4. Special Case: Formatting Cmdlets

- `Format-Table`, `Format-List`, etc. **replace objects with formatting instructions.*

- After this point, the pipeline is no longer carrying the original data, just “how to render it.”
- That’s why you should only use `Format-*` at the **end** of pipelines.
    

---

## ⚙️ 5. Mental Model

- Imagine the pipe as a **conveyor belt**.
    
- Each station (cmdlet) either:
    
    - filters objects (like `Where-Object`),
    - reshapes them (like `Select-Object`),
    - consumes them (like `Out-File`),
    - or just displays them (`Format-Table`).
        
- The objects themselves can be any .NET type — not generic “records,” but full structured entities.
    

---

✅ So:

- PowerShell pipeline **passes real .NET objects**.
- Objects are **typed**, not generic, but cmdlets can often bind by property names, which gives them a “loose fit” feel.
- Formatting destroys object fidelity, so use it only at the end.
    

---


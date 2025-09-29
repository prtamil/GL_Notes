## 1️⃣ **Cmdlet (Command-let)**

**Definition:**

- A **cmdlet** is a lightweight, specialized .NET class that performs a single action.
- It’s **compiled**, strongly typed, and designed to integrate seamlessly with PowerShell’s **object-oriented pipeline**.
    

**Characteristics:**

- Always follows **Verb-Noun** naming convention: `Get-Process`, `Set-Item`, `Remove-User`.
- Returns **.NET objects**, not plain text.
- Runs inside PowerShell, not a separate executable.
- Has **parameters** with built-in parsing and validation.
- Supports **help system** (`Get-Help CmdletName`).
    

**Example:**

`Get-Process -Name powershell`

- `Get-Process` is a cmdlet.
- Returns a collection of `System.Diagnostics.Process` objects.
    

---

## 2️⃣ **Command (in PowerShell context)**

**Definition:**

- A **command** in PowerShell is a general term that can refer to **any executable instruction you can run**, including:
    
    - Cmdlets
    - Functions
    - Aliases
    - Scripts (`.ps1`)
    - Native executables (`.exe` or `.bat`)
        

**Example:**

```ps
ping google.com 
.\myscript.ps1 
Get-Process
````

- `ping` → external executable
- `.\myscript.ps1` → script file
- `Get-Process` → cmdlet
    

---

## 3️⃣ **Key Differences**

|Feature|Cmdlet|Command (general)|
|---|---|---|
|Type|Compiled .NET class|Anything executable in PowerShell|
|Output|.NET objects|Usually text (unless cmdlet or script returns objects)|
|Naming|Verb-Noun|Any name (script, alias, executable)|
|Pipeline|Fully integrated (objects pass cleanly)|Text-based if external executable|
|Help|Integrated (`Get-Help`)|May not have structured help (depends on script/executable)|

---

## 4️⃣ **Mental Model**

```txt
 PowerShell “command” = umbrella term
 ├─ Cmdlet → compiled .NET, objects, pipeline-aware
 ├─ Function → user-defined cmdlet-like scripts
 ├─ Script → .ps1 files, can call cmdlets or other commands
 └─ External executable → .exe/.bat, usually outputs text

```

✅ **Takeaway:**

- Every **cmdlet is a command**, but not every **command is a cmdlet**.
- Cmdlets are **first-class PowerShell citizens**, optimized for the pipeline and object-oriented scripting.
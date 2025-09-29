Creating a **cmdlet in PowerShell** can be done in two main ways: **advanced functions (script cmdlets)** or **compiled cmdlets in C#**. I’ll break both approaches step by step.

---

## 1️⃣ **Advanced Function (Script Cmdlet)**

This is the easiest way — you write a function in PowerShell and expose it as a cmdlet using `[CmdletBinding()]`.

### Example: Create `Get-Square` Cmdlet

```ps
function Get-Square {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$true)]
        [int]$Number
    )

    process {
        $Number * $Number
    }
}

```

### How it works

- `[CmdletBinding()]` → makes the function behave like a real cmdlet:
    - Supports `-Verbose`, `-Debug`, `-ErrorAction`, etc.
        
- `param` → defines typed parameters.
- `process {}` → the block that runs for each input from the pipeline.
    

### Usage

```ps
Get-Square -Number 5
# Output: 25

1..5 | Get-Square
# Outputs squares of numbers 1 through 5

```

✅ **Pros:**

- Quick, no compilation needed
- Fully integrated with pipeline and PowerShell conventions
    

---

## 2️⃣ **Compiled Cmdlet in C#**

For production-grade cmdlets or modules, you can write a **compiled cmdlet in C#** that derives from `System.Management.Automation.Cmdlet`.

### Example: C# Cmdlet

```cs
using System;
using System.Management.Automation;

[Cmdlet(VerbsCommon.Get, "Square")]
public class GetSquareCmdlet : Cmdlet
{
    [Parameter(Mandatory = true, ValueFromPipeline = true)]
    public int Number { get; set; }

    protected override void ProcessRecord()
    {
        WriteObject(Number * Number);
    }
}

```

### How to Use

1. Compile into a DLL using Visual Studio or `csc.exe`.
2. Import in PowerShell:
    

```psh
Import-Module "C:\Path\To\YourModule.dll"
Get-Square -Number 5

```

### Pros of Compiled Cmdlets

- Strong typing, better performance
- Can be shipped as modules for enterprise use
- Full access to .NET runtime
    

---

## 3️⃣ **Mental Model**

```txt
PowerShell Cmdlet
 ├─ Script Cmdlet → advanced functions in .ps1
 └─ Compiled Cmdlet → C# class inheriting from Cmdlet base class

```

- Both are **first-class cmdlets**: they can take pipeline input, support `-Verbose`, and return objects.
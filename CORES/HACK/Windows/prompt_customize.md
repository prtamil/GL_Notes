# Customizing Poweshell path 
```powershell

function prompt {
  $p = Split-Path -leaf -path (Get-Location)
  "$p> "
}

```

PowerShell profile  
```powershell
 (`%userprofile%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1`); 
 ```
 it may be blank or even not exist if you have never modified it before.

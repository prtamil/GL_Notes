
## Get Logs from CMI(COmmon INformation Model) (WMI's Upgrade)
```pwsh
Get-CIMInstance 
Get-CimInstance -ClassName Win32_NTLogEvent 
```
## Get windows Event 
```pwsh
Get-WinEvent -LogName System -MaxEvents 10
```

## NtObjectManager
```txt
1. NtObjectManager (pwsh) (NtCoreLib) (https://github.com/googleprojectzero/sandbox-attacksurface-analysis-tools/tree/main) for Nt internals
```

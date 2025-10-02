# 🔟 Top Object-Based Cmdlets in PowerShell

### 1. **`Get-Member`**

👉 Explore objects (properties, methods, types).

`Get-Process | Get-Member`

(Most important for learning PowerShell’s object-oriented world.)

---

### 2. **`Select-Object`**

👉 Project/shape objects, pick/rename properties, create calculated ones.

`Get-Process | Select-Object Name, @{n='MemoryMB';e={[math]::Round($_.WS/1MB,2)}}`

---

### 3. **`Where-Object`**

👉 Filter objects by condition.

`Get-Service | Where-Object Status -eq 'Running'`

---

### 4. **`Sort-Object`**

👉 Order objects by property.

`Get-Process | Sort-Object CPU -Descending`

---

### 5. **`Group-Object`**

👉 Aggregate/group objects by property.

`Get-Process | Group-Object Company`

---

### 6. **`Measure-Object`**

👉 Summarize objects (count, min, max, average, sum).

`Get-Process | Measure-Object CPU -Sum -Average`

---

### 7. **`ForEach-Object`**

👉 Transform or apply actions per object. (Like `map` + `reduce`).

`Get-Process | ForEach-Object { $_.Name.ToUpper() }`

---

### 8. **`Format-Table` / `Format-List`**

👉 Pretty-print output for human eyes (not for further pipeline use).

`Get-Service | Format-Table Name, Status -AutoSize`

---

### 9. **`Out-File` / `Export-Csv` / `ConvertTo-Json`**

👉 Send objects out of PowerShell as text, CSV, or JSON.

`Get-Process | Export-Csv procs.csv -NoTypeInformation`

---

### 10. **`Compare-Object`**

👉 Diff two object sets.

`Compare-Object (Get-Content file1.txt) (Get-Content file2.txt)`

---

# ⚡ Bonus Mentions

- **`Tee-Object`** → clone pipeline stream (see data mid-pipeline).
- **`Select-String`** → object-based grep.
- **`Out-GridView`** → interactive GUI view of objects.
- **`Join-Object`** (community module) → relational joins on objects.
    

---

✅ **Mental model**:

- **Get-Member** → discover
- **Where-Object** → filter
- **Select-Object** → project/shape
- **Sort-Object** → order
- **Group-Object** → aggregate
- **Measure-Object** → summarize
- **ForEach-Object** → transform/apply
- **Format-*** → display
- **Export/Convert** → persist/share
- **Compare-Object** → diff
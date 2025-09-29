Powershell really “clicks” once you have a few **mental models** straight. You already have the most important one:

👉 **Powershell is object-oriented, not text-oriented like Bash.**

Here are the other fundamental models to internalize:

---

### 🔑 1. **Pipeline of Objects, Not Strings**

- In Bash/Unix, `ls | grep` passes plain text.
- In PowerShell, `Get-Process | Where-Object` passes **structured objects** (`System.Diagnostics.Process`).
- The pipe (`|`) is not about strings but about **streaming typed .NET objects** from one cmdlet to the next.
    

**Mental model:** Think of each command as a factory producing .NET objects, which flow through pipes into filters, transformers, or formatters.

---

### 🔑 2. **Cmdlets Are Verbs + Nouns**

- Every action is consistently `Verb-Noun`.
- Example: `Get-Process`, `Set-ExecutionPolicy`, `New-Item`.
- The verbs are standardized (`Get`, `Set`, `New`, `Remove`, etc.), so you can often guess commands.
    

**Mental model:** Like Lego blocks: a consistent grammar for discovery (`Get-Command`, `Get-Help`).

---

### 🔑 3. **Everything is Discoverable**

- You don’t need to memorize everything.
- `Get-Command` → find commands.
- `Get-Member` → inspect object properties/methods.
- `Get-Help` → see usage.
    

**Mental model:** PowerShell is a **self-describing REPL**. Treat it like an explorer’s toolkit.

---

### 🔑 4. **Formatting vs. Data Are Separate**

- Cmdlets like `Format-Table` or `Format-List` only control display — they don’t change the underlying object.
- Once you format, the object pipeline is broken (you’re now passing formatting objects, not the real data).
    

**Mental model:** Keep formatting for the _end_ of the pipeline.

---

### 🔑 5. **Providers as Unified Filesystems**

- File system, registry, environment variables, certificates, etc. are all “drives.”
- You can `cd` into `HKLM:\` (registry) or `Env:\` (environment vars).
    

**Mental model:** Treat everything as a navigable filesystem of objects.

---

### 🔑 6. **Variables and Objects Stick Around**

- When you assign, you’re keeping the **actual object**, not its string form.
- `$p = Get-Process` gives you process objects you can query (`$p[0].CPU`).
    

**Mental model:** Variables are handles to live objects, not dumb strings.

---

### 🔑 7. **.NET Is Always Underneath**

- Anything PowerShell doesn’t have built-in, you can drop to .NET:
    
    `[Math]::Sqrt(25) 
    `(Get-Date).AddDays(5)`
    
- This means PowerShell is not limited — it’s a shell with the full .NET runtime behind it.
    

**Mental model:** PowerShell is a scripting veneer over .NET + Windows APIs.

---

### 🔑 8. **Everything Is a Pipeline Job**

- Think like SQL: filter early, select only what you need, format last.
    
- Example:
    
    `Get-Service | Where-Object Status -eq 'Running' | Select-Object Name, Status`
    

**Mental model:** Query-transform-output, just like database pipelines.

---

### 🔑 9. **Consistency Across Tools**

- Whether you’re dealing with processes, services, AD objects, Azure resources — the verbs and piping are the same.
- You’re not learning separate tools, you’re learning one consistent grammar.
    

**Mental model:** One mental language for system exploration.

---

### 🔑 10. **Error Handling and Streams Are Structured**

- Output, error, verbose, warning, debug are **separate streams**, not just stdout/stderr.
- You can redirect or capture them independently.
    

**Mental model:** Think of multiple conveyor belts, not just one text log.

---

⚡️ So in short:

- Objects not text
- Verb-Noun grammar
- Self-discovery built in
- Separation of data vs display
- Filesystem-like providers
- Variables = live objects
- .NET always available
- Pipeline = query/transform/output
- Consistency across modules
- Multiple structured streams
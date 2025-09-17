## **In-Depth Look at Kernel Internals of Seccomp**

### **1. Where Seccomp is Implemented in the Linux Kernel**

Seccomp is implemented in the **Linux security subsystem** and interacts with the **syscall entry path**. The key kernel files involved in Seccomp include:

- **`security/seccomp.c`** → Core Seccomp implementation
- **`kernel/seccomp.c`** → BPF-based syscall filtering
- **`arch/x86/entry/common.c`** → Syscall handling integration
- **`include/linux/seccomp.h`** → Seccomp data structures

---

### **2. Seccomp Lifecycle in the Kernel**

When a process enables Seccomp, the kernel enforces syscall restrictions **before executing any system call**. The flow is as follows:

1. **Process calls `prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, filter)`**
2. **Kernel validates and installs the filter** (using a BPF verifier).
3. **Every syscall entry point checks Seccomp rules**:
    - If a syscall is **allowed**, it proceeds as usual.
    - If a syscall is **denied**, the process is killed or restricted based on the action (`SECCOMP_RET_KILL`, `SECCOMP_RET_ERRNO`, etc.).

#### **Key Kernel Functions Involved**

- **`do_seccomp()`** → The main entry point for Seccomp checks
- **`seccomp_set_mode_filter()`** → Registers the BPF filter
- **`seccomp_run_filters()`** → Evaluates syscall against installed filters
- **`__seccomp_filter()`** → Executes the BPF rules

---

### **3. How Seccomp Hooks into Syscall Execution**

Seccomp integrates with the Linux syscall execution path **at the entry point of every system call**.

#### **Syscall Entry Flow (x86_64)**

1. **Syscall enters kernel mode** (`do_syscall_64()` in `arch/x86/entry/common.c`)
2. **Kernel checks for Seccomp filters**:

```c
if (secure_computing())
    return -EPERM;

```

3. **`secure_computing()`** calls `do_seccomp()`, which runs the BPF filter.
4. If the syscall is allowed, it continues to `syscall_dispatch()`.
5. If blocked, the kernel enforces the action (`kill`, `errno`, `trap`, etc.).

---

### **4. Seccomp and BPF (Berkeley Packet Filter)**

Seccomp uses **BPF (Berkeley Packet Filter)** to evaluate syscalls **at runtime**.

#### **BPF Workflow in Seccomp**

1. **Filter Compilation**: The user passes a filter using `struct sock_fprog` (a BPF program).
2. **BPF Verifier**: The kernel **validates the BPF program** before installing it.
3. **Filter Execution**: Every syscall is evaluated against the installed BPF rules.
4. **Action Decision**: The filter decides whether to allow, deny, or log the syscall.

#### **Example of a BPF Rule**

```c
struct sock_filter filter[] = {
    BPF_STMT(BPF_LD+BPF_W+BPF_ABS, offsetof(struct seccomp_data, nr)), // Load syscall number
    BPF_JUMP(BPF_JMP+BPF_JEQ+BPF_K, __NR_write, 0, 1), // Allow write()
    BPF_STMT(BPF_RET+BPF_K, SECCOMP_RET_KILL), // Kill all other syscalls
};

```

---

### **5. Seccomp Actions (Return Values of BPF Filters)**

Seccomp can enforce different security policies using **return values from BPF programs**:

|Return Value|Action|
|---|---|
|`SECCOMP_RET_ALLOW`|Allow the syscall|
|`SECCOMP_RET_KILL_PROCESS`|Kill the process|
|`SECCOMP_RET_KILL_THREAD`|Kill only the offending thread|
|`SECCOMP_RET_ERRNO`|Block syscall with an error code|
|`SECCOMP_RET_TRACE`|Send a `PTRACE_EVENT` to a monitoring process|
|`SECCOMP_RET_LOG`|Log the syscall (Linux 4.14+)|
|`SECCOMP_RET_TRAP`|Deliver `SIGSYS` to the process|

---

### **6. Seccomp Notify (Linux 5.9+)**

In **Linux 5.9**, Seccomp gained the **notify feature**, which allows an external process (like a security daemon) to decide whether to allow or block syscalls in real-time.

**Workflow:**

1. The process triggers a restricted syscall.
2. The kernel **pauses the process** and sends a notification to a monitoring program.
3. The external process **reviews the syscall** and responds with "allow" or "deny."
4. The original process continues execution based on the response.

**Example Use Case:**  
Docker uses `seccomp_notify()` to allow privileged helper processes (outside the container) to handle restricted operations.

---

### **7. Performance Overhead of Seccomp**

Seccomp is designed to be **lightweight**, but syscall filtering introduces a small overhead:

- **Strict mode (`SECCOMP_MODE_STRICT`)**: Near-zero overhead.
- **Filter mode (`SECCOMP_MODE_FILTER`)**:
    - **Direct syscall filtering (fast)**: ~200–500ns per syscall.
    - **Complex BPF logic (slower)**: Can reach 1–3μs per syscall.
    - **Seccomp Notify (slowest)**: Requires IPC with an external process.

To optimize performance, use **minimal filters** and **avoid unnecessary BPF complexity**.

---

### **8. Known Bypasses and Limitations**

#### **1. Bypassing Seccomp via `execve()`**

- If a process **executes a new binary**, Seccomp **does not persist** unless explicitly configured.
- Fix: Use **"no_new_privs"** (`PR_SET_NO_NEW_PRIVS`) to prevent privilege escalation.

#### **2. Kernel Bugs Breaking Seccomp**

- Certain **kernel exploits** (e.g., `userfaultfd()`, `ptrace()`) have been used to **bypass Seccomp**.
- Fix: Always combine Seccomp with **namespaces, capabilities, and AppArmor/SELinux**.

#### **3. Not a Full Sandbox**

- Seccomp **only filters syscalls**; it **does not** restrict file access or network access.
- Fix: Combine Seccomp with **cgroups, namespaces, and LSMs (AppArmor/SELinux)**.

---

### **9. Future of Seccomp**

- **More granular syscall filtering** (e.g., limiting by arguments, return values).
- **Improved seccomp logging** for better debugging.
- **Optimized BPF performance** to reduce syscall overhead.
- **Integration with eBPF** for more dynamic security policies.

---

## **Conclusion**

✅ Seccomp filters syscalls **at the kernel level** before execution.  
✅ Uses **BPF rules** to allow or deny syscalls dynamically.  
✅ **Hooks directly into the syscall entry path** (`do_seccomp()`).  
✅ **Seccomp Notify (Linux 5.9+)** allows real-time security decisions.  
✅ **Minimal overhead**, but should be combined with **namespaces, cgroups, and LSMs** for full security.

Would you like **example code** to implement a custom Seccomp filter?
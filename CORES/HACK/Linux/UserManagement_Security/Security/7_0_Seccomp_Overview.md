## **Deep Dive into Seccomp in Modern Linux Security**

### **Mental Model of Seccomp**

Seccomp (**Secure Computing Mode**) is a **kernel-level syscall filter** that restricts the system calls a process can execute. It is used for **sandboxing applications** by reducing the attack surface.

**Key Concepts:**

- **Default-Deny Model**: Processes can be configured to allow only a limited set of syscalls.
- **BPF-Based Filtering**: Uses Berkeley Packet Filters (BPF) to enforce syscall policies.
- **Minimal Overhead**: Unlike full-fledged sandboxing tools (e.g., AppArmor, SELinux), seccomp is lightweight.
- **Process-Specific**: Applied per process, making it ideal for containerization and untrusted code execution.

---

## **Structured Topic List**

### **1. Basics of Seccomp**

- What is Seccomp?
- History and Evolution
- Use Cases in Modern Security

### **2. How Seccomp Works in the Linux Kernel**

- **Seccomp Modes**:
    - **Strict Mode (`SECCOMP_MODE_STRICT`)** – Only allows `read`, `write`, `_exit`, and `sigreturn`.
    - **Filter Mode (`SECCOMP_MODE_FILTER`)** – Custom syscall filtering using BPF.
- Kernel Internals:
    - `sys_seccomp()` syscall
    - Seccomp hooks in `do_syscall_64()`
    - `security/seccomp.c` implementation

### **3. BPF (Berkeley Packet Filter) for Seccomp**

- Understanding BPF Bytecode
- How Seccomp Uses BPF to Filter Syscalls
- BPF Performance & Security Considerations

### **4. Using Seccomp in Applications**

- **Syscalls for Seccomp**:
    - `prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, ...)`
    - `seccomp()` syscall
- **Creating a Seccomp Policy**
    - Allowing only necessary syscalls
    - Blocking dangerous syscalls like `execve`, `ptrace`
    - Handling logging and debugging

### **5. Seccomp in Containers**

- Docker and Kubernetes Seccomp Profiles
- Running Containers with Seccomp Restrictions
- Example: `docker run --security-opt seccomp=profile.json`

### **6. Seccomp in Systemd Services**

- Configuring Seccomp via `Systemd`
- Example `seccomp.conf` for restricting services
- Preventing Privilege Escalation

### **7. Seccomp and Other Security Mechanisms**

- Seccomp + Namespaces (Unprivileged Containers)
- Seccomp vs. AppArmor vs. SELinux
- Seccomp + Capabilities: Combining Fine-Grained Controls

### **8. Bypasses and Weaknesses**

- Known Seccomp Bypasses
- Why **Filtering Syscalls is Not Enough**
- Kernel Bugs that Break Seccomp Security

---

Would you like to focus on **kernel implementation**, **practical usage**, or **real-world examples** (e.g., hardening a service like Nginx or OpenSSH)?
can you give Basics of Seccomp What is Seccomp? History and Evolution Use Cases in Modern Security

###### ChatGPT said:

## **Basics of Seccomp**

### **What is Seccomp?**

Seccomp (**Secure Computing Mode**) is a **Linux kernel security feature** that restricts the system calls (syscalls) a process can make. It acts as a lightweight **syscall firewall**, allowing processes to run with only the minimal permissions they need.

Seccomp is commonly used in **sandboxing** and **container security** to prevent applications from making unexpected syscalls that could lead to privilege escalation, kernel exploits, or security breaches.

---

### **History and Evolution of Seccomp**

#### **1. Initial Design (2005 – Linux 2.6.12)**

- Introduced by **Andrea Arcangeli** in **Linux 2.6.12** (2005).
- Original **strict mode**: A process could only make **read, write, exit, and sigreturn** syscalls after enabling Seccomp.
- Used in **high-security environments** but was **too restrictive** for general applications.

#### **2. Seccomp-BPF (2012 – Linux 3.5)**

- **Will Drewry** (Google) expanded Seccomp by integrating it with **Berkeley Packet Filter (BPF)**.
- Allowed fine-grained filtering of **specific syscalls**, their **arguments**, and **return values**.
- **First major use case:** **Google Chrome Sandbox** to isolate untrusted code execution.

#### **3. Integration with Containers & Systemd (2015 – Linux 4.x)**

- **Docker (2015)**: Started using Seccomp profiles to sandbox containers.
- **Systemd (2016)**: Introduced Seccomp-based service hardening (`SystemCallFilter=`).
- **Kubernetes (2018)**: Seccomp became a **default security feature** for pods.

#### **4. Modern Enhancements (Linux 5.x and Beyond)**

- **Seccomp Notify (Linux 5.9, 2020)**: Allows processes to handle blocked syscalls dynamically (used in sandboxing).
- **Performance Improvements**: Optimized BPF JIT compilation for faster syscall filtering.
- **More Widespread Use**: Adopted by Firefox, Flatpak, Snap, and systemd to isolate services.

---

### **Use Cases of Seccomp in Modern Security**

#### **1. Sandboxing Untrusted Applications**

- **Google Chrome and Firefox** use Seccomp to **isolate rendering processes**, preventing web-based exploits from escaping the browser sandbox.
- **Flatpak and Snap** use Seccomp to restrict what applications can do outside their isolated environment.

#### **2. Container Security**

- **Docker & Kubernetes** use Seccomp to enforce **least privilege** on containerized applications.
- Default **Docker seccomp profile** blocks **dangerous syscalls** like `ptrace`, `mount`, `kexec`, and `swapon`.

#### **3. Hardening System Services (Systemd Seccomp)**

- **Restricting system services** from making unnecessary syscalls, preventing privilege escalation.
- Example:
    
```ini
[Service]
SystemCallFilter=@default @mount
SystemCallArchitectures=native

```
    

#### **4. Preventing Kernel Exploits**

- Blocks **syscalls commonly used in privilege escalation**, such as `unshare()`, `clone()`, `mmap()`.
- Example: **Preventing container escapes by blocking `userfaultfd()`** (common in exploits).

#### **5. Protecting High-Security Applications**

- Used in **OpenSSH sandbox** to limit syscalls available to authentication processes.
- Example:
    
    
    `sshd -D -o UsePrivilegeSeparation=sandbox`
    

---

### **Conclusion**

- **Seccomp provides fine-grained syscall filtering** to reduce the attack surface.
- **Evolved from a strict model** (Linux 2.6) to a **flexible BPF-based filter** (Linux 3.5+).
- **Now widely used** in **containers, browsers, systemd, and security-focused applications**.

Would you like a **hands-on tutorial on writing a Seccomp filter** or an **in-depth look at kernel internals**?
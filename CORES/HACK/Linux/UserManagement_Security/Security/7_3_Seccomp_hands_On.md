## **Hands-On Tutorial: Writing a Seccomp Filter in C**

We will create a simple **Seccomp filter** that restricts a process to only using `read()`, `write()`, and `_exit()` syscalls.

---

### **1. Prerequisites**

To compile and run the Seccomp filter, install the **libseccomp** development package:

#### **Debian/Ubuntu**:


`sudo apt install libseccomp-dev`

#### **Fedora/RHEL**:


`sudo dnf install libseccomp-devel`

#### **Arch Linux**:


`sudo pacman -S libseccomp`

---

### **2. Writing a Basic Seccomp Filter**

We will write a **C program** that applies a **Seccomp filter** using `seccomp_rule_add()`.

#### **seccomp_filter.c**

```c
#include <stdio.h>
#include <stdlib.h>
#include <seccomp.h>
#include <unistd.h>

void setup_seccomp() {
    scmp_filter_ctx ctx;

    // Create a new filter context
    ctx = seccomp_init(SCMP_ACT_KILL); // Default action: Kill process if syscall is not allowed
    if (ctx == NULL) {
        perror("seccomp_init");
        exit(1);
    }

    // Allow read, write, and exit syscalls
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(read), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit_group), 0);

    // Load the seccomp filter
    if (seccomp_load(ctx) < 0) {
        perror("seccomp_load");
        seccomp_release(ctx);
        exit(1);
    }

    seccomp_release(ctx); // Cleanup
}

int main() {
    setup_seccomp();

    // Allowed syscalls
    write(STDOUT_FILENO, "Seccomp enabled! Try running ls or another command.\n", 52);

    // Forbidden syscall (this will cause the process to be killed)
    system("ls");

    return 0;
}

```

---

### **3. Compiling and Running the Program**

Compile the program with `gcc`:


`gcc seccomp_filter.c -o seccomp_example -lseccomp`

Run it:


`./seccomp_example`

**Expected output:**


`Seccomp enabled! Try running ls or another command. Killed`

The `system("ls")` call triggers a **fork + exec syscall**, which is **not allowed**, so the kernel **kills the process**.

---

### **4. Modifying Seccomp Actions**

Seccomp supports various actions instead of **killing the process**:

|Action|Description|
|---|---|
|`SCMP_ACT_ALLOW`|Allow syscall|
|`SCMP_ACT_KILL_PROCESS`|Kill process (default)|
|`SCMP_ACT_KILL_THREAD`|Kill thread only|
|`SCMP_ACT_TRAP`|Send `SIGSYS` signal to process|
|`SCMP_ACT_ERRNO(EPERM)`|Return an error (EPERM)|
|`SCMP_ACT_LOG`|Log syscall (requires `auditd`)|

For example, to return **EPERM** (`Operation not permitted`) instead of killing the process:

```c
ctx = seccomp_init(SCMP_ACT_ERRNO(EPERM));

```

---

### **5. Debugging Seccomp Policies**

To debug blocked syscalls, run the program under `strace`:

`strace ./seccomp_example`

You will see output like:

```sh
write(1, "Seccomp enabled! Try running ls or another command.\n", 52) = 52
execve("/bin/sh", ["sh", "-c", "ls"], 0x7ffcc2e15c38 /* 30 vars */) = -1 EPERM (Operation not permitted)

```
---

### **6. Applying Seccomp to a Running Process**

Instead of embedding Seccomp in your program, you can **apply it externally** to any running process using `prctl()`:


`sudo prctl --seccomp=2 --exec /bin/bash`

This runs `bash` with **Seccomp mode 2** (`SECCOMP_MODE_FILTER`), blocking restricted syscalls.

---

### **7. Using Seccomp in Containers (Docker Example)**

You can apply Seccomp profiles to **Docker containers**:


`docker run --rm --security-opt seccomp=unconfined alpine sh`

- `seccomp=unconfined` → Disables Seccomp (for testing).
- `seccomp=profile.json` → Applies a custom Seccomp profile.

To generate a **default Docker Seccomp profile**:


`docker run --rm --security-opt seccomp=default alpine sh`

---

### **8. Conclusion**

✅ **Seccomp filters syscalls at the kernel level** for enhanced security.  
✅ **BPF-based filtering** allows fine-grained control over allowed syscalls.  
✅ **Used in containers, systemd, browsers, and secure applications**.  
✅ **Minimal overhead**, making it an efficient security mechanism.

Would you like to see **a real-world example**, like securing **Nginx or OpenSSH** with Seccomp?
## **Theoretical Deep Dive: How Linux Implements Capabilities at the Kernel Level**

### **Mental Model: How Capabilities Work in the Kernel**

- Capabilities in Linux are implemented as **bitmasks** that are associated with **processes** and **files**.
- Instead of a **binary root/non-root** model, Linux assigns **specific privileges** to processes.
- The kernel enforces **capability checks** at various security-sensitive points.

---

## **1. Kernel Structures for Capabilities**

### **Process Credentials (`task_struct` and `cred`)**

- Each process in Linux is represented by a **task structure (`task_struct`)**.
- **Capabilities are stored in the `cred` structure**, which is referenced by `task_struct`:
    
```c
struct task_struct {
    ...
    const struct cred __rcu *real_cred;  // Real credentials
    const struct cred __rcu *cred;       // Effective credentials
    ...
};

```
    
- The `cred` structure contains **capability sets**:
    
```c
struct cred {
    ...
    kernel_cap_t cap_effective;  // Capabilities in effect
    kernel_cap_t cap_permitted;  // Maximum capabilities a process can use
    kernel_cap_t cap_inheritable; // Capabilities passed via exec
    ...
};

```
    

### **File Capability Storage (`fs/xattr.c`)**

- Capabilities can be stored as **extended attributes** (`xattr`) in the filesystem:
    - Namespace: `security.capability`
    - Used by `setcap` and `getcap`
    - Checked by the kernel during `execve()`

---

## **2. Capability Sets in the Kernel**

Each process in Linux has **three capability sets**:

|**Capability Set**|**Description**|**Syscalls to Modify**|
|---|---|---|
|**Permitted** (`cap_permitted`)|The capabilities a process is allowed to use.|`capset()`|
|**Effective** (`cap_effective`)|The capabilities currently active (used by kernel checks).|`capset()`, `prctl()`|
|**Inheritable** (`cap_inheritable`)|Capabilities that survive an `execve()`.|`prctl(PR_CAP_AMBIENT, ...)`|

---

## **3. How Capabilities Are Enforced in the Kernel**

When a process tries to perform a privileged operation, the kernel **checks capabilities** instead of checking UID=0.

### **Kernel Capability Checks**

- The kernel uses the `capable()` function to check whether a process has a capability.
    
```c
int capable(int cap) {
    return security_capable(current_cred(), cap, 0);
}

```
    
- Common kernel functions using `capable()`:
    - **Network Operations**
    ```c
    if (!capable(CAP_NET_ADMIN))
    return -EPERM;

	```
        
    - **Mounting Filesystems**
        
    ```c
    if (!capable(CAP_SYS_ADMIN))
    return -EPERM;

	```
        
    - **Changing System Time**
        
	```c
	if (!capable(CAP_SYS_TIME))
    return -EPERM;

	```
        

---

## **4. System Calls for Capability Management**

### **Checking Capabilities**

- `capget()` – Get current process capabilities:
    
```c
struct __user_cap_header_struct hdr;
struct __user_cap_data_struct data[2];
capget(&hdr, data);

```
    

### **Modifying Capabilities**

- `capset()` – Set process capabilities:
    
```
struct __user_cap_header_struct hdr;
struct __user_cap_data_struct data[2];
capset(&hdr, data);

```
    
    - This **keeps capabilities across execve()**.

### **File Capabilities**

- Kernel uses **extended attributes (`xattr`)** to store file capabilities.
- Example of setting `CAP_NET_RAW` on `tcpdump`:
    
```bash
sudo setcap cap_net_raw+ep /usr/bin/tcpdump

```
    
- Kernel verifies file capabilities during `execve()` in `fs/exec.c`:
    
```c
static int bprm_caps_from_file(struct linux_binprm *bprm, struct file *file) {
    struct cpu_vfs_cap_data vcaps;
    ...
    error = get_vfs_caps_from_disk(file, &vcaps);
}

```
---

## **5. Capability Bounding & Restriction**

### **Bounding Set (`cap_bset`)**

- Defines **maximum** capabilities a process can have.
- If a capability is removed from `cap_bset`, it **can never be added again**.
- Set using:
    
```c
prctl(PR_CAPBSET_DROP, CAP_SYS_ADMIN);

```
    
- Used to **prevent privilege escalation**.

### **NoNewPrivileges (`PR_SET_NO_NEW_PRIVS`)**

- Ensures that **execve() does not add new privileges**.
- Used in sandboxing and systemd:
    
```c
prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0);

```
    

---

## **6. Interaction with Other Security Mechanisms**

### **Capabilities & Seccomp**

- Seccomp (`seccomp-bpf`) **restricts system calls** beyond capabilities.
- Example:
```c
seccomp(SECCOMP_MODE_FILTER, 0, &prog);

```
    
- Example seccomp profile for Docker:
    
 ```json
 {
    "defaultAction": "SCMP_ACT_ERRNO",
    "syscalls": [
        { "names": ["read", "write", "exit", "sigreturn"], "action": "SCMP_ACT_ALLOW" }
    ]
}

```

### **Capabilities & Namespaces**

- Inside **user namespaces**, capabilities are **re-mapped**.
- Example: Creating an unprivileged container
    
```bash
    `unshare --user --map-root-user --net bash`
```
    
- Inside the container, `CAP_NET_ADMIN` is local but **not global**.

### **Capabilities & Systemd**

- Systemd restricts services using:
    
```ini
[Service]
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_ADMIN

```
    
- This **prevents privilege escalation** in system services.

---

## **7. Security Risks & Bypasses**

### **Why `CAP_SYS_ADMIN` is Dangerous**

- `CAP_SYS_ADMIN` is **too powerful** (similar to root).
- Allows:
    - Mounting filesystems
    - Changing system security settings
    - Bypassing some security checks

### **How Attackers Exploit Capabilities**

1. **Leaking Capabilities via Execve**
    
    - If a binary keeps `cap_effective`, it can be misused.
    - Fix: Use `NoNewPrivileges=yes` in systemd.
2. **Container Breakout with `CAP_SYS_ADMIN`**
    
    - If a container has `CAP_SYS_ADMIN`, it can escape by mounting the host filesystem.
    - Fix: Use `--cap-drop=ALL` in Docker.

---

## **Conclusion**

- Linux capabilities **replace the all-powerful root model** with **fine-grained privilege separation**.
- The kernel enforces capabilities using **bitmasks**, **task_struct → cred**, and **capable() checks**.
- **Syscalls like `capset()`, `capget()`, and `prctl()`** manage capabilities at runtime.
- Capabilities interact with **seccomp, namespaces, systemd, and LSMs (SELinux, AppArmor)**.
- **Security risks exist**, especially with `CAP_SYS_ADMIN` and `execve()` privilege leaks.

Would you like an **example of kernel capability debugging** (e.g., tracing `capable()` calls in a running system)? 🚀
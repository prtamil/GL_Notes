## **Hands-On Approach: Securing a Real-World Application with Capabilities**

### **Scenario**

We will secure **`tcpdump`**, a network packet capture tool that traditionally requires **root** privileges but can be run with minimal capabilities.

---

## **1. Identify the Required Capabilities**

Instead of running `tcpdump` as root, we need to determine **which specific privileges** it requires.

### **Test Running Without Root**

`tcpdump -i eth0`

**Error Message:**


`tcpdump: eth0: You don't have permission to capture on that device (socket: Operation not permitted)`

This suggests **`tcpdump` needs permission to open raw network sockets.**

### **Checking Capabilities Required**

Using `strace` to analyze system calls:


`strace -e trace=capset,capget tcpdump -i eth0`

Output:


`capget(...) = {CAP_NET_RAW, CAP_NET_ADMIN, ...}`

This tells us `tcpdump` needs:

- `CAP_NET_RAW` (To capture packets)
- `CAP_NET_ADMIN` (To configure network interfaces)

---

## **2. Assign Capabilities to `tcpdump`**

Instead of running as **root**, assign only the required capabilities:


`sudo setcap cap_net_raw,cap_net_admin+ep /usr/bin/tcpdump`

Verify:


`getcap /usr/bin/tcpdump`

Output:


`/usr/bin/tcpdump = cap_net_raw,cap_net_admin+ep`

### **Testing Without Root**

Now, running `tcpdump` as a regular user should work:


`tcpdump -i eth0`

---

## **3. Restrict Privileges Further**

### **Dropping `CAP_NET_ADMIN`**

- If `tcpdump` only captures packets and doesn't configure interfaces, remove `CAP_NET_ADMIN`:


`sudo setcap cap_net_raw+ep /usr/bin/tcpdump`

- Verify:


`getcap /usr/bin/tcpdump`

Output:


`/usr/bin/tcpdump = cap_net_raw+ep`

### **Ensuring Privilege Drop with `NoNewPrivileges`**

Prevent child processes from gaining new privileges:


`sudo systemd-run --user --property=NoNewPrivileges=yes tcpdump -i eth0`

---

## **4. Combining with Seccomp for Extra Security**

Even with `CAP_NET_RAW`, `tcpdump` doesn’t need all syscalls. We use **seccomp** to restrict it further.

### **Create a Seccomp Filter**

Use `seccomp-bpf` to **allow only necessary system calls**:


`sudo apt install libseccomp-dev`

Create a simple seccomp profile:

```c
#include <seccomp.h>
#include <unistd.h>

int main() {
    scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_KILL);  // Default: kill process
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(read), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(socket), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(bind), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(recvmsg), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(sendmsg), 0);
    seccomp_load(ctx);
    
    execl("/usr/bin/tcpdump", "tcpdump", "-i", "eth0", NULL);
}

```
Compile and run:


`gcc seccomp_tcpdump.c -o seccomp_tcpdump -lseccomp ./seccomp_tcpdump`

---

## **5. Applying Systemd Security Hardening**

If running `tcpdump` as a systemd service:

```ini
[Service]
ExecStart=/usr/bin/tcpdump -i eth0
CapabilityBoundingSet=CAP_NET_RAW
NoNewPrivileges=true
ProtectSystem=full
ProtectKernelModules=true

```

Then reload and restart:



`sudo systemctl daemon-reexec 
`sudo systemctl restart tcpdump.service`

---

## **Conclusion**

✅ Removed full root privileges  
✅ Assigned only `CAP_NET_RAW`  
✅ Used **seccomp** to restrict system calls  
✅ Hardened with **systemd security settings**

Would you like to try this with another tool (e.g., Nginx, Docker, or a custom application)? 🚀

# SetUID Bits Intro with example
chmod u+s in linux set setuid bit. but when it runs whuch user does it run how. can i change to another user

# chmod u+s
###### ChatGPT said:

### **Understanding `chmod u+s` (SetUID) in Linux**

The `chmod u+s` command sets the **SetUID (Set User ID)** bit on an executable file. This means that when the program is run, it executes **with the privileges of the file's owner** rather than the user who launched it.

---

## **1. How Does SetUID Work?**

- Normally, when you run a program, it executes with **your** privileges.
- If the SetUID bit is set, the program executes **with the privileges of the file’s owner**.

### **Example**

```bash
# Create an executable
touch myscript
chmod +x myscript

# Change owner to root
sudo chown root myscript

# Set SetUID
chmod u+s myscript

```
Now, whenever **any user** runs `./myscript`, it will execute **with root privileges** (because `root` is the owner).

---

## **2. Who Does the Program Run As?**

- If the **owner** of the file is `root`, the program runs **as root**.
- If the **owner** is another user (`bob`), the program runs **as bob**.

### **Checking SetUID Bit**


`ls -l myscript`

Output:

`-rwsr-xr-x 1 root root 12345 Mar 3 10:00 myscript`

- The **`s`** in **`rwsr-xr-x`** means the SetUID bit is set.
- Any user who runs `myscript` will execute it **as root**.

---

## **3. Can You Change to Another User Instead of Root?**

Yes, but **only to the file’s owner**.  
To change the user that runs the program:

`sudo chown bob myscript`

Now, when anyone runs `myscript`, it will execute as `bob` instead of `root`.

---

## **4. Can I SetUID to Arbitrary Users?**

**No, you cannot change the effective user arbitrarily.**  
The program always runs **as the file's owner**, not an arbitrary user.

If you need to switch to another user, you can:

1. Use **`sudo`** (if the user has sudo privileges).
2. Use **`setuid()`** in a compiled program (if running as root).
3. Use **capabilities** (`cap_setuid`) instead of SetUID for finer control.

---

## **5. SetUID on Scripts (`#!/bin/bash` Issues)**

SetUID **does not work on scripts** (like Bash, Python, etc.) due to security risks.  
If you try:

`chmod u+s script.sh`

Linux will **ignore** the SetUID bit. Instead, use:

- **C wrapper**: A small compiled C program that calls the script.
- **`sudo` with restricted permissions**.


# C Wrapper 

Here’s a **C wrapper** that allows you to run a script with **SetUID privileges**. This works because **SetUID does not work on scripts** directly, but it does on compiled binaries.

---

### **1. Steps to Create the Wrapper**

#### **1️⃣ Write the C Wrapper**

Create a C program, say `wrapper.c`:

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main() {
    // The script you want to run with elevated privileges
    char *script = "/path/to/your/script.sh";

    // Drop to lower privileges (optional, for security)
    setuid(geteuid());

    // Execute the script
    execl(script, script, (char *)NULL);

    // If execl fails
    perror("execl failed");
    return 1;
}

```

---

#### **2️⃣ Compile the Wrapper**


`gcc -o wrapper wrapper.c`

---

#### **3️⃣ Set Owner and SetUID**

```bash
sudo chown root:root wrapper   # Make root the owner
sudo chmod 4755 wrapper        # SetUID (4 means SetUID in octal)

```

Now, **any user** who runs `./wrapper` will execute `/path/to/your/script.sh` with **root privileges** (or the owner of the binary).

---

### **2. Explanation**

- `setuid(geteuid());` ensures the **effective UID** remains elevated.
- `execl(script, script, NULL);` replaces the current process with the script.
- **No shell is involved**, so users can’t inject malicious commands.

---

### **3. Important Security Considerations**

🔴 **Do NOT use this on public systems** unless necessary.  
🔴 **Ensure the script is secure** (no arbitrary command execution).  
🔴 **Use capabilities (`cap_setuid`) as a better alternative if possible.**

Would you like a **capabilities-based** solution instead of SetUID? 🚀


Yes

# Capabilities
### **Using Capabilities Instead of SetUID**

SetUID can be risky because it grants **full root privileges** to the program. A better alternative is **Linux capabilities**, which allow finer control over what privileges a process gets.

---

## **1️⃣ What Are Capabilities?**

Linux capabilities **break down root privileges** into smaller, manageable permissions. Instead of giving full root access (`SetUID`), you can grant **only the permissions needed**.

For example:

- `CAP_NET_BIND_SERVICE` → Allow binding to low-numbered ports.
- `CAP_DAC_OVERRIDE` → Bypass file permissions.
- `CAP_SETUID` → Allow changing user ID without full root.

---

## **2️⃣ Example: Running a Script as Another User Without Full Root**

### **1️⃣ Write a C Wrapper Using `setuid()`**

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main() {
    char *script = "/path/to/your/script.sh";
    
    // Change to target user (e.g., user "bob", UID=1001)
    setuid(1001);  

    // Execute the script
    execl(script, script, (char *)NULL);

    perror("execl failed");
    return 1;
}

```

---

### **2️⃣ Compile the C Wrapper**



`gcc -o wrapper wrapper.c`

---

### **3️⃣ Give It the Right Capabilities Instead of SetUID**

Instead of `chmod u+s`, we use `setcap`:


`sudo setcap cap_setuid+ep wrapper`

This **allows the binary to change its user ID** (`setuid()`), but **without full root privileges**.

---

## **3️⃣ Why Is This Better Than SetUID?**

|Feature|SetUID (`chmod u+s`)|Capabilities (`setcap`)|
|---|---|---|
|Grants full root?|✅ Yes|❌ No|
|Fine-grained control?|❌ No|✅ Yes|
|Security risk|🔴 High|🟢 Lower|
|Can limit permissions?|❌ No|✅ Yes|

With capabilities, **even if the binary is exploited, it won't gain full root access**—only the specific capability given.

---

## **4️⃣ Checking Capabilities**

You can verify the capabilities of the wrapper with:


`getcap wrapper`

Expected output:


`wrapper = cap_setuid+ep`

---

## **5️⃣ Removing Capabilities**

If you need to remove the capability:

`sudo setcap -r wrapper`

---

### **Conclusion**

✅ **SetUID is powerful but risky** (use only if necessary).  
✅ **Capabilities (`setcap`) provide a safer alternative**.  
✅ **Use `cap_setuid+ep` for privilege control instead of full root access**.
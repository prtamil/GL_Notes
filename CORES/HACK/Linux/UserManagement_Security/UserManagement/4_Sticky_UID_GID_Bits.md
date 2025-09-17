

# UID_GID_Sticky Bits

what is Special Permissions: SUID, SGID, Sticky Bit in linux

###### ChatGPT said:

Linux has three **special file permissions**:

1. **SUID (Set User ID)**
2. **SGID (Set Group ID)**
3. **Sticky Bit**

Each of these permissions modifies how files and directories behave. Let’s break them down one by one.

## 1. **SUID (Set User ID)**

- **Applies to:** Executable files
- **Effect:** When a user runs an executable with SUID, the process runs with the file owner’s privileges instead of the user’s.
- **Example:**   
    `ls -l /usr/bin/passwd`
    
    `-rwsr-xr-x 1 root root 54256 Jan 1 12:34 /usr/bin/passwd`
    
    - The **`s`** in **`rws`** (instead of `rwx`) in the **owner's** field indicates SUID.
    - `passwd` runs as **root** even if a normal user executes it.

- **Setting SUID on a file:**
    
    `chmod u+s filename`
    
- **Removing SUID:**
        
    `chmod u-s filename`
    
- **Security Risk:** If a SUID binary has vulnerabilities, an attacker may gain escalated privileges.
    

---

## 2. **SGID (Set Group ID)**

- **Applies to:** **Executable files** & **directories**
    
- **Effect on Files:** When an executable file has SGID set, it runs with the privileges of the **group** that owns the file, not the user running it.
    
- **Effect on Directories:** New files created inside an SGID directory **inherit the group ownership** of the directory instead of the user’s primary group.
    
- **Example of SGID on an Executable:**
    
    
    `ls -l /usr/bin/newgrp`
    
    
    `-r-xr-sr-x 1 root root 19456 Jan 1 12:34 /usr/bin/newgrp`
    
    - The **`s`** in **`r-xr-sr-x`** (instead of `r-xr-xr-x`) in the **group** field indicates SGID.
- **Setting SGID on a File:**
    
    
    `chmod g+s filename`
    
- **Removing SGID:**
    
    `chmod g-s filename`
    
- **Setting SGID on a Directory:**
    
    
    `chmod g+s dirname`
    
- **Use Case (SGID on a Directory):**

``` bash
mkdir shared
chown root:developers shared
chmod 2775 shared

```
    
	- Now, all files inside `shared/` will automatically belong to the `developers` group.

---

## 3. **Sticky Bit**

- **Applies to:** Directories (rarely used on files)
    
- **Effect:** In a directory with the **sticky bit**, only the file **owner** or `root` can delete or rename files inside it, even if others have write permissions.
    
- **Common Use Case:** `/tmp` directory (world-writable but protected).
    
    
    `drwxrwxrwt 10 root root 4096 Jan 1 12:34 /tmp`
    
    - The **`t`** in **`rwxrwxrwt`** (instead of `rwxrwxrwx`) in the **others** field indicates the **sticky bit**.
- **Setting the Sticky Bit:**
    
    
    `chmod +t dirname`
    
- **Removing the Sticky Bit:**
    
    
    `chmod -t dirname`
    

---

## **Numeric Representation of Special Permissions**

- **SUID = 4000**
- **SGID = 2000**
- **Sticky Bit = 1000**

Example:

```bash
chmod 4755 myscript.sh   # SUID set (4)
chmod 2775 mydir         # SGID set (2)
chmod 1777 /my/tmp       # Sticky Bit set (1)

```



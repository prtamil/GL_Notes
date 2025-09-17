# PAM Intro
One doubt on linux we have user managment (useradd, groups) etc. but we have passwd, ACL, SSH and AppArmour SELinux etc.. you can add if i left something. can you categoruze this on based on authentication and autorization im confused all have permsiions which will work on which scenario

###### ChatGPT said:

Good question! Authentication and authorization both involve permissions but serve different purposes. Let’s break them down:

---

### **Authentication (Who you are)**

Authentication verifies a user’s identity. The following are authentication-related mechanisms:

1. **User Management (useradd, passwd, groups, shadow, etc.)**
    
    - `useradd`, `usermod`, `groupadd`: Manage user and group accounts.
    - `/etc/passwd`, `/etc/shadow`: Store user account details and hashed passwords.
    - `passwd`: Change user passwords.
2. **SSH (Secure Shell)**
    
    - Used for remote authentication via passwords or keys (`~/.ssh/authorized_keys`).
    - Authentication methods:
        - Password-based authentication.
        - Key-based authentication (public-private keys).
        - PAM-based authentication.
3. **Pluggable Authentication Module (PAM)**
    
    - Provides modular authentication.
    - Used in login, SSH, sudo, and other authentication scenarios.
    - Located at `/etc/pam.d/`.

---

### **Authorization (What you can do)**

Authorization controls access and permissions after authentication. These mechanisms handle authorization:

1. **File and Directory Permissions**
    
    - `chmod`, `chown`, `chgrp`: Set ownership and permissions (`rwx`).
    - `/etc/group`: Manages user groups.
2. **Access Control Lists (ACLs)**
    
    - `getfacl`, `setfacl`: Provide fine-grained permissions beyond standard Unix permissions.
3. **sudo (Privilege Escalation)**
    
    - `/etc/sudoers` controls which users can run commands as root.
    - Uses PAM for additional policies.
4. **SELinux (Security-Enhanced Linux)**
    
    - Mandatory Access Control (MAC).
    - Uses security policies (`Enforcing`, `Permissive`, `Disabled`).
    - Works based on security contexts (`ls -Z`).
5. **AppArmor**
    
    - Similar to SELinux but profile-based.
    - Uses predefined security policies to confine applications.
6. **Capabilities (`capsh`, `setcap`, `getcap`)**
    
    - Divide root privileges into smaller units (`CAP_NET_BIND_SERVICE`, `CAP_SYS_ADMIN`).
    - Applied to binaries.

---

### **Hybrid (Authentication + Authorization)**

Some mechanisms handle both authentication and authorization:

1. **PAM (Pluggable Authentication Modules)**
    
    - Handles authentication (`pam_unix.so`, `pam_ldap.so`).
    - Can also enforce authorization policies (`pam_limits.so`, `pam_time.so`).
2. **SSH**
    
    - Authenticates users via keys or passwords.
    - Can enforce authorization (`AllowUsers`, `DenyUsers` in `sshd_config`).

---

### **Scenarios**

|Scenario|Mechanism|
|---|---|
|User login|Authentication (`passwd`, `PAM`)|
|Remote login|Authentication (`SSH`)|
|Restricting file access|Authorization (`chmod`, `ACLs`)|
|Giving limited root access|Authorization (`sudo`, `capabilities`)|
|Restricting network access for a process|Authorization (`SELinux`, `AppArmor`)|
|Fine-grained user policies|Hybrid (`PAM`, `SSH configs`)|

Would you like a deeper dive into any of these?

4o

# How does PAM Fit in Auth and Authz

in Authentication (Who you are) how does pam fit in. if i installed linux them will pam be active if i login with ssh will pam be active i think of pam is active is controlling the system it will redirect to subsystems such as ssh, kerbros etc.. am i right or wrong

###### ChatGPT said:

You're thinking in the right direction! PAM (Pluggable Authentication Module) is **always active** in modern Linux systems, and it acts as a flexible authentication framework that integrates with various authentication mechanisms like SSH, local login, Kerberos, and more. Let’s break it down:

---

### **1. Is PAM active by default?**

Yes!

- When you install Linux, PAM is **enabled by default** in most distributions (Ubuntu, RHEL, Debian, etc.).
- It manages authentication for various services like `login`, `ssh`, `sudo`, `passwd`, and more.
- Configuration files are found in `/etc/pam.d/`.

---

### **2. How does PAM fit into Authentication?**

PAM is like a **middleware** that connects authentication requests (from services like SSH, `login`, `sudo`) to actual authentication mechanisms (like `/etc/passwd`, Kerberos, LDAP, etc.).

💡 **Think of PAM as a gatekeeper that checks "Who you are" before allowing access.**  
It determines **how** authentication happens but doesn't store passwords itself.

---

### **3. When you log in (SSH, local, etc.), does PAM control it?**

Yes!

- **If you log in via SSH** (`sshd`), PAM is used for authentication.
- **If you log in locally** (`login` command), PAM is used.
- **If you use `sudo`**, PAM is used.
- **If you change passwords (`passwd`)**, PAM is used.
- **If you use GUI login (GDM, SDDM, LightDM)**, PAM is used.

So, PAM is **always in action** for authentication unless explicitly disabled.

---

### **4. How does PAM "redirect" authentication?**

PAM works as a **framework**, and different authentication methods (passwords, Kerberos, LDAP, etc.) are configured as modules inside `/etc/pam.d/`.

When a service (like SSH) requests authentication, PAM does the following:

1. **Checks its rules** for that service in `/etc/pam.d/`.
2. **Calls the required authentication module** (e.g., `pam_unix.so` for local passwords, `pam_krb5.so` for Kerberos).
3. **The module performs the authentication** (password check, fingerprint scan, etc.).
4. **Returns success or failure** to PAM.
5. **PAM tells the service (SSH, sudo, etc.)** whether authentication was successful.

💡 **Example: When you log in via SSH**

1. SSH daemon (`sshd`) asks PAM to authenticate the user.
2. PAM checks `/etc/pam.d/sshd` for rules.
3. It may use `pam_unix.so` (local passwords) or `pam_krb5.so` (Kerberos) based on configuration.
4. The authentication module verifies your credentials.
5. If successful, PAM grants access to SSH.

---

### **5. PAM and Subsystems (Kerberos, LDAP, etc.)**

- **PAM itself does NOT authenticate**—it just forwards authentication to the correct module.
- Modules like `pam_krb5.so`, `pam_ldap.so`, and `pam_unix.so` handle actual authentication.
- PAM allows the system admin to **choose which authentication method to use** for each service.

---

### **6. Example PAM Configuration (`/etc/pam.d/sshd`)**

This file controls SSH authentication.

```bash
# Standard Unix authentication (passwords)
auth required pam_unix.so

# Allow Kerberos authentication
auth optional pam_krb5.so

# Deny access to users in /etc/nologin
account required pam_nologin.so

```

- Here, SSH will first check local passwords (`pam_unix.so`).
- If Kerberos is configured, it will also check `pam_krb5.so`.
- If `/etc/nologin` exists, PAM will block access.

---

### **7. What happens if PAM is disabled?**

- If you remove PAM (`pam_unix.so`, etc.), **authentication will break**.
- Services like SSH, `sudo`, and `login` will stop working unless they have an alternative authentication method.

---

### **Conclusion**

✅ PAM **is always active** and controls authentication.  
✅ It **redirects authentication requests** to subsystems like passwords, Kerberos, and LDAP.  
✅ It **does not store credentials** but enforces authentication policies.  
✅ It **works with every authentication service** (SSH, login, sudo, passwd, etc.).

You got the right idea! PAM is a central controller for authentication, and it decides where to send the authentication request (password, Kerberos, etc.).

Would you like to see a specific example or configuration? 🚀


# PAM and Configuration Customization
##### You said:

say for sudo i need unix authentication for ssh i need ldap how does pam config looks like and can you explain line by line

###### ChatGPT said:

Great question! Let’s configure PAM to use **Unix authentication (`/etc/shadow`) for `sudo`** and **LDAP authentication for `ssh`**.

---

## **1. Understanding PAM Configuration**

PAM configuration files are in `/etc/pam.d/`.  
Each service (like `sudo`, `ssh`) has its own file, which tells PAM how to authenticate users.

- **`/etc/pam.d/sudo`** → Controls authentication for `sudo`
- **`/etc/pam.d/sshd`** → Controls authentication for SSH (`sshd` service)

### **Modules used:**

- `pam_unix.so` → Unix authentication (uses `/etc/shadow` for passwords).
- `pam_ldap.so` → LDAP authentication (uses an external LDAP server).

---

## **2. Configuring `sudo` to use Unix authentication**

Edit `/etc/pam.d/sudo` to ensure only Unix authentication is used:

```bash
#%PAM-1.0
auth    required    pam_unix.so
account required    pam_unix.so
session required    pam_unix.so

```

### **Explanation (Line by Line)**

|Line|Meaning|
|---|---|
|`auth required pam_unix.so`|User must authenticate using Unix password (`/etc/shadow`).|
|`account required pam_unix.so`|Checks if the account is valid (not expired or locked).|
|`session required pam_unix.so`|Ensures session is properly opened and logged.|

✅ **Result**:  
When a user runs `sudo`, PAM will check their password in `/etc/shadow`.

---

## **3. Configuring SSH to use LDAP authentication**

Edit `/etc/pam.d/sshd` to make SSH use LDAP authentication:

```bash
#%PAM-1.0
auth    required    pam_ldap.so
account required    pam_ldap.so
session required    pam_ldap.so

```

### **Explanation (Line by Line)**

|Line|Meaning|
|---|---|
|`auth required pam_ldap.so`|Authenticate user via LDAP (external directory server).|
|`account required pam_ldap.so`|Check if the LDAP account is valid.|
|`session required pam_ldap.so`|Manage user session (e.g., log activity).|

✅ **Result**:  
When a user logs in via SSH, PAM will authenticate them using LDAP instead of local Unix passwords.

---

## **4. What happens now?**

- `sudo` will **only** check `/etc/shadow` (local passwords).
- `ssh` will **only** check LDAP for authentication.
- Other services (like `login`) will behave according to their respective PAM configurations.

💡 **Bonus:**

- If you want **both** Unix and LDAP authentication for SSH, you can do:
    ```bash
    auth required pam_unix.so
	auth required pam_ldap.so
	```
    
    This forces both checks.
    
- If you want **either** Unix **or** LDAP authentication for SSH, you can do:
    
```bash
auth sufficient pam_ldap.so
auth required pam_unix.so

```
    
    This means:
    
    - If LDAP authentication succeeds, no need to check Unix (`sufficient`).
    - If LDAP fails, fallback to Unix (`required`).

---

## **5. Testing the Configuration**

### ✅ **Test `sudo` with Unix authentication**

`sudo -l`

- It should ask for your **Unix password** (from `/etc/shadow`).

### ✅ **Test `ssh` with LDAP authentication**



`ssh user@your-server`

- It should authenticate using **LDAP credentials**.

---

## **6. Debugging Issues**

If something is not working:

- Check `/var/log/auth.log` (Ubuntu/Debian) or `/var/log/secure` (RHEL).
- Run PAM tests:
    

    `pamtester sudo youruser authenticate`
    
    
    `pamtester sshd youruser authenticate`
    
- Verify LDAP connection:
    
    
    `ldapsearch -x -LLL -H ldap://your-ldap-server -b "dc=example,dc=com"`
    

---

## **Final Thoughts**

✅ PAM allows fine-grained control over authentication for each service.  
✅ You can **customize authentication** per service (`sudo` → Unix, `ssh` → LDAP).  
✅ PAM modules (`pam_unix.so`, `pam_ldap.so`) handle different authentication mechanisms.

Would you like to dive deeper into any part? 🚀

4o
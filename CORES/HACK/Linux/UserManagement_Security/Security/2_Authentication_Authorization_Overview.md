how Authentication & Authorization → Who gets in & what they can do. works in linux explain detail

###### ChatGPT said:

# **Authentication & Authorization in Linux**

**🔹 Concept: "Who Gets In & What They Can Do"**  
Linux enforces security by ensuring that only authorized users can access the system (**Authentication**) and controlling what they can do once logged in (**Authorization**).

---

## **1️⃣ Authentication → "Prove Who You Are"**

Authentication verifies a user's identity before allowing system access.

### **🔹 Authentication Methods in Linux**

1. **Password-Based Authentication** (Traditional)
2. **Key-Based Authentication** (SSH keys, GPG keys)
3. **Pluggable Authentication Modules (PAM)** (Flexible framework)
4. **Biometric & Multi-Factor Authentication (MFA)**
5. **Kerberos & LDAP** (For centralized authentication)

---

### **🔹 1. Password-Based Authentication**

Users authenticate using a username and password. Passwords are securely stored in `/etc/shadow`, not `/etc/passwd`.

🔹 **File: `/etc/shadow`** (Stores Encrypted Passwords)


`user1:$6$A3B4hGFt$Xk..hashedpassword..bXM:18900:0:99999:7:::`

|Field|Description|
|---|---|
|`user1`|Username|
|`$6$`|Hashing algorithm (SHA-512)|
|`A3B4hGFt$Xk..`|Salt & Hash|
|`18900`|Last password change (days since 1970)|
|`0`|Minimum days before changing password|
|`99999`|Maximum days before requiring change|
|`7`|Warning days before expiry|

🔹 **Password Commands**

|Action|Command|
|---|---|
|Change user password|`passwd username`|
|Expire user password|`passwd -e username`|
|Check password aging|`chage -l username`|
|Force password reset on next login|`chage -d 0 username`|

---

### **🔹 2. Key-Based Authentication (SSH & GPG Keys)**

🔹 **Used for:** Secure remote login without passwords.

- Uses **public-private key pairs** (`id_rsa` and `id_rsa.pub`).
- **Public key** goes to `~/.ssh/authorized_keys` on the server.
- **Private key** stays on the client machine.

🔹 **Setting up SSH Key-Based Authentication:**


```bash
ssh-keygen -t rsa -b 4096           # Generate SSH keys
ssh-copy-id user@remote-server      # Copy public key to server
ssh user@remote-server              # Login using key

```

🔹 **GPG Keys** → Used for encrypting files, signing commits, etc.

---

### **🔹 3. PAM (Pluggable Authentication Modules)**

🔹 **How PAM Works**

- A **modular authentication system** allowing different methods (passwords, biometrics, 2FA).
- Configuration stored in `/etc/pam.d/`.
- Example: `/etc/pam.d/sshd` controls SSH authentication.

🔹 **Example PAM Rules in `/etc/pam.d/common-auth`**

```sh
auth required pam_unix.so try_first_pass
auth required pam_tally2.so deny=3 unlock_time=600

```

|Rule|Meaning|
|---|---|
|`pam_unix.so`|Standard password authentication|
|`pam_tally2.so`|Locks user after 3 failed attempts, unlocks after 10 min|

🔹 **Check PAM Logs for Failed Logins**


`sudo grep 'authentication failure' /var/log/auth.log`

---

### **🔹 4. Multi-Factor Authentication (MFA)**

🔹 **Google Authenticator or YubiKey for Extra Security**

```bash
sudo apt install libpam-google-authenticator
google-authenticator

```

Then configure `/etc/pam.d/sshd` to require a one-time password (OTP).

---

### **🔹 5. Centralized Authentication (LDAP & Kerberos)**

🔹 **LDAP** → Used in enterprises for a **single sign-on (SSO)** experience.  
🔹 **Kerberos** → Ticket-based authentication (e.g., MIT Kerberos).

---

## **2️⃣ Authorization → "What Can You Do?"**

Authorization determines **user permissions** after authentication.

### **🔹 1. User & Group-Based Permissions**

🔹 **File Permission Model** (`ls -l file.txt`)


`-rw-r--r-- 1 alice developers 1234 Feb 20 12:00 file.txt`

|Permission|Owner (`alice`)|Group (`developers`)|Others|
|---|---|---|---|
|`rwx` (7)|Read & Write (`rw-`)|Read (`r--`)|Read (`r--`)|

🔹 **Change Ownership**


`chown alice file.txt 
`chgrp developers file.txt`

🔹 **Modify Permissions**



`chmod 750 file.txt`

🔹 **Set Advanced Permissions (ACLs)**


`setfacl -m u:bob:rw file.txt`

---

### **🔹 2. Privilege Escalation (`sudo`, `su`)**

|Command|Function|
|---|---|
|`sudo command`|Run a command as root|
|`su - user`|Switch to another user|
|`sudo -i`|Open an interactive root shell|

🔹 **Configure `sudo` Permissions** (`/etc/sudoers`)



`alice ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart apache2`

(Grants Alice permission to restart Apache without a password.)

---

### **🔹 3. Restricting User Access**

🔹 **Restrict Login to Specific Users:**  
Edit `/etc/ssh/sshd_config`:


`AllowUsers alice bob`

Then restart SSH:


`sudo systemctl restart sshd`

🔹 **Lock and Unlock Accounts**

```bash
usermod -L alice  # Lock user
usermod -U alice  # Unlock user

```

---

## **3️⃣ Logging & Auditing → "Who Did What?"**

🔹 **Log Authentication Attempts:**

`sudo cat /var/log/auth.log | grep "Failed password"`

🔹 **See All Active Sessions**
```bash
w
who
last

```

🔹 **Enable User Command Auditing** (`auditd`)

```
sudo apt install auditd
auditctl -w /etc/passwd -p wa -k passwd_changes

```

(This logs any modifications to `/etc/passwd`.)

---

## **🔹 Quick-Recall Summary**

|Topic|Command|
|---|---|
|Check logged-in users|`who`, `w`|
|Verify user identity|`id`|
|Change password|`passwd username`|
|Lock/unlock user|`usermod -L/U username`|
|View failed logins|`grep "Failed password" /var/log/auth.log`|
|Generate SSH keys|`ssh-keygen -t rsa -b 4096`|
|View `sudo` rules|`sudo -l`|
|Set file ACL|`setfacl -m u:bob:rw file.txt`|

---

## **🔹 Retention & Practice Exercises**

🔥 **Retention Hack:**

- Think **"Who Gets In?"** → Authentication
- Think **"What Can They Do?"** → Authorization

### **💡 Practice These:**

1️⃣ Set up an SSH key-based login.  
2️⃣ Restrict user `bob` from logging in via SSH.  
3️⃣ Allow `alice` to run `apt update` without a password using `sudo`.  
4️⃣ Lock user `dev1` for 10 minutes after 3 failed login attempts.

---

Want a deep dive on **PAM, Kerberos, or LDAP?** 🚀
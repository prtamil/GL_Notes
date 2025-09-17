how users and group work in linux.

###### ChatGPT said:

## **How Users and Groups Work in Linux**

### **🔹 Core Concept: Users & Groups = Identity + Access Control**

Linux uses users and groups to manage access to files, directories, and system resources. Every user belongs to at least one group, and permissions are assigned based on user identity and group membership.

---

## **1️⃣ Users in Linux**

### **🔹 Types of Users**

|User Type|Description|
|---|---|
|**Root User** (`UID 0`)|Superuser with full control.|
|**Regular Users** (`UID 1000+`)|Normal users for daily tasks.|
|**System Users** (`UID 1-999`)|Created by the OS for services like `www-data`, `mysql`.|

### **🔹 User Identification**

- Each user is identified by a **User ID (UID)** and associated with a **Primary Group (GID)**.
- Check user details:
    
    `id username`
    

### **🔹 Where Users Are Stored**

- **User information** → `/etc/passwd`
- **Passwords (hashed)** → `/etc/shadow`
- **Example `/etc/passwd` Entry:**

    
    `user1:x:1001:1001:John Doe:/home/user1:/bin/bash`
    
    - `user1` → Username
    - `x` → Password stored in `/etc/shadow`
    - `1001` → UID
    - `1001` → GID (Primary Group)
    - `John Doe` → Full name (optional)
    - `/home/user1` → Home directory
    - `/bin/bash` → Default shell

---

## **2️⃣ Groups in Linux**

### **🔹 What Are Groups?**

- **Primary Group:** Assigned when a user is created (e.g., `useradd -g developers alice`).
- **Secondary Groups:** Additional groups a user belongs to (`usermod -aG sudo alice`).

### **🔹 Where Groups Are Stored**

- **Group Information** → `/etc/group`
- **Shadow Group (secure data)** → `/etc/gshadow`
- **Example `/etc/group` Entry:**
    
    
    `sudo:x:27:alice,bob`
    
    - `sudo` → Group name
    - `x` → Password (usually empty)
    - `27` → Group ID (GID)
    - `alice, bob` → Members

### **🔹 Group Commands**

|Action|Command|
|---|---|
|Show user groups|`groups username`|
|Show all groups|`getent group`|
|Add a group|`groupadd developers`|
|Add user to group|`usermod -aG developers alice`|
|Change primary group|`usermod -g newgroup alice`|
|Remove user from group|`gpasswd -d alice developers`|
|Delete group|`groupdel developers`|

---

## **3️⃣ How Users & Groups Work Together**

Linux permissions are based on **User (U), Group (G), and Others (O)**.

**Example: File Permissions** (`ls -l /home/alice/file.txt`)


`-rw-r----- 1 alice developers 1234 Feb 20 12:00 file.txt`

|Field|Value|
|---|---|
|`rw-`|Alice (Owner) can read and write.|
|`r--`|Group `developers` can read.|
|`---`|Others have no access.|

---

## **4️⃣ Managing Users & Groups Practically**

|Task|Command|
|---|---|
|Add a new user|`useradd -m -s /bin/bash alice`|
|Set password|`passwd alice`|
|Modify user details|`usermod -l newname alice`|
|Lock user account|`usermod -L alice`|
|Unlock user account|`usermod -U alice`|
|Delete user|`userdel -r alice`|

---

## **5️⃣ Practical Use Case: Creating a Restricted User**

💡 **Scenario:** You want to create a user `dev1`, add them to `developers` group, and restrict their access.


`sudo groupadd developers              # Create group sudo useradd -m -G developers dev1    # Create user and assign group sudo passwd dev1                      # Set password sudo chmod 750 /home/dev1             # Restrict home folder`

### **🔹 Quick-Recall Hook:**

- **"Who am I?"** → `whoami`, `id`
- **"Who’s in which group?"** → `groups`, `getent group`
- **"Can I read/write?"** → `ls -l`, `chmod`, `chown`

Want more deep dives, like **SUID, ACLs, or user namespace isolation?** 🚀
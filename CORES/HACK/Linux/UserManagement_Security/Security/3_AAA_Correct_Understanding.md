Corrected Summary: Linux Authentication, Authorization, and Accountability (AAA)

Here’s a clear, concise summary covering Authentication, Authorization, and Accountability (the AAA triad) with PAM, SELinux, ACLs, /etc/passwd, /etc/shadow, and related concepts.

1. **Authentication (Who Are You?)**

	- Core Mechanism: Users (UID) and passwords (hashed in /etc/shadow) are the primary identity, defined in /etc/passwd.
	    - /etc/passwd: Stores user info (username, UID, GID, home dir, shell).        
	    - /etc/shadow: Stores encrypted passwords and aging policies.
	        
	- PAM: Pluggable Authentication Modules (/etc/pam.d/ or /etc/pam.conf) extend this. It’s a framework to stack auth methods (e.g., local password, LDAP, Kerberos).   
	    - Example: pam_unix.so checks /etc/shadow; pam_ldap.so queries an LDAP server.
	       
	- Process: User logs in → PAM modules validate credentials → Success/Failure.   
	- Transparency: No SELinux, ACLs, or namespaces here—just identity verification.   
2. **Authorization (What Can You Do?)**

	- Basic Level: Groups (/etc/group) and traditional permissions (rwx, stored in file inodes). 
	    - Example: User alice in group devs gets group-level access to /code.       
	- ACLs: Fine-grained control over files/directories beyond owner/group/other.
	    - Commands: setfacl (set), getfacl (view).
	    - Example: Give bob read-only access to alice’s file without group changes.
	        
	- SELinux: Kernel-level mandatory access control (MAC).
	    - Policies define what subjects (users/processes) can do to objects (files/resources).
	    - Example: Even if alice has rwx perms, SELinux can block based on context (e.g., httpd_t).
	    - Config: /etc/selinux/config, uses labels (e.g., ls -Z).
	        
	- Transparency: Authorization layers—basic (groups/perms), refined (ACLs), enforced (SELinux). PAM doesn’t play here; it’s pre-authorization.
    
3. **Accountability (What Did You Do?)**
	- Core Mechanism: Logging and auditing.
	    - /var/log/auth.log or /var/log/secure: Tracks login attempts (via PAM).
	    - SELinux: Audit logs (/var/log/audit/audit.log) record policy violations.
	    - Commands: last, who, w track user activity.
	        
	- Transparency: Accountability ties auth and authz together—PAM logs entry, SELinux logs enforcement, basic tools log usage. ACLs don’t log directly.
	    

Bonus: **Namespaces and Cgroups**

- Namespaces: Isolate environments (e.g., user namespaces map UID 1000 to a container-specific UID). Not auth/authz, but security via separation.
- Cgroups: Limit resources (CPU, memory) per user/process. Not about permissions, but control.
- Transparency: These are orthogonal to AAA—think of them as sandboxing tools, not identity or access management.
    

---

Revised Connection Pattern

- Authentication: /etc/passwd → /etc/shadow → PAM → “You’re in.”
- Authorization: Groups → ACLs → SELinux → “Here’s what you can touch.”
- Accountability: Logs → Audits → “Here’s what you did.”
- Namespaces/Cgroups: “Here’s your sandbox and leash”—not AAA, but containment.
    

---

Memory Hook

- Story: “King Passwd names you (auth), Queen Group assigns your rank (basic authz), Lord PAM checks your ID card, Duke ACL refines your privileges, Emperor SELinux enforces the law, and Scribe Log writes it all down. Meanwhile, Jailor Namespace locks you in a cell, and Warden Cgroup rations your bread.”
    
- Quick-Recall: “P-S-P-A-S-N-C” → “Passwd-Shadow-PAM-ACL-SELinux-Namespace-Cgroup.”
    

---

**Final Transparency**

Your assumption had the right pieces but misaligned them. Linux AAA is a pipeline: auth (PAM, /etc/shadow) → authz (groups, ACLs, SELinux) → accountability (logs). Namespaces and cgroups are sidekicks, not core players. If you want deeper examples or a diagram, just ask!
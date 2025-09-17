what are the ids and what's it purpose are assigned to linux process. please take info from linux process control block. and map the ids with usages and purpose.

###### ChatGPT said:

In Linux, each process is represented by a **Process Control Block (PCB)**, which is a data structure in the kernel that stores essential information about the process. The PCB is implemented as a **task_struct** structure in the Linux kernel. Several unique **identifiers (IDs)** are assigned to a process for different purposes. Below is a mapping of these IDs with their usages and purposes:

|**ID Name**|**Kernel Field in `task_struct`**|**Purpose and Usage**|
|---|---|---|
|**Process ID (PID)**|`pid`|Uniquely identifies a process. Used for process management (e.g., `kill`, `ps`, `top`).|
|**Parent Process ID (PPID)**|`real_parent->pid`|Identifies the parent process of the current process. Helps track process hierarchy.|
|**Thread Group ID (TGID)**|`tgid`|Identifies the main thread in a multi-threaded process. All threads in the process share this ID.|
|**Session ID (SID)**|`session`|Identifies the session leader. Used in session management, job control, and controlling terminals (`setsid`).|
|**Process Group ID (PGID)**|`pgrp`|Identifies a group of processes, used for job control and signal management (`kill -SIGSTOP -<PGID>`).|
|**User ID (UID)**|`cred->uid`|Identifies the real user who owns the process. Used for permission checks.|
|**Effective User ID (EUID)**|`cred->euid`|Used for privilege escalation (e.g., `setuid` programs). Determines access rights for system resources.|
|**Saved User ID (SUID)**|`cred->suid`|Stores the previous UID before privilege changes, allowing restoration.|
|**File System User ID (FSUID)**|`cred->fsuid`|Used for filesystem access checks (can differ from UID/EUID).|
|**Group ID (GID)**|`cred->gid`|Identifies the primary group of the process. Used for group-based permissions.|
|**Effective Group ID (EGID)**|`cred->egid`|Similar to EUID, determines group permissions for access control.|
|**Saved Group ID (SGID)**|`cred->sgid`|Stores the previous GID before privilege changes, allowing restoration.|
|**File System Group ID (FSGID)**|`cred->fsgid`|Used for filesystem permission checks, similar to FSUID.|
|**Capabilities**|`cred->cap_effective`, `cred->cap_permitted`|Fine-grained privileges (e.g., `CAP_NET_ADMIN` for networking tasks).|

These IDs help in managing process security, access control, privilege management, and process relationships within the OS
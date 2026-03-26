# FUSE — Filesystem in Userspace

> A complete technical guide: architecture, usage, benefits, and real-world applications

---

## Table of Contents

1. [Introduction](https://claude.ai/chat/f3b5f83b-1080-4ca7-abc4-d8d92a759c7e#introduction)
2. [How Traditional Filesystems Work](https://claude.ai/chat/f3b5f83b-1080-4ca7-abc4-d8d92a759c7e#how-traditional-filesystems-work)
3. [What is FUSE?](https://claude.ai/chat/f3b5f83b-1080-4ca7-abc4-d8d92a759c7e#what-is-fuse)
4. [Why FUSE Exists: The Problems It Solves](https://claude.ai/chat/f3b5f83b-1080-4ca7-abc4-d8d92a759c7e#why-fuse-exists-the-problems-it-solves)
5. [How to Use FUSE](https://claude.ai/chat/f3b5f83b-1080-4ca7-abc4-d8d92a759c7e#how-to-use-fuse)
6. [Real-World FUSE Filesystems](https://claude.ai/chat/f3b5f83b-1080-4ca7-abc4-d8d92a759c7e#real-world-fuse-filesystems)
7. [Benefits of FUSE](https://claude.ai/chat/f3b5f83b-1080-4ca7-abc4-d8d92a759c7e#benefits-of-fuse)
8. [Tradeoffs and Limitations](https://claude.ai/chat/f3b5f83b-1080-4ca7-abc4-d8d92a759c7e#tradeoffs-and-limitations)
9. [What Would Happen Without FUSE?](https://claude.ai/chat/f3b5f83b-1080-4ca7-abc4-d8d92a759c7e#what-would-happen-without-fuse)
10. [Conclusion](https://claude.ai/chat/f3b5f83b-1080-4ca7-abc4-d8d92a759c7e#conclusion)

---

## Introduction

Modern operating systems handle storage through filesystems — mechanisms that translate application requests like `open`, `read`, and `write` into operations on physical storage or other resources. Traditionally, filesystems live inside the kernel because they must interact closely with memory management, caching, device drivers, and process isolation.

However, kernel-level development is difficult and risky. **FUSE (Filesystem in Userspace)** solves this by allowing developers to implement filesystem logic in ordinary user-space programs while seamlessly integrating with the kernel's existing filesystem interface.

> **Core Idea:** FUSE separates filesystem _routing_ (kernel responsibility) from filesystem _logic_ (user-space program), enabling safe and rapid filesystem development without ever touching kernel code.

---

## How Traditional Filesystems Work

In a standard Unix-like OS, filesystem drivers run entirely in kernel space. When an application calls:

```c
open("file.txt")
```

The request flows through the kernel's **Virtual Filesystem Switch (VFS)** layer, which acts as a uniform abstraction over all filesystem types — ext4, xfs, btrfs, and others.

### The VFS Layer

The VFS defines a common set of data structures and operations that every filesystem must implement:

- **inodes** — represent files and directories
- **dentries** — represent directory entries (filenames)
- **superblocks** — represent mounted filesystem metadata
- **file objects** — represent open file handles

This abstraction allows multiple filesystem types to coexist transparently. Applications interact with the VFS interface, never with a specific driver.

### Traditional Execution Path

```
Application
   ↓  system call (open / read / write)
VFS (kernel)
   ↓  dispatches to driver
Filesystem Driver (ext4 / xfs / btrfs)
   ↓
Storage Device
```

This is fast and efficient, but adding a new filesystem requires writing, testing, and maintaining kernel-level code — a high barrier with serious consequences for mistakes.

---

## What is FUSE?

FUSE is a kernel module (and accompanying user-space library) that makes user-space filesystem implementation possible. It acts as a bridge between the VFS interface and an ordinary user-space process that contains the filesystem logic.

Instead of implementing a driver inside the kernel, a developer writes a regular application that listens for and responds to filesystem operation requests forwarded by the FUSE kernel module.

### FUSE Execution Path

```
Application
   ↓  system call
VFS (kernel)
   ↓  routes to FUSE module
FUSE Kernel Module
   ↓  writes request to /dev/fuse
User-Space Filesystem Process
   ↓  handles request, returns result
FUSE Kernel Module
   ↓  forwards result back
Application
```

The filesystem becomes a **message-handling service**. The FUSE kernel module manages the communication channel (`/dev/fuse`) and handles all the bookkeeping. The user-space process only needs to implement the actual filesystem operations.

---

## Why FUSE Exists: The Problems It Solves

### 1. Kernel Development Is Dangerous

Bugs in kernel code can crash the entire operating system. There is no safety net — a bad pointer dereference or memory corruption brings down everything. FUSE isolates filesystem logic in user space where:

- Crashes only affect the filesystem process, not the OS
- Standard debuggers (`gdb`, `lldb`) work normally
- Memory sanitizers (AddressSanitizer, Valgrind) can be applied
- Logging and tracing work just like any other application

### 2. Kernel Development Is Slow

Kernel modules require recompilation and often a full system restart to test. The development loop is slow. User-space programs can be iterated on rapidly, making FUSE ideal for:

- Rapid prototyping of new filesystem ideas
- Research into filesystem behavior and policies
- Custom filesystem experiments without kernel maintenance burden

### 3. Not All Filesystems Are About Disks

Many useful filesystems do not interact with physical storage at all. They present virtual or derived views of data:

- Remote files served over SSH or HTTP
- Files inside compressed archives (ZIP, tar)
- Encrypted layers over existing directories
- Configuration or process information as virtual files
- Cloud storage exposed as a local directory

Implementing any of these as kernel modules would be impractical. FUSE makes them simple application development tasks.

### 4. Privilege Requirements

Kernel modules require root or administrative privileges to install and load. FUSE filesystems can be mounted by unprivileged users (depending on system configuration), enabling:

- Per-user encrypted filesystem mounts
- User-controlled remote filesystem access
- Rootless container filesystem layers
- Developer sandboxes without system-level access

---

## How to Use FUSE

### Core Components

A FUSE setup has three parts:

1. **The FUSE kernel module** — ships with Linux, usually pre-loaded
2. **libfuse** — the user-space library that handles protocol communication
3. **Your filesystem program** — the application you write

### Basic Usage Pattern

A FUSE filesystem program implements callback functions for each filesystem operation. The libfuse library connects these callbacks to the kernel protocol.

```c
// Minimal FUSE filesystem in C
#define FUSE_USE_VERSION 31
#include <fuse.h>
#include <string.h>
#include <errno.h>

static int my_getattr(const char *path, struct stat *st, ...) {
    st->st_mode = S_IFREG | 0444;
    st->st_size = 13;
    return 0;
}

static int my_read(const char *path, char *buf, size_t size, ...) {
    const char *content = "Hello, FUSE!\n";
    memcpy(buf, content, 13);
    return 13;
}

static struct fuse_operations ops = {
    .getattr = my_getattr,
    .read    = my_read,
};

int main(int argc, char *argv[]) {
    return fuse_main(argc, argv, &ops, NULL);
}
```

### Mounting and Unmounting

Once compiled, the filesystem is launched by specifying a mount point:

```bash
# Mount the filesystem
./my_fs /mnt/myfs

# List contents through FUSE
ls /mnt/myfs

# Unmount when done
fusermount -u /mnt/myfs    # Linux
umount /mnt/myfs           # macOS
```

### High-Level vs Low-Level API

libfuse provides two levels of API:

||High-Level API|Low-Level API|
|---|---|---|
|**Works with**|File paths|Inodes directly|
|**Complexity**|Simpler to implement|More control and flexibility|
|**Best for**|Most use cases|Advanced features|
|**Entry point**|`fuse_main()`|`fuse_session_loop()`|

### FUSE in Other Languages

libfuse bindings and FUSE libraries exist for many languages beyond C:

|Language|Library|
|---|---|
|Go|`github.com/hanwen/go-fuse` or `bazil.org/fuse`|
|Python|`fusepy` or `pyfuse3`|
|Rust|`fuser` crate|
|Java|`fuse4j`|
|Node.js|`fuse-native`|

---

## Real-World FUSE Filesystems

FUSE enables an entire category of filesystems that would be impractical or impossible to implement as kernel drivers:

|Filesystem|What It Does|Category|
|---|---|---|
|`sshfs`|Mounts remote directories over SSH as if they were local|Remote / Network|
|`rclone mount`|Mounts cloud storage (S3, GDrive, etc.) as a local filesystem|Remote / Cloud|
|`EncFS`|Transparent per-file encryption layer over a directory|Security / Encryption|
|`gocryptfs`|Modern encrypted filesystem with integrity checking|Security / Encryption|
|`fuse-overlayfs`|Merges read-only and writable layers — used in containers|Container Tooling|
|`mergerfs`|Merges multiple directories into a unified namespace|Aggregation|
|`archivemount`|Mounts tar/zip archives as a browsable directory|Archive Access|
|`s3fs-fuse`|Mounts Amazon S3 buckets as local directories|Cloud Storage|
|`ntfs-3g`|Full read-write access to NTFS volumes on Linux|Interoperability|
|`bindfs`|Re-mounts a directory with different permissions/ownership|Policy / Security|

---

## Benefits of FUSE

### Safety

The most critical benefit of FUSE is **fault isolation**. A crash in a FUSE filesystem process kills only that process. The kernel, the OS, and all other applications continue running. In contrast, a kernel filesystem bug can trigger a system panic and corrupt data.

||Kernel Filesystem Crash|FUSE Filesystem Crash|
|---|---|---|
|**Impact**|Kernel panic, possible data corruption|Process exits, mount point unavailable|
|**System state**|Full restart required|OS continues running|
|**Recovery**|Reboot, fsck|Restart the process|

### Ease of Development

FUSE dramatically lowers the expertise barrier for filesystem development:

- Write in any language with FUSE bindings
- Use standard debuggers, profilers, and memory tools
- `printf` and logging work normally
- No kernel build system or module signing required
- Test and iterate without rebooting
- Apply unit tests just like any application

### Portability

A FUSE filesystem written using libfuse works across Linux distributions without modification. With **macFUSE** (formerly OSXFUSE), the same code can often be compiled for macOS. This is impossible with native kernel filesystem drivers, which are OS-specific and kernel-version-specific.

### Flexibility and Composability

FUSE filesystems can be stacked and composed. One FUSE filesystem can use another mounted FUSE filesystem as its backing store:

```
Remote directory (sshfs)
   ↓  mounted via FUSE
Encrypted layer (gocryptfs)
   ↓  mounted via FUSE
Application sees decrypted remote files locally
```

### Access Control and Policy Enforcement

FUSE allows arbitrary policy enforcement on every filesystem operation:

- Audit and log all file accesses
- Block reads or writes based on application identity
- Inject delays or artificial errors for testing
- Transform file content on read or write
- Enforce data loss prevention (DLP) rules at filesystem level

### Enabling Container Ecosystems

FUSE has become foundational to modern container tooling:

- **Overlay filesystems** — `fuse-overlayfs` allows rootless containers (Docker, Podman) without kernel privileges
- **Image distribution** — container runtimes use FUSE to lazily fetch image layers on demand
- **Sandboxing** — container filesystems can be isolated and monitored via FUSE

---

## Tradeoffs and Limitations

### Performance Overhead

Every filesystem operation crosses the kernel-to-userspace boundary twice — once to send the request, once to return the result. This context switching introduces latency compared to native kernel filesystems.

```
Native kernel filesystem:   kernel → driver → storage
FUSE filesystem:            kernel → /dev/fuse → userspace → /dev/fuse → kernel
```

Benchmarks typically show FUSE filesystems running at **60–85% of native filesystem throughput** for sequential I/O, with larger penalties for metadata-intensive workloads (many small files, frequent `stat` calls).

### When to Use FUSE vs. Kernel Filesystems

|Use FUSE|Use a Kernel Filesystem|
|---|---|
|Remote or network-backed storage|High-performance local storage (databases, VMs)|
|Encrypted or policy-enforcing layers|Latency-sensitive workloads|
|Container filesystem layers|Production storage requiring maximum throughput|
|Virtual or procedurally generated content|Storage backing real-time systems|
|Prototyping and research|Filesystems needing tight kernel integration|
|Unprivileged user mounts|Systems where kernel module signing is enforced|

> **Performance Reminder:** FUSE is not ideal for high-throughput local storage workloads. For database backing stores, VM images, or latency-critical applications, native kernel filesystems (ext4, xfs, btrfs) remain the right choice.

---

## What Would Happen Without FUSE?

Without FUSE, many technologies that developers take for granted today would either not exist or would be dramatically more difficult to build and maintain:

- **Remote filesystems** — `sshfs` alone is used by millions of developers daily. Without FUSE, mounting remote directories would require kernel drivers or heavy infrastructure like NFS servers.
- **Rootless containers** — Docker and Podman's rootless mode depends on `fuse-overlayfs`. Without it, running containers without root would require kernel privilege.
- **User-controlled encryption** — EncFS and gocryptfs provide encrypted filesystems any user can create and mount without administrator involvement.
- **Cloud storage integration** — `rclone mount` and `s3fs-fuse` allow cloud buckets to appear as local directories. Without FUSE, this would require kernel modules for every cloud provider.
- **Filesystem research** — researchers can implement and test novel filesystem algorithms without risking system stability or needing kernel commit access.
- **Cross-platform filesystem access** — `ntfs-3g` provides full NTFS read-write access on Linux. A kernel-space implementation would be far more complex to maintain and certify.

---

## Conclusion

FUSE represents one of the most successful applications of the Unix philosophy — do one thing well. By handling only the routing of filesystem requests, the FUSE kernel module enables an entire ecosystem of user-space filesystems that would otherwise be impossible.

Its benefits — safety, ease of development, portability, flexibility, and support for unprivileged users — have made it foundational to modern container tooling, encrypted storage, remote filesystem access, and operating system research.

While FUSE filesystems carry a performance cost versus native kernel implementations, that tradeoff is almost always acceptable for the categories of workloads they serve. For any filesystem that involves remote data, virtual content, policy enforcement, or encryption, FUSE is the practical and correct architectural choice.
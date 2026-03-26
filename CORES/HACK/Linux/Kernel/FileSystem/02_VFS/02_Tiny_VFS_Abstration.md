Great exercise. Building a **tiny VFS simulator** is exactly the kind of thing that makes OS internals “click”. We’ll keep it **small (~150 lines)** but structurally similar to the real concepts used by the Linux Kernel inside the Virtual File System.

Goal: simulate

- **Superblock** → filesystem root
    
- **Inode** → file object / metadata
    
- **Dentry** → filename → inode mapping
    
- **File** → open file instance
    

No disk, no page cache — just the **object relationships**.

---

# Minimal Tiny VFS (C++)

```cpp
#include <iostream>
#include <memory>
#include <unordered_map>
#include <vector>

using namespace std;

enum class InodeType { FILE, DIRECTORY };

struct Inode {
    int id;
    InodeType type;
    string data;

    Inode(int id, InodeType type) : id(id), type(type) {}
};

struct Dentry {
    string name;
    shared_ptr<Inode> inode;
    unordered_map<string, shared_ptr<Dentry>> children;

    Dentry(string name, shared_ptr<Inode> inode)
        : name(name), inode(inode) {}
};

struct File {
    shared_ptr<Inode> inode;
    size_t offset = 0;

    File(shared_ptr<Inode> inode) : inode(inode) {}

    string read(size_t size) {
        string result = inode->data.substr(offset, size);
        offset += result.size();
        return result;
    }

    void write(const string& buf) {
        inode->data.insert(offset, buf);
        offset += buf.size();
    }
};

class Superblock {
    int next_inode = 1;

public:
    shared_ptr<Dentry> root;

    Superblock() {
        auto root_inode = make_shared<Inode>(next_inode++, InodeType::DIRECTORY);
        root = make_shared<Dentry>("/", root_inode);
    }

    shared_ptr<Dentry> mkdir(shared_ptr<Dentry> parent, const string& name) {
        auto inode = make_shared<Inode>(next_inode++, InodeType::DIRECTORY);
        auto dentry = make_shared<Dentry>(name, inode);
        parent->children[name] = dentry;
        return dentry;
    }

    shared_ptr<Dentry> create_file(shared_ptr<Dentry> parent, const string& name) {
        auto inode = make_shared<Inode>(next_inode++, InodeType::FILE);
        auto dentry = make_shared<Dentry>(name, inode);
        parent->children[name] = dentry;
        return dentry;
    }

    shared_ptr<Dentry> lookup(shared_ptr<Dentry> dir, const string& name) {
        if (dir->children.count(name))
            return dir->children[name];
        return nullptr;
    }
};

int main() {

    Superblock fs;

    auto home = fs.mkdir(fs.root, "home");
    auto user = fs.mkdir(home, "user");
    auto file_dentry = fs.create_file(user, "notes.txt");

    File file(file_dentry->inode);

    file.write("Hello Virtual File System!");

    file.offset = 0;

    cout << "Read: " << file.read(100) << endl;

    return 0;
}
```

---

# What This Program Demonstrates

## 1. Superblock → Filesystem root

```
Superblock
   │
   └── root dentry "/"
```

Creates the **filesystem tree root**.

---

## 2. Dentry → Directory tree

```
/
└── home
    └── user
        └── notes.txt
```

Each node is a **Dentry**.

---

## 3. Inode → Actual file object

The file:

```
notes.txt
```

maps to:

```
inode #3
```

Which stores:

```
data = "Hello Virtual File System!"
```

Multiple dentries could point to the same inode (hard links).

---

## 4. File → Open file instance

```
File file(file_dentry->inode);
```

This is equivalent to:

```
fd = open("notes.txt")
```

It stores:

```
inode pointer
file offset
```

Two processes could open the same inode with different offsets.

---

# Result When Running

Output:

```
Read: Hello Virtual File System!
```

---

# Mental Model After This Exercise

You now see the relationships clearly:

```
Superblock
   │
   ▼
Dentry tree
   │
   ▼
Inode
   │
   ▼
File (open instance)
```

Which mirrors the real kernel pipeline in the Linux Kernel.

---

# If You Want a More Realistic Version (Next Step)

We can extend this tiny VFS to include:

1. **Path lookup algorithm (`/home/user/file`)**
    
2. **File descriptor table**
    
3. **Hard links**
    
4. **Page cache simulation**
    
5. **Mount points**
    
6. **Syscall-like API (`open/read/write`)**
    

That version becomes about **400–600 lines** and starts looking surprisingly close to the real VFS architecture.

If you'd like, I can also show you a **~300 line version that implements real path traversal (`namei`)**, which is the **core algorithm Linux uses to resolve file paths.**
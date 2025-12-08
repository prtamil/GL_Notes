## **Naming Conventions for Clojure Project Root and `src/` Directory**

When creating a Clojure project, two layers of naming are involved:

1. **The project / repository root directory**
2. **The namespaces inside the `src/` directory**
    

Although they may look similar, they serve different purposes and follow different conventions.

---

### **1. Project Root Directory — Human-Facing Name**

The project root directory is the folder that contains `deps.edn`, `src/`, `dev/`, and so on.  
This name is **not interpreted by the Clojure compiler**. Instead, it is used by:

- GitHub repository name
- Dependency managers (e.g., Clojars, Maven)
- Developers reading the project
    

Because it is a human-facing name, the established Clojure convention is:

`lowercase words separated by hyphens`

Examples:

```js
template-specter
ring-core
my-clojure-app

```

Hyphens are preferred because they improve readability and match artifact naming in the wider JVM ecosystem. You **can** use underscores or other patterns, but hyphens are the idiomatic choice.

---

### **2. Namespaces Inside `src/` — Compiler-Facing Names**

Files inside `src/` (and other classpath directories) represent **Clojure namespaces**.  
Namespaces are part of the **language**, so their names must follow the expectations of the compiler and JVM.

Namespace names in code use **dots and hyphens**:

```clj
(ns template-specter.core)

```

But the **file path** must use **dots → directories** and **hyphens → underscores**:
```js
src/template_specter/core.clj
```


This mapping exists because:

- Clojure allows hyphens in symbols (very idiomatic)
- The JVM does **not** allow hyphens in class names
- Namespaces may compile into JVM `.class` files, so hyphens become underscores on disk
    

Therefore:

|Namespace symbol in code|Required file path|
|---|---|
|`template-specter.core`|`src/template_specter/core.clj`|
|`my-app.service.http`|`src/my_app/service/http.clj`|

---

### **3. Why the Two Levels Differ**

The root directory name is **human-facing**.  
The namespace directory inside `src` is **compiler-facing**.

|Level|Audience|Rules|Reason|
|---|---|---|---|
|Project root|Humans & package systems|Hyphens recommended|Readability and artifact naming|
|Namespace under `src/`|Clojure + JVM|Hyphens in code, underscores in files|JVM class-name compatibility|

---

### **4. Summary**

- Use hyphens for the **project root folder** (e.g., `template-specter`)
- Use hyphens in **namespace names in code** (e.g., `template-specter.core`)
- Use underscores in **folders under `src/`** (e.g., `src/template_specter/core.clj`)
    

Final mapping example:

```js
Project root:  template-specter/
Namespace:     template-specter.core
File path:     src/template_specter/core.clj

```


This pattern is considered the most idiomatic and compatible across the Clojure ecosystem.
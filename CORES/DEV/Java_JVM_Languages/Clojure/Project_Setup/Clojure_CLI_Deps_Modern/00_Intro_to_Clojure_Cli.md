# Introduction
Clojure CLI and the newer  deps.edn/tools.deps  setup replace the older Leiningen “all-in-one” model with a simpler, more flexible, data-driven approach to managing Clojure projects. Instead of mixing configuration, logic, plugins, and build behavior in a single `project.clj`, the new system cleanly separates responsibilities: `deps.edn` holds pure dependency and path data, **tools.deps** resolves those dependencies and builds classpaths, and **Clojure CLI** provides the command-line interface for running code, invoking tools, and managing builds. This modular design is lighter, more composable, supports modern features like git dependencies, and avoids the lock-in and complexity of monolithic build tools, giving developers a more transparent and extensible workflow.
# 🧠 Mental Model: “Three Layers Working Together”

Think of the newer Clojure setup as **three layered components**:

```js
┌────────────────────────┐
│      Clojure CLI       │  ← the *interface*
└────────────────────────┘
┌────────────────────────┐
│       tools.deps       │  ← the *engine*
└────────────────────────┘
┌────────────────────────┐
│        deps.edn        │  ← the *configuration*
└────────────────────────┘

```

This separation gives:  
✔ composability  
✔ extensibility  
✔ simpler semantics  
✔ freedom from “one big build tool”

Leiningen was great, but it mixed **tooling**, **configuration**, **scripting**, and **build logic** into one thing (project.clj).

---

# 🔹 1. `deps.edn` — _pure data describing your project_

**Analogy:** your project’s “shopping list” of dependencies, paths, aliases.

It contains **no logic**, **no DSL**, just data:

```js
{:paths ["src"]
 :deps {org.clojure/clojure {:mvn/version "1.11.1"}}

 :aliases
 {:dev {:extra-paths ["dev"]
        :extra-deps {criterium/criterium {:mvn/version "0.4.6"}}}
  :uberjar {:extra-deps {uberdeps/uberdeps {:mvn/version "1.2.0"}}}}}

```

`deps.edn` is deliberately simple — essentially a map that tools.deps reads.

### Why separate it?

Because you don’t want logic mixed with dependency declarations.  
Leiningen mixed both in `project.clj`.

---

# 🔹 2. `tools.deps` — the “dependency solver / classpath builder”

**Analogy:** npm / cargo's dependency resolution engine.

It is a library (not a tool itself) that:

- reads `deps.edn`
- fetches Maven deps
- computes classpaths
- runs dependency conflict resolution
- supports git deps (huge advantage over Lein)
    

You normally _don’t run_ tools.deps directly — the **CLI calls it**.

---

# 🔹 3. Clojure CLI (`clj` / `clojure`) — the user interface

**Analogy:** a “toolbelt” that invokes the engine.

It provides commands like:

```js
clj -M:dev
clj -X:uberjar
clj -T:build uber
clojure -A:dev -m my.app

```

**What the CLI is responsible for:**

- parsing command line flags (`-A`, `-M`, `-X`, `-T`)
- choosing how to execute (`-M` = main, `-X` = function call, `-T` = tool)
- invoking tools.deps to compute classpath
- running JVM with correct classpath + your code
    

### Why separate this from tools.deps?

Because the CLI evolves separately from dependency resolution logic.  
Different execution modes (`-X`, `-T`) became possible _without_ altering dep resolution.

---

# 🧩 Why three things instead of one (like Leiningen)?

### **Reason 1: Separation of Concerns**

|Thing|Single responsibility|
|---|---|
|deps.edn|data only|
|tools.deps|dependency resolution + classpath building|
|clojure CLI|command execution + UX wrapper|

Leiningen lumped all of this together.

---

### **Reason 2: Tools are composable, not monolithic**

Leiningen plugins were heavily tied to Lein’s internal model.
The new approach lets you install “tools” independent of Clojure CLI releases:

```js
clj -Ttools install io.github.clojure/tools.build
clj -T:build uber

```

This creates a small ecosystem of indendent single-purpose tools (like tools.build, tools.deps.graph, tools.deployer, etc.).

---

### **Reason 3: Data-first configuration**

`project.clj` used code (Clojure DSL) to configure a build.

`deps.edn` is pure edn — no macros, no code, no hidden behavior.  
This makes tooling simpler and safer.

---

### **Reason 4: Git deps (huge improvement)**

Older Clojure tools (Lein, Boot) only supported Maven.

Now you can depend on a Git SHA or tag:

```js
:deps {my/lib {:git/url "https://github.com/me/lib"
               :sha "28fe20c"}}

```

This is a fundamental change → it made tools.deps necessary.

---

### **Reason 5: Flexibility, not one build tool**

Clojure CLI doesn’t assume Lein’s opinionated structure.

You can pick:

- tools.build for building/packaging
- babashka for scripts
- kaocha for tests
- shadow-cljs for CLJS builds
- uberdeps, deps-deploy, etc.
    

The ecosystem becomes modular rather than “everything through Lein plugins”.

---

# 🧠 Final mental model summary

If Leiningen is:

> **A big Swiss army knife with everything built in**

Then Clojure CLI is:

> **A toolbelt where each tool is simple, replaceable, and composable.**

- `deps.edn` → describes what you want
- `tools.deps` → figures out how to get it
- `clj` / `clojure` → runs it
    

This separation gives you better reproducibility, simpler mental overhead, and the ability to mix and match tools.
Yes — that's actually the **better separation**.

We'll treat **JavaScript language**, **Node.js runtime**, and **Browser runtime** as three different things. Frameworks like React come later as a separate layer.

## Browser JavaScript — Interview Master Topic Map

```text
BROWSER JAVASCRIPT
│
├── 1. JavaScript Language
│   ├── Execution Context
│   ├── Scope / Lexical Environment
│   ├── Closures
│   ├── this
│   ├── Prototype / Prototype Chain
│   ├── Objects
│   ├── Arrays
│   ├── Map / Set
│   ├── Iterators / Generators
│   ├── Classes
│   ├── Modules
│   └── Symbols
│
├── 2. JavaScript Engine
│   ├── Parser
│   ├── AST
│   ├── Bytecode
│   ├── JIT
│   ├── Hidden Classes / Shapes
│   ├── Inline Caches
│   └── Deoptimization
│
├── 3. Browser Runtime
│   ├── JavaScript Engine
│   ├── Web APIs
│   ├── Event Loop
│   ├── Task Queue
│   ├── Microtask Queue
│   └── Rendering Pipeline
│
├── 4. Event Loop ⭐⭐⭐⭐⭐
│   ├── Tasks
│   ├── Microtasks
│   ├── Promise callbacks
│   ├── Timers
│   ├── MutationObserver
│   ├── requestAnimationFrame
│   └── Rendering opportunities
│
├── 5. DOM ⭐⭐⭐⭐⭐
│   ├── DOM Tree
│   ├── Nodes
│   ├── Elements
│   ├── Attributes
│   ├── DOM APIs
│   ├── DOM Mutation
│   ├── Events
│   └── Event Delegation
│
├── 6. Browser Rendering ⭐⭐⭐⭐⭐
│   ├── Style Calculation
│   ├── Layout
│   ├── Paint
│   ├── Compositing
│   ├── Layers
│   ├── Reflow
│   ├── Repaint
│   └── Rendering Performance
│
├── 7. Browser Events ⭐⭐⭐⭐⭐
│   ├── Event propagation
│   ├── Capturing
│   ├── Target
│   ├── Bubbling
│   ├── stopPropagation
│   ├── preventDefault
│   ├── Event delegation
│   └── Passive listeners
│
├── 8. Networking ⭐⭐⭐⭐⭐
│   ├── fetch
│   ├── XMLHttpRequest
│   ├── HTTP
│   ├── HTTPS
│   ├── DNS
│   ├── TCP
│   ├── TLS
│   ├── HTTP/2
│   ├── HTTP/3
│   ├── CORS
│   └── Preflight
│
├── 9. Browser Storage
│   ├── Cookies
│   ├── localStorage
│   ├── sessionStorage
│   ├── IndexedDB
│   ├── Cache API
│   └── Storage quotas
│
├── 10. Web Workers ⭐⭐⭐⭐
│   ├── Worker
│   ├── Dedicated Worker
│   ├── Shared Worker
│   ├── postMessage
│   ├── Structured Clone
│   ├── Transferable Objects
│   ├── SharedArrayBuffer
│   └── Atomics
│
├── 11. Browser Memory ⭐⭐⭐⭐⭐
│   ├── JS Heap
│   ├── GC
│   ├── GC Roots
│   ├── Closures
│   ├── Detached DOM
│   ├── Event listener leaks
│   ├── Timer leaks
│   └── SPA memory leaks
│
├── 12. Security ⭐⭐⭐⭐⭐
│   ├── Same-Origin Policy
│   ├── CORS
│   ├── XSS
│   ├── CSRF
│   ├── CSP
│   ├── Clickjacking
│   ├── DOM XSS
│   ├── Prototype Pollution
│   └── Cookie security
│
├── 13. Performance ⭐⭐⭐⭐⭐
│   ├── Main-thread blocking
│   ├── Long Tasks
│   ├── Layout thrashing
│   ├── Forced synchronous layout
│   ├── requestAnimationFrame
│   ├── Web Workers
│   ├── Code splitting
│   ├── Lazy loading
│   └── Core Web Vitals
│
└── 14. Advanced Browser APIs
    ├── WebSocket
    ├── Server-Sent Events
    ├── WebRTC
    ├── IntersectionObserver
    ├── ResizeObserver
    ├── MutationObserver
    ├── BroadcastChannel
    ├── Service Workers
    └── Web Streams
```

### The key mental model

Don't think of browser JavaScript as simply:

```text
JavaScript → Browser
```

Think:

```text
                    BROWSER
                       │
        ┌──────────────┼───────────────┐
        │              │               │
        ▼              ▼               ▼
 JavaScript         Web APIs       Rendering
  Engine                               │
   │                    │              │
   │                    │              ├── Style
   │                    │              ├── Layout
   │                    │              ├── Paint
   │                    │              └── Composite
   │                    │
   └────────────┬───────┘
                │
                ▼
            Event Loop
                │
        ┌───────┴────────┐
        ▼                ▼
      Tasks          Microtasks
```

And this gives us a very useful distinction:

> **JavaScript is the language. V8/SpiderMonkey/JavaScriptCore is the engine. The browser is the host environment.**

For example:

```javascript
fetch("/users");
```

`fetch` isn't a JavaScript language feature. It's a **browser Web API**.

Likewise:

```javascript
document.querySelector("#app");
```

`document` isn't provided by JavaScript itself. It's supplied by the browser's **DOM API**.

And:

```javascript
setTimeout(...)
```

isn't fundamentally a JavaScript language primitive either; it's a host-provided timer API.

---

### Our eventual "shock question" set

Once we start studying this, I'd use questions like:

> **"When I click a button, tell me everything that happens from the OS input event until pixels appear on the screen."**

or:

> **"Why can a 200 ms JavaScript function freeze the entire webpage?"**

or:

> **"Explain exactly what happens when `fetch()` is called. Does JavaScript execute the network request?"**

or:

> **"Why does `Promise.then()` execute before `setTimeout(..., 0)`?"**

or:

> **"What happens when you modify the DOM? Does the browser immediately repaint?"**

or the really good senior question:

> **"Why can reading `offsetHeight` after modifying the DOM cause a performance problem?"**

That takes us through **JavaScript → event loop → DOM → style → layout → paint → compositor**, which is exactly the kind of first-principles understanding you're building with Python internals.

And yes: **React, Vue, Angular, etc. stay completely outside this track.** We'll put frameworks on top later.
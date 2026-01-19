### 1. **Event-Driven, Non-Blocking I/O (Reactor Pattern)**

**Used by:** Node.js, libuv, asyncio, libevent  
**Core idea:**  
Single event loop reacts to I/O readiness; user code must never block.

---

### 2. **Communicating Sequential Processes (CSP)**

**Used by:** Go (goroutines + channels)  
**Core idea:**  
Lightweight threads communicate via channels; blocking is cheap and expected.

---

### 3. **Actor Model**

**Used by:** Erlang/OTP, Elixir, Akka  
**Core idea:**  
Isolated processes communicate only by asynchronous message passing.

---

### 4. **Thread-Per-Request / Blocking I/O Model**

**Used by:** Early Java servers, Apache prefork, traditional C/C++  
**Core idea:**  
Each request runs on its own OS thread and blocks on I/O.

---

### 5. **Dataflow / Reactive Streams Model**

**Used by:** Reactive Streams, Rx, some streaming frameworks  
**Core idea:**  
Data flows through a graph of operators with explicit backpressure.
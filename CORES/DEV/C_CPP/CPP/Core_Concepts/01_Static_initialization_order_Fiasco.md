# Static Initialization Order Fiasco  


The **Static Initialization Order Fiasco (SIOF)** is a C++ problem where **global/static objects in different translation units (`.cpp` files) depend on each other during initialization**.

Within the same `.cpp` file, initialization order is defined by declaration order. Across different `.cpp` files, you generally **must not depend on dynamic initialization order**.

```cpp
// a.cpp
Config config;

// b.cpp
extern Config config;
Logger logger(config);   // dangerous
```

If `logger` is dynamically initialized before `config`, it accesses an object whose initialization is not complete.

```text
Global A (a.cpp)
     ↑
     │ depends on
Global B (b.cpp)

Cross-TU dynamic initialization order
        = don't depend on it
```

The standard solution is **Construct on First Use**:

```cpp
Config& getConfig()
{
    static Config config;
    return config;
}
```

The object is initialized the first time the function is called. Since **C++11, function-local static initialization is thread-safe**. C++20 `constinit` is another useful tool when an object can be guaranteed to use static initialization.

**Interview definition:** SIOF is an initialization-order bug caused by dependencies between dynamically initialized static-storage objects in different translation units.

# Static Deinitialization Order Fiasco

The **Static Deinitialization Order Fiasco** is a C++ problem where **global/static objects depend on each other during program shutdown**.

Global objects are destroyed after `main()` finishes, generally in the **reverse order of their completed initialization**. Across translation units, this can become dangerous when one object's destructor uses another object that has already been destroyed.

```cpp
// logger.cpp
Logger logger;

// service.cpp
extern Logger logger;

Service::~Service()
{
    logger.log("Service destroyed"); // dangerous
}
```

If `logger` is destroyed before `Service`, then:

```text
main() ends
    │
    ▼
Logger destroyed
    │
    ▼
Service destructor
    │
    ▼
tries to use Logger
    │
    ▼
BUG / undefined behavior
```

A common solution for process-lifetime infrastructure is to deliberately keep the object alive until process termination:

```cpp
Logger& getLogger()
{
    static Logger* logger = new Logger;
    return *logger;
}
```

The pointer itself is destroyed, but the `Logger` is intentionally never deleted, so destructor-order dependencies disappear.

**Interview definition:** The static deinitialization order fiasco occurs when the destructor of one static-storage object accesses another static object whose lifetime has already ended.


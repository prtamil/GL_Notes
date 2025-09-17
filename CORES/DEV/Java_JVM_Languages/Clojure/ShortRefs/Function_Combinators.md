## 🔹 What are Function Combinators?

Function combinators are **higher-order functions** that **take functions as input and return new functions**. These allow you to **compose, transform, or combine** functions in flexible and powerful ways.

They are especially core to **functional programming**, where functions are first-class values.

---

## 🧠 Functions in this "Function Combinators" Family

Here's a categorized list of Clojure's most common **function combinators**:

### 🔁 Function Composition & Transformation

|Function|Description|
|---|---|
|`comp`|Compose functions right-to-left: `(comp f g h)` → `f(g(h(x)))`|
|`complement`|Returns a function that negates the result of another: `(complement pred)`|
|`partial`|Returns a partially applied version of a function|
|`juxt`|Takes multiple functions and returns a function that returns a vector of results from all of them|
|`fnil`|Wraps a function to replace nil arguments with default values|
|`memoize`|Returns a version of a function that caches its results|

---

### 🧮 Function Combination

|Function|Description|
|---|---|
|`every-fn`|Combines multiple predicates into one that returns true if **all** are true|
|`some-fn`|Combines multiple predicates into one that returns true if **any** are true|

---

### 📦 Function Utilities

|Function|Description|
|---|---|
|`identity`|Returns its argument unchanged; often used as a default or placeholder|
|`constantly`|Returns a function that always returns the same value|
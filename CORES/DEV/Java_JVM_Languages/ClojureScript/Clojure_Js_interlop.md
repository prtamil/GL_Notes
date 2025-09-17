```clojurescript
;; =====================================
;; CLOJURESCRIPT JAVASCRIPT INTEROP CHEAT SHEET
;; =====================================

;; 1. PROPERTY ACCESS
;; =====================================

;; Reading properties
(def obj #js{:name "John" :age 30})
(.-name obj)                    ;; => "John"
(.-age obj)                    ;; => 30
(.. js/document -body -style)  ;; Nested property access

;; Writing properties
(set! (.-name obj) "Jane")     ;; Mutate property
(set! (.-newProp obj) "value") ;; Create new property
(set! (.. js/document -body -className) "dark") ;; Nested set

;; 2. METHOD CALLS
;; =====================================

;; Basic method calls
(.log js/console "Hello")      ;; console.log("Hello")
(.getElementById js/document "app") ;; document.getElementById("app")

;; Method calls with multiple arguments
(.setAttribute elem "class" "active") ;; elem.setAttribute("class", "active")

;; Chaining method calls
(-> (js/Date.)
    (.getTime)
    (.toString))

;; 3. CONSTRUCTORS
;; =====================================

;; Creating JavaScript objects
(js/Date.)                     ;; new Date()
(js/Array.)                    ;; new Array()
(js/Object.)                   ;; new Object()

;; Constructor with arguments
(js/Date. "2024-01-01")       ;; new Date("2024-01-01")
(js/Array. 1 2 3)             ;; new Array(1, 2, 3)

;; 4. GLOBAL OBJECTS & FUNCTIONS
;; =====================================

;; Accessing global objects
js/window                      ;; window
js/document                    ;; document
js/console                     ;; console

;; Global functions
(js/parseInt "42")            ;; parseInt("42")
(js/parseFloat "3.14")        ;; parseFloat("3.14")
(js/isNaN js/NaN)            ;; isNaN(NaN)

;; 5. JS OBJECTS & ARRAYS
;; =====================================

;; Creating JS objects
#js{:name "John"}             ;; {name: "John"}
#js{"key" "value"}           ;; {key: "value"}

;; Creating JS arrays
#js[1 2 3]                    ;; [1, 2, 3]
(array 1 2 3)                 ;; [1, 2, 3]

;; 6. EVENT HANDLING
;; =====================================

;; Adding event listeners
(.addEventListener elem "click"
                   (fn [e] (.log js/console "clicked!")))

;; Removing event listeners
(.removeEventListener elem "click" handler)

;; Preventing default
(fn [e]
  (.preventDefault e)
  (.stopPropagation e))

;; 7. PROMISES & ASYNC
;; =====================================

;; Working with Promises
(-> (js/fetch "https://api.example.com/data")
    (.then #(.-json %))
    (.then #(js->clj % :keywordize-keys true))
    (.catch #(.log js/console "Error:" %)))

;; Async/Await (needs special macro support)
(async/go
  (try
    (let [response (async/<! (js/fetch "https://api.example.com/data"))
          data (async/<! (.json response))]
      (js->clj data :keywordize-keys true))
    (catch js/Error e
      (.log js/console "Error:" e))))

;; 8. DOM MANIPULATION
;; =====================================

;; Creating elements
(def div (.createElement js/document "div"))

;; Setting attributes
(.setAttribute div "class" "container")
(set! (.-innerHTML div) "Hello!")

;; Appending children
(.appendChild parent-elem child-elem)
(.removeChild parent-elem child-elem)

;; 9. TYPE CHECKS & CONVERSION
;; =====================================

;; Type checking
(instance? js/Array obj)      ;; obj instanceof Array
(js/Array.isArray obj)        ;; Array.isArray(obj)

;; Type conversion
(str obj)                     ;; Convert to string
(js/Number "42")             ;; Convert to number
(js/Boolean 0)               ;; Convert to boolean

;; 10. ADVANCED PATTERNS
;; =====================================

;; Destructuring JS objects
(let [{:keys [name age]} (js->clj #js{:name "John" :age 30} 
                                 :keywordize-keys true)]
  [name age])

;; Creating JS classes
(deftype Person [name age]
  Object
  (getName [_] name)
  (getAge [_] age))

;; Extending JS prototypes (be careful!)
(set! (.-customMethod (.-prototype js/Array))
      (fn [] (this-as this (.join this ","))))

;; 11. BEST PRACTICES
;; =====================================

;; 1. Wrap JS interop in ClojureScript functions
(defn log [& args]
  (.apply (.-log js/console) js/console (clj->js args)))

;; 2. Use threading macros for chains
(defn get-computed-style [elem prop]
  (-> (js/window.getComputedStyle elem)
      (.getPropertyValue prop)))

;; 3. Handle null/undefined safely
(defn get-prop [obj prop]
  (when obj
    (aget obj prop)))

;; 4. Create facade for JS libraries
(ns my-app.lodash
  (:require ["lodash" :as lodash]))

(defn deep-clone [obj]
  (.cloneDeep lodash obj))

;; 12. DEBUGGING
;; =====================================

;; Console logging
(.log js/console obj)         ;; View object in console
(.dir js/console obj)         ;; Interactive object view
(.table js/console obj)       ;; Tabular view

;; Type inspection
(type obj)                    ;; Get CLJS type
(js/typeof obj)              ;; Get JS type

;; Property enumeration
(js/Object.keys obj)          ;; Get object keys
(js-keys obj)                 ;; ClojureScript helper
```

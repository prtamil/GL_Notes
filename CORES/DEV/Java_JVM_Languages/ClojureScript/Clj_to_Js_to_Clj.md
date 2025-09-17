1. **Simple Conversions:**
    - `js->clj`: Converts JavaScript objects to ClojureScript data structures
    - `clj->js`: Converts ClojureScript data structures to JavaScript objects
    - The `:keywordize-keys true` option converts string keys to keywords
2. **Key Differences:**
    - JavaScript objects are mutable; ClojureScript data structures are immutable
    - JavaScript uses dot notation; ClojureScript uses function calls
    - JavaScript arrays vs ClojureScript vectors
    - JavaScript objects vs ClojureScript maps
3. **Common Use Cases:**
    - Working with JavaScript libraries
    - Handling API responses
    - Passing props to React components
    - Processing complex nested data structures
4. **Best Practices:**
    - Convert at the boundaries of your system (API calls, library interfaces)
    - Work with ClojureScript data structures in your business logic
    - Convert back to JavaScript only when needed
    - Use `:keywordize-keys true` for more idiomatic ClojureScript
5. **Things to Watch Out For:**
    - Nested structures need deep conversion
    - JavaScript Date objects need special handling
    - JavaScript Sets and Maps have different semantics
    - Some JavaScript objects might not convert cleanly

Here's a simple mental model to remember:

- Think of `js->clj` as "entering ClojureScript land"
- Think of `clj->js` as "entering JavaScript land"
- Convert at the boundaries of these "lands"
- Stay in "ClojureScript land" as much as possible

```clojurescript
;; ================= SIMPLE EXAMPLES =================

;; Basic JavaScript Object -> ClojureScript Map
(def js-user #js{:name "John" :age 30})
(js->clj js-user)
;; => {"name" "John", "age" 30}

;; With keyword keys
(js->clj js-user :keywordize-keys true)
;; => {:name "John", :age 30}

;; Basic ClojureScript Map -> JavaScript Object
(def clj-user {:name "Alice" :age 25})
(clj->js clj-user)
;; => #js{:name "Alice", :age 25}

;; ================= INTERMEDIATE EXAMPLES =================

;; Nested Structures
(def js-nested #js{:user #js{:address #js{:city "New York"}}
                   :scores #js[10 20 30]})

;; Convert with nested structures
(js->clj js-nested :keywordize-keys true)
;; => {:user {:address {:city "New York"}}
;;     :scores [10 20 30]}

;; Arrays and Collections
(def mixed-data #js[#js{:id 1} #js{:id 2} #js["a" "b"]])
(js->clj mixed-data :keywordize-keys true)
;; => [{:id 1} {:id 2} ["a" "b"]]

;; ================= COMPLEX EXAMPLES =================

;; Complex Data Structure Example
(def complex-js-data
  #js{:metadata #js{:created "2024-01-01"
                    :version "1.0"
                    :flags #js[true false true]}
      :users #js[#js{:id 1
                     :profile #js{:name "John"
                                :settings #js{:theme "dark"
                                            :notifications true}
                                :friends #js[2 3 4]}
                     :posts #js[#js{:id "p1"
                                   :comments #js[#js{:text "Nice!"
                                                   :author 2}]}]}]
      :statistics #js{:active true
                     :counts #js{:posts 10
                               :comments 20}
                     :tags #js["important" "featured"]}})

;; Convert complex JS -> CLJ
(defn process-js-data []
  (let [clj-data (js->clj complex-js-data :keywordize-keys true)]
    ;; Now we can use ClojureScript idioms
    (-> clj-data
        (get-in [:users 0 :profile :friends])
        (conj 5)))) ;; Add a friend

;; Convert complex CLJ -> JS
(def complex-clj-data
  {:config {:api {:endpoints [{:url "/users"
                              :methods [:get :post]
                              :auth {:required true
                                    :roles #{:admin :user}}
                              :rate-limit {:max 100
                                         :window "1h"}}]
                  :fallback {:enabled true
                            :retry {:count 3
                                  :delay 1000}}}
           :features {:enabled #{:chat :notifications}
                     :beta #{:dark-mode}
                     :flags (into {} (map (fn [x] [x true]) 
                                        [:feature1 :feature2]))}}
   :data {:users (vec (for [i (range 5)]
                       {:id i
                        :metadata {:created (str "2024-" i)
                                 :tags (set (range i))}}))
          :settings (reduce (fn [acc k] 
                            (assoc acc k {:enabled (odd? k)}))
                          {}
                          (range 10))}})

;; ================= PRACTICAL USAGE EXAMPLES =================

;; Example 1: Working with JavaScript Libraries
(ns example.lodash-usage
  (:require ["lodash" :as _]))

(defn sort-users-by-age [users]
  (let [js-users (clj->js users)
        sorted-js-users (.sortBy js/_ js-users "age")
        sorted-clj-users (js->clj sorted-js-users :keywordize-keys true)]
    sorted-clj-users))

;; Example 2: API Integration
(ns example.api-handling
  (:require ["axios" :as axios]))

(defn process-api-response [response]
  (let [js-data (-> response .-data)
        clj-data (js->clj js-data :keywordize-keys true)]
    (-> clj-data
        (update-in [:users] #(filter :active %))
        (update-in [:metadata :timestamp] #(js/Date. %))
        clj->js))) ;; Convert back to JS if needed

;; Example 3: React Component Props
(ns example.react-props
  (:require ["react" :as react]))

(defn prepare-component-props [clj-props]
  (let [js-props (clj->js clj-props)]
    (.createElement react "Component" js-props)))

;; ================= UTILITY FUNCTIONS =================

(defn deep-transform
  "Utility function to transform nested data structures"
  [data transform-fn]
  (cond
    (map? data) (reduce-kv
                  (fn [m k v]
                    (assoc m k (deep-transform v transform-fn)))
                  {}
                  data)
    (sequential? data) (mapv #(deep-transform % transform-fn) data)
    :else (transform-fn data)))

;; Example usage of deep transform
(defn process-dates [data]
  (deep-transform
    data
    (fn [v]
      (if (string? v)
        (try
          (js/Date. v)
          (catch :default _ v))
        v))))
```
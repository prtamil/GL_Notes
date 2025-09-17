# Javascript
## Falsy Items
1. 0
2. false
3. undefined
4. null
5. NaN
6. ""
## Arrow functions
    - Arrow Function
        + No seprate this. Uses this from scope
        + No bindings of arguments
        + No constructor no allocate thru New
        + No prototype propery
        + yield cannot be used
## Promises
   - new Promise((resolve,reject) => {})
   - Promise.all
   - Promise.race

## Async Await
   - function should begin with async : async function dowork(){}
   - let x = await Promise();
        + eqv to: promise.then(x=>{}) 
   - catch 
        + use try catch
   - async function return promise
   - then calls should be called with await
   - all promise should be called with await

## Curried Functions

   const fn = (a) => (b) => (c) => a*b*c;

   fn(10)(20)(30);

   const gn = function(a) {
       return function(b) {
           return function(c) {
               return a*b*c;
           }
       }
   }

  Both are equivalent.

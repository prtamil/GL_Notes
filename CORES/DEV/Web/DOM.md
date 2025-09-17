
# Enable paste
```js
const dontTreadOnMe = (e) => e.stopImmediatePropagation();

document.addEventListener('paste',dontTreadOnMe,true);
```
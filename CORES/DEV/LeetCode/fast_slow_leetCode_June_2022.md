# Fast,slow ptr technique for removing duplicate [:Sorted Array, :InPlace]

use 2 index fast, slow to solve the problem.

```python
In [28]: def removeDupl(arr):
    ...:     if len(arr) == 0:
    ...:         return 0
    ...:     slow = 0
    ...:     fast = 0
    ...:     while fast < len(arr):             #1. Stop Program
    ...:         if arr[fast] != arr[slow]:     #2. check Fast != Slow this is detecting Condition
    ...:             slow += 1                  #3. Only move slow when find non duplicated value
    ...:             arr[slow] = arr[fast]      #4. fast=nondupl-value, slow=prev+1, so slow = next nonduplicated val.
    ...:         fast+=1                        #5. Move fast by step.
    ...:     return [arr, slow+1]
    ...:

> arr,idx = removeDupl([1,1,2,2,2,3,3,3,4])
res = arr[0:idx]
```

Remove Zero in Array

```python
def removeElement(arr,e):
    if len(arr) == 0:
        return 0
    slow = 0
    fast = 0
    while fast+1 < len(arr):
        if arr[fast] == 0:
            slow = fast
            fast += 1
            arr[slow] = arr[fast]
        fast += 1
    return arr

//remove zero
a = [1,0,2,0,3,0,4,0]
arr = removeElement(a,0)
res,idx = removeDupl(arr)
fres = res[0:idx]

```


```python
 def flat(lst):
         res = []
         for l in lst:
             if type(l) is list:
                 res += flat(l)
             else:
                 res.append(l)
         return res
```


```py
import heapq

l = [5,4,3,7,8,9]
heapq.heapify(l)
heapq.nlargest(3,l)
heapq.nsmallest(3,l)

def heapsort(l):
   h = []
   for x in l:
	   heapq.heappush(h,x)
   res = []
   for x in range(len(h)):
      res.append(heapq.heappop(h))
   return res
```
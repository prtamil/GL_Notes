go lang slices are refrences.
so passing same variable will lead to mess in recursive function.

so use new variables instead of and append.

```golang

func sum(n int, res []int) []int {
    if n < 1 {
        return res
    } else {
        x := append(res, n)  // <- Use different variable instead of same res because slice is reference
        return sum(n-1,x)

    }
}
```

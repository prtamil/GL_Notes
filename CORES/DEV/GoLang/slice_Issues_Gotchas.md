# slices:

Is a struct of

[Ptr|Len|Cap]

## Copy

Copy => Copy(dest, source) -> Copiedcount

## Append creates lots of problems

Append => append(sl,items...) -> returns new slice and change
source slice as well.

Changing source depends on cap/len

1. problem Code. Unexpected Results

```golang
    s1 := []int{}
    s1 = append(s1, 1)
    s1 = append(s1, 2)
    s1 = append(s1, 3)
    s2 := append(s1, 4)
    s3 := append(s1, 5)

    fmt.Println(s1, s2, s3)
    //s1 => [1,2,3]
    //s2 => [1,2,3,5] it should be [1,2,3,4] where did 4 go .
    //s3 => [1,2,3,5]

	s1[0] = 11
	fmt.Println(s1, s2, s3)

    //s1 => [11,2,3]
    //s2 => [11,2,3,5]
    //s3 = [11,2,3,5]

```

2. Explanation of Above Code

```golang
    s1 := []int{}         //Zero Initalize

	s1 = append(s1, 1)    //len = 1, cap = 1, new array

    s1 = append(s1, 2)    //len = 2, cap = 2, new array

    s1 = append(s1, 3)   // len = 3, cap = 3, new array

    s2 := append(s1, 4)  // len = 4, cap 4, new array, changes s1, s1 now => len 3, cap 4. if print s1 => [1,2,3] but s2 append added 4 its hidden in last. due to len 3 and cap 4 is hidden. because append modifies source and return both

    s3 := append(s1, 5) //len = 4, cap 4 old array , copies s1 to s3 so 1,2,3 and appends . while appending cap is 4 so no new array so 5 is replaced in last element . it replaces 4 to 5. Since s1,s2,s3 all points same array now it has confused state. 1,2,3,5 and 4 is gone.

    fmt.Println(s1, s2, s3)
    //s1 => [1,2,3]
    //s2 => [1,2,3,5] it should be [1,2,3,4] where did 4 go .
    //s3 => [1,2,3,5]

	s1[0] = 11
	fmt.Println(s1, s2, s3)

    //if we change s1[0] or s2[0] or s3[0] changes everything because all are pointing to same array.

    //s1 => [11,2,3]
    //s2 => [11,2,3,5]
    //s3 = [11,2,3,5]

```

### Why does this happens

1. Capacity, length, Underlying array combination of these plays major role.

### Tips to use slice append properly

1. append and save it to same variable .
2. dont use empty slices allocate proper capacity improves perf
3. make([]int,5,len(oldslice)) will make life better perf wise and result wise.

## Slice empty and Nil confusion

```golang
  len(s) == 0  //empty check
  s == nil     //nil check
```

```golang
var s []string       // empty = true, nil = true
s = []string(nil)    // empty = true, nil = true
s = []string{}       // empty = true, nil = false
s = make([]string,0) // empty = true , nil = false
```

# Start Project in golang

> go mod init github.com/prtamil/first
> go get dependencies //Dependeis gen

go.mod, go.sum :go get generates.

go.mod => Ingredient
go.sum => Instructions.

go mod commands manage project
go get commands add dependency

# Local Depedency
```sh
>  go mod edit -replace example.com/duba=../duba 
>  # Replaces Remote module to local module.
```
use go mod edit -replace <orig module namespace>=<local dep>

This is how we do local dependency
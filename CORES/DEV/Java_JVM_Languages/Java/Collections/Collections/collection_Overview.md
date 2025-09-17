#  Collection

## Interfaces

| Interface | Methods                          |
| --------- | -------------------------------- |
| Iterator  | hasNext, next, remove            |
| Iterable  | iterator, splitIterator, forEach | 

## Classes
```mermaid
classDiagram  
    Collection <|-- List  
    Collection <|-- Queue  
    Collection <|-- Set  
    List <|-- ArrayList
    List <|-- LinkedList
    Queue <|-- LinkedList
    Queue <|-- Deque
    Set <|-- HashSet
    Set <|-- TreeSet
```

```mermaid
classDiagram
	Map <|-- HashMap
	Map <|-- TreeMap
```
## Collection common Operations
1. add
2. remove
3. isEmpty, size
4. clear
5. contains
6. removeIf(lambdafn)
7. forEach, for(el:cl), iterator
8. equals


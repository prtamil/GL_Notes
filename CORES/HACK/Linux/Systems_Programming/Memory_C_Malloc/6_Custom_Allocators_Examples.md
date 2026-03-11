can you give example codes for String Arrays dynamic

1. Arena allocator
2. Bumb allocator
3. Stack allocator
4. Pool allocator
5. Free List Allocator
6. Slab Allocator

Let’s implement dynamic string arrays using each of the allocators you asked for—arena, bump, stack, pool, free list, and slab—in pure C. A "dynamic string array" here will mean an array of char* pointers, where each pointer points to a dynamically allocated string, and the array itself can grow. Since each allocator has unique traits, I’ll adapt the implementation to fit its strengths and quirks, keeping the examples simple but functional. I’ll assume we’re storing strings like "apple", "banana", etc., and provide a way to add strings and clean up. Here we go!

---

## 1. Arena Allocator

Idea: One big block for both the array and string data, freed all at once.

```c
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    char *base;    // Arena memory
    size_t size;   // Total size
    size_t offset; // Current position
} Arena;

typedef struct {
    char **strings; // Array of string pointers
    size_t count;   // Number of strings
    Arena *arena;   // Arena for memory
} StringArray;

Arena arena_create(size_t size) {
    Arena a = { malloc(size), size, 0 };
    return a;
}

void *arena_alloc(Arena *a, size_t size) {
    if (a->offset + size > a->size) return NULL;
    void *ptr = a->base + a->offset;
    a->offset += size;
    return ptr;
}

void arena_free(Arena *a) {
    free(a->base);
}

StringArray str_array_create(Arena *a, size_t initial_capacity) {
    StringArray sa = {0};
    sa.arena = a;
    sa.strings = arena_alloc(a, initial_capacity * sizeof(char*));
    return sa;
}

void str_array_add(StringArray *sa, const char *str) {
    size_t len = strlen(str) + 1;
    char *copy = arena_alloc(sa->arena, len);
    if (copy) {
        strcpy(copy, str);
        sa->strings[sa->count++] = copy;
    }
}

int main() {
    Arena a = arena_create(1024);
    StringArray sa = str_array_create(&a, 10);
    str_array_add(&sa, "apple");
    str_array_add(&sa, "banana");
    for (size_t i = 0; i < sa.count; i++) {
        printf("%s\n", sa.strings[i]); // apple, banana
    }
    arena_free(&a); // Frees everything
    return 0;
}
```

Notes: The array and strings live in the same contiguous arena. No resizing—capacity is fixed at creation. Freeing the arena wipes it all.

## 2. Bump Allocator

Idea: Linear allocation with a reset option, no individual frees.


```c
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    char *base;    // Memory block
    char *current; // Bump pointer
    size_t size;   // Total size
} Bump;

typedef struct {
    char **strings;
    size_t count;
    size_t capacity;
    Bump *bump;
} StringArray;

Bump bump_create(size_t size) {
    Bump b = {0};
    b.base = b.current = malloc(size);
    b.size = size;
    return b;
}

void *bump_alloc(Bump *b, size_t size) {
    if ((b->current + size) > (b->base + b->size)) return NULL;
    void *ptr = b->current;
    b->current += size;
    return ptr;
}

void bump_reset(Bump *b) {
    b->current = b->base;
}

void bump_free(Bump *b) {
    free(b->base);
}

StringArray str_array_create(Bump *b, size_t capacity) {
    StringArray sa = { bump_alloc(b, capacity * sizeof(char*)), 0, capacity, b };
    return sa;
}

void str_array_add(StringArray *sa, const char *str) {
    if (sa->count >= sa->capacity) return; // No resizing
    size_t len = strlen(str) + 1;
    char *copy = bump_alloc(sa->bump, len);
    if (copy) {
        strcpy(copy, str);
        sa->strings[sa->count++] = copy;
    }
}

int main() {
    Bump b = bump_create(1024);
    StringArray sa = str_array_create(&b, 10);
    str_array_add(&sa, "apple");
    str_array_add(&sa, "banana");
    for (size_t i = 0; i < sa.count; i++) {
        printf("%s\n", sa.strings[i]);
    }
    bump_reset(&b); // Reset for reuse
    str_array_add(&sa, "cherry"); // Overwrites old data
    printf("%s\n", sa.strings[0]); // cherry
    bump_free(&b);
    return 0;
}
```

Notes: Like arena, but bump_reset lets you reuse the block without freeing. No dynamic growth here—fixed capacity.

---
## 3. Stack Allocator

Idea: LIFO order—push strings, pop them off in reverse.


```c
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    char *base;
    char *top;
    size_t size;
} Stack;

typedef struct {
    char **strings;
    size_t count;
    size_t capacity;
    Stack *stack;
} StringArray;

Stack stack_create(size_t size) {
    Stack s = { malloc(size), NULL, size };
    s.top = s.base;
    return s;
}

void *stack_push(Stack *s, size_t size) {
    if ((s->top + size) > (s->base + s->size)) return NULL;
    void *ptr = s->top;
    s->top += size;
    return ptr;
}

void stack_pop(Stack *s, size_t size) {
    if (s->top - size >= s->base) s->top -= size;
}

void stack_free(Stack *s) {
    free(s->base);
}

StringArray str_array_create(Stack *s, size_t capacity) {
    StringArray sa = { stack_push(s, capacity * sizeof(char*)), 0, capacity, s };
    return sa;
}

void str_array_push(StringArray *sa, const char *str) {
    if (sa->count >= sa->capacity) return;
    size_t len = strlen(str) + 1;
    char *copy = stack_push(sa->stack, len);
    if (copy) {
        strcpy(copy, str);
        sa->strings[sa->count++] = copy;
    }
}

void str_array_pop(StringArray *sa) {
    if (sa->count > 0) {
        sa->count--;
        stack_pop(sa->stack, strlen(sa->strings[sa->count]) + 1);
    }
}

int main() {
    Stack s = stack_create(1024);
    StringArray sa = str_array_create(&s, 10);
    str_array_push(&sa, "apple");
    str_array_push(&sa, "banana");
    printf("%s\n", sa.strings[1]); // banana
    str_array_pop(&sa); // Removes "banana"
    printf("%s\n", sa.strings[0]); // apple
    stack_free(&s);
    return 0;
}
```

Notes: You can pop strings off, but only in reverse order. Fixed capacity, stack-like discipline.

---

## 4. Pool Allocator

Idea: Pre-allocated slots for strings of a fixed max length.


```c
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define MAX_STR_LEN 32

typedef struct {
    char *pool;    // Contiguous memory for strings
    int *free;     // Free slot flags
    size_t capacity;
} Pool;

typedef struct {
    char **strings;
    size_t count;
    Pool *pool;
} StringArray;

Pool pool_create(size_t capacity) {
    Pool p = { malloc(capacity * MAX_STR_LEN), malloc(capacity * sizeof(int)), capacity };
    for (size_t i = 0; i < capacity; i++) p.free[i] = 1; // 1 = free
    return p;
}

char *pool_alloc(Pool *p) {
    for (size_t i = 0; i < p->capacity; i++) {
        if (p->free[i]) {
            p->free[i] = 0;
            return p->pool + (i * MAX_STR_LEN);
        }
    }
    return NULL;
}

void pool_free(Pool *p, char *ptr) {
    size_t index = (ptr - p->pool) / MAX_STR_LEN;
    p->free[index] = 1;
}

void pool_destroy(Pool *p) {
    free(p->pool);
    free(p->free);
}

StringArray str_array_create(Pool *p, size_t capacity) {
    StringArray sa = { malloc(capacity * sizeof(char*)), 0, p };
    return sa;
}

void str_array_add(StringArray *sa, const char *str) {
    char *slot = pool_alloc(sa->pool);
    if (slot) {
        strncpy(slot, str, MAX_STR_LEN - 1);
        slot[MAX_STR_LEN - 1] = '\0';
        sa->strings[sa->count++] = slot;
    }
}

int main() {
    Pool p = pool_create(10);
    StringArray sa = str_array_create(&p, 10);
    str_array_add(&sa, "apple");
    str_array_add(&sa, "banana");
    printf("%s, %s\n", sa.strings[0], sa.strings[1]);
    pool_destroy(&p);
    free(sa.strings);
    return 0;
}
```

Notes: Strings are fixed-size (e.g., 32 chars). Pool reuses slots, but the array itself uses malloc for simplicity.

---

## 5. Free List Allocator

Idea: Linked list of free blocks, reusable for variable-sized strings.


```c
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

typedef struct Block {
    struct Block *next;
    size_t size;
} Block;

typedef struct {
    char *base;
    Block *free_list;
    size_t size;
} FreeList;

typedef struct {
    char **strings;
    size_t count;
    FreeList *fl;
} StringArray;

FreeList fl_create(size_t size) {
    FreeList fl = { malloc(size), NULL, size };
    fl.free_list = (Block*)fl.base;
    fl.free_list->next = NULL;
    fl.free_list->size = size - sizeof(Block);
    return fl;
}

void *fl_alloc(FreeList *fl, size_t size) {
    Block *prev = NULL, *curr = fl->free_list;
    while (curr && curr->size < size) {
        prev = curr;
        curr = curr->next;
    }
    if (!curr) return NULL;
    if (prev) prev->next = curr->next;
    else fl->free_list = curr->next;
    return (char*)curr + sizeof(Block);
}

void fl_free(FreeList *fl, void *ptr) {
    Block *b = (Block*)((char*)ptr - sizeof(Block));
    b->next = fl->free_list;
    fl->free_list = b;
}

void fl_destroy(FreeList *fl) {
    free(fl->base);
}

StringArray str_array_create(FreeList *fl, size_t capacity) {
    StringArray sa = { malloc(capacity * sizeof(char*)), 0, fl };
    return sa;
}

void str_array_add(StringArray *sa, const char *str) {
    size_t len = strlen(str) + 1;
    char *copy = fl_alloc(sa->fl, sizeof(Block) + len);
    if (copy) {
        strcpy(copy, str);
        sa->strings[sa->count++] = copy;
    }
}

int main() {
    FreeList fl = fl_create(1024);
    StringArray sa = str_array_create(&fl, 10);
    str_array_add(&sa, "apple");
    str_array_add(&sa, "banana");
    printf("%s, %s\n", sa.strings[0], sa.strings[1]);
    fl_free(&fl, sa.strings[0]); // Free "apple"
    str_array_add(&sa, "cherry"); // Reuses space
    printf("%s, %s\n", sa.strings[1], sa.strings[2]);
    fl_destroy(&fl);
    free(sa.strings);
    return 0;
}
```

Notes: Supports variable-sized strings, with explicit freeing and reuse via the free list.

---

## 6. Slab Allocator

Idea: Multiple pools (slabs) for different string sizes.


```c
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define SLAB_SIZE 32 // One slab for 0-32 bytes

typedef struct {
    char *slab;
    int *free;
    size_t capacity;
} Slab;

typedef struct {
    char **strings;
    size_t count;
    Slab *slab;
} StringArray;

Slab slab_create(size_t capacity) {
    Slab s = { malloc(capacity * SLAB_SIZE), malloc(capacity * sizeof(int)), capacity };
    for (size_t i = 0; i < capacity; i++) s.free[i] = 1;
    return s;
}

char *slab_alloc(Slab *s) {
    for (size_t i = 0; i < s->capacity; i++) {
        if (s->free[i]) {
            s->free[i] = 0;
            return s->slab + (i * SLAB_SIZE);
        }
    }
    return NULL;
}

void slab_free(Slab *s, char *ptr) {
    size_t index = (ptr - s->slab) / SLAB_SIZE;
    s->free[index] = 1;
}

void slab_destroy(Slab *s) {
    free(s->slab);
    free(s->free);
}

StringArray str_array_create(Slab *s, size_t capacity) {
    StringArray sa = { malloc(capacity * sizeof(char*)), 0, s };
    return sa;
}

void str_array_add(StringArray *sa, const char *str) {
    char *slot = slab_alloc(sa->slab);
    if (slot) {
        strncpy(slot, str, SLAB_SIZE - 1);
        slot[SLAB_SIZE - 1] = '\0';
        sa->strings[sa->count++] = slot;
    }
}

int main() {
    Slab s = slab_create(10);
    StringArray sa = str_array_create(&s, 10);
    str_array_add(&sa, "apple");
    str_array_add(&sa, "banana");
    printf("%s, %s\n", sa.strings[0], sa.strings[1]);
    slab_free(&s, sa.strings[0]); // Free "apple"
    str_array_add(&sa, "cherry"); // Reuses slot
    printf("%s, %s\n", sa.strings[1], sa.strings[2]);
    slab_destroy(&s);
    free(sa.strings);
    return 0;
}
```

Notes: Simplified to one slab size (32 bytes). Real slab allocators would have multiple slabs for different sizes.

---

## Key Observations

- Arena/Bump: Fast, simple, no individual frees (bump can reset).
    
- Stack: LIFO order, explicit popping.
    
- Pool/Slab: Fixed-size slots, reusable; slab could scale to multiple sizes.
    
- Free List: Flexible sizes, explicit freeing, more overhead.
    
- Dynamic Growth: These examples use fixed capacity for simplicity. For true dynamism, you’d need to reallocate the strings array (e.g., with realloc), separate from the allocator’s string storage.
    

Which one fits your use case? Want to tweak any for resizing or a specific twist? Let me know!
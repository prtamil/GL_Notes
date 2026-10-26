### Deletion strategies in hash tables

In **open addressing**, deletion is tricky because simply marking a slot **empty** can break the probing chain and cause existing keys to become unreachable.

Common strategies:

- **Tombstone / dummy** — mark the slot as deleted. Lookup continues probing through it, while insertion can reuse it. Simple, but too many tombstones increase probe length.
    
- **Backward-shift deletion** — after deletion, shift subsequent entries backward when safe, preserving the probing chain without tombstones.
    
- **Rehash / rebuild** — periodically rebuild the table, removing accumulated deleted slots and restoring efficient probing.
    

For interviews, remember:

```text
Delete
  ↓
Don't simply make slot EMPTY
  ↓
Tombstone / shift / rebuild
  ↓
Preserve probing chain
```

**Complexity:** deletion is typically **O(1) average** in hash tables, but can become **O(n)** in the worst case depending on probing and deletion strategy.
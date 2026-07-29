This is the version I'd put in notes.

```text
===========================
COUNTING USING TREES
===========================

1) ADD = Count BRANCHES
-----------------------

One decision.
Choose ONE alternative.

          Start
        /   |   \
     Train Flight Bus
       15     2    10

Total choices
= 15 + 2 + 10
= 27

Memory:
"How many branches leave this node?"


2) MULTIPLY = Count PATHS
-------------------------

Multiple decisions.
Build ONE complete outcome.

             Start
            /     \
        Shirt1   Shirt2
         /  \      /  \
      Pant1 Pant2 Pant1 Pant2

Complete paths:

Shirt1 → Pant1
Shirt1 → Pant2
Shirt2 → Pant1
Shirt2 → Pant2

Total paths
= 2 × 2
= 4

Memory:
"How many complete root-to-leaf paths exist?"


===========================
ONE-LINE RULE
===========================

One Decision
    ↓
Count BRANCHES
    ↓
ADD

Multiple Decisions
    ↓
Count COMPLETE PATHS
    ↓
MULTIPLY
```

⭐ **One tiny correction to make this universally true:** The multiplication rule isn't just "multiple decisions"—it's **multiple sequential decisions**. That's why we count **root-to-leaf paths** in the tree. This wording will stay correct even for advanced probability and AI decision trees.

### One sentence to remember forever

> **ADD counts choices at a node. MULTIPLY counts journeys through the tree.**

I think that's the simplest and deepest intuition for counting. Once you see a problem as a tree, you naturally know whether you're counting **branches** (alternatives) or **root-to-leaf paths** (complete outcomes).
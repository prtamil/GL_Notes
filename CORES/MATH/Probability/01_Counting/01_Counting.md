```txt
                 COUNTING

      BUILD                     PICK
        │                         │
        ▼                         ▼
   MULTIPLY                  Order matter?
                                  │
                     ┌────────────┴────────────┐
                     ▼                         ▼
              PERMUTATION              COMBINATION
               (Position)                 (Group)

Alternative choices only
        │
        ▼
      ADD
```

```txt
Q1. Am I BUILDING one object?
    YES → Multiply

Q2. Am I choosing ONE from alternatives?  (choose one brach from alternatives)
    YES → Add

Q3. Am I PICKING from a collection?
    YES →
        Order matters? → Permutation
        Order doesn't? → Combination
```

```txt
BUILD  → Multiply

ALTERNATIVES → Add

POSITIONS → Permutation

GROUPS → Combination
```
## Quick intuition for each

### ① MULTIPLY (Build)

```
Need ALL parts.

CPU + RAM + SSD
↓

Computer
```

Examples

- 🍕 Pizza
- 👕 Outfit
- 🍔 Meal
- 💻 Computer
- 🔐 Password

**Keyword:** Build

---

### ② ADD (OR) — Alternative Paths

**Intuition:**  
You are standing at **one decision point** and must choose **exactly one** alternative.

```
                 Start
                   │
        ┌──────────┼──────────┐
        │          │          │
      Train     Flight      Bus
      (15)        (2)        (10)
```

You can travel by:

- Train **OR**
    
- Flight **OR**
    
- Bus
    

You cannot choose more than one path for this journey.

Total possible travel options:

```
15 + 2 + 10 = 27
```

**Why Add?**

Each branch represents a different possible choice. Since you choose **one branch only**, the total number of possibilities is the **sum** of all branches.

```
Total possibilities
=
Train options
+
Flight options
+
Bus options
```

### More OR Examples

- Coffee **OR** Tea **OR** Milk
    
- Laptop **OR** Tablet **OR** Desktop
    
- Windows **OR** Linux **OR** macOS
    
- Red **OR** Blue **OR** Green shirt (buying one shirt)
    
- Bus **OR** Train **OR** Flight
    

**Memory Keyword:** **Alternatives**

**Mental Picture:**

```
One Decision
      │
Choose ONE branch
      │
     ADD
```

---

### ③ PERMUTATION

```
Same people
Different positions

Gold Silver Bronze

Alice Bob Charlie

≠

Bob Alice Charlie
```

Examples

- Race ranking
- Seating
- Password characters
- PIN digits
- President & Vice President

**Keyword:** Position

---

### ④ COMBINATION

```
Same group

Alice Bob Charlie

=

Charlie Alice Bob
```

Examples

- Committee
- Team
- Lottery numbers
- Choose 5 cards
- Choose 3 students

**Keyword:** Group

If you can remember just these **four words**:

- **Build**
- **Alternatives**
- **Position**
- **Group**

you'll be able to identify the right approach for most beginner counting problems.
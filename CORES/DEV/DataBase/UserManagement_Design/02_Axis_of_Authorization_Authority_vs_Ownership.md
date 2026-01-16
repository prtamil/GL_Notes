## Axis 1 and Axis 2: A Simple Mental Model for Database Authorization

Good authorization design is not about complexity — it’s about **separation**.

Every serious system (including ERPs) works because it separates **authority** from **responsibility**.  
These are two different questions, and confusing them is the root of most auth bugs.

---

### Axis 1 — Authority (RBAC: Roles & Permissions)

Axis 1 answers a timeless question:

> **“What is this user allowed to do, in general?”**

This is **policy**.

Roles and permissions describe **organizational intent**, not daily work.  
They change slowly, usually through admin decisions or compliance rules.

Examples of Axis 1 thinking:

- Can a user process orders?
- Can a dealer assign work?
- Can an admin manage users?
    

Notice something important:

- These questions make sense **without any specific record**
- No order ID, no proposal ID, no dealer ID
    

That’s the giveaway.

Axis 1 is implemented using:

- Users
- Roles
- Permissions
- Role ↔ Permission mappings
- User ↔ Role mappings
    

Once designed correctly, Axis 1 almost never needs redesign.

**Mental shortcut:**  
Axis 1 answers **“Can I ever do this?”**

---

### Axis 2 — Responsibility (Ownership, Scope, State)

Axis 2 answers a different question:

> **“Which specific data can this user act on right now?”**

This is **business reality**.

Ownership and responsibility change constantly:

- Orders get assigned
- Proposals move through states
- Users switch tasks
- Data visibility shifts
    

Examples of Axis 2 thinking:

- Which orders are assigned to this processor?
- Does this proposal belong to this dealer?
- Is this record still pending?
    

Notice:

- These questions **always involve specific data**
- They always require IDs, relationships, or state
    

Axis 2 is implemented using:

- Ownership columns (dealer_id, owner_user_id)
- Assignment tables
- Status fields
- Domain relationships
    

Axis 2 is not configuration — it’s **live data**.

**Mental shortcut:**  
Axis 2 answers **“Which ones?”**

---

### How the Two Axes Work Together

Authorization is never one axis alone.

The real rule is always:

> **A user may perform an action  
> if they have permission (Axis 1)  
> and the data is within their scope (Axis 2).**

Permissions without ownership are dangerous.  
Ownership without permissions is meaningless.

They are independent, and that’s why they scale.

---

### Why This Model Prevents Surprises

- You don’t encode business logic into permissions
- You don’t create new roles for every situation
- You don’t redesign tables when workflows change
- You don’t hardcode exceptions
    

Policy stays stable.  
Business moves fast.  
The system stays sane.

---

### Final Mental Anchor (remember this)

> **Axis 1 decides power.  
> Axis 2 decides reach.**

If you ask:

- _“Can I?”_ → Axis 1
- _“Which one?”_ → Axis 2
    

If you keep this separation, your database authorization design will remain clean, flexible, and ERP-grade for years.
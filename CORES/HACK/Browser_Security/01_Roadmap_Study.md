# Browser & Web Security Learning Roadmap

## LEVEL 0 — Foundations (must be solid)

**Goal:** Understand _what the browser is protecting_

### Study:

- What is a **request / response**
- HTTP methods (GET, POST, PUT, DELETE)
- Headers vs body
- Stateless nature of HTTP
    

### Outcome:

You can read raw HTTP and know what’s happening.

---

## LEVEL 1 — Identity & State (core to everything)

**Goal:** Understand how users stay logged in

### Study:

- Cookies (Domain, Path, Secure, HttpOnly, SameSite)
- Sessions vs JWT
- How browsers attach cookies
- Logout mechanics
    

### Outcome:

You understand **why CSRF exists**.

👉 **Do not move forward until cookies feel boring.**

---

## LEVEL 2 — Origin & Isolation (the security boundary)

**Goal:** Understand _who can access what_

### Study:

- Origin (scheme + host + port)
- Same-Origin Policy (SOP)
- Storage isolation (cookies, localStorage, IndexedDB)
- iframe basics
    

### Outcome:

You know **what JS can and cannot read**.

---

## LEVEL 3 — Cross-Origin Interaction (controlled sharing)

**Goal:** Understand _how SOP is relaxed_

### Study:

- CORS headers
- Simple vs complex requests
- Preflight (`OPTIONS`)
- `credentials: include`
    

### Outcome:

You stop guessing why “CORS errors” happen.

---

## LEVEL 4 — Acting vs Reading (the CSRF realization)

**Goal:** Understand unintended actions

### Study:

- CSRF root cause
- Form-based CSRF
- JS-based CSRF
- CSRF tokens
- SameSite cookies
    

### Outcome:

You understand the **difference between reading data and triggering actions**.

This is the **big mental jump**.

---

## LEVEL 5 — Script Injection (the most dangerous class)

**Goal:** Understand how attackers execute code

### Study:

- XSS (stored, reflected, DOM)
- Why XSS bypasses SOP
- HttpOnly vs non-HttpOnly cookies
    

### Outcome:

You understand why **XSS > CSRF in severity**.

---

## LEVEL 6 — Execution Control (modern defenses)

**Goal:** Prevent code execution

### Study:

- Content Security Policy (CSP)
- Nonces & hashes
- Trusted Types (conceptually)
    

### Outcome:

You know how modern apps stop XSS.

---

## LEVEL 7 — Transport & Network Safety

**Goal:** Protect data in transit

### Study:

- HTTPS / TLS
- Mixed content
- HSTS
    

### Outcome:

You know why HTTPS is mandatory, not optional.

---

## LEVEL 8 — Advanced Isolation (browser internals)

**Goal:** Understand defense-in-depth

### Study:

- Site Isolation
- Process models
- Spectre/Meltdown (high-level)
- COOP / COEP
    

### Outcome:

You understand **why browsers isolate memory**, not just JS.

---

## LEVEL 9 — UI & User Deception Attacks

**Goal:** Protect user interaction

### Study:

- Clickjacking
- X-Frame-Options
- CSP `frame-ancestors`
    

### Outcome:

You understand how attackers trick users visually.

---

## LEVEL 10 — Real-World Mapping

**Goal:** Connect theory to reality

### Study:

- OWASP Top 10 (web)
- Real CVEs
- Browser bug reports (read-only)
    

### Outcome:

You can reason about security, not memorize rules.

---

# The golden rule (do not skip)

`Cookies → Origin → SOP → CORS → CSRF → XSS → CSP → Isolation`

If this order is respected, confusion disappears.

---

# How to study each level (practical advice)

For every topic:

1. Read **concept**
2. Write a **tiny example**
3. Break it intentionally
4. Fix it
    

Security is learned by _failure_, not reading.

---

# Final coaching advice (important)

- Do not rush advanced topics
    
- If CORS feels confusing, **you skipped origin**
- If CSRF feels confusing, **you skipped cookies**
- If CSP feels confusing, **you skipped XSS**
    

This is non-negotiable.
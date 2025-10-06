# Top 25 skills & traits (psych + tech)

1. **Deliberate programming craft**
    
    - Why: Red-team tooling, exploit PoCs and reliable lab automation require high-quality code (not quick scripts).
        
    - Target: _Expert_ in C/C++ and _Advanced_ in Python/C#/.NET and PowerShell.
        
    - Practice/KPIs: ship 1 non-trivial tool per quarter; code reviews with linters and tests.
        
    - Effort: 4–8 hr/week (ongoing).
        
2. **Systems internals fluency (Windows + Linux)**
    
    - Why: You must know OS behaviour to find/instrument vulnerabilities and bypass detection.
        
    - Target: _Advanced → Expert_ for Windows kernel and Linux kernel basics.
        
    - Practice/KPIs: explain and diagram process/IPC/auth flows; reproduce experiments from Windows Internals or Linux kernel docs.
        
    - Effort: 3–6 hr/week for 6–12 months to reach strong fluency.
        
3. **Networking & TCP/IP practical skills**
    
    - Why: Lateral movement, pivoting, C2, detection analysis rely on networking knowledge.
        
    - Target: _Mid → Advanced_ (TCP, TLS, routing, ports, capture analysis).
        
    - Practice/KPIs: read/interpret pcap; build simple custom C2 over raw sockets; complete packet-capture forensic exercises.
        
    - Effort: 2–4 hr/week for 3–6 months.
        
4. **Active Directory mastery**
    
    - Why: The dominant enterprise target — understanding AD is non-negotiable for red teamers.
        
    - Target: _Advanced_ (Kerberos, delegation, GPO, trust relationships).
        
    - Practice/KPIs: run full AD lab compromises; document escalation paths; BloodHound fluency.
        
    - Effort: 4–6 hr/week for first 6 months, then maintenance.
        
5. **Exploit development basics**
    
    - Why: To convert findings into impact and to understand mitigation/EDR behavior.
        
    - Target: _Intermediate → Advanced_ (memory corruption, ROP basics).
        
    - Practice/KPIs: write small exploits, reproduce public exploit writeups.
        
    - Effort: 3–6 hr/week for 6–12 months.
        
6. **Reverse engineering (binaries)**
    
    - Why: Malware analysis, rootkit detection, and vulnerability verification.
        
    - Target: _Intermediate_ (Ghidra/IDA, PE format, x86/x64).
        
    - Practice/KPIs: reverse 1 binary/month; produce IOC + detection suggestions.
        
    - Effort: 3–5 hr/week.
        
7. **Kernel & driver engineering**
    
    - Why: Deep persistence, stealth, and high-value research opportunities.
        
    - Target: _Advanced_ (driver dev, DDK, debugging, fuzzing).
        
    - Practice/KPIs: build driver PoCs, fuzz drivers, responsibly disclose bugs.
        
    - Effort: 3–6 hr/week.
        
8. **PowerShell offensive/defensive mastery**
    
    - Why: Most Windows post-exploitation runs through PowerShell; defenders instrument it heavily.
        
    - Target: _Advanced_ (pipeline, objects, remoting, constrained language, AMSI bypass awareness).
        
    - Practice/KPIs: write 10 robust modules; demonstrate detection evasion/telemetry tradeoffs in lab.
        
    - Effort: 2–4 hr/week.
        
9. **Telemetry & detection engineering (ETW/Sysmon/Logs)**
    
    - Why: To understand how attacks are seen and how to avoid/trigger/log them responsibly.
        
    - Target: _Advanced_ (craft Sigma rules, analyze EDR alerts).
        
    - Practice/KPIs: write detection rules for 10 techniques; validate in lab.
        
    - Effort: 2–4 hr/week.
        
10. **Fuzzing & vulnerability discovery**
    
    - Why: Source of original research and CVEs. Driver/parse fuzzing is high-value.
        
    - Target: _Intermediate → Advanced_ (AFL, libFuzzer, harness design).
        
    - Practice/KPIs: fuzz one target weekly; triage crashes and reproduce root cause.
        
    - Effort: 3–6 hr/week.
        
11. **C2 & post-exploitation architecture**
    
    - Why: Building reliable, stealthy, modular ops frameworks differentiates professional red teams.
        
    - Target: _Advanced_ (OPSEC-friendly, modular agents).
        
    - Practice/KPIs: architect and test a minimal C2; instrument telemetry and sandbox detection.
        
    - Effort: 3–5 hr/week.
        
12. **Cloud & container security (DevSecOps)**
    
    - Why: Modern environments include cloud, k8s, container escape vectors and persistence options.
        
    - Target: _Intermediate → Advanced_ (K8s misconfigurations, container breakout basics).
        
    - Practice/KPIs: run capture-from-container exercises; practice k8s privilege escalation.
        
    - Effort: 2–4 hr/week.
        
13. **OpSec & tradecraft discipline**
    
    - Why: Running realistic, professional ops requires OPSEC: compartmentalization, pivoting, plausible activities.
        
    - Target: _Advanced_ (procedures, staging, comms hygiene).
        
    - Practice/KPIs: document op plan; simulate clean-up and evidence trails in lab.
        
    - Effort: 1–2 hr/week (process work).
        
14. **Measurement & experiment design**
    
    - Why: Science-like rigor in testing detection, defenses, and exploitation increases credibility.
        
    - Target: _Intermediate_ (hypothesis → test → reproducible results).
        
    - Practice/KPIs: run controlled A/B tests of technique vs EDR.
        
    - Effort: 1–2 hr/week.
        
15. **Communication & technical writing**
    
    - Why: Clear reports, blog posts, and CVEs spread your work and get you recognized.
        
    - Target: _Advanced_ (client-level reports and public writeups).
        
    - Practice/KPIs: publish 1 thorough writeup per quarter; prepare polished pentest reports.
        
    - Effort: 2–4 hr/week.
        
16. **Teaching / Presentation skills**
    
    - Why: Talks/books/courses are the fastest route to reputation and clarity of thought.
        
    - Target: _Intermediate → Advanced_ (slide decks, demos, Q&A).
        
    - Practice/KPIs: submit CFPs; deliver local workshops; record webinars.
        
    - Effort: 1–3 hr/week prep; more when creating a talk.
        
17. **Analytical curiosity & pattern recognition**
    
    - Why: Core to finding subtle attack paths and creative exploit chains.
        
    - Target: _High_ (mental habit rather than credential).
        
    - Practice/KPIs: daily micro-exercises (e.g., analyze odd logs), weekly puzzle/CTF.
        
    - Effort: 30–60 min/day.
        
18. **Grit / persistence / tolerance for frustration**
    
    - Why: Deep research and exploit dev require many failed attempts before breakthroughs.
        
    - Target: _High_ (learn to iterate and keep momentum).
        
    - Practice/KPIs: track attempt counts + learning from failures; adopt timeboxing.
        
    - Effort: ongoing mindset work; schedule rest to avoid burnout.
        
19. **Attention to detail & documentation**
    
    - Why: Small mistakes cause correctness/security problems; good docs make research reusable.
        
    - Target: _High_ (habitual).
        
    - Practice/KPIs: every experiment has README + reproducible steps.
        
    - Effort: 1–2 hr/week.
        
20. **Ethics & legal literacy**
    
    - Why: Protects you legally and preserves career; responsible disclosure is essential.
        
    - Target: _Intermediate_ (know ROE, NDA basics, disclosure timelines).
        
    - Practice/KPIs: set checklist for any real-world testing; use consent forms in engagements.
        
    - Effort: initial study 10–20 hrs, then occasional refresh.
        
21. **Project management & delivery**
    
    - Why: Running engagements & publishing consistent research requires planning and delivery skills.
        
    - Target: _Intermediate_ (agile sprints, milestones, ticketing).
        
    - Practice/KPIs: plan quarter projects with milestones; hit 80% of milestones.
        
    - Effort: 1–3 hr/week.
        
22. **Networking (personal/professional)**
    
    - Why: Visibility & collaborations require relationships: conferences, GitHub, peers, vendors.
        
    - Target: _Intermediate → Advanced_ (authorship, collaborations).
        
    - Practice/KPIs: attend 2 conferences/year; contribute upstream to 2 projects/year.
        
    - Effort: variable — 2–4 hr/week during active networking phases.
        
23. **Tooling & automation (infra-as-code)**
    
    - Why: Reproducible labs, deployment of C2, fuzzing infra requires automation.
        
    - Target: _Advanced_ (Terraform, Ansible, Docker, Vagrant).
        
    - Practice/KPIs: publish automated lab repos; CI for tests.
        
    - Effort: 2–4 hr/week.
        
24. **Business & consulting skills**
    
    - Why: If you want to found a shop or consult, you need scoping, pricing, sales basics, and legal awareness.
        
    - Target: _Intro → Intermediate_ (learn to write SOWs and price engagements).
        
    - Practice/KPIs: draft 3 SOW templates and a simple pricing model.
        
    - Effort: 1–2 hr/week.
        
25. **Public-facing productization (writing/tools/courses)**
    
    - Why: To become “world-known” you must publish a durable artifact: book, signature tool, or course.
        
    - Target: _Intermediate_ to start producing one major artifact in 1–2 years.
        
    - Practice/KPIs: roadmap → MVP → public release (tool/blog/course).
        
    - Effort: 4–8 hr/week while building a major artifact.
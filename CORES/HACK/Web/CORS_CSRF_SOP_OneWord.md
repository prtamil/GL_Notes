Modern web security carefully separates **reading data** from **performing actions**. Browsers protect sensitive information using **Same-Origin Policy (SOP)** and **Cross-Origin Resource Sharing (CORS)**. SOP ensures that JavaScript can only read responses from the same origin, while CORS allows servers to selectively relax this rule for trusted origins. This protects against data leaks and unauthorized access.

At the same time, browsers **automatically send requests** — including cookies and other credentials — to matching domains. This convenience is necessary for seamless user experiences but introduces the risk of **Cross-Site Request Forgery (CSRF)**. CSRF exploits the fact that the browser cannot know the user’s intent and may send credentials to an untrusted site.

To mitigate this, servers implement **CSRF protections** such as tokens or rely on **SameSite cookie rules**, which prevent sensitive credentials from being sent cross-site without explicit user action. In this way, the web enforces a clear separation: **browsers control who can read**, while **CSRF protections control who can act**.

**In short:**

> Browser protects reading with SOP/CORS; it sends requests automatically, but CSRF protections stop sensitive credentials (cookies) from being sent cross-site without user intent.


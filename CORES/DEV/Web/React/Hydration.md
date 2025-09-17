Hydration or rehydration is a technique in which client-side js converts a static HTML web page delivered thru static hosting or ssr into dynamic webpage by attaching event handlers to the HTML elements.

React v16.0 introduces hydrate() function.

Variants

1. Streaming SSR
   1. send HTML in chunks to browser progressivly render it.
2. Progressive rehydration.
   1. individual pieces of server rendered app are booted-up over time. rather than initializing entire app at once.
3. Partial rehydration
   1. proven difficult to implement.
4. Trisomorphic rendering
   1. Uses SSR for initial no-js navigations
   2. Uses Service worker to take on rendering HTML for navigations after is been installed.

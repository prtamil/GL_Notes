### Elixir/Erlang
The last few years the Elixir ecosystem has started to become the simplest solution to so many use cases:
- Web development with **Phoenix** and **Liveview** is immensely enjoyable and fast

- AI with **NX**, **Axon**, **Bumblebee**

- Audio and Video streaming and manipulation with **Membrane**

- CQRS and Event Sourcing with **Commanded**

- Embedded with **Nerves** to make your own devices

- Mobile apps with **Liveview Native** ( in development )

- Queues, pipelines and batch processing, etc... natively or with **GenStage**, **Broadway** or Oban depending on your use case

but for me, the killer feature is IEX, Elixir's REPL. Being able to interact directly with my running code easily ( in dev or in production ), introspect it, debugging it, is just life changing.

Adding types is indeed the last piece to the puzzle to bring even more confidence in the code we ship.



Don't forget:
- **ExUnit** for incredibly easy tests

- **Hex package manager** that just works

- **FLAME** for the ability to scale different processes to different computers with nearly 1 line of code (the whole library itself is just a few hundred LoC if I remember)

- **Ecto** for interacting with SQL databases in a functional manner (I still never know how to feel about ORMs, but I was able to write a few composable queries and get rid of 90% of my SQL, so I'll call that a win)

After months of struggling with deployments, uptimes, segfaults, package times, etc I moved my webserver & data layer over to Elixir + Phoenix. It's more well tested than ever, so much easier to reason about, I trust it will scale, and deployment was a breeze.

Because of convention over configuration, I was able to get up and running _insanely_ quickly with Phoenix (way more than FastAPI). I really wish I did this months ago.

Now I'm training models in Nx, playing around with Bumblebee/Livebooks, and adding presence/live functionality to my app for nearly free
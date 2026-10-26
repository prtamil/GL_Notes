# Repository Instructions

## Writing standard

Use ASD-STE100 Simplified Technical English as the writing target for all technical prose in this repository.

Use these rules:

- Use short and common words when they keep the technical meaning.
- Use one term for one concept.
- Use American English spelling.
- Use the active voice when the actor is important.
- Use the simple present tense for facts and instructions.
- Put one main idea in each sentence.
- Keep procedural sentences at 20 words or fewer.
- Keep descriptive sentences at 25 words or fewer.
- Split a long sentence instead of using a semicolon.
- Do not use filler, marketing language, slang, or unnecessary metaphors.
- Define an abbreviation before you use it.
- Keep lists parallel and concise.
- Keep headings short and direct.
- Keep examples close to the rule that they explain.
- Preserve code, API names, language keywords, and algorithm names as technical terms.
- Do not claim formal ASD-STE100 compliance unless an approved dictionary and a compliant checker verify the text.

## Clojure articles

- Target the latest stable Clojure release recorded in the course overview.
- Use idiomatic Clojure rather than a direct translation from another language.
- Use kebab-case names, such as `process-single-row`.
- Add `?` to predicate names.
- Add `!` only to names of functions that mutate state.
- Use named functions when anonymous code is difficult to read.
- Prefer `mapv` when the result must be a vector.
- Prefer `map` when the result can stay lazy.
- State the behavior for empty input, finite input, and ragged input when it is relevant.
- Keep each example small, complete, and runnable.
- Test important examples with the current local Clojure runtime.

## Structure and scope

- Keep the same article directory and lesson order as the Python reference.
- Preserve existing filenames unless the user approves a rename.
- Preserve useful user content and unrelated worktree changes.
- Use the Python material as a coverage reference, not as a source for direct syntax translation.

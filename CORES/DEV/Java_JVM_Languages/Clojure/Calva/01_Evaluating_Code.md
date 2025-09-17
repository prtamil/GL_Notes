
## *Evaluate*

| Action                                                          | Keybinding (new default) | What it does                                                                                                   |
| --------------------------------------------------------------- | ------------------------ | -------------------------------------------------------------------------------------------------------------- |
| Evaluate current form (smallest enclosing form under cursor)    | `Ctrl + Enter`           | Evaluate that form inline                                                                                      |
| Evaluate current top-level form                                 | `Alt + Enter`            | Evaluate the top-level form (def, defn, etc.) and show result inline. Works also inside `(comment ...)` forms. |
| Evaluate selection/list up to cursor (closing missing brackets) | `Ctrl + Alt + Enter`     | Good when you want partial evaluation up to a point.                                                           |
| Evaluate from start of top-level form to cursor (closing)       | `Shift + Alt + Enter`    | When you want to evaluate parts of a top-level form.                                                           |



Think of **forms** like **parentheses “bubbles”**. Each `( … )` is a bubble.

---

### 🔑 Rule of Thumb

- **`Ctrl+Enter`** = _“Run the bubble I’m in.”_
- **`Ctrl+Alt+Enter`** = _“Run the bubble, but **cut it off** at my cursor.”_

## 🌳 Mental picture

- **Ctrl+Enter** → Small bubble (current form)
- **Ctrl+Alt+Enter** → Small bubble, cut at cursor
- **Alt+Enter** → Big bubble (top-level)
- **Shift+Alt+Enter** → Big bubble, cut at cursor
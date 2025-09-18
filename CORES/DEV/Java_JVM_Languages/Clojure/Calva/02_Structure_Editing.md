# Overview
## 🧠 Mental model

- **Slurp/Barf** = move things _in/out_ of parens.
- **Raise** = promote a child up, deleting its parent.
- **Splice** = delete the current parens, but keep the inside.
- **Wrap** = put new parens/brackets around something.
- **Kill/Copy sexp** = delete/copy whole forms instead of characters.


### ⚡ Notes & Mental Hooks for keyboard shortcuts
1. **Ctrl = “look/move”** → don’t touch structure.
2. **Alt = “change structure”** → slurp, barf, raise, splice, wrap, kill.
3. **Shift = reverse / special key** → backward slurp/barf, wraps needing Shift.
4. **Alt+Ctrl = “copy instead of delete”**

# 📝 Calva Paredit Cheat Sheet (Windows / Laptop-Friendly)

---

## **1️⃣ Navigation**

| Action             | Keybinding     | Notes                                  |
| ------------------ | -------------- | -------------------------------------- |
| Move forward form  | `Ctrl + Right` | Move cursor over next s-expression     |
| Move backward form | `Ctrl + Left`  | Move cursor over previous s-expression |

---

## **2️⃣ Structural Editing: Slurp & Barf**

| Action         | Keybinding            | Notes                                   |
| -------------- | --------------------- | --------------------------------------- |
| Slurp forward  | `Alt + Right`         | Pull next sibling into current form     |
| Slurp backward | `Shift + Alt + Right` | Pull previous sibling into current form |
| Barf forward   | `Alt + Left`          | Push last element out of current form   |
| Barf backward  | `Shift + Alt + Left`  | Push first element out of current form  |

---

## **3️⃣ Structural Editing: Raise & Splice**

| Action      | Keybinding | Notes                                            |
| ----------- | ---------- | ------------------------------------------------ |
| Raise form  | `Alt + R`  | Replace parent form with current form            |
| Splice form | `Alt + S`  | Remove parentheses of current form, keep content |

---

## **4️⃣ Wrapping**

| Action           | Keybinding        | Notes                                         |
| ---------------- | ----------------- | --------------------------------------------- |
| Wrap round `()`  | `Alt + Shift + 9` | Wrap selection / next form in parentheses     |
| Wrap square `[]` | `Alt + [`         | Wrap selection / next form in square brackets |
| Wrap curly `{}`  | `Alt + Shift + [` | Wrap selection / next form in curly braces    |

---

## **5️⃣ Kill & Copy**

| Action          | Keybinding         | Notes                               |
| --------------- | ------------------ | ----------------------------------- |
| Kill forward    | `Alt + K`          | Delete next form                    |
| Kill backward   | `Alt + Shift + K`  | Delete previous form                |
| Select forward  | `Ctrl + Shift + .` | Copy next form without deleting     |
| Select backward | `Ctrl + Shift + ,` | Copy previous form without deleting |

---

### ⚡ **Tips**

1. **Laptop Shift combos**: Wrap keys use the Shift combo that produces the character.    
2. Slurp/Barf are **key for restructuring nested forms** efficiently.
3. This cheat-sheet is **Clojure/Calva-only**, safe for multi-language projects.


# keybindings.json  VSCODE (So i can apply these without confusion)

```json
[

  {

    "key": "ctrl+right",

    "command": "paredit.forwardSexp",

    "when": "calva:keybindingsEnabled && editorTextFocus && editorLangId == 'clojure' && paredit:keyMap =~ /original|strict/"

  },

  {

    "key": "ctrl+left",

    "command": "paredit.backwardSexp",

    "when": "calva:keybindingsEnabled && editorTextFocus && editorLangId == 'clojure' && paredit:keyMap =~ /original|strict/"

  },

  {

    "key": "alt+right",

    "command": "paredit.slurpSexpForward",

    "when": "calva:keybindingsEnabled && editorTextFocus && editorLangId == 'clojure' && paredit:keyMap =~ /original|strict/"

  },

  {

    "key": "shift+alt+right",

    "command": "paredit.slurpSexpBackward",

    "when": "calva:keybindingsEnabled && editorTextFocus && editorLangId == 'clojure' && paredit:keyMap =~ /original|strict/"

  },

  {

    "key": "alt+left",

    "command": "paredit.barfSexpForward",

    "when": "calva:keybindingsEnabled && editorTextFocus && editorLangId == 'clojure' && paredit:keyMap =~ /original|strict/"

  },

  {

    "key": "shift+alt+left",

    "command": "paredit.barfSexpBackward",

    "when": "calva:keybindingsEnabled && editorTextFocus && editorLangId == 'clojure' && paredit:keyMap =~ /original|strict/"

  },

  {

    "key": "alt+r",

    "command": "paredit.raiseSexp",

    "when": "calva:keybindingsEnabled && editorTextFocus && editorLangId == 'clojure' && paredit:keyMap =~ /original|strict/"

  },

  {

    "key": "alt+s",

    "command": "paredit.spliceSexp",

    "when": "calva:keybindingsEnabled && editorTextFocus && editorLangId == 'clojure' && paredit:keyMap =~ /original|strict/"

  },

  {

    "key": "alt+shift+9",

    "command": "paredit.wrapRound",

    "when": "calva:keybindingsEnabled && editorTextFocus && editorLangId == 'clojure' && paredit:keyMap =~ /original|strict/"

  },

  {

    "key": "alt+[",

    "command": "paredit.wrapSquare",

    "when": "calva:keybindingsEnabled && editorTextFocus && editorLangId == 'clojure' && paredit:keyMap =~ /original|strict/"

  },

  {

    "key": "alt+shift+[",

    "command": "paredit.wrapCurly",

    "when": "calva:keybindingsEnabled && editorTextFocus && editorLangId == 'clojure' && paredit:keyMap =~ /original|strict/"

  },

  {

    "key": "alt+k",

    "command": "paredit.killSexpForward",

    "when": "calva:keybindingsEnabled && editorTextFocus && editorLangId == 'clojure' && paredit:keyMap =~ /original|strict/"

  },

  {

    "key": "alt+shift+k",

    "command": "paredit.killSexpBackward",

    "when": "calva:keybindingsEnabled && editorTextFocus && editorLangId == 'clojure' && paredit:keyMap =~ /original|strict/"

  },

  {

    "key": "ctrl+shift+.",

    "command": "paredit.selectForwardSexp",

    "when": "calva:keybindingsEnabled && editorTextFocus && editorLangId == 'clojure' && paredit:keyMap =~ /original|strict/"

  },

  {

    "key": "ctrl+shift+,",

    "command": "paredit.selectBackwardSexp",

    "when": "calva:keybindingsEnabled && editorTextFocus && editorLangId == 'clojure' && paredit:keyMap =~ /original|strict/"

  },

   {

    "key": "alt+f",

    "command": "calva-fmt.formatCurrentForm",

    "when": "calva:keybindingsEnabled && editorTextFocus && editorLangId == 'clojure' && paredit:keyMap =~ /original|strict/"

  },

  {

    "key": "alt+c",

    "command": "editor.action.commentLine",

    "when": "calva:keybindingsEnabled && editorTextFocus && editorLangId == 'clojure' && paredit:keyMap =~ /original|strict/"

  },

  {

    "key": "alt+shift+c",

    "command": "editor.action.removeCommentLine",

    "when": "calva:keybindingsEnabled && editorTextFocus && editorLangId == 'clojure' && paredit:keyMap =~ /original|strict/"

  }

  

]

```
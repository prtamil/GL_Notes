---
tags: calva
---
# Calva Learning

## Editor Keys

*Evaluate*

Alt + Enter => Evaluate Current Toplevel Form
Ctrl + Enter => Evaluate Current Form , Whereever cursor places.
Ctrl+Alt+C Enter => Evaluate Current File and Print last form results in REPL
Tab => Format Current Enclosing Form
Ctrl+Alt+Enter => Evaluating in Threaded Expressions. Current Enclosing Form
Shift+Alt+Enter => Evaluate from current TopLevel to current position Cursor, can execute Threaded Expression inside let, do etc..


*View and Clear Results*

Ctrl K + Ctrl I => On Evaluated Result . Full Result view.
ESC => Clear Inline display

## PAREDIT

1. Bydefault Paredit strict mode is on. You cannot delete (), [] unless you delete everything inbetween.
2. Alt+BackSpace, Alt+Delete => Bypasses PareEdit Strict mode.

*Select*

Command: _Paredit Expand Selection_ => Shift+Alt+RightArrow.
Command: _Paredit Shrink Selection_ => Shift+Alt+LeftArrow.

*Slurp*

Command: _ Paredit Slurp Forward _ => .Ctrl + Alt + .
Command: _ Paredit Slurp Backward _ => Ctlr + Shift + Alt LeftArrow

*Barf*

Command: _ Paredit Barf Forward _ => Ctrl + Alt + ,
Command: _ Paredit Barf Backward _ => Ctrl + Shift + Alt RightArrow

## REPL Keys

1. Alt+UP, Alt+Down => REPL , REPL History.
2. Command: _Clear REPL History_ => Clears REPL History

## Calva Debugger

*Initiate Debug*
Place the cursor in function form Then
Execute Command : ;; _Instrument Current Top Level Form for Debugging_
Then Call function with Debugger.

*Remove Debug*
Simple Alt+Enter in function will remove debugger. and execute as normal.

*Stopping Infinite Loops*
Any Evaluation caused infinite loops
use Calva command: _Interrupt Running Evaluations_

## Calva Commands

VS Code: Ctrl+P and > in search box add Calva it will list commands. then select what you want

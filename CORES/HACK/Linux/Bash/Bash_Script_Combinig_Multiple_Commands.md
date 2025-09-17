### **Understanding `$()` in Bash Scripts**

In Bash, **`$()` is called command substitution**. It **executes a command** and **stores its output** in a variable or uses it inline within another command.

---

### **Basic Example of `$()`**



``DATE=$(date)  # Runs the `date` command and stores its output in DATE variable echo "Current Date: $DATE"``

Output:

`Current Date: Tue Feb 5 12:00:00 UTC 2025`

Equivalent **without `$()`**:


``DATE=`date`  # Older syntax, but less readable``

---

## **Using Pipes (`|`) to Combine Commands**

Pipes (`|`) pass the **output of one command** as the **input to another command**.

### **Example 1: Single Pipe**


`ls -l | grep ".txt"`

- `ls -l` → Lists files with details.
- `grep ".txt"` → Filters only `.txt` files.

---

### **Example 2: Multiple Pipes**



`ps aux | grep "firefox" | awk '{print $2}'`

- `ps aux` → Lists all running processes.
- `grep "firefox"` → Filters only Firefox processes.
- `awk '{print $2}'` → Extracts the **second column** (process ID).

---

### **Example: Using `$()` with Pipes**


`UPTIME=$(uptime | awk '{print $3}') 
`echo "System has been running for: $UPTIME"`

- **Executes `uptime | awk '{print $3}'`**
- Stores the **third column of `uptime` output** in `$UPTIME`.

---

## **Example: Your JSON Case**



`JSON_RESPONSE='{"users": [{"name": "Alice"}, {"name": "Bob"}]}' NAMES=$(echo "$JSON_RESPONSE" | jq -r '.users[].name')
`echo "User names: $NAMES"`

- `echo "$JSON_RESPONSE"` → Prints the JSON.
- `jq -r '.users[].name'` → Extracts names from JSON.
- `$()` → Captures the extracted names into `NAMES`.

Output:


`User names: Alice Bob`

---

### **Combining Multiple Commands in a Single Line**



`echo "Users: $(echo "$JSON_RESPONSE" | jq -r '.users[].name' | tr '\n' ', ')"`

- `jq -r '.users[].name'` extracts names.
- `tr '\n' ', '` replaces **newline** with a **comma**.

Output:


`Users: Alice, Bob`

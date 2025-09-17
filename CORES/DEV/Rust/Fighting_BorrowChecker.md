### Fight borrow checker
1. Understand borrowchecker rules
	1. Each value in rust has an Owner
	2. There can be one owner at a time
	3. When owner will go out of scope value will be dropped
2. Steps to clear Compiler Errors
	1. Read and understand error message. Most of time error message will tell you what it is
	2. Deeper understanding on Rust (Borrowing rules, lifetimes, memeory etc)
	3. Use AI tools (Github copilot, ChatGPT)
3. Avoid War 
	1. Make it work (use simple structs and solve the problem)
	2. Make it right (make it idiomatic rust)
	3. Make it fast (Then finetune performance)
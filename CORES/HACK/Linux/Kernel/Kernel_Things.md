What kind of Kernel is Linux ?
-------------------------------
Linux is MonoLithic Kernel. 
But it has Modules which support dynamic support
What does exec do ?
----------------------------------------
- Exec loads new program into existing content
- After loading it executes it
- Previous pages reserved by old programs are flushed
- Their content is replaced by new programs

What does fork do ?
----------------------------------------

- Fork generates exact copy of the current process
- fork generated process differ from child procees with only by PID
- As Theory memory content is duplicated.
- But Linux uses Copy-On-Write that allow defering copy operations
  untill either parent or child writes to a page

Tell me about Linux Process and its Hiearchy ?
----------------------------------------
- Linux Employs Hiearchial Scheme in which process depends on a parent ps
- INIT is the first process that is responsible for futher process

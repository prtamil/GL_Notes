# Threads

1. extends Thread -> Class inheritance, Java no mulplile inheritance
2. implements Runnable -> Interface inheritance can support mi

Thread t = new Thread(runnable)
t.start();

void run => method override.

# Thread LifeCycle

1. New :Born Thread. Untill Start
2. Runnable :After STart
3. Running : entered Run/Yield method
4. Terminated : Completes or Terminated.
5. Waiting : Wait/Sleep/Block.

# Daemon Thread

t1.setDaemon(true); //Creates Daemon Thread
t1.isDaemon() => returns status

1. Low priority
2. Not recommentd for I/O tasks
3. Thread.join on daemon thread can block shutdown of application.
4. Most jvm threads are Daemon Threads (GC,cache etc..)

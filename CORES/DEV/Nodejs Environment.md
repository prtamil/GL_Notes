#### Nodejs Cli
1. commander.js
2. inquiry.js
3. chalk.js
4. node-spinner
5. figlet

#### Nodejs CPP Extensions

CPP-AddOn are (dlls, require will load it as normal js modules )

There are four different interfaces for a Node.js addons

1. The raw `node.h` (**C++**) which is no interface at all - in this case you will have to deal with different V8/Node.js versions - which is very hard and cumbersome;
2. The old Node.js Nan (**C++**) which is still maintained and it allows you to have an uniform C++ API across all Node.js versions - but it requires that your addon is built separately for every Node.js version and does not support `worker_threads`;
3. The new `napi.h` (**C**) which has an uniform ABI across all versions - meaning that a binary module built for one version will work with all later versions;
4. The newest Node Addon API (**C++**) which is a set of C++ classes around `napi.h` that allows you to use NAPI with C++ semantics. It is fully compatible with `napi.h` and you can mix the two.

For a new module, Node Addon API is by far the best choice.

Model = Architecture + Weights + Configuration + Tokenizer
```txt
Architecture is the neural-network blueprint and computation path.

Configuration gives the dimensions and settings needed to instantiate that architecture.

Weights are the billions of learned numeric values produced by training.

Tokenizer contains the logic and vocabulary needed to translate between human text and the token IDs used by the neural network.
```


Quick analogy  (might be incorrect but gives basic idea)
```txt
1. ollama llm runtime similar to docker runtime
2. architecture is similar to docker container image 
3. weights is similar to docker volume contains data 
4. configuration is similar to configmap
5. tokernizer is part of docker runtime like library doing tokenization
```

Prompt 
 Propmt = system prompt + user prompt + assistant roles
  
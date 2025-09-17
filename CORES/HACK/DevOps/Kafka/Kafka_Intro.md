1. Producer -> Broker <- Consumer
2. Rabbitmq broker pushes data to consumer
3. Kafka Consumer polls data from broker.
4. Producer -> Topics

pubsub vs Queue

queue : Published once , consumed once
pubsub : published once, consumed many times.

kafka both:

Consumer Group can have more partition

1. To act like a queue , put all consumers in one group.
2. To act like pub/sub. put each consumers in unique group.

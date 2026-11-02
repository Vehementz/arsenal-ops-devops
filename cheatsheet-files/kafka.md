# Kafka

Apache Kafka is a distributed event streaming platform. These commands use the CLI scripts shipped with Kafka (`kafka-*.sh`) to manage topics, produce and consume messages, and inspect consumer groups.

#platform/multiple #target/Messaging #cat/DevOps

% kafka, topics, producer, consumer, consumer groups, streaming

## Kafka - List Topics

List all topics in the cluster.

```
kafka-topics.sh --bootstrap-server <host:port> --list
```

## Kafka - Create a Topic

Create a topic with a given number of partitions and replication factor.

```
kafka-topics.sh --bootstrap-server <host:port> --create --topic <topic> --partitions <partitions> --replication-factor <replication_factor>
```

## Kafka - Describe a Topic

Show partitions, leaders, replicas and ISR for a topic.

```
kafka-topics.sh --bootstrap-server <host:port> --describe --topic <topic>
```

## Kafka - Delete a Topic

Delete a topic and its data.

```
kafka-topics.sh --bootstrap-server <host:port> --delete --topic <topic>
```

## Kafka - Increase Topic Partitions

Partitions can be increased but never decreased.

```
kafka-topics.sh --bootstrap-server <host:port> --alter --topic <topic> --partitions <partitions>
```

## Kafka - Alter Topic Configuration

Set a topic-level config such as retention.

```
kafka-configs.sh --bootstrap-server <host:port> --entity-type topics --entity-name <topic> --alter --add-config retention.ms=<milliseconds>
```

## Kafka - Describe Topic Configuration

Show the config overrides of a topic.

```
kafka-configs.sh --bootstrap-server <host:port> --entity-type topics --entity-name <topic> --describe
```

## Kafka - Produce Messages

Send messages interactively, one per line.

```
kafka-console-producer.sh --bootstrap-server <host:port> --topic <topic>
```

Produce keyed messages (`key:value`).

```
kafka-console-producer.sh --bootstrap-server <host:port> --topic <topic> --property parse.key=true --property key.separator=:
```

## Kafka - Consume Messages

Read new messages from a topic.

```
kafka-console-consumer.sh --bootstrap-server <host:port> --topic <topic>
```

Read all messages from the beginning.

```
kafka-console-consumer.sh --bootstrap-server <host:port> --topic <topic> --from-beginning
```

Show keys and timestamps.

```
kafka-console-consumer.sh --bootstrap-server <host:port> --topic <topic> --from-beginning --property print.key=true --property print.timestamp=true
```

Consume as part of a consumer group.

```
kafka-console-consumer.sh --bootstrap-server <host:port> --topic <topic> --group <group>
```

## Kafka - List Consumer Groups

List all consumer groups.

```
kafka-consumer-groups.sh --bootstrap-server <host:port> --list
```

## Kafka - Describe a Consumer Group

Show offsets, log end offsets and lag per partition.

```
kafka-consumer-groups.sh --bootstrap-server <host:port> --describe --group <group>
```

## Kafka - Reset Consumer Group Offsets

Preview the reset with `--dry-run`, then apply it with `--execute`. The group must be inactive.

```
kafka-consumer-groups.sh --bootstrap-server <host:port> --group <group> --topic <topic> --reset-offsets --to-earliest --dry-run
```

```
kafka-consumer-groups.sh --bootstrap-server <host:port> --group <group> --topic <topic> --reset-offsets --to-earliest --execute
```

## Kafka - Delete a Consumer Group

Delete an inactive consumer group.

```
kafka-consumer-groups.sh --bootstrap-server <host:port> --delete --group <group>
```

## Kafka - Get Topic Offsets

Show the latest offset per partition.

```
kafka-get-offsets.sh --bootstrap-server <host:port> --topic <topic>
```

## Kafka - Check Cluster API Versions

Verify connectivity and list broker API versions.

```
kafka-broker-api-versions.sh --bootstrap-server <host:port>
```

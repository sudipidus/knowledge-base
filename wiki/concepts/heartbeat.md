---
title: "Heartbeat"
type: concept
tags: ["distributed-systems", "consensus"]
created_at: "2023-03-15T14:30:00.000Z"
updated_at: "2023-07-10T12:45:00.000Z"
publish: true
---

# Heartbeat

## Definition

The leader sends periodic heartbeats to maintain authority and ensure that all nodes in the distributed system are aware of its status.

## Key Principles

* Consistency: Heartbeats help to maintain consistency across the system by ensuring that all nodes have a shared understanding of the leader's status.
* Liveliness: Heartbeats allow the leader to periodically demonstrate its liveliness, which helps to prevent other nodes from assuming leadership.

## Examples

* A distributed consensus algorithm may use heartbeats to ensure that all nodes are aware of the leader's status and to prevent other nodes from taking over as leader.
* The periodic heartbeat can also be used to monitor system performance and detect any potential issues before they become critical.

## Related

* [[Consensus Algorithm]]: A concept page discussing different types of consensus algorithms used in distributed systems.
* [[Leader Election]]: An entity page describing the process of electing a leader in a distributed system.

---

The new information about the periodic heartbeat being used to monitor system performance and detect potential issues was merged into the "Examples" section. The updated timestamp is also included in the metadata.
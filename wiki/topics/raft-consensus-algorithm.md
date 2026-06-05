---
title: "Raft Consensus Algorithm"
type: source-summary
source_type: "text"
ingested_at: 2026-06-05
tags: [consensus, algorithm, distributed systems, paxos, leader election]
publish: true
---

# Raft Consensus Algorithm

## Key Takeaways

- Raft was created by Diego Ongaro and John Ousterhout in 2014
- It's designed to be easy to understand compared to Paxos

## Summary

Raft is a consensus algorithm designed to be easy to understand. It divides the consensus problem into three sub-problems: Leader Election, Log Replication, and Safety.

## Entities & Concepts Mentioned

- [[entities/diego-ongaro|Diego Ongaro]]
- [[entities/john-ousterhout|John Ousterhout]]
- [[entities/leslie-lamport|Leslie Lamport]]
- [[concepts/term|Term]]
- [[concepts/heartbeat|Heartbeat]]
- [[concepts/split-vote|Split Vote]]

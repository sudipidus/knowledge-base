# Raft Consensus Algorithm

Raft is a consensus algorithm designed to be easy to understand. It was created by Diego Ongaro and John Ousterhout at Stanford University in 2014.

## How It Works

Raft divides the consensus problem into three sub-problems:
1. **Leader Election** - A leader is elected among the servers
2. **Log Replication** - The leader accepts log entries from clients and replicates them
3. **Safety** - If any server has applied a log entry, no other server may apply a different entry for the same index

## Key Concepts

- **Term**: Raft divides time into terms of arbitrary length, numbered with consecutive integers
- **Heartbeat**: The leader sends periodic heartbeats to maintain authority
- **Split Vote**: When two candidates start simultaneously, the election may fail and a new term begins

## Comparison with Paxos

Unlike Paxos, Raft was designed from the ground up for understandability. The authors conducted a user study showing that Raft is significantly easier to learn than Paxos.

Paxos, created by Leslie Lamport, has been the dominant consensus algorithm for decades but is notoriously difficult to understand and implement correctly.

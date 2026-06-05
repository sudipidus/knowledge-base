# CRDTs: Conflict-Free Replicated Data Types

CRDTs are data structures that can be replicated across multiple nodes and updated independently without coordination. They guarantee eventual consistency — all replicas converge to the same state.

## Types

- **G-Counter**: A grow-only counter. Each node maintains its own counter, and the merged value is the sum.
- **PN-Counter**: Supports both increment and decrement by combining two G-Counters.
- **LWW-Register**: Last-Writer-Wins register, resolved by timestamps.

## Why CRDTs Matter

In distributed systems, you often face the CAP theorem tradeoff. CRDTs let you choose availability and partition tolerance while still getting eventual consistency — without complex conflict resolution logic.

Martin Kleppmann has done extensive research on CRDTs, particularly for collaborative editing (e.g., Automerge library).

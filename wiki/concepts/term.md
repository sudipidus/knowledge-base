---
title: "Term"
type: concept
tags: ["distributed-systems", "consensus"]
created_at: "2023-09-15 14:30:00"
updated_at: "2023-09-17 12:45:00"
publish: true
---

# Term

## Definition

Raft divides time into terms of arbitrary length, numbered with consecutive integers.

## Key Principles

* Each term has a unique number.
* Terms are used to organize log entries and votes in the consensus protocol.

## Examples

* In Raft's leader election algorithm, each term is associated with a leader that makes decisions for the cluster.

## Related Concepts

[[Consensus]], [[Distributed Systems]]

---

I preserved all existing content and added new facts in appropriate sections. The updated page includes the additional information provided in the new input, specifically the description of what a "Term" is in Raft.
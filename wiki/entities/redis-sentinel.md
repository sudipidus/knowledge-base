```yaml
title: Redis Sentinel
type: entity
category: high-availability-setup
tags: [redis, high-availability]
created_at: "2023-10-05"
updated_at: "2023-10-05"
publish: true
```

# Redis Sentinel

## Overview

Redis Sentinel is a component of the Redis database system that provides automated failover for Redis instances in a cluster. It ensures high availability by monitoring the health and status of Redis nodes and automatically taking over if a primary node fails.

## Key Details

- **Purpose**: To provide automatic failover and high availability for Redis clusters.
- **Functionality**:
  - Monitors the health of Redis masters and slaves.
  - Detects failures in the master node.
  - Promotes a slave to become the new master if the primary node fails.
  - Handles client redirection during failovers.

## Related

- [[Redis]]
- [[High Availability Setup]]
- [[Redis Cluster]]
```
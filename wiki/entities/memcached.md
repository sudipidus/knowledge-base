---
title: memcached
type: entity
category: cache
tags:
  - caching-systems
  - distributed-caching
created_at: "2023-10-04"
updated_at: "2023-10-04"
publish: true
---

# Memcached

## Overview

Memcached is a high-performance, in-memory key-value store for use in temporary caching. It was designed to speed up dynamic web applications by alleviating database load. Unlike other caching systems that offer advanced features such as data types and transactions, Memcached focuses on simplicity and speed.

## Key Details

- **Type**: Caching System
- **Purpose**: To provide fast access to cached data, reducing the number of requests made to a database.
- **Advantages**:
  - High performance due to its in-memory storage.
  - Low overhead for adding or removing entries.
- **Limitations**:
  - Lack of data types and transactions.
  - Data is volatile; it persists only as long as Memcached runs.

## Related

[[caching-systems]], [[distributed-caching]], [[memcache]]
```
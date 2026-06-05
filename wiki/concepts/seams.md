---
title: Seams
type: concept
tags:
  - software-architecture
  - design-patterns
created_at: "2023-10-01"
updated_at: "{{date}}"
publish: true
---

# Seams

## Definition

Seams in software architecture are points where different components of a system can be easily separated and replaced with others. These seams allow for incremental modernization, making it easier to introduce changes or integrate new technologies without affecting the entire system.

## Key Principles

1. **Modularity**: Each seam represents a module that is loosely coupled with other parts of the application.
2. **Incremental Change**: Changes can be made in small increments, reducing risk and facilitating testing.
3. **Replaceability**: Components can be easily swapped out for new implementations without impacting the overall architecture.

## Examples

1. **Database Access Layer**:
   - Using an abstraction like a repository pattern to interact with the database allows easy switching between different databases or storage systems.

2. **UI/Backend Separation**:
   - Designing the application such that UI components can be updated independently of backend logic, e.g., using APIs for communication between frontend and backend.

3. **Third-Party Services**:
   - Implementing a service proxy to interact with external services allows for easier switching or updating of third-party providers without changing the core system architecture.

## Related

- [[Software-Architecture]]
- [[Design-Patterns]]
- [[Modularity]]
- [[Replaceability]]
- [[Incremental-Change]]

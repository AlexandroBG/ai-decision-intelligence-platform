# ADR-004: Use SQLite for Initial Persistence

## Status

Accepted

## Context

The initial DecisionAI MVP is local-first, has limited expected
concurrency, and should minimize infrastructure complexity.

The project requires lightweight persistence without introducing
a separate database server at this stage.

## Decision

SQLite will be the initial persistence technology.

Database access should remain behind an explicit persistence
boundary so the storage implementation can evolve later.

## Alternatives Considered

- No persistence.
- SQLite.
- PostgreSQL from the beginning.
- Managed cloud databases.

## Consequences

Positive consequences include:

- Simple local setup.
- Low operational overhead.
- Easy portability.
- Strong Python ecosystem support.

Negative consequences include:

- Limited concurrent-write capability.
- Less suitable for large multi-user production workloads.
- A future migration may be required.

## Revisit When

This decision should be revisited when:

- Concurrent users increase.
- Write contention becomes measurable.
- Production availability requirements increase.
- Operational requirements justify PostgreSQL or another
  database technology.
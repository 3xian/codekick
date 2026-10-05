---
name: understand
description: Investigate how an existing behavior, business concept, module, field, API, job, event, or code path actually works. Use before making assumptions about unfamiliar code.
---

# Objective

Build the smallest evidence-backed model of the system required to answer the current question.

Do not attempt to document or understand the entire system.

# Context first

Before broad source search:

1. read `.ai/PROJECT_MAP.md` if present,
2. resolve relevant module/flow cards,
3. read relevant durable knowledge,
4. check whether selected cards may be stale,
5. use the cards as navigation hints, not truth.

# Protocol

## 1. Define the question

Determine exactly what must be understood and avoid broadening it unnecessarily.

## 2. Find entry points

Locate plausible entry points before following one:

- HTTP/RPC handlers
- UI-triggered commands
- consumers/listeners
- scheduled jobs
- CLI commands
- application services
- public methods
- triggers/procedures

## 3. Trace the execution path

Follow only the relevant path:

`Entry -> orchestration -> business/domain logic -> persistence -> side effects`

Inspect callers/callees only when they can affect the behavior under investigation.

## 4. Trace state and data

Identify relevant:

- entities/tables
- controlling fields
- state transitions
- read/write operations
- transaction boundaries
- caches

Do not infer behavior solely from names.

## 5. Trace side effects

Check relevant interactions with:

- events/messages
- background jobs
- external APIs
- files/object storage
- caches
- notifications
- accounting/inventory/other subsystems

## 6. Prefer behavioral evidence

Prefer evidence in this order when available:

1. executable tests
2. implementation code
3. database schema/constraints
4. configuration
5. git history
6. project documentation
7. naming conventions

Documentation is not authoritative when it conflicts with executable behavior.

## 7. Preserve uncertainty

Classify material conclusions as `FACT`, `INFERENCE`, `HYPOTHESIS`, or `UNKNOWN` when needed.

Never present a hypothesis as fact.

# Evidence rules

For important behavioral claims, provide concrete anchors when possible:

- file path
- symbol/function/class
- line or code location
- SQL/schema
- test
- configuration
- git commit/history
- runtime evidence supplied by the user

# Card maintenance

If the investigation discovers durable navigation knowledge:

- create/update the relevant module/flow card,
- update `verified_commit`,
- keep the card concise,
- write only durable non-obvious knowledge into `KNOWLEDGE.md`.

Do not persist task-specific scratch reasoning.

# Stop conditions

Stop when:

1. the original question can be answered,
2. the main execution path is identified,
3. relevant state/data is understood,
4. important side effects are identified,
5. remaining unknowns would not materially change the answer.

# Output

## Summary

## Execution Flow

## Key Business Rules

## Key Data

## Dependencies / Side Effects

## Evidence

## Unknowns

Prefer compression over completeness. Spend output tokens on non-obvious behavior, risks, evidence, and unknowns.

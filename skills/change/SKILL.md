---
name: change
description: Analyze a requested software change and determine the smallest safe implementation. Use before editing unfamiliar or business-critical code.
---

# Objective

Determine the smallest correct change that satisfies the requested behavior while minimizing regression risk.

# Context first

Resolve only the relevant project map, module/flow cards, durable knowledge, and source anchors before broad exploration.

Treat summaries as navigation caches. Re-validate potentially stale claims against executable evidence.

# Modification gate

DO NOT modify code until all of the following are known well enough to act:

1. current behavior
2. desired behavior
3. relevant execution path
4. likely semantic change point
5. important affected dependencies
6. validation strategy

If any item is materially unclear, continue investigation first.

# Protocol

## 1. Normalize the requirement

Identify:

- requested behavior
- conditions under which it applies
- expected outcome
- behavior that must remain unchanged

Separate explicit requirements from assumptions.

## 2. Establish current behavior

Trace the existing implementation and identify:

- entry point
- decision/business logic
- persistence
- side effects
- existing tests

Do not design the change before understanding current behavior.

## 3. Identify invariants

Look for relevant invariants such as:

- API compatibility
- database compatibility
- valid state transitions
- transaction semantics
- idempotency
- authorization
- old-client behavior

## 4. Find candidate change points

Evaluate candidate locations by:

- semantic ownership
- scope of impact
- duplication
- coupling
- testability
- consistency with existing architecture

Prefer the location where the business rule conceptually belongs, not merely the easiest patch point.

## 5. Determine blast radius

Trace only credible effects:

- callers/callees
- DB reads/writes
- state transitions
- transactions
- events/messages
- jobs
- caches
- external integrations
- authorization
- public contracts

Do not mechanically apply unrelated checklist categories.

## 6. Search for existing patterns

Before introducing a new abstraction/mechanism, search for similar behavior already present.

Prefer established project conventions unless they are demonstrably wrong for the case.

## 7. Design the smallest safe change

The preferred solution should:

- touch the fewest conceptual boundaries
- preserve contracts where possible
- avoid unrelated refactoring
- reuse existing domain concepts
- remain testable
- make failure behavior explicit

## 8. Derive validation

At minimum consider:

- primary success path
- case where the new behavior should not apply
- boundary condition
- existing behavior that must remain unchanged
- failure path when relevant

Additional tests should follow from actual implementation risks.

# During implementation

- stay within analyzed scope,
- do not perform opportunistic refactoring,
- if unexpected behavior/architecture appears, stop expanding the edit and update the analysis first.

# Evidence rules

Tie major conclusions to repository evidence.

A proposed change point must include evidence explaining why it owns the behavior.

# Stop conditions

Analysis is complete when:

1. current behavior is understood,
2. ambiguity is resolved or explicit,
3. the preferred change point is identified,
4. material blast radius is known,
5. implementation can be described concretely,
6. validation can detect likely regressions.

# Output

## Requirement
## Current Behavior
## Invariants
## Recommended Change Point
## Affected Components
## Implementation Plan
## Risks
## Validation Plan
## Evidence
## Unknowns

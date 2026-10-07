---
name: change
description: Analyze and implement the smallest safe change for a requested behavior in an existing system. Use before editing unfamiliar or business-critical code.
---

# Objective

Satisfy the requested behavior with the smallest semantically correct change and bounded regression risk.

# Context Loading

1. Read `AGENTS.md`.
2. Read `.ai/PROJECT.md`.
3. Read only relevant `.ai/KNOWLEDGE.md` sections.
4. Read/create a task artifact when the task is complex, cross-module, long-running, ambiguous or high-risk.
5. Search real source evidence.

# Modification Gate

Do not modify production code until all material items below are known:

1. `Current Behavior`
2. `Desired Behavior`
3. `Relevant Execution Path`
4. `Likely Change Point`
5. `Important Invariants / Side Effects`
6. `Validation Strategy`

If one item is materially unclear, investigate first.

# Protocol

## 1. Normalize the requirement

Separate:

- explicit requested behavior;
- conditions;
- expected result;
- behavior that must stay unchanged;
- assumptions / ambiguities.

## 2. Establish current behavior

Trace the real implementation from entry to relevant state and side effects.

Look for existing tests before designing the change.

## 3. Identify invariants

Examples:

- API compatibility;
- state transition rules;
- transaction semantics;
- authorization;
- idempotency;
- old-client behavior;
- message contracts;
- database compatibility.

Only include invariants relevant to this task.

## 4. Find candidate change points

For each realistic candidate, evaluate:

- does this layer actually own the business rule?
- impact surface;
- duplication;
- coupling;
- consistency with existing patterns;
- testability.

Prefer the semantic owner of the rule, not the easiest patch site.

## 5. Determine the credible blast radius

Trace upstream/downstream effects only when relevant:

- callers/callees;
- state/database writes;
- transactions;
- events/messages;
- jobs;
- caches;
- external integrations;
- permissions;
- public API contracts.

Do not perform checklist theater.

## 6. Search for established project patterns

Before adding abstractions, mechanisms, helpers, error models or config styles, search the repository for comparable existing behavior.

## 7. Design the smallest safe change

Prefer a solution that:

- changes the fewest conceptual boundaries;
- reuses existing domain concepts;
- preserves contracts where possible;
- avoids unrelated refactoring;
- has explicit failure behavior;
- can be tested directly.

## 8. Implement

Only after the Modification Gate is satisfied.

During implementation:

- stay within analyzed scope;
- keep unrelated cleanup out;
- if new evidence invalidates the plan, stop expanding the change and revise the analysis first.

## 9. Derive validation

At minimum consider:

- primary success path;
- case where new behavior should not apply;
- important boundary;
- existing invariant that must remain true;
- failure path when meaningful.

Additional checks must come from actual implementation risk.

## 10. Persist only durable learning

After implementation:

- task-specific reasoning → task artifact;
- stable project structure → PROJECT.md;
- hidden reusable knowledge → KNOWLEDGE.md.

# Evidence Rules

Every proposed change point must have evidence showing why it owns or controls the relevant behavior.

Distinguish `FACT`, `INFERENCE`, `HYPOTHESIS`, `UNKNOWN` when uncertainty affects the implementation.

# Negative Constraints

- Do not patch before understanding current behavior.
- Do not introduce a new abstraction before searching for an existing pattern.
- Do not combine architectural cleanup with the business change unless required for correctness.
- Do not widen API or persistence surface speculatively.
- Do not silently assume unknown business rules.

# Stop Conditions

Analysis is ready for implementation when:

1. current behavior is evidence-backed;
2. requirement ambiguity is resolved or explicitly bounded;
3. preferred change point is justified;
4. credible blast radius is known;
5. implementation steps are concrete;
6. validation can detect likely regressions.

# Output

Before or alongside implementation, keep the analysis compact:

## Requirement
## Current Behavior
## Invariants
## Recommended Change Point
## Affected Components
## Implementation Plan
## Risks
## Validation Plan
## Unknowns

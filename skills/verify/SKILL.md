---
name: verify
description: Verify whether an implementation correctly satisfies the requested change without introducing unacceptable regressions. Use after code changes and before considering the task complete.
---

# Objective

Determine whether the actual implementation is correct, minimal, and safe.

Verification must be based on the actual diff, not only on the intended design.

# Core principle

`Diff -> behavioral changes -> risks -> validation`

Do not apply unrelated checklist items mechanically.

# Protocol

## 1. Re-read the requirement

Identify required behavior, conditions, expected outcomes, and invariants.

Verify against the requirement, not the earlier implementation plan alone.

## 2. Inspect the complete diff

Understand every meaningful changed line.

Classify changes into:

- intended behavior change
- supporting change
- test change
- unrelated/suspicious change

Flag unexplained changes.

## 3. Reconstruct post-change behavior

Trace the actual changed path and confirm the rule is implemented at the intended semantic layer.

Do not assume the code matches the plan.

## 4. Derive risks from the diff

Examples of triggers:

- transaction changes -> atomicity, rollback, propagation
- SQL/schema changes -> compatibility, constraints, nullability, migration/query behavior
- events/messages -> duplicates, ordering, retries, partial failure
- state transitions -> illegal/terminal/backward transitions
- caches -> invalidation, stale reads, consistency
- public API changes -> backward compatibility and error semantics
- concurrency-sensitive changes -> races, lost updates, locking, idempotency

Only inspect categories triggered by the actual change.

## 5. Review test coverage

Confirm tests prove:

- requested behavior works
- previous behavior remains intact
- material edge cases are covered
- identified risks are exercised

Do not treat test existence as proof. Inspect assertions.

## 6. Look for silent failures

Examples:

- swallowed exceptions
- partial persistence
- event emitted before commit
- ignored failures
- unsafe defaults
- fallbacks hiding errors
- broad exception handling

## 7. Evaluate minimality

Flag behaviorally relevant:

- unnecessary refactors
- unrelated churn
- speculative abstractions
- duplicated logic
- widened API surface

# Findings quality

Every issue should include:

- location
- observed behavior
- why it matters
- plausible failure scenario
- recommended fix

Avoid warnings with no plausible failure scenario.

# Severity

- `CRITICAL` — corruption, security failure, major production failure
- `HIGH` — likely incorrect behavior or significant regression
- `MEDIUM` — realistic edge case or maintainability issue with behavioral risk
- `LOW` — minor issue or improvement opportunity

Do not inflate severity.

# Stop conditions

Verification is complete when:

1. every meaningful diff is understood,
2. requirement coverage is checked,
3. diff-triggered risks are reviewed,
4. tests are evaluated against those risks,
5. remaining uncertainty is explicit.

# Output

## Verdict

One of: `PASS`, `PASS WITH CONCERNS`, `FAIL`.

## Requirement Coverage
## Findings
## Regression Risks
## Test Gaps
## Unrelated Changes
## Evidence
## Remaining Unknowns

---
name: verify
description: Verify whether an actual implementation satisfies the requested change without unacceptable regressions. Use after code changes and before considering a task complete.
---

# Objective

Verify the real implementation, not the intended plan.

# Core Rule

```text
Requirement + Actual Diff
        ↓
Changed Behavior
        ↓
Plausible Failure Modes
        ↓
Tests / Checks
```

# Context Loading

1. Read `AGENTS.md`.
2. Read the requirement/task artifact.
3. Read relevant PROJECT/KNOWLEDGE context only as needed.
4. Inspect the complete actual diff.
5. Read changed code plus enough surrounding source to reconstruct behavior.

# Protocol

## 1. Re-establish requirement and invariants

Confirm:

- required behavior;
- conditions;
- expected result;
- behavior that must stay unchanged.

Do not verify only against the implementation plan.

## 2. Inspect every meaningful diff

Classify changes as:

- intended behavior change;
- supporting change;
- test change;
- unrelated/suspicious change.

Flag unexplained changes.

## 3. Reconstruct post-change behavior

Trace the changed path and confirm the rule was implemented at an appropriate semantic layer.

## 4. Derive risks from the actual diff

Only inspect categories triggered by the change.

Examples:

### Transaction changes

Check atomicity, rollback and propagation.

### SQL/schema changes

Check compatibility, constraints, nullability, migration safety and query behavior.

### Event/message changes

Check duplicate delivery, ordering, retry and partial failure.

### State transition changes

Check illegal transitions, terminal states and unintended paths.

### Cache changes

Check invalidation, stale reads and consistency.

### Public API changes

Check compatibility, field optionality and error semantics.

### Concurrency-sensitive changes

Check races, lost updates, locking and idempotency.

## 5. Evaluate tests, not just test presence

Confirm assertions prove:

- requested behavior works;
- relevant previous behavior remains intact;
- meaningful edge/risk scenarios are covered.

## 6. Look for silent failure modes

Examples:

- swallowed exceptions;
- partial persistence;
- event before commit;
- ignored failure response;
- accidental default/fallback;
- broad exception handling hiding incorrect state.

## 7. Evaluate minimality

Flag changes that materially expand regression surface without being required:

- unrelated refactoring;
- speculative abstractions;
- duplicated logic;
- widened API surface;
- unrelated churn.

## 8. Execute feasible validation

Run focused tests/checks first. Broaden only when risk justifies it.

Record commands and outcomes in the task artifact when one exists.

## 9. Persist durable learning

After verification:

- stable structure → PROJECT.md;
- hidden reusable knowledge → KNOWLEDGE.md;
- verification evidence/status → task artifact.

# Evidence Rules

Every reported defect should include:

- location;
- observed behavior;
- why it matters;
- plausible failure scenario;
- recommended correction when clear.

Avoid speculative warnings without a credible scenario.

# Severity

- `CRITICAL`: corruption, severe security issue, catastrophic production behavior.
- `HIGH`: likely incorrect behavior or significant regression.
- `MEDIUM`: realistic edge case or design defect with behavioral risk.
- `LOW`: minor risk/improvement.

Do not inflate severity.

# Stop Conditions

Verification is complete when:

1. every meaningful diff is understood;
2. requirement coverage is checked;
3. diff-triggered risks are reviewed;
4. tests/checks address credible risks;
5. remaining uncertainty is explicit.

# Output

## Verdict

`PASS` / `PASS WITH CONCERNS` / `FAIL`

## Requirement Coverage

## Findings

For each finding: severity, location, problem, failure scenario, recommended fix.

## Regression Risks

## Test Gaps

## Unrelated Changes

## Remaining Unknowns

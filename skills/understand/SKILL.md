---
name: understand
description: Investigate how an existing behavior, business concept, module, field, API, job, event, or code path actually works. Use when the user needs an evidence-backed explanation before changing code.
---

# Objective

Build the smallest evidence-backed model needed to answer the current question.

# Context Loading

1. Read `AGENTS.md` if present.
2. Read `.ai/PROJECT.md` if present.
3. Read only relevant sections of `.ai/KNOWLEDGE.md`.
4. Read a current task artifact if the user/task identifies one.
5. Then search real source evidence.

Do not load unrelated project context for completeness.

# Protocol

## 1. Define the exact question

Internally identify what must be understood and what is out of scope.

## 2. Find plausible entry points

Search for relevant:

- HTTP/RPC handlers;
- UI/server actions;
- message consumers;
- jobs;
- public application services;
- database procedures/triggers when applicable.

If multiple plausible entry points exist, identify them before committing to one path.

## 3. Trace the minimal execution path

Follow only the relevant chain:

```text
Entry
→ orchestration/application layer
→ business/domain logic
→ persistence/state
→ relevant side effects
```

Inspect callers/callees only when they can materially affect the answer.

## 4. Trace state and side effects

When relevant, identify:

- important entities/tables/fields;
- state transitions;
- reads/writes;
- transaction boundaries;
- messages/events;
- jobs;
- caches;
- external systems.

Do not inspect categories that the actual path does not touch.

## 5. Resolve ambiguity with evidence

Prefer, in order:

1. executable tests/runtime evidence;
2. implementation code;
3. schema/constraints;
4. configuration;
5. git history;
6. project documentation;
7. naming assumptions.

Classify material conclusions as `FACT`, `INFERENCE`, `HYPOTHESIS`, or `UNKNOWN` when uncertainty matters.

## 6. Update persistent context only if warranted

After answering:

- update `.ai/PROJECT.md` only for newly discovered stable structure;
- update `.ai/KNOWLEDGE.md` only for non-obvious reusable knowledge;
- update current task artifact if one exists.

Do not persist ordinary code facts.

# Negative Constraints

- Do not understand the entire repository.
- Do not infer behavior from names alone.
- Do not treat stale docs as authoritative over executable behavior.
- Do not modify code unless the user explicitly asks for a change.
- Do not hide conflicting evidence; report the conflict.

# Stop Conditions

Stop when:

1. the original question can be answered;
2. the main relevant execution path is known;
3. important state/data is understood;
4. relevant side effects are known;
5. remaining unknowns would not materially change the answer.

# Output

Use a compact structure:

## Summary

## Execution Flow

## Key Rules / State

## Evidence

## Unknowns

Omit sections that add no value.

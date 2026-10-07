---
name: bootstrap
description: Perform a shallow first-pass onboarding of an unfamiliar repository and create or refresh .ai/PROJECT.md. Use when taking over a project for the first time or when PROJECT.md is missing or clearly obsolete.
---

# Objective

Create a small, useful project map that helps future tasks answer one question quickly:

> Where should I look first?

Do not attempt to fully understand or document the repository.

# Preconditions

- Read `AGENTS.md` if present.
- Read existing `.ai/PROJECT.md` and `.ai/KNOWLEDGE.md` if present.
- Preserve correct existing knowledge; refresh only what evidence shows is wrong or missing.

# Protocol

## 1. Shallow repository scan

Inspect only enough to identify:

- primary languages / frameworks;
- top-level directory responsibilities;
- build/package files;
- runtime entry points;
- test layout;
- configuration locations;
- schema/migration locations;
- obvious messaging/jobs/integrations.

Do not recursively read large numbers of implementation files.

## 2. Identify business/module boundaries

Use evidence such as:

- directory/package structure;
- application entry points;
- route/controller registration;
- dependency configuration;
- module/build definitions;
- database ownership;
- message consumers/producers.

Prefer 5–15 useful module/domain entries over an exhaustive inventory.

## 3. Identify key flows only when obvious

Record a flow only if the repository makes it reasonably clear from direct evidence.

Examples:

```text
HTTP endpoint
→ application service
→ domain/service
→ repository
→ event
```

Do not invent business flows from naming alone.

## 4. Record external boundaries

Identify obvious:

- databases;
- queues/topics;
- scheduled jobs;
- external APIs;
- authentication/authorization entry points;
- observability entry points.

## 5. Record run/test commands

Prefer commands proven by:

- README/build files;
- package scripts;
- Makefile/task runner;
- CI configuration.

Do not fabricate commands.

## 6. Update `.ai/PROJECT.md`

Keep it concise and navigational.

Delete placeholder TODO sections that add no value, but retain genuinely unknown items under `Unknown Areas`.

# Evidence Rules

Every non-obvious structural claim should be backed by repository evidence.

Do not use `.ai/PROJECT.md` itself as the sole evidence for refreshing `.ai/PROJECT.md`.

# Negative Constraints

- Do not document every class/function/table.
- Do not perform a full architecture review.
- Do not create module cards or flow cards.
- Do not put hidden business knowledge into PROJECT.md; use KNOWLEDGE.md.
- Do not spend large context on areas unrelated to navigation.

# Stop Conditions

Stop when a new developer/agent can reliably answer:

- What kind of system is this?
- What are the main modules/domains?
- Where are the primary entry points?
- Where are data, jobs, messages, integrations, config and tests?
- Which area should I search first for a given business topic?

# Output

1. Update `.ai/PROJECT.md`.
2. Report the most important project areas discovered.
3. List significant unknown areas without investigating them further.

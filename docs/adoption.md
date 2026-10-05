# Adoption Guide

## Phase 1 — One real project

Start with one legacy system and use only:

- `AGENTS.md`
- `/bootstrap`
- `/understand`
- `/change`
- `/verify`
- `.ai/PROJECT_MAP.md`
- `.ai/KNOWLEDGE.md`

Do not add vector databases, graph databases, multi-agent orchestration, or organization-wide indexing yet.

## Phase 2 — Failure-driven rules

Whenever the agent makes the same category of mistake twice, encode a concrete decision rule.

Examples:

- misses async consumers -> add a rule to search listeners/consumers when triggers may be asynchronous
- trusts stale docs -> strengthen source precedence/freshness handling
- refactors unrelated code -> strengthen scope gate
- misses database triggers -> add a trigger/procedure check when app behavior and DB state disagree

Avoid turning the policy into a generic textbook.

## Phase 3 — Better retrieval only when needed

Upgrade the resolver when simple ranking fails on real tasks.

Possible later additions:

- embeddings for card retrieval
- symbol graph / call graph indexing
- structured DB schema graph
- issue/commit linking
- runtime trace ingestion

Keep these behind the same "smallest useful context" principle.

## Practical team rule

Every task should leave the project in one of two states:

1. no new durable knowledge was learned, or
2. the relevant card/knowledge entry was updated.

Never require documentation updates merely because code changed.

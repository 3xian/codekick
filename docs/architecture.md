# Architecture

## Why summaries exist

Large repositories make repeated source exploration expensive. The `.ai/` layer is therefore a **context cache**:

- fast to load,
- small enough to fit in task context,
- grounded in source anchors,
- easy to invalidate,
- progressively built by real work.

It is deliberately not a second source of truth.

## Layers

### L0 — Project Map

One small `.ai/PROJECT_MAP.md` that answers "where should I look?".

Target size: roughly 1k–3k tokens for most repositories.

### L1 — Module Cards

`.ai/context/modules/*.md`

One card per meaningful module/domain/service boundary. Cards should point to entry points, data ownership, dependencies, and key invariants.

### L2 — Flow Cards

`.ai/context/flows/*.md`

Cross-module business flows such as order cancellation, refund, settlement, shipment, onboarding, etc.

These are often more useful than module documentation because business changes frequently cross technical boundaries.

### L3 — Durable Knowledge

`.ai/KNOWLEDGE.md`

Store only facts that are expensive to rediscover: business vocabulary, hidden rules, historical constraints, operational quirks, dangerous areas.

## Progressive indexing

Do not generate all module/flow cards on day one.

Instead:

```text
real task
 -> resolve existing cards
 -> inspect missing evidence
 -> create/refresh only the touched cards
 -> persist only durable knowledge
```

This keeps the cache aligned with actual work and prevents low-value documentation explosion.

## Freshness model

Each card may record:

- `verified_commit`
- `source_paths`

A card is "potentially stale" when relevant source paths changed after that commit.

Freshness is advisory, not proof. A changed path may be irrelevant to the card; an unchanged path may still hide runtime/environment drift. The agent must validate material claims.

## Context selection

The resolver ranks cards using textual overlap across:

- title/body
- scope
- aliases
- tags

This is intentionally simple and debuggable. If you later need semantic retrieval, replace the ranker while keeping the same card contracts and freshness rules.

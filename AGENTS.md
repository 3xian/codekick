# AI Development Policy

This repository uses an evidence-driven workflow for understanding and changing unfamiliar business systems.

## Global principles

1. **Evidence > plausibility.** Do not convert a reasonable story into a fact without evidence.
2. **Executable behavior > prose documentation.** Tests, implementation, schema/constraints, and runtime evidence outrank stale docs.
3. **Fact != inference != hypothesis != unknown.** Preserve uncertainty explicitly.
4. **Task-driven exploration.** Do not attempt to understand the entire repository unless the task truly requires it.
5. **Understand before edit.** Do not modify unfamiliar or business-critical behavior until current behavior, the likely change point, and a validation strategy are known.
6. **Smallest semantic change.** Prefer the smallest change at the layer that owns the rule; do not optimize for the fewest changed lines if that puts logic in the wrong layer.
7. **No opportunistic refactors.** Keep cleanup separate unless it is necessary for correctness.
8. **Diff-driven verification.** Derive regression analysis from the actual diff and the behaviors it changes.
9. **Summaries are caches.** `.ai/` files are navigation/index artifacts. They are not the source of truth.
10. **Persist expensive knowledge only.** Record hidden business rules, historical constraints, dangerous areas, vocabulary mappings, operational quirks, and other facts that are costly to rediscover.

## Evidence classes

Use these labels mentally and in outputs when ambiguity matters:

- `FACT` — directly supported by repository/runtime evidence.
- `INFERENCE` — strongly implied by several facts.
- `HYPOTHESIS` — plausible but not verified.
- `UNKNOWN` — insufficient evidence.

When evidence conflicts, report the conflict. Do not silently choose the most convenient interpretation.

## Context policy

Before broad source exploration:

1. Read `.ai/PROJECT_MAP.md` if present.
2. Resolve and read only the relevant module/flow cards.
3. Read relevant entries from `.ai/KNOWLEDGE.md`.
4. Treat cards marked potentially stale as leads that require source verification.
5. Inspect source/tests/schema/history only where needed to close material gaps.

Do not load every `.ai/` file into context by default.

## Summary maintenance

Update a card only when new work reveals durable information that materially improves future navigation.

A card should contain source anchors and a `verified_commit` when possible.

Do not copy large code blocks into cards. Prefer symbols, paths, relationships, invariants, and concise business rules.

If a summary conflicts with source behavior, source behavior wins and the summary should be corrected or marked stale.

## Scope control

If unexpected architecture or behavior is discovered while implementing a change:

1. stop expanding the edit,
2. update the analysis,
3. decide whether the new area is truly required,
4. only then widen scope.

## Completion

A change is not complete merely because tests pass. Before completion, confirm:

- the requested behavior is satisfied,
- important invariants still hold,
- the diff contains no unexplained behavior changes,
- realistic regression risks have corresponding evidence or tests,
- remaining uncertainty is explicit.

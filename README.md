# CodeKick - AI Handover Kit

[中文说明](README.zh-CN.md)

A small, evidence-driven operating system for taking over unfamiliar business systems with AI.

The goal is not to make an agent understand the whole repository. The goal is to repeatedly build the **smallest useful context** for the task, change the system at the **smallest correct semantic point**, and verify the result from the **actual diff**.

## Core model

```text
Source code / DB / config / tests / git
                |
                v
          PROJECT_MAP.md
                |
        +-------+-------+
        |               |
   Module Cards      Flow Cards
        |               |
        +-------+-------+
                |
         Context Resolver
                |
      smallest useful context
                |
     understand -> change -> verify
                |
       durable non-obvious knowledge
                |
          KNOWLEDGE.md
```

## What is included

- `AGENTS.md` — global agent policy.
- `skills/bootstrap` — create a shallow project index.
- `skills/understand` — investigate a behavior with evidence.
- `skills/change` — plan the smallest safe change before editing.
- `skills/verify` — verify the actual diff and derive regression risks.
- `templates/` — project map, module card, flow card, knowledge templates.
- `ai-handover` CLI — initialize `.ai/`, create cards on demand, rank context cards for a task, build a context pack, and check whether cards may be stale relative to Git.
- `examples/sample-project` — a small example `.ai/` knowledge layer.
- `tests/` — tests for the resolver and freshness logic.

## Quick start

Zero-install usage from the unpacked kit:

```bash
/path/to/ai-handover-kit/bin/ai-handover init /path/to/your/project
/path/to/ai-handover-kit/bin/ai-handover new-card module order /path/to/your/project
/path/to/ai-handover-kit/bin/ai-handover resolve "订单取消增加信用额度校验" /path/to/your/project
/path/to/ai-handover-kit/bin/ai-handover pack "订单取消增加信用额度校验" /path/to/your/project --output .ai/context-pack.md
/path/to/ai-handover-kit/bin/ai-handover freshness /path/to/your/project
```

Or install the CLI:

```bash
python -m pip install -e .
```

Then point your coding agent at:

1. `AGENTS.md` from this repository (or copy it into your project).
2. The relevant `skills/*/SKILL.md`.
3. The generated `.ai/context-pack.md`.
4. Source files named by the selected cards and the agent's own evidence search.

## Recommended workflow

### First day on a project

```text
/bootstrap
    -> .ai/PROJECT_MAP.md
```

Keep the first map shallow. Do not attempt to document the entire system.

### Every task

```text
Task
  -> resolve context
  -> /understand if behavior is unclear
  -> /change
  -> implement
  -> /verify
  -> persist only durable, non-obvious knowledge
```

### Progressive indexing

Create module/flow cards only when a task touches that area. Over time the system becomes cheaper to navigate without a large up-front indexing project.

## Principles

1. Evidence before conclusion.
2. Repository behavior outranks prose documentation.
3. Fact != inference != hypothesis != unknown.
4. Explore only what the current task requires.
5. Understand before editing unfamiliar or business-critical behavior.
6. Prefer the smallest correct semantic change.
7. Derive verification from the actual diff.
8. Persist only knowledge that is expensive to rediscover.
9. Treat summaries as caches, never as the source of truth.
10. When summaries and executable evidence conflict, update or invalidate the summary.

## Card freshness

Cards can contain:

```yaml
verified_commit: abc123
source_paths:
  - src/order/**
  - db/order/**
```

`ai-handover freshness` checks whether files under those paths changed after `verified_commit`.

Freshness is deliberately conservative: a card becoming "potentially stale" does not mean it is wrong; it means the relevant source should be re-validated before relying on it.

## Context resolver

The resolver is intentionally simple and transparent. It ranks:

- `PROJECT_MAP.md`
- `KNOWLEDGE.md`
- module cards
- flow cards

using title, scope, aliases, tags, and body text. It is a pre-filter, not an oracle. The agent still has to verify material claims against source code/tests/schema/runtime evidence.

## Adapting to your tools

The repository is vendor-neutral. Common options:

- Claude Code: reference `AGENTS.md` and the selected `SKILL.md` in project instructions.
- Codex: copy/merge `AGENTS.md` into your repository-level agent instructions and invoke the skill text as task policy.
- Cursor: use the policies as project rules and keep `.ai/` in the repository.
- Other agents: treat each `SKILL.md` as a protocol, not a one-shot prompt.

## What not to do

- Do not create a complete knowledge base before real work starts.
- Do not load every summary on every task.
- Do not let the agent edit code before it can state current behavior and the change point.
- Do not let old summaries override tests or implementation.
- Do not persist obvious facts that can be re-derived cheaply.
- Do not mix unrelated refactors into business changes.

## Repository layout

```text
ai-handover-kit/
├── AGENTS.md
├── README.md
├── pyproject.toml
├── skills/
│   ├── bootstrap/SKILL.md
│   ├── understand/SKILL.md
│   ├── change/SKILL.md
│   └── verify/SKILL.md
├── src/ai_handover/
│   ├── cli.py
│   ├── frontmatter.py
│   ├── git_utils.py
│   ├── models.py
│   ├── resolver.py
│   └── templates/        # packaged copies used by the CLI
├── templates/
│   ├── PROJECT_MAP.md
│   ├── KNOWLEDGE.md
│   └── context/
│       ├── modules/_MODULE.md
│       └── flows/_FLOW.md
├── docs/
│   ├── architecture.md
│   └── adoption.md
├── examples/sample-project/.ai/
└── tests/
```

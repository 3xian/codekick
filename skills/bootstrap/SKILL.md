---
name: bootstrap
description: Build or refresh a shallow project navigation map for an unfamiliar repository. Use when first taking over a repository or when its top-level architecture has materially changed.
---

# Objective

Create the smallest useful project index that lets future tasks find the right area quickly.

Do not attempt to fully document the repository.

# Inputs

- repository root
- existing README/build files
- top-level source structure
- runtime/deployment configuration
- database/messaging/integration configuration if discoverable cheaply

# Protocol

## 1. Establish the system boundary

Identify what the repository appears to own and what it delegates elsewhere.

## 2. Inventory top-level modules

Identify modules/services/packages that represent meaningful runtime or business boundaries.

Ignore generated/vendor directories unless they affect build/runtime behavior.

## 3. Locate primary entry points

Look for:

- HTTP/RPC entry points
- message consumers/listeners
- scheduled jobs
- CLI workers
- application bootstraps

## 4. Locate state and infrastructure

Identify, at a shallow level:

- primary databases
- migration/schema locations
- cache systems
- messaging systems
- object/file storage
- external integrations

## 5. Locate verification and operations

Identify:

- test layout
- build/run commands
- CI/CD entry points
- deployment manifests
- observability/logging configuration

## 6. Create `.ai/PROJECT_MAP.md`

Keep it compact. Prefer pointers over explanations.

Include:

- system purpose
- module map
- entry points
- data/infrastructure map
- integrations
- testing/build/deploy pointers
- high-risk/unknown areas only when supported by evidence
- source anchors

## 7. Do not create deep cards preemptively

Only create module or flow cards if the initial task already needs them.

# Evidence rules

Important claims must reference repository evidence where possible.

Do not infer business ownership from directory names alone.

# Stop conditions

Stop when a new engineer/agent can answer:

1. Where should I start looking for a given business capability?
2. What are the main runtime boundaries?
3. Where are data, messaging, tests, and deployment defined?

Do not continue into detailed business flow analysis unless required by an active task.

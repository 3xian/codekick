---
type: module
scope: inventory
aliases: [库存, stock, reservation]
tags: [inventory, reservation, release]
source_paths:
  - src/inventory/**
verified_commit: ""
---

# Module: Inventory

## Responsibility

Owns stock reservation and release.

## Entry Points

- `InventoryConsumer`

## Core Components

- `InventoryService`
- `ReservationRepository`

## Important Rules

- Cancellation flow may release a previously created reservation.

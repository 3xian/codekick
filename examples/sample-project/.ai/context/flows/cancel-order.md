---
type: flow
scope: cancel-order
aliases: [订单取消, cancel order, cancellation]
tags: [order, inventory, cancellation]
source_paths:
  - src/order/**
  - src/inventory/**
verified_commit: ""
---

# Flow: Cancel Order

## Purpose

Cancel an eligible order and release downstream reservation state.

## Entry

`POST /orders/{id}/cancel`

## Execution Flow

```text
OrderController
-> OrderApplicationService.cancel
-> Order.cancel
-> OrderRepository.save
-> InventoryReleasedEvent
-> InventoryConsumer
-> InventoryService.release
```

## State Transitions

`CONFIRMED -> CANCELLED`

## Important Conditions / Invariants

- Example invariant: `SHIPPED` orders cannot be cancelled.

## Source Anchors

- `src/order/**`
- `src/inventory/**`

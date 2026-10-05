---
type: module
scope: order
aliases: [订单, sales-order, order-service]
tags: [order, cancellation, lifecycle]
source_paths:
  - src/order/**
  - db/order/**
verified_commit: ""
---

# Module: Order

## Responsibility

Owns order lifecycle and order state transitions.

## Entry Points

- `OrderController`
- `OrderCommandConsumer`

## Core Components

- `OrderApplicationService`
- `Order`
- `OrderRepository`

## Data Ownership

- `sales_order`
- `sales_order_item`

## Important States / Invariants

- `CREATED -> CONFIRMED -> SHIPPED`
- Example invariant: shipped orders cannot be cancelled.

## Outbound Dependencies / Side Effects

- emits inventory-release behavior during cancellation

## Source Anchors

- `src/order/**`
- `db/order/**`

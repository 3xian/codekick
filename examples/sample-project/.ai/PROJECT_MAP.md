---
type: project-map
verified_commit: ""
tags: [project, order, payment, inventory]
---

# Sample Commerce Project Map

## System Purpose

A sample order-processing system used only to demonstrate the context-card format.

## Runtime / Module Map

| Area | Responsibility | Entry points | Main source paths |
| --- | --- | --- | --- |
| Order | order lifecycle | OrderController, OrderCommandConsumer | src/order/** |
| Inventory | reservations/releases | InventoryConsumer | src/inventory/** |
| Payment | authorization/refund | PaymentController | src/payment/** |

## Data & Infrastructure

- Order DB tables: `sales_order`, `sales_order_item`
- Messaging: order lifecycle events

## External Integrations

- payment provider

## Tests / Build / Run

- Example only; no runnable application is included.

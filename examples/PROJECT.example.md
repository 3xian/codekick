# Project Map — Example

## System Purpose

- B2B order management service.
- Handles order creation, approval, cancellation and shipment coordination.
- Integrates with inventory, credit and CRM services.

## Repository Layout

| Path | Responsibility | Notes |
|---|---|---|
| `src/order/` | order lifecycle | core business area |
| `src/inventory/` | reservation/release client | external service adapter |
| `src/credit/` | credit validation | external service adapter |
| `db/migrations/` | schema evolution | PostgreSQL |
| `tests/` | integration/unit tests | mirrors src domains |

## Modules / Domains

### Order

- Responsibility: order lifecycle and state transitions
- Main paths: `src/order/`
- Entry points: `OrderController`, `OrderCommandConsumer`
- Core components: `OrderApplicationService`, `Order`
- Owned data: `sales_order`, `sales_order_item`
- Depends on: Credit, Inventory
- Emits / calls out: `OrderConfirmed`, inventory reservation/release

## Key Business Flows

### Cancel Order

```text
POST /orders/{id}/cancel
→ OrderController.cancel
→ OrderApplicationService.cancel
→ Order.cancel
→ OrderRepository.save
→ InventoryReleased event
```

## Build / Run / Test

```bash
./gradlew test
./gradlew bootRun
```

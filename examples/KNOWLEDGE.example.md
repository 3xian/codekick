# Project Knowledge — Example

## Business Vocabulary

| Business Term | Meaning in Code / System | Notes |
|---|---|---|
| 锁单 | `OrderStatus.CONFIRMED` | 业务团队不会使用“confirmed”这个说法 |

## Hidden Business Rules

### Credit check ordering

- Rule: CreditCheck 必须发生在 InventoryReserve 之前。
- Why it exists: 财务希望失败订单不要占用库存。
- Evidence / source of knowledge: 交接会议 + 历史事故复盘。
- Affected area: order approval.

## External System Quirks

### CRM

- Non-obvious behavior: HTTP 200 不代表业务同步成功。
- Correct handling: 必须同时检查 response body 的业务 code。

## Production Gotchas

### SettlementJob

- Symptom: 重跑同一日期可能重复生成结算项。
- Risk: 当前实现并非完全幂等。
- Safe procedure: 生产重跑前必须先检查 settlement_batch 状态。

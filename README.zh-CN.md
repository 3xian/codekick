# CodeKick - AI Handover Kit

用于资深开发者接手陌生大型业务系统的一套轻量 AI 工作流。

它不追求“让 AI 一次性理解整个系统”，而是解决三个问题：

1. 每个任务只加载**最小有用上下文**；
2. 修改前找到**真正拥有业务规则的 change point**；
3. 修改后根据**实际 diff 推导风险和验证范围**。

## 核心结构

```text
源码 / DB / 配置 / 测试 / Git
             ↓
      .ai/PROJECT_MAP.md
             ↓
   Module Cards + Flow Cards
             ↓
       Context Resolver
             ↓
        最小任务上下文
             ↓
 understand → change → verify
             ↓
     .ai/KNOWLEDGE.md
```

`.ai/` 中的内容是 **Context Cache**，不是事实源。真正的事实仍来自代码、测试、Schema、配置、Git 和运行时证据。

## 零安装开始

解压后直接运行：

```bash
/path/to/ai-handover-kit/bin/ai-handover init /path/to/customer-project
```

按需创建模块卡片：

```bash
/path/to/ai-handover-kit/bin/ai-handover new-card module Order /path/to/customer-project --scope order
```

按需创建业务流卡片：

```bash
/path/to/ai-handover-kit/bin/ai-handover new-card flow "Cancel Order" /path/to/customer-project --scope cancel-order
```

处理需求前解析最相关的上下文：

```bash
/path/to/ai-handover-kit/bin/ai-handover resolve "订单取消增加信用额度校验" /path/to/customer-project
```

生成可直接喂给 Agent 的上下文包：

```bash
/path/to/ai-handover-kit/bin/ai-handover pack \
  "订单取消增加信用额度校验" \
  /path/to/customer-project \
  --output .ai/context-pack.md
```

检查摘要是否可能已经过期：

```bash
/path/to/ai-handover-kit/bin/ai-handover freshness /path/to/customer-project
```

在验证完某张卡片后，把它标记到当前 Git commit：

```bash
/path/to/ai-handover-kit/bin/ai-handover stamp \
  .ai/context/modules/order.md \
  /path/to/customer-project
```

## 四个 Skill

### bootstrap

第一次接手仓库时建立浅层 `PROJECT_MAP.md`。不要做全量知识库。

### understand

回答“这个东西现在到底怎么工作”。先用现有 Context Cache 导航，再只查缺失的源码证据。

### change

回答“这个需求应该在哪里、以多小的范围修改”。在当前行为、change point、影响范围和验证方案明确以前禁止直接改代码。

### verify

基于真实 diff 验证需求覆盖和回归风险。原则是：

```text
Diff → 行为变化 → 风险 → 验证
```

## 推荐项目目录

客户项目中只需要：

```text
.ai/
├── PROJECT_MAP.md
├── KNOWLEDGE.md
└── context/
    ├── modules/
    │   ├── order.md
    │   └── payment.md
    └── flows/
        ├── cancel-order.md
        └── refund.md
```

不要预先创建几十张卡片。真实任务触达哪个领域，就渐进式建立哪个领域的索引。

## Freshness 机制

Module/Flow Card 可以记录：

```yaml
source_paths:
  - src/order/**
  - db/order/**
verified_commit: "abc123..."
```

之后 `freshness` 会检查这些路径从 `verified_commit` 到当前 HEAD/工作区是否发生变化。

结果含义：

- `fresh`：相关路径没有变化；
- `potentially-stale`：相关源码发生变化，需要重新验证；
- `unknown`：没有足够 metadata 判断。

注意：`fresh` 也不是“事实保证”，只是说明 Git 层面没有发现相关路径变化。

## 推荐使用方式

把本仓库的 `AGENTS.md` 作为全局开发纪律，把具体任务交给对应 `SKILL.md`：

```text
AGENTS.md
   ├── bootstrap/SKILL.md
   ├── understand/SKILL.md
   ├── change/SKILL.md
   └── verify/SKILL.md
```

真正应该长期迭代的不是 Prompt 文采，而是 Agent 真实犯过的错误：同类错误重复出现，就把它沉淀成具体 decision rule。

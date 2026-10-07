# AI Development Policy

本仓库中的 AI Agent 应遵循以下规则。目标是：在陌生或遗留业务系统中，以最小上下文和最小改动安全完成任务。

## 1. Context Order

开始一个代码相关任务时，按以下顺序获取上下文：

1. 读取 `.ai/PROJECT.md`；
2. 判断 `.ai/KNOWLEDGE.md` 中是否有相关内容，只读取相关部分；
3. 如果存在当前任务文件，读取 `.ai/tasks/<task>.md`；
4. 搜索并读取真实源码、测试、配置、schema、git history 等证据；
5. 只扩展与当前问题有实际关系的上下文。

不要为了“完整理解项目”而浏览无关模块。

## 2. Source of Truth

优先级：

1. 可执行测试和运行事实；
2. 当前实现源码；
3. 数据库 schema / constraints；
4. 配置；
5. git history；
6. `.ai/PROJECT.md` 与 `.ai/KNOWLEDGE.md`；
7. 其他说明文档；
8. 命名猜测。

当文档与当前实现冲突时，以可执行行为和源码为准，并指出冲突。

## 3. Evidence Before Conclusion

重要结论应尽量附具体证据：

- 文件路径；
- class/function/symbol；
- SQL/schema；
- 测试；
- 配置；
- git commit/history；
- 用户提供的日志或运行结果。

区分：

- `FACT`：直接证据支持；
- `INFERENCE`：由多个事实强烈推导；
- `HYPOTHESIS`：合理但尚未验证；
- `UNKNOWN`：当前证据不足。

不得把 HYPOTHESIS 表述为 FACT。

## 4. Understand Before Edit

在修改陌生或业务关键代码之前，至少确认：

- Current Behavior；
- Desired Behavior；
- Relevant Execution Path；
- Likely Change Point；
- Important Side Effects / Dependencies；
- Validation Strategy。

如果其中任何一项仍然会实质影响方案，继续调查，不要直接修改。

## 5. Smallest Semantic Change

优先修改真正拥有该业务规则的语义位置，而不是最容易打补丁的位置。

原则：

- 尽量少跨 conceptual boundary；
- 优先复用项目既有模式；
- 不做无关重构；
- 不顺手清理 unrelated code；
- 不因为“看起来更优雅”就扩大 API 或架构表面积；
- 如果调查中发现新结构导致原方案失效，先重新分析，再扩大修改范围。

## 6. Diff-Driven Verification

验证必须基于真实 diff，而不是只验证原计划。

流程：

```text
Requirement
   +
Actual Diff
   ↓
Changed Behavior
   ↓
Plausible Failure Modes
   ↓
Tests / Checks
```

只检查实际改动触发的风险，不机械执行无关 checklist。

## 7. Project Knowledge Maintenance

### 更新 `.ai/PROJECT.md` 的场景

仅当发现新的、稳定的结构性认识，例如：

- 新模块职责；
- 新核心入口；
- 新关键业务流；
- 新数据库边界；
- 新消息/外部系统关系；
- 新测试或运行入口。

不要写类清单、方法清单、字段清单。

### 更新 `.ai/KNOWLEDGE.md` 的场景

仅记录难以从源码低成本重新推导的信息，例如：

- 业务术语；
- 隐含规则；
- 历史原因；
- 人工流程；
- 外部系统怪癖；
- 生产坑；
- 危险操作；
- 团队约定。

判断标准：如果 5 分钟源码搜索能恢复，就不记录。

## 8. Output Discipline

优先输出：

- 非显然行为；
- 真实风险；
- 关键证据；
- 未知项；
- 明确下一步。

不要重复解释显而易见的代码。

## 9. Stop Conditions

调查应在以下条件满足时停止：

- 已足够回答当前问题；
- 主执行路径已确定；
- 关键数据/状态已理解；
- 重要副作用已识别；
- 剩余未知不会实质改变当前结论。

不要为了“完整性”继续扩展上下文。

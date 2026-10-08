# CodeKick

CodeKick 是一套面向大型遗留业务系统二次开发的轻量 AI 工作流。

目标不是让 AI 先“理解整个系统”，而是让它在每个真实任务中：

1. 先用项目地图快速定位；
2. 再用源码证据理解当前行为；
3. 找到最小正确修改点；
4. 用实际 diff 推导回归风险；
5. 只沉淀以后无法低成本重新推导的知识。

整个方案刻意保持简单，不依赖向量数据库、知识图谱、MCP 或专用索引服务。

## 核心结构

```text
.
├── AGENTS.md                 # 全局 AI 工作纪律
├── .ai/
│   ├── PROJECT.md            # 项目地图：系统有什么、去哪里找
│   ├── KNOWLEDGE.md          # 隐含业务知识、历史原因、生产坑
│   └── tasks/                # 复杂任务的持久工作记忆
├── skills/
│   ├── bootstrap/SKILL.md    # 第一次接手项目时建立 PROJECT.md
│   ├── understand/SKILL.md   # 理解现有行为
│   ├── change/SKILL.md       # 分析并实施最小安全修改
│   └── verify/SKILL.md       # 基于 requirement + diff 验证修改
├── templates/
│   └── TASK.md               # 复杂任务模板
├── scripts/
│   └── new-task.py           # 创建任务文件
└── examples/                 # 示例
```

## 核心原则

### 1. PROJECT.md 是导航，不是第二份源码

它只回答：

- 系统负责什么；
- 模块在哪里；
- 核心入口在哪里；
- 关键业务流大致怎么走；
- 主要数据库、消息、外部系统是什么；
- 测试和运行入口在哪里。

不要把类、方法、表字段逐条复制进去。

建议长期控制在约 2k~5k tokens。

### 2. KNOWLEDGE.md 只保存“源码看不出来”的东西

适合记录：

- 业务术语和代码概念的映射；
- 隐含业务规则；
- 历史原因；
- 外部系统的非显然行为；
- 生产环境坑；
- 团队约定；
- 已知危险区域。

判断标准：

> 如果通过 5 分钟代码搜索就能重新得到，不要写进 KNOWLEDGE.md。

### 3. Task Artifact 只用于复杂任务

简单 bug 不需要创建任务文件。

当一个任务具有以下特征时再创建：

- 跨模块；
- 需要多次会话；
- 需求有歧义；
- 调查链较长；
- 风险较高；
- 需要保留诊断与验证过程。

任务完成后，可保留归档；只有真正可复用的知识才提炼进 KNOWLEDGE.md。

### 4. Evidence first

AI 的重要结论必须尽量有证据：

- 文件路径；
- symbol；
- SQL / schema；
- 配置；
- 测试；
- git history；
- 用户提供的日志或运行结果。

必须区分：

- FACT：直接有证据；
- INFERENCE：由多个事实强烈推导；
- HYPOTHESIS：合理但尚未验证；
- UNKNOWN：证据不足。

## 推荐工作流

### 第一次接手项目

让 Agent 执行 `bootstrap`：

```text
/bootstrap
```

目标只是建立一份足够好用的 `.ai/PROJECT.md`，不要一次性分析整个系统的每个细节。

### 日常理解问题

```text
/understand 订单取消为什么会释放库存？
```

执行顺序：

```text
PROJECT.md
  ↓
定位相关区域
  ↓
读取相关 KNOWLEDGE
  ↓
搜索真实源码
  ↓
追最小必要调用链
  ↓
给出证据化结论
```

### 修改需求

```text
/change 订单审核时增加客户信用额度校验
```

AI 在修改前必须先确定：

- Current Behavior；
- Desired Behavior；
- Change Point；
- 重要影响范围；
- 验证方案。

这些没有搞清楚之前，不允许直接改代码。

### 修改完成后

```text
/verify
```

验证逻辑：

```text
Requirement + Actual Diff
          ↓
Changed Behavior
          ↓
Real Risks
          ↓
Tests / Checks
```

不是机械跑一张 50 项 checklist。

## 安装到已有项目

用安装器，不要整目录覆盖复制：

```bash
python scripts/install.py /path/to/project
```

安装内容：

```text
AGENTS.md
.ai/
skills/
templates/
scripts/
```

项目里已经存在、且和本次安装内容不同的 `AGENTS.md`、`.ai/PROJECT.md`、`.ai/KNOWLEDGE.md` 会保留。直接复制会覆盖它们。安装记录里的哈希是磁盘上实际留下的内容；被保留的文件不会被标成这次模板的版本。同版本再运行不会改写未变化的文件。如果上次安装中断并留下 `.ai/.codekick-install.pending`，下次运行会补齐其余 CodeKick 文件，仍然不覆盖这三份内容，也不会覆盖安装后被改过的 skill。

如果你的 Agent/IDE 对 skill 路径有自己的约定，可以只复制 `SKILL.md` 内容到对应目录。

## 最小使用方式

如果你不想引入任何命令机制，也可以只让 Agent 遵守：

```text
1. 开始任务前读取 AGENTS.md 和 .ai/PROJECT.md。
2. 只在相关时读取 .ai/KNOWLEDGE.md。
3. 理解当前行为后才修改代码。
4. 重要结论附源码证据。
5. 修改后基于实际 diff 做验证。
6. 发现新的项目结构时更新 PROJECT.md。
7. 发现新的隐含知识时更新 KNOWLEDGE.md。
```

## 什么时候再升级架构

不要提前引入更复杂基础设施。只有遇到真实瓶颈时再升级：

- 经常找不到 callers/callees → 引入 Serena/LSP 级 symbol navigation；
- 跨大量服务做 blast radius 很困难 → 引入 code graph；
- PROJECT.md 膨胀到不可控 → 再做分层 memory；
- 多项目知识检索成为瓶颈 → 再考虑搜索/向量层。

先拿真实遗留系统跑 10~20 个任务，根据 AI 实际犯的错误修改规则，比预先设计完整平台更有效。

## 真实任务改进评估

Controller/Judge 的历史 benchmark、隐藏 oracle 和运行证据位于 [`evals/`](evals/README.md)；当前门禁与逐项决策见 [`IMPROVEMENT-DECISIONS.md`](IMPROVEMENT-DECISIONS.md)。

该目录不是 CodeKick runtime，也不属于上述安装列表。它含有真实历史解法，禁止向 benchmark Coding Actor 暴露。当前只有两项 oracle 完成真实 pre-fix FAIL / reference PASS，Phase 0 仍受阻；没有 Candidate 被 ACCEPT 或进入产品。

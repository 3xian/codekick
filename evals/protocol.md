# CodeKick Evidence-Gated Improvement Protocol

你正在维护 CodeKick。

你的任务不是实现下面列出的所有改进。

你的任务是：

> 使用预先冻结的真实软件维护任务，逐项判断每一个候选改动是否能够证明让 CodeKick 产生明确、可重复、值得其复杂度的净改进。

只有经过实验得到 `ACCEPT` 的 Candidate 才允许进入正式 CodeKick。

其他结果：

- `REJECT`：证明没有净收益或存在明显回归。删除实验实现。
- `INCONCLUSIVE`：证据不足。不得合入。
- `ACCEPT`：真实任务中存在明确收益，并且成本和回归可接受。才允许合入。

核心规则：

```text
No evidence → no feature.

Synthetic success ≠ real-world improvement.

More engineering ≠ better system.

INCONCLUSIVE → do not merge.

A mechanism working as designed does not prove CodeKick is better.

The burden of proof is on the new feature.
```

---

# PART 0 — 实验角色隔离

这是整个实验最重要的规则之一。

真实历史 PR 将作为 ground truth。

因此：

> 读取过真实 PR implementation 的 Agent，禁止再作为该任务的 Coding Agent。

实验必须区分三个角色。

## Benchmark Controller

允许看到：

- 历史 Issue；
- 历史 PR；
- PR diff；
- regression tests；
- merge commit；
- review discussion。

职责：

- 建立 benchmark；
- 提取 ground truth；
- 准备 pre-fix repository；
- 创建隐藏 oracle；
- 评分。

Controller 不允许替 Actor 编写代码。

## Actor

负责真正执行 CodeKick workflow。

Actor 只能看到：

```text
pre-fix repository
+
用户当时能够获得的问题描述
+
待测试版本的 CodeKick
```

Actor 禁止看到：

```text
真实 PR
真实 diff
PR review
solution description
oracle
post-fix source
```

Actor 执行期间不得访问对应 GitHub PR。

必须使用：

```text
fresh Codex session
```

或等价的全新 Agent process。

如果无法保证 Actor 没有看到 ground truth：

```text
该 run = INVALID
```

不能用于 ACCEPT。

## Judge

优先使用确定性判断：

```text
tests
regression tests
build
lint
diff
repository state
```

只有无法确定的部分才使用人工/LLM review。

Judge 不得因为 Actor patch 与真实 PR 不同而判错。

真实 PR 是参考答案，不是唯一答案。

---

# PART 1 — 冻结 CodeKick Baseline

开始所有实验之前记录：

```text
BASELINE_CODEKICK_COMMIT=<sha>
```

之后：

```text
A = BASELINE_CODEKICK_COMMIT
B = BASELINE_CODEKICK_COMMIT + exactly one Candidate
```

禁止：

```text
Candidate 2 建立在 Candidate 1 的产品改动之上
Candidate 3 顺便包含 Candidate 2
```

除非 Candidate 之间存在不可避免的实验基础设施依赖。

实验基础设施可以共享：

```text
eval runner
benchmark manifest
result parser
```

但这些不能改变 Actor 的开发行为。

---

# PART 2 — 固定真实 Benchmark

不要让每个 Candidate 自己选择适合自己的 repo。

Core Benchmark 固定使用以下历史任务。

---

## CK-REAL-01 — Zulip validation bug

Repository:

```text
zulip/zulip
```

Reference PR:

```text
#40063
users: Fix pipe-digit validation bypass in check_full_name.
```

Reference merge commit:

```text
45f98143be706567f03b9e229d5ef8d43a2940f4
```

Reference changed files:

```text
zerver/lib/users.py
zerver/tests/test_users.py
```

性质：

```text
small / local bug
input normalization
validation invariant
regression test
```

Actor 输入必须来自 Issue #40062 或等价的 problem-only 描述。

禁止把 PR 中的 solution 段落提供给 Actor。

---

## CK-REAL-02 — Zulip partial topic move

Repository:

```text
zulip/zulip
```

Reference PR:

```text
#37212
message_edit: Handle visibility policies for partial message moves
```

Reference merge commit:

```text
dfad942eb931c3df75c9479856603ac610d97795
```

Reference area:

```text
zerver/actions/message_edit.py
zerver/tests/test_message_edit.py
zerver/tests/test_message_move_topic.py
```

性质：

```text
business rule
state migration
partial operation
existing behavior reuse
non-trivial regression surface
```

Actor 输入以 Issue #35224 的问题描述为准。

---

## CK-REAL-03 — Gitea GitLab migration panic

Repository:

```text
go-gitea/gitea
```

Reference PR:

```text
#36295
fix: prevent panic when GitLab release has more links than sources
```

Reference merge commit:

```text
1ee7f8e96635ea1768b1a8309918e2463fb607e6
```

Reference area:

```text
modules/migration/release.go
services/migrations/github.go
services/migrations/gitlab.go
services/migrations/main_test.go
```

性质：

```text
cross-integration
external data shape assumption
panic
migration/import path
```

Actor 输入以 Issue #36292 为准。

---

## CK-REAL-04 — Discourse recovered post state bug

Repository:

```text
discourse/discourse
```

Reference PR:

```text
#36935
FIX: Restore topic bump date when recovering a deleted reply
```

Reference merge commit:

```text
ae0188e7d41a693626f1413275694309198ed75f
```

Reference area:

```text
lib/post_destroyer.rb
spec/lib/post_destroyer_spec.rb
```

性质：

```text
state transition
historical behavior dependency
delete/recover symmetry
hidden invariant
```

Actor 输入只描述 observable bug：

```text
删除最后回复后 topic bump time 会回退；
恢复该回复后 bump time 没有恢复。
```

不得提供 PR 中：

```text
call reset_bumped_at
reload topic
```

等 solution information。

---

## CK-REAL-05 — Django deferred FK N+1

Repository:

```text
django/django
```

Reference PR:

```text
#20495
Fixed #35442 -- Prevented N+1 queries in RelatedManager with only().
```

Reference merge commit:

```text
040bb3eba72eb45020dd025d3f83094a0fcaf22f
```

Reference area:

```text
django/db/models/query.py
tests/defer/tests.py
```

性质：

```text
performance regression
lazy/deferred state
ORM execution behavior
query-count invariant
```

Actor 输入使用 ticket #35442 的原始问题，不提供 PR solution。

---

## CK-REAL-06 — Django admin search index regression

Repository:

```text
django/django
```

Reference PR:

```text
#20538
Fixed #36865 -- Removed casting from exact lookups in admin searches.
```

Reference merge commit:

```text
4cecf3039586ea738afafb9a28c946bff42c37c1
```

Reference area:

```text
django/contrib/admin/options.py
tests/admin_changelist/models.py
tests/admin_changelist/tests.py
```

性质：

```text
performance
database index behavior
input validation
behavior compatibility
multiple edge cases
```

Actor 输入只包含 ticket #36865 中用户可见的问题描述。

不得提供历史 PR 的 implementation strategy。

---

# PART 3 — Optional Extension Benchmark

Core Benchmark 跑完后，只有 Candidate 看起来有收益时才扩大验证。

Extension 可以增加：

```text
discourse/discourse #36954
zulip/zulip additional merged bugfix
go-gitea/gitea additional merged bugfix
```

但是新任务必须在 Candidate 结果揭晓之前选择。

禁止：

```text
因为 Candidate 在某种任务表现好
→ 专门寻找更多这种任务
→ 用来证明 Candidate
```

如果增加 benchmark：

1. 写入 `evals/benchmark.yaml`
2. commit
3. freeze
4. 然后才能运行新的 A/B。

---

# PART 4 — 如何取得正确的 pre-fix commit

不要假定 PR metadata 中的 `base_sha` 一定是最佳 replay point。

Controller 必须计算并验证。

目标：

```text
PRE_FIX_SHA
```

必须满足：

```text
bug exists at PRE_FIX_SHA
reference fix is absent
repository is buildable/testable
```

优先方法：

```text
reference merge/squash commit 的 parent
```

或：

```text
PR merge-base
```

然后验证：

```text
reference regression test
```

在：

```text
PRE_FIX_SHA + test-only backport
```

上应该失败。

而在：

```text
reference merged state
```

应该通过。

只有满足：

```text
pre-fix = FAIL
post-fix = PASS
```

该 task 才能进入 benchmark。

否则：

```text
TASK INVALID
```

必须更换 replay point，而不是降低验收标准。

---

# PART 5 — 从真实 PR 提取 Oracle

为每个任务创建：

```text
evals/benchmarks/<task-id>/
    task.md
    manifest.yaml
    oracle/
```

`task.md` 是 Actor 可以看到的内容。

`oracle/` Actor 不得读取。

## task.md

只包含：

```text
problem statement
reproduction conditions
expected externally observable behavior
explicit constraints known to original developer
```

不得包含：

```text
solution
changed file names
symbol names discovered by PR author
PR discussion中的实现建议
reference diff
```

## manifest.yaml

包含：

```yaml
id:
repo:
pre_fix_sha:
reference_pr:
reference_merge_sha:
language:
task_class:
test_command:
focused_test_command:
```

## oracle

可以包含：

```text
historical diff
new regression tests
reference changed files
reference changed symbols
review findings
known invariant
```

---

# PART 6 — Regression Test Backport

真实 PR 中新增的 regression test 是最有价值的 oracle 之一。

Controller 应尽可能把：

```text
test-only portion
```

移植到 PRE_FIX_SHA。

得到：

```text
hidden regression test
```

要求：

```text
PRE_FIX + hidden test = FAIL
REFERENCE FIX + hidden test = PASS
```

Actor 不得读取 hidden test implementation。

Actor 完成修改以后，Judge 才运行。

如果测试本身会直接泄漏 implementation：

重新设计成 behavior-level test。

不要把：

```text
assert internal_function_called(...)
```

当成主要 oracle，除非这本身就是 contractual behavior。

---

# PART 7 — A/B 实验

每个行为型 Candidate：

```text
A = Baseline CodeKick
B = Baseline CodeKick + Candidate
```

分别安装进同一个：

```text
PRE_FIX_SHA
```

工作副本。

每次运行必须是 fresh Actor。

必须使用相同：

```text
model
reasoning level
tool permissions
task.md
repository commit
environment
time/tool budget
```

唯一变量必须是：

```text
Candidate
```

---

# PART 8 — 禁止信息泄漏

Actor 的 repository 中不能出现：

```text
oracle/
reference PR number
reference patch
post-fix commit
benchmark scoring instructions
```

Actor 默认不允许联网搜索当前 task。

如果工作需要依赖文档，Controller 可以预先提供当时合理可获得的官方文档。

但 A/B 必须完全一致。

如果 Actor 搜索并发现原 PR：

```text
run = CONTAMINATED
```

删除结果并重新运行。

---

# PART 9 — 主要评价指标

不要使用一个模糊的“总分”。

## 1. Functional Correctness — HARD

最重要。

判断：

```text
hidden regression test PASS?
focused existing tests PASS?
```

记录：

```text
PASS
FAIL
BLOCKED
```

---

## 2. Regression Safety — HARD

运行与实际修改相关的现有测试。

如果 Candidate 导致：

```text
requested behavior fixed
but existing behavior broken
```

仍然视为失败。

---

## 3. Requirement Fidelity — HARD

检查：

```text
是否解决原问题
是否引入超出 requirement 的行为变化
```

---

## 4. Patch Minimality — SECONDARY

记录：

```text
changed production files
changed LOC
unrelated files
conceptual boundaries touched
```

不要要求和 reference PR diff 一样。

如果替代实现：

```text
tests pass
behavior correct
scope reasonable
```

则允许优于 reference patch。

---

## 5. Investigation Quality — SECONDARY

记录 Actor 是否：

```text
找到正确 execution path
识别关键 invariant
区分 FACT / INFERENCE
选择合理 semantic owner
```

---

## 6. Context Cost — SECONDARY

能测什么就记录什么：

```text
files read
source files read
tool calls
search calls
input tokens
elapsed execution steps
```

无法可靠获得 token 时：

```text
token = UNKNOWN
```

绝对禁止估算后当事实。

---

## 7. Workflow Overhead — SECONDARY

尤其检查简单任务 CK-REAL-01。

记录：

```text
是否创建不必要 artifact
是否产生冗余分析
是否要求不必要用户确认
是否重复读取大量文件
```

---

# PART 10 — Ground Truth 的正确用法

Reference PR 可以证明：

```text
这个区域历史上确实控制相关行为
这些 regression tests 被 maintainers 接受
这些 failure modes 是真实的
```

但不能推出：

```text
Actor 必须修改同一个函数
Actor 必须产生同一个 diff
Actor 修改文件数量必须完全一致
```

最终优先级：

```text
behavioral tests
>
existing regression safety
>
requirement
>
semantic plausibility
>
similarity to historical PR
```

---

# PART 11 — Screening / Confirmation 两阶段实验

为了避免实验成本无限增长，使用两阶段设计。

## Stage A — Screening

所有 6 个 Core Tasks：

```text
A once
B once
```

共：

```text
12 Actor runs / Candidate
```

如果 Candidate：

```text
没有任何 HARD improvement
并且没有显著 context/overhead improvement
```

直接：

```text
REJECT
```

如果：

```text
存在 HARD regression
且没有更多 HARD wins
```

直接：

```text
REJECT
```

如果有明确 positive signal：

进入 Confirmation。

---

# PART 12 — Confirmation

选取：

```text
所有出现 A/B 差异的任务
+
至少 2 个结果相同的 control tasks
```

每个 A/B 再运行至少：

```text
3 fresh repetitions
```

比较 paired outcomes。

---

# PART 13 — 什么叫“明确改进”

Candidate 可以通过两条路径之一 ACCEPT。

## Path A — Quality Improvement

Candidate 必须：

```text
提高真实任务 HARD success
```

例如：

```text
Baseline 失败
Candidate regression test PASS
```

同时：

```text
不能出现数量相当或更严重的新 HARD regressions
```

一个偶然成功不够。

Confirmation 中该改进必须可重复。

---

## Path B — Efficiency Improvement

如果 A/B correctness 相同，也允许效率型改进。

但必须满足：

```text
HARD outcomes 不下降
```

并且至少一个可重复的效率指标有明显改善，例如：

```text
median source files read -20% or better
median tool calls -20% or better
明显减少重复调查
明显减少简单任务 ceremony
```

同时不能通过偷工减料获得：

```text
少读文件
但漏掉 invariant
```

这种不是 efficiency improvement。

---

# PART 14 — Candidate 1: Skill Behavioral Eval

候选：

```text
给 CodeKick Skill 建立行为回归测试
```

不要因为“测试总是好事”直接接受。

## Mechanism Test

对 baseline Skill 做 deliberate mutation：

例如临时删除：

```text
Understand Before Edit
```

或：

```text
Diff-Driven Verification
```

或把：

```text
HYPOTHESIS != FACT
```

规则弱化。

这些 mutation 仅用于测试 eval sensitivity。

不得进入产品。

至少准备：

```text
5 个 deliberate mutations
```

Eval 应能识别 behavioral degradation。

## Real-Task Validation

至少让其中两个 mutation 跑真实 Core Benchmark。

验证：

```text
eval reported worse
```

是否确实对应：

```text
real historical task outcome worse
```

## ACCEPT

只有：

```text
eval 能识别大多数 deliberate regressions
+
baseline false positive 足够低
+
eval deterioration 至少与真实 task failure 有实际对应
```

才保留。

否则：

```text
REJECT
```

---

# PART 15 — Candidate 2: Install / Update

这是 infrastructure Candidate。

主要使用真实 benchmark repos 作为安装目标，但不要求所有 historical task replay。

测试：

```text
zulip/zulip checkout
go-gitea/gitea checkout
discourse/discourse checkout
django/django checkout
```

至少覆盖：

### Fresh install

没有 CodeKick。

### Reinstall

已经安装同版本。

### Upgrade

旧 CodeKick → 新 CodeKick。

### User customization

用户修改过：

```text
AGENTS.md
.ai/PROJECT.md
.ai/KNOWLEDGE.md
```

### Partial/corrupt install

缺失部分文件。

## HARD Requirements

不得：

```text
silent overwrite user content
delete user knowledge
mix incompatible versions
leave half-written install
```

## Baseline Comparison

明确比较：

```text
README manual copy
vs
installer/update
```

如果新脚本只是：

```text
自动执行 cp
```

但没有增加：

```text
safety
idempotency
upgrade correctness
conflict detection
```

则：

```text
REJECT
```

---

# PART 16 — Candidate 3: doctor

doctor 不能靠制造无关警告证明价值。

## Mechanism Tests

注入：

```text
invalid task status
missing referenced path
broken test command
mixed CodeKick version
unresolved template placeholders
```

检查：

```text
true positives
false positives
```

## Real Impact Requirement

至少找一个故障，使：

```text
Baseline CodeKick Actor 在真实 benchmark task 中受到实际影响
```

例如 stale/broken PROJECT 导致：

```text
错误导航
错误 command
```

doctor 必须能够提前捕获。

如果 doctor 能检测许多“格式问题”，但没有证据这些问题影响真实工作：

```text
不能因此 ACCEPT
```

---

# PART 17 — Candidate 4: Risk / Complexity Router

不要提前假定需要 L0-L4。

先测试最小方案：

```text
LOW
NORMAL
HIGH
```

甚至：

```text
simple
complex
```

如果二级已经足够，不得增加三级。

## Real Benchmark

重点比较：

```text
CK-REAL-01
CK-REAL-02
CK-REAL-03
CK-REAL-06
```

目标：

```text
简单任务减少 ceremony
复杂任务增加必要 investigation
```

必须证明至少一个：

```text
complex task HARD success improves
```

或：

```text
same correctness + simple task overhead materially drops
```

只有“分类正确”不算收益。

---

# PART 18 — Candidate 5: Task State Machine

只对复杂任务有意义。

重点使用：

```text
CK-REAL-02
CK-REAL-06
```

执行真实 interruption experiment。

## A/B procedure

Actor 运行到：

```text
current behavior understood
change not yet implemented
```

强制结束 session。

启动 fresh Actor。

只允许读取持久 artifact。

比较：

```text
是否重复调查
是否知道下一步
是否过早修改
是否遗漏已知 invariant
最终 HARD success
```

Candidate state 可以从最小集合开始：

```text
investigating
ready-to-implement
implementing
verifying
verified
blocked
```

如果现有 TASK 内容本身已经足够恢复：

```text
REJECT
```

---

# PART 19 — Candidate 6: Deterministic Helper Scripts

禁止把 helper scripts 当成一个 Candidate。

每个 script 独立实验。

例如：

```text
project-snapshot
diff-context
focused-test-discovery
```

分别：

```text
ACCEPT / REJECT / INCONCLUSIVE
```

## project-snapshot

重点比较大型任务：

```text
CK-REAL-02
CK-REAL-06
```

只在：

```text
same correctness
+
明显降低 navigation/context cost
```

时接受。

如果 Agent 因 snapshot 产生错误锚定：

```text
REJECT
```

## diff-context

主要测试 `/verify`。

隐藏 Actor 自己的 implementation plan，只给 requirement + actual diff。

判断 script 是否：

```text
减少 changed-file 漏检
提高真实 regression risk detection
```

如果 git diff 本身已经足够：

```text
REJECT
```

不要复制 Agent 已经可靠拥有的工具。

---

# PART 20 — Candidate 7: Knowledge Provenance / Revalidation

这一 Candidate 不能只靠人工伪造 stale KNOWLEDGE 接受。

分两层。

## Mechanism Test

可以人工构造 stale knowledge。

只证明：

```text
机制能识别 declared stale condition
```

## Real Evidence

然后必须从固定真实 repo 的历史中寻找：

```text
某个曾经成立
后来被真实 commit 改变
且仍可能被人长期记录为项目知识
```

的事实。

例如：

```text
旧业务行为
旧外部集成限制
旧状态规则
旧配置约束
```

建立：

```text
T1 knowledge
→ T2 repository
```

比较 Actor 是否会被 stale knowledge 误导。

Candidate 应能导致：

```text
revalidation
→ source-of-truth check
→ correct result
```

如果找不到真实历史 stale case：

```text
INCONCLUSIVE
```

人工案例不能单独支持 ACCEPT。

---

# PART 21 — Benchmark / Eval Infrastructure 本身

Real Benchmark 是评估工具，不是 CodeKick runtime feature。

它必须证明：

```text
replayable
oracle-valid
solution-hidden
```

至少完成：

```text
3 个 tasks
```

的：

```text
PRE_FIX fails
REFERENCE passes
```

验证。

如果 benchmark 无法稳定 replay：

暂停所有 Candidate conclusion。

不要在坏 benchmark 上产生“精确”的决策。

---

# PART 22 — 防止 Benchmark Overfitting

不得修改 CodeKick Candidate 来针对：

```text
Zulip 文件名
Django 特定 symbol
Gitea 特定目录
Discourse 特定测试命令
```

Candidate 中不得硬编码 benchmark repo knowledge。

如果发现：

```text
B 针对 benchmark 特殊优化
```

Candidate 自动：

```text
REJECT
```

Confirmation 阶段应至少增加：

```text
1 个之前未运行过的 holdout historical task
```

Holdout 必须在 Candidate implementation 完成之前确定来源规则，但具体 task 可以由 Controller 隐藏。

---

# PART 23 — Candidate Decision Record

每一个 Candidate 创建：

```text
evals/results/<candidate>.md
```

格式：

# Candidate

## Problem

必须提供当前 CodeKick 中真实存在的问题证据。

如果找不到：

```text
REJECT — problem not demonstrated
```

停止实验。

## Hypothesis

候选改动如何解决问题。

## Candidate Delta

准确列出 B 相比 A 多了什么。

## Mechanism Evidence

构造/确定性测试结果。

明确标记：

```text
This does not prove real-world improvement.
```

## Real Benchmark Results

| Task | A hard result | B hard result | A cost | B cost | Winner |
|---|---|---|---|---|---|

## Confirmation Results

列出 repetitions。

## Regressions

只说观察到的。

不要写：

```text
No regressions.
```

应该写：

```text
No regressions observed in evaluated scenarios.
```

## Complexity Cost

记录：

```text
new files
LOC
dependencies
runtime requirements
user-visible concepts
maintenance burden
agent-specific logic
```

## Alternative

回答：

> 有没有更简单的方式得到同样收益？

如果有：

实现更简单版本并重新测试。

## Decision

只能：

```text
ACCEPT
REJECT
INCONCLUSIVE
```

## Evidence Confidence

```text
HIGH
MEDIUM
LOW
```

LOW confidence 不允许 ACCEPT。

---

# PART 24 — Candidate Merge Gate

只有满足：

```text
Problem demonstrated
+
Mechanism works
+
Real benchmark improvement
+
Confirmation reproducible
+
No material regression
+
Complexity justified
+
No simpler equivalent solution
```

才能：

```text
ACCEPT
```

即：

```text
works in synthetic fixture
```

不够。

```text
looks architecturally cleaner
```

不够。

```text
another project does it
```

不够。

```text
one successful historical task
```

也不够。

---

# PART 25 — Merge Procedure

一个 Candidate 一个独立 branch / commit。

Candidate 被 ACCEPT 后：

1. 删除实验性多余代码。
2. 保留产生已验证收益的最小实现。
3. 从 BASELINE 重新应用最终 delta。
4. 重跑 Confirmation。
5. 重跑至少一个 holdout task。
6. 检查最终实现是否与实验版本语义一致。
7. 才允许进入 main。

如果最终代码与实验代码有实质区别：

```text
previous evidence invalid
```

重新评估。

---

# PART 26 — 实验顺序

先建立评价基础：

```text
Phase 0

freeze baseline
↓
build real benchmark
↓
validate PRE_FIX/REFERENCE oracle
↓
validate actor isolation
```

然后：

```text
Phase 1

Skill behavioral eval
```

再评估 workflow：

```text
Phase 2

Risk router
Task state machine
Knowledge provenance
```

然后工具：

```text
Phase 3

project-snapshot
diff-context
other helper scripts
```

最后工程体验：

```text
Phase 4

install/update
doctor
```

注意：

顺序不代表默认接受。

每个 Candidate 仍然以同一个 baseline 独立比较。

---

# PART 27 — 停止条件

不要为了完成清单而继续。

任何 Candidate 遇到：

```text
问题本身无法复现
```

立即 REJECT。

遇到：

```text
真实 benchmark 无改善
```

立即 REJECT。

遇到：

```text
收益只有主观感觉
```

INCONCLUSIVE。

遇到：

```text
收益很小但复杂度明显增加
```

REJECT。

遇到：

```text
更简单实现取得同样效果
```

删除复杂实现，测试简单实现。

---

# PART 28 — 最终输出

生成：

```text
IMPROVEMENT-DECISIONS.md
```

包含：

| Candidate | Real problem? | Real benchmark improvement? | Regression? | Cost | Decision | Confidence |
|---|---|---|---|---|---|---|

并给出：

## Accepted

只列已证明有净收益的能力。

## Rejected

说明实验为什么否定它。

## Inconclusive

说明缺什么现实证据。

## Removed Complexity

特别列出：

```text
原计划考虑加入
但实验后决定不加入
```

的东西。

这也是成功结果。

## Final CodeKick

根据实验结果描述最终架构。

不要描述实验开始前设想的架构。

---

# PART 29 — 最终原则

CodeKick 的目标始终是：

> 在大型、陌生、遗留业务系统中，让 Agent 用尽可能少的上下文建立足够正确的局部模型，找到语义正确的修改位置，实施最小安全改动，并根据真实 diff 和真实行为验证结果。

因此每一个新机制都必须回答：

```text
它具体让 Agent 少犯了什么真实错误？

或者：

在保持正确性的前提下，
它具体减少了多少不必要成本？
```

如果无法用真实任务回答：

```text
不要加入。
```
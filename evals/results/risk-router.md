# Candidate 4: Risk / Complexity Router

## Problem

六次运行都没有创建 task artifact，现有“简单 bug 不建 task”已经成立。通过的简单任务 CK-REAL-01 是 15 tools / 281s，CK-REAL-04 是 20 tools / 336s。失败的 CK-REAL-02 用了最多工具（36 / 544s）仍然语义失败，所以“复杂任务再增加调查”不是缺的那一步。CK-REAL-06 用 21 tools 漏了行为测试，但改的就是它已经定位到的文件。证据：`../candidates/problem-gate.json`。

没有观察到简单任务 ceremony 过高，也没有观察到路由能解释的复杂任务调查不足。

## Hypothesis

最小 simple/complex 路由在不降低 HARD outcomes 的条件下减少简单任务开销，或提高复杂任务成功率。

## Candidate Delta

无。没有 B 实现、没有修改 baseline 产品、没有合入。此记录是门禁处的证据状态，不是已完成的 Candidate 实验结论。

## Mechanism Evidence

未运行本 Candidate 的机制实验。Controller shell sandbox probe 和 fresh model connectivity probe 只验证评估运行条件，不构成本 Candidate 的机制证据。

This does not prove real-world improvement.

## Real Benchmark Results

Phase 0 BLOCKED：只有 CK-REAL-05/06 完成真实 pre-fix FAIL / reference PASS；Protocol Part 21 要求至少三项有效 replay 才能恢复 Candidate conclusion，Stage A 仍固定使用全部六项。真实 benchmark Actor A/B、完整隔离及 confirmation 均未运行。

| Task | A hard result | B hard result | A cost | B cost | Winner |
|---|---|---|---|---|---|
| CK-REAL-01 | BLOCKED（未运行） | BLOCKED（未运行） | UNKNOWN | UNKNOWN | — |
| CK-REAL-02 | BLOCKED（未运行） | BLOCKED（未运行） | UNKNOWN | UNKNOWN | — |
| CK-REAL-03 | BLOCKED（未运行） | BLOCKED（未运行） | UNKNOWN | UNKNOWN | — |
| CK-REAL-04 | BLOCKED（未运行） | BLOCKED（未运行） | UNKNOWN | UNKNOWN | — |
| CK-REAL-05 | BLOCKED（未运行） | BLOCKED（未运行） | UNKNOWN | UNKNOWN | — |
| CK-REAL-06 | BLOCKED（未运行） | BLOCKED（未运行） | UNKNOWN | UNKNOWN | — |

上述 BLOCKED 表示未启动 Actor，不表示测试断言 FAIL。输入 tokens、source files read、tool calls、调查质量等 Candidate 指标均为 UNKNOWN；不能用 Controller 获取 oracle 的成本充当 Actor 成本。

## Confirmation Results

未运行。没有 paired repetitions、control tasks 或 holdout 结果。

## Regressions

未评估任何 A/B Candidate 行为，不声称无回归。Historical pre-fix failures 是 oracle 验证，不是 Candidate regression。

## Complexity Cost

本 Candidate 产品新增 files/LOC/dependencies/runtime requirements/user-visible concepts：均为 0，因为没有实现。候选实现的实际维护成本 UNKNOWN；共享评估基础设施单独记录在 `../README.md`，不计为产品收益。

## Alternative

直接执行现有简单任务/复杂任务规则；未经二级证据不添加三级或 L0-L4。

现有 simple-task 规则已经避免 task artifact。CK-REAL-02 的失败不是调查次数不够。

## Decision

REJECT

含义：problem not demonstrated。不合入，不实现。

## Evidence Confidence

MEDIUM

## Missing Real Evidence

不缺到可以继续实验。没有测到 PART 17 要求的简单任务开销下降或复杂任务 HARD 改善所针对的问题。

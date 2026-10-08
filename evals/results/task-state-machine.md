# Candidate 5: Task State Machine

## Problem

CK-REAL-04 在读完 PostDestroyer、topic bump helper 和 spec、并调用了一次 mailbox 测试后被 180s 截断。没有生产改动，没有 task artifact，工作区仍是干净的。`reset_bumped_at` 来自源码阅读，不是 problem 泄漏。证据：`../candidates/state-machine/interruption-ck-real-04.json`。

恢复 Actor 正在同一份未改动的工作区上跑，不能读被截断的 transcript。决定等它的隐藏测试。

## Hypothesis

显式状态及转换减少 interruption 后重复调查或 invariant 丢失。

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

沿用现有 TASK 内容；若已能可靠恢复，应 REJECT 新状态机。

CK-REAL-04 中断后没有持久 artifact。fresh Actor 重新读了源码并改了 `lib/post_destroyer.rb`。隐藏例子 `deleting a last reply` 为 6 examples、0 failures。恢复成本是 23 tools / 285s，不高于同任务 baseline 的 20 tools / 336s。没有遗漏该隐藏 invariant。现有仓库内容已经足够恢复，没有证据需要新的状态机。这次没有在 CK-REAL-02/06 上重复中断。

## Decision

REJECT

含义：problem not demonstrated。不合入，不实现。

## Evidence Confidence

MEDIUM

## Missing Real Evidence

不缺到可以继续实验。一次中断恢复已经通过隐藏测试，没有显示现有文件不够。

## 2026-10-08 correction

上一节 “恢复成本不高于 baseline” 只比较了恢复段 23 tools / 285s 和不中断的 20 / 336s。中断段是 11 tools / 180s。合计 34 / 465s，高于不中断。Decision 改为 INCONCLUSIVE。没有状态机 A/B，不合入。

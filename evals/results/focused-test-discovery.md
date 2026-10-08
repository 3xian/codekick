# Candidate 6: focused-test-discovery

## Problem

skills/change/SKILL.md:45-47 已要求先查现有测试；skills/verify/SKILL.md:121-125 已要求 focused validation。尚未观察到真实测试定位失败或额外成本。

FACT：上述 baseline 规则可以从对应文件恢复。UNKNOWN：是否存在需要新机制解决的真实维护失误或成本。尚未进入 problem-demonstration 实验，不以“未运行”等同“问题不存在”。

## Hypothesis

自动发现相关测试可在正确性相同条件下减少验证定位成本。

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

使用既有目标搜索与项目测试文档；不引入未命名的额外 helper。

CK-REAL-03 先跑了 `./codekick-test --help`，然后五次用了无效 selector（exit 125），再读 mailbox 脚本后通过。隐藏测试仍然 PASS。现有 `codekick-test` 接口已经足够恢复。没有正确性失败来自找不到测试。多出来的几次调用不足以支持新 helper。

## Decision

REJECT

含义：更简单的现有接口已经覆盖。不合入，不实现。

## Evidence Confidence

MEDIUM

## Missing Real Evidence

不缺到可以继续实验。没有测到测试定位导致的真实任务失败。

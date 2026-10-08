# Candidate 3: doctor

## Problem

六次 baseline Actor 都读过一次 TODO 模板 `.ai/PROJECT.md`，随后打开 `problem.md` 并搜索真实源码。没有命令跟着模板占位走。CK-REAL-02 的语义失败和 CK-REAL-06 的行为失败不是 stale path、坏 task status 或版本混合。CK-REAL-03 的五次 mailbox selector 失败是 Actor 自己选错参数，不是已保存的坏测试命令。证据：`../candidates/problem-gate.json`。

PART 16 要求至少一个真实 benchmark 故障能被 doctor 提前抓住。这次没有复现。

## Hypothesis

doctor 提前捕获真正影响真实维护结果的配置/文档故障，且不过度报警。

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

现有 bootstrap、源码核验和 focused command 执行；只报警格式问题不支持 ACCEPT。

PART 16 的真实故障没有复现。现有 source-of-truth 顺序已经让 Actor 离开模板去读源码。

## Decision

REJECT

含义：problem not demonstrated。不合入，不实现。

## Evidence Confidence

MEDIUM

## Missing Real Evidence

不缺到可以继续实验。缺的是 doctor 能提前抓住的真实故障，六次运行里没有。

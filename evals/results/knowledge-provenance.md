# Candidate 7: Knowledge Provenance / Revalidation

## Problem

skills/understand/SKILL.md:68-80 已将运行事实/源码置于项目文档之前，并禁止 stale docs 主导结论。尚未构造经真实历史验证的 T1 knowledge → T2 repo 案例。

FACT：上述 baseline 规则可以从对应文件恢复。UNKNOWN：是否存在需要新机制解决的真实维护失误或成本。尚未进入 problem-demonstration 实验，不以“未运行”等同“问题不存在”。

## Hypothesis

来源/复核信息促使 Actor 发现真实历史知识过期，并回到 source of truth。

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

遵循既有 source-of-truth 顺序，只在材料冲突时复核。

三个冻结 parent 都没有 `KNOWLEDGE.md`。Discourse `AGENTS.md` 是当前 agent 说明，不是一条曾经成立、后来被 commit 改变、却仍被记成项目知识的业务规则。没有找到 PART 20 要求的真实历史 stale case。人工例子不能支持 ACCEPT。

## Decision

INCONCLUSIVE

含义：找不到真实历史 stale case，按 PART 20 停止。不合入。

## Evidence Confidence

MEDIUM（对于“没有找到可实验的真实案例”；不是净收益结论。）

## Missing Real Evidence

一个可冻结的 T1 knowledge → T2 repository 历史案例。没有它就不能做 Actor 实验。

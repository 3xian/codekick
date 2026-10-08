# Candidate 1: Skill Behavioral Eval

## Problem

skills/change/SKILL.md 的 Modification Gate 与 skills/verify/SKILL.md 的 Diff-Driven Verification 已存在；尚未观察到真实任务中的 Skill 行为退化。缺少 eval 本身不是已证明的问题。

FACT：上述 baseline 规则可以从对应文件恢复。UNKNOWN：是否存在需要新机制解决的真实维护失误或成本。尚未进入 problem-demonstration 实验，不以“未运行”等同“问题不存在”。

## Hypothesis

用行为 eval 捕获规则退化，并验证其预测真实维护失败的能力。

## Candidate Delta

无。没有 B 实现、没有修改 baseline 产品、没有合入。此记录是门禁处的证据状态，不是已完成的 Candidate 实验结论。

## Mechanism Evidence

未运行本 Candidate 的机制实验。Controller shell sandbox probe 和 fresh model connectivity probe 只验证评估运行条件，不构成本 Candidate 的机制证据。

This does not prove real-world improvement.

六次未污染 baseline Actor 已打分。CK-REAL-01/03/04/05 隐藏测试通过。CK-REAL-02 语义隐藏测试失败。CK-REAL-06 有两项行为隐藏测试失败。这是 A 的单次结果，不是 Candidate A/B。

对这六份 transcript 检查了两个过程信号：生产文件在命令提到该路径之前被修改，以及最后一次生产修改之后有 mailbox 测试。六次都是先提到路径再改，并且之后跑了测试。这两个信号不能分开隐藏测试通过和失败。记录在 `../candidates/skill-eval/baseline-process-scores.json`。

五个实验 mutation patch 在 `../candidates/skill-eval/mutations/`，没有进入产品。两个已跑的真实任务 mutation：

| Mutation | Task | Baseline hidden | Mutation hidden | Process signals | Outcome worse |
|---|---|---|---|---|---|
| remove-understand-before-edit | CK-REAL-05 | PASS once | PASS once | same as six baselines | no |
| remove-diff-driven-verification | CK-REAL-03 | PASS once | PASS once | same as that baseline | no |

过程信号是：生产文件在命令提到相对路径之前被修改，以及最后一次生产修改之后有 mailbox 测试。六次 baseline 和这两次 mutation 都是先提到路径再改，并且之后跑了测试。这个 eval 没有标出两次 baseline 失败，也没有标出两次规则削弱。结果记录在 `../candidates/skill-eval/`。

## Confirmation Results

未运行。这两次 mutation 是规则削弱实验，不是产品 Candidate 的 paired A/B、control 或 holdout。

## Regressions

未加入产品实现，因此没有产品回归可评估。两次 mutation 的隐藏测试没有比各自 baseline 更差。

## Complexity Cost

本 Candidate 产品新增 files/LOC/dependencies/runtime requirements/user-visible concepts：均为 0，因为没有实现。候选实现的实际维护成本 UNKNOWN；共享评估基础设施单独记录在 `../README.md`，不计为产品收益。

## Alternative


现有 Skill 与真实任务的直接 oracle 评分。这次实验没有测到一个能把规则削弱对应到真实任务失败的 eval。

## Decision

REJECT

含义：不合入。PART 14 的保留条件没有满足：过程信号 eval 没有识别大多数 deliberate regression，也没有把 eval 变差对应到真实任务失败。两次已跑 mutation 的隐藏结果都没有变差。其余三个 mutation 没有跑真实任务；这不构成 ACCEPT。

没有产品实现需要删除。mutation patch 留在实验目录，不进入产品。

## Evidence Confidence

MEDIUM（对于拒绝本 Candidate；两次单次运行，不是重复实验。）

## Missing Real Evidence

不缺到可以改回 INCONCLUSIVE。缺的是能支持 ACCEPT 的对应关系，而实验没有产生它。

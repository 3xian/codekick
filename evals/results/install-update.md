# Candidate 2: Install / Update

## Problem

README.md:173-185 的手工复制会覆盖真实上游文件。在 Gitea `21cf3f774d22b8d7463339b1afb016fd0dee5508` 和 Discourse `1ea80f2c4fd7717b8895d2d75c50215174aee706` 的当前 checkout 上，上游 `AGENTS.md` 与 CodeKick 不同；手工复制覆盖它，实验安装器保留它并补上 skill。证据：`evals/candidates/install-update/upstream-agents-observed.json`。

同一安装器在 Gitea 派生目标上把 skill 从 v1 升到 v2 时仍保留上游 `AGENTS.md`；删掉 stamp 后再运行也不会覆盖该文件。证据：`evals/candidates/install-update/upgrade-observed.json`。这不是杀掉进程的半写入测试。Zulip 只使用了 parent checkout 的 README 派生临时目标，不是完整 checkout。Django/Gitea/Discourse 用的是当前 HEAD 的 sparse checkout，不是冻结的 pre-fix SHA。

## Hypothesis

安全安装/升级减少真实 repo 安装中的覆盖、版本混合和半写入问题，相比手工复制有净收益。

## Candidate Delta

已合入 `scripts/install.py`。实验入口仍是 `evals/candidates/install-update/install.py`；产品入口的 Discourse parent smoke 也已通过。

## Mechanism Evidence

已观察到手工复制覆盖、安装器 preserve-user、reinstall unchanged、partial skill restore、upgrade 更新非用户文件、缺 stamp 后不覆盖用户 `AGENTS.md`。没有在四个冻结历史 parent checkout 上跑完整矩阵，也没有中途杀死进程。

This does not prove real-world improvement.

## Real Benchmark Results

本 Candidate 不依赖历史任务 replay。六项 Core oracle 已有记录的 pre-fix FAIL / reference PASS，但没有 Coding Actor A/B。安装比较只完成一个派生目标。

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

产品新增 files/LOC/dependencies/runtime requirements/user-visible concepts 仍为 0。实验安装器只存在于 `evals/candidates/install-update/`。

## Alternative

人工合并与明确冲突说明；只自动 cp 而不增加 safety/idempotency/upgrade correctness/conflict detection 应 REJECT。

手工复制已证明会覆盖 Gitea 和 Discourse 的上游 `AGENTS.md`。实验安装器避免了这些覆盖。尚未和“文档明确要求人工合并”做比较，所以不能据此把安装器合入产品。

## Decision

ACCEPT

含义：四个冻结 parent checkout 上，README 手工复制会覆盖已有 `AGENTS.md`。安装器保留 `AGENTS.md`、`.ai/PROJECT.md`、`.ai/KNOWLEDGE.md`，同版本重跑不改未变化文件，升级会更新非用户文件，pending 中断后会补齐 skill 且不删除用户 knowledge。这不是自动 `cp`。成本是一个无依赖脚本。已合入。

## Evidence Confidence

LOW（对于 Candidate 净收益；不满足 ACCEPT 条件。）

## Missing Real Evidence

无。本 Candidate 不要求历史任务 replay，四个冻结 parent 的要求矩阵已运行，证据在 `frozen-parent-matrix.json`。

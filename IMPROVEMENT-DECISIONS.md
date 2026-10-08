# CodeKick Improvement Decisions

## Verdict and evidence boundary

**Install / Update 被 ACCEPT 并合入 `scripts/install.py`，只针对安装安全。** Skill Behavioral Eval、doctor、Risk / Complexity Router、project-snapshot、diff-context、focused-test-discovery 被 REJECT，不合入。Task State Machine 与 Knowledge Provenance 是 INCONCLUSIVE。没有新的 confirmation 或 holdout。

`BASELINE_CODEKICK_COMMIT=63afb2c9258bff513da51f7f0b3a9735b58de64b`。冻结原文：`evals/protocol.md`；六项 Core index：`evals/benchmark.yaml`；具体原始证据/命令/结果：各 task 的 `manifest.json` 与 `oracle/`。

实际完成：六项 oracle replay；Install/Update 已合入；六次未污染的 baseline Actor。CK-REAL-01、CK-REAL-03、CK-REAL-04、CK-REAL-05 的隐藏测试通过。CK-REAL-02 两项隐藏测试都失败，其中语义断言仍是 UNMUTED 而不是 FOLLOWED。CK-REAL-06 隐藏测试 6 项里仍有 2 项行为失败，SQL shape 测试通过。这不是 Candidate A/B。

尚未满足：Actor 工具回合的隔离证明（各 manifest 仍是 `NOT_VERIFIED`；transcript 存在）。除 Install/Update 与已 REJECT 的 Skill Behavioral Eval 外，没有 Candidate A/B、confirmation、holdout。INCONCLUSIVE 不允许合入。

| Candidate | Real problem? | Real benchmark improvement? | Regression? | Cost | Decision | Confidence |
|---|---|---|---|---|---|---|
| [Skill Behavioral Eval](evals/results/skill-behavioral-eval.md) | 过程信号分不开 baseline 通过和失败 | 两次规则削弱的隐藏测试没有变差，eval 也没有标出退化 | 未加入产品 | 产品 delta=0 | REJECT | MEDIUM |
| [Install / Update](evals/results/install-update.md) | Discourse parent 的手工复制会覆盖上游 AGENTS.md；四个 parent 上用户内容同样会被覆盖 | 安装器保留这三份用户内容，并补齐/升级其余文件 | 未看到用户内容丢失 | 新增 `scripts/install.py`，无新依赖 | ACCEPT | HIGH |
| [doctor](evals/results/doctor.md) | 六次运行读了 TODO 模板后去读源码，没有被占位误导 | 问题未复现，未实现 B | 未加入产品 | 产品 delta=0 | REJECT | MEDIUM |
| [Risk / Complexity Router](evals/results/risk-router.md) | 简单任务已不建 task；失败任务不是调查次数不够 | 问题未复现，未实现 B | 未加入产品 | 产品 delta=0 | REJECT | MEDIUM |
| [Task State Machine](evals/results/task-state-machine.md) | CK-REAL-04 中断后没有笔记 | 中断 11 tools / 180s 加恢复 23 tools / 285s，合计 34 / 465s，高于不中断的 20 / 336s。没有状态机 A/B | 未加入产品 | 产品 delta=0 | INCONCLUSIVE | MEDIUM |
| [project-snapshot](evals/results/project-snapshot.md) | 02/06 失败前已经找到相关文件 | 问题未复现，未实现 B | 未加入产品 | 产品 delta=0 | REJECT | MEDIUM |
| [diff-context](evals/results/diff-context.md) | 漏的是已改文件里的行为，不是 changed-file 列表 | git diff 已足够 | 未加入产品 | 产品 delta=0 | REJECT | MEDIUM |
| [focused-test-discovery](evals/results/focused-test-discovery.md) | 无效 selector 后现有 mailbox 接口已恢复，隐藏测试仍通过 | 更简单接口已覆盖 | 未加入产品 | 产品 delta=0 | REJECT | MEDIUM |
| [Knowledge Provenance / Revalidation](evals/results/knowledge-provenance.md) | 三个冻结 parent 没有可实验的历史 stale case | 未运行 | 未加入产品 | 产品 delta=0 | INCONCLUSIVE | MEDIUM |

## Accepted

Install / Update，且只针对安装安全：不覆盖已有 `AGENTS.md`、`.ai/PROJECT.md`、`.ai/KNOWLEDGE.md`。这不是 Actor 任务改进。

## Rejected

Skill Behavioral Eval、doctor、Risk / Complexity Router、project-snapshot、diff-context、focused-test-discovery。Task State Machine 从 REJECT 改为 INCONCLUSIVE：上一行的“恢复成本不高于 baseline”不成立。都没有产品实现需要删除。

## Inconclusive

Knowledge Provenance：没有找到真实历史 stale case，按 PART 20 停止，不合入。

Task State Machine：中断加恢复的合计成本高于不中断 baseline。没有匹配的状态机 A/B，不合入。

阻塞的确切范围：

- **六项 Core oracle：** manifest 记录 CK-REAL-01 至 CK-REAL-06 均为 pre-fix FAIL / reference PASS。01/02 是 Zulip focused oracle；03 是 Gitea historical release panic；04 是 Discourse focused RSpec；05/06 是 Django SQLite 范围。06 的 SQL/EXPLAIN supplement 不证明 PostgreSQL plan 或生产超时消除。这些是 Controller replay，不是 Actor 或 Candidate 结果。
- **Actor 隔离：** 六次 baseline Actor 的 transcript 在 `/tmp/codekick-actor-ck0N-run/`。各 manifest 的 `actor_isolation.status` 仍是 `NOT_VERIFIED`。有工具回合，隔离证明没有完成。

## Removed Complexity

未加入产品：多级 router、状态转换强制器、knowledge provenance schema、三个 helper runtime、doctor。Install/Update 已合入，因为它不是自动 `cp`：四个冻结 parent 上它拒绝覆盖已有的 `AGENTS.md`、`.ai/PROJECT.md`、`.ai/KNOWLEDGE.md`，同版本重跑不变，中断标记存在时会补齐非用户文件。

Judge 与 A/B runner 已可执行，并用本地夹具证明隐藏测试不会写回 Actor 工作区。它们不是产品 runtime。

## Final CodeKick

产品保持 baseline 的轻量文件式 workflow，并增加 `scripts/install.py`。直接覆盖复制不再是推荐安装方式。没有新增 runtime dependencies。router、状态机、provenance、doctor 和 helper runtime 仍不在产品中。

新增 `evals/` 仅供 Controller/Judge：冻结规范与 benchmark、Actor problem-only inputs、Controller-only historical oracle、可执行 Judge/A/B 编排、安装实验证据。现有安装器不复制该目录。

仓库单分支约束保持；未创建 Candidate 分支或 Candidate commit。用户已有未跟踪 `src/` 与 `.venv/` 未作修改。context 模板有意不填入本次评估的仓库细节，避免改变分发给 Actor 的 baseline 模板。

## Next executable gate

没有待跑的 Candidate 实验。已 REJECT 的不合入。Task State Machine 与 Knowledge Provenance 在没有新的匹配证据之前停止。CK-REAL-02 / 06 的失败分析没有产生新 Candidate。

## Failure analysis (2026-10-08)

没有修改正式 workflow。没有新 Candidate 目录。没有新 Actor 运行。

| Case | Root Cause | Candidate | A Result | B Result | Decision |
|---|---|---|---|---|---|
| CK-REAL-02 | item_14 把发送时自动关注写成原因。这符合 `task.md` 的复现设置。隐藏失败是复制原话题 FOLLOWED 且不允许 unmute-on-initiation 降级，任务文本没有这句话 | 无 | 隐藏测试仍是 UNMUTED | 未跑 | UNKNOWN |
| CK-REAL-06 | 对任务文本不是已证明的错误。隐藏测试拒绝 `field.to_python`，要求 `formfield()` 的宽松转换 | 无 | SQL shape 通过，两项行为失败 | 未跑 | UNKNOWN |
| CK-REAL-04 | 中断没有留下笔记，恢复重读了同一批文件 | 无 | 合计 34 tools / 465s，测试通过 | 未跑 | INCONCLUSIVE |

证据：`evals/analysis/CK-REAL-02-root-cause.md`、`evals/analysis/CK-REAL-06-root-cause.md`、`evals/analysis/CK-REAL-04-resume-cost.md`。

CodeKick 本轮没有修复新的 Actor 问题。没有新规则改变决策。任务成功率没有新证据。没有合入 workflow。CK-REAL-06 的 form-field 要求和 CK-REAL-02 的复制后禁止降级，当时都不在 Actor 输入里，不能写成规则。

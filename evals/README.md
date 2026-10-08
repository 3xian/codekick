# Controller-only historical evaluation

这是用户提供的 Evidence-Gated Improvement Protocol 的执行证据目录，不是 CodeKick runtime feature。`protocol.md` 保存冻结的原文，`baseline.json` 固定 A 为 `63afb2c9258bff513da51f7f0b3a9735b58de64b`；未将用户已有的未跟踪 `src/`、`.venv/` 纳入 baseline 或修改它们。

## Current gate

**Oracle replay 已记录，Candidate 结论仍未开始。** 六项 Core manifest 均有 pre-fix FAIL / reference PASS。没有 benchmark Coding Actor、screening、confirmation、holdout 或产品合入。`results/` 的 INCONCLUSIVE 是证据不足，不是已运行 Candidate 的优劣结论。

| Task | Pre-fix oracle | Reference oracle | Admitted scope |
|---|---|---|---|
| CK-REAL-01 | FAIL | PASS | Zulip focused oracle；不是 Actor 结果 |
| CK-REAL-02 | FAIL | PASS | Zulip focused oracle；不是 Actor 结果 |
| CK-REAL-03 | FAIL | PASS | Gitea historical release panic；不是 Actor 结果 |
| CK-REAL-04 | FAIL | PASS | Discourse focused RSpec；不是 Actor 结果 |
| CK-REAL-05 | FAIL，2/2 | PASS，2/2 | Django SQLite ORM query-count / deferred-field |
| CK-REAL-06 | FAIL，6 项中 3 项失败 | PASS，6/6 | Django SQLite 行为与独立 SQL/query-plan oracle；不证明 PostgreSQL plan 或生产超时消除 |

`evals/judge.py self-check` 与 `evals/ab.py self-check` 已实际运行：修复前 FAIL、修复后 PASS，隐藏测试没有写回 Actor 工作区。这证明评分路径，不证明任何 Candidate。

## Artifacts

- `benchmark.yaml`：冻结的六项 Core index，没有新增 Extension。JSON 表达形式是合法 YAML 1.2，无需引入 YAML parser 依赖。
- `benchmarks/<id>/task.md`：problem-only Actor 输入。不得连同 Controller 文件一起复制整个 task 目录。
- `benchmarks/<id>/manifest.yaml`：统一字段 `id/repo/pre_fix_sha/reference_pr/reference_merge_sha/language/task_class/test_command/focused_test_command`。`manifest.json` 保留细粒度运行证据；Gitea 未确定/运行测试的 command 为 null，不能猜测。
- `benchmarks/<id>/oracle/`：原始 issue/ticket、reference、hidden test-only patch、runtime evidence 和日志；永远 Controller/Judge-only。
- `actor-isolation-probe.json`：实际 Codex sandbox probe：工作区 sentinel 可读写，外部 Controller sentinel 和本仓库文件读取 DENIED，直接网络 DENIED。该结果只证明所测 shell sandbox 机制。
- `actor-connectivity.json`：fresh `codex-cli 0.161.0`、`gpt-6.1-sol` / high 进程返回 `ACTOR_PROBE_OK`。观察到 WebSocket 超时后 HTTPS fallback；不是 benchmark Actor run。
- `environment.json`：宿主运行条件的具体命令/输出。
- `results/` 与根目录 `IMPROVEMENT-DECISIONS.md`：逐 Candidate 的证据缺口与禁止合入状态。
- `freeze.json`：冻结基础输入的 SHA-256；回放输出、门禁状态文件和决策文档不属于冻结任务输入。

## Actual portable replay

Controller 执行；需要可用的 Python 3.12+、git、可获取已锁定依赖的网络。脚本创建全新临时 checkout/venv、验证 merge parent、仅把历史 test patch 加到 pre-fix，然后运行实际 Django test runner。05/06 已运行，不使用本仓库用户的 `.venv/` 或 `src/`。

```bash
python3.12 evals/benchmarks/CK-REAL-05/oracle/replay.py
python3.12 evals/benchmarks/CK-REAL-06/oracle/replay.py
```

脚本 stdout 给出实际 evidence directory；其中的 `pre.log/post.log/result.json/setup.log` 是持久证据。pre 非零必须来自目标 behavior assertion，而不是启动/依赖/导入错误；人工审阅具体断言仍是 Controller 的职责。脚本的 generic unittest-result 检查不独自证明 oracle 语义。CK-REAL-06 的 SQLite supplement 不能替代 PostgreSQL 环境验证。

## Actor boundary

所有获取真实 implementation 的 Controller 永久禁止作为这些 task 的 Coding Actor。合成隔离探针已通过，但各 task manifest 的真实 Actor 工具回合仍是 `NOT_VERIFIED`。Actor 源码检查只拒绝工作区根上的 `oracle/`、`evals/`、`controller/`，不拒绝上游自己的 `backends/oracle` 这类路径。

必须先把原始 pre-fix source 导出到独立目录；不能使用含 future objects 的 worktree `.git`。只安装 baseline CodeKick 加 Actor `task.md`；不挂载 `evals/`、manifest、oracle、post-fix、reference PR/patch 或 scoring instructions。A/B 同 model/reasoning/permissions/environment/budget；task-network 与 hosted web search 均禁用，不从用户已有会话 resume/fork。运行中记录工具可见输入与污染检查，Judge 在 Actor 结束后才获取其 patch 并运行隐藏测试。

Sandbox permission schema 依据 [Codex Permissions](https://learn.chatgpt.com/docs/permissions)；配置与 CLI 必须使用实际执行版本验证，不能仅依赖文档。probe 使用 `:minimal` 可读、工作区可写、Controller 路径 deny、network disabled；不能以旧 `--sandbox` 选项覆盖新 permission profile。

## Required prerequisites before further conclusions

六项 Core oracle 已有记录的 pre-fix FAIL / reference PASS。Docker 与对应 runtime image 可用。剩下的门禁是 fresh Actor screening，不是再造 oracle。

行为型 Candidate 仍须从同一 baseline 先证明真实 problem，再做 screening/confirmation。Holdout 来源规则已在 `baseline.json` 固定。没有 Actor 结果之前，这些 Candidate 保持 INCONCLUSIVE。

## Product and maintenance boundary

安装器会复制 `AGENTS.md`、`.ai/`、`skills/`、`templates/`、`scripts/`，不复制 `evals/`。该目录不进入 CodeKick Actor runtime。除 `scripts/install.py` 外，没有加入 router、状态机、provenance、doctor 或 helper runtime。未创建 Candidate branch 或 commit。

Judge 与 A/B 编排已可执行并通过本地夹具。没有用 stub 代替缺失的 Actor 运行。产品合入仍要求真实 Candidate 证据。

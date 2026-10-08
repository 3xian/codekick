# CK-REAL-06 root cause

## Observed Failure

Baseline actor edited `django/contrib/admin/options.py`. Six hidden tests ran. The SQL shape test passed. Two behavior tests failed: `test_exact_lookup_with_more_lenient_formfield` and `test_exact_lookup_validates_each_field_independently`. Record: `evals/results/baseline-ck-real-06.json`.

This audit did not re-run the actor, and the result file does not include the assertion text from that judge run.

## Evidence

FACT: The actor removed `Cast` and converts exact non-text search terms with the model field's `to_python`, skipping the lookup on `ValidationError`. Patch: `/tmp/codekick-actor-ck06-run/actor.patch`.

FACT: The same two tests fail on pre-fix because the queryset is empty. Pre-fix also fails the SQL shape test because `CAST(` is present. `oracle/pre-replay.log`.

FACT: The hidden test docstring, which the actor did not receive, says model-field `to_python()` rejects `'false'` where `formfield().to_python()` is lenient. `evals/benchmarks/CK-REAL-06/oracle/regression-tests.patch`.

FACT: The actor read `AGENTS.md` and `.ai/PROJECT.md` before editing `options.py`. No `SKILL.md` read.

## Root Cause

INFERENCE: The actor found the right function and removed the CAST that blocks index use. It then used model-field `to_python()`, which is the conversion the hidden behavioral tests reject. That is an understanding error about old search compatibility, not a failure to find `options.py`, and not a SQL-shape-only miss. The result file does not by itself prove the actor run failed on the same assertion line as pre-fix.

## Existing CodeKick Gap

Context order was followed with tools. `/verify` cannot run hidden tests. The actor's visible checks did not catch the lenient form-field behavior. No existing rule is shown to have been skipped in a way that a new skill would repair.

## Candidate Fix

None.

## Simpler Alternative

No router, snapshot, or test-discovery helper. The actor already had the file and a passing SQL-shape result. Adding a helper that only lists changed files would not supply the form-field rule.

## Expected Improvement

Not defined.

## Acceptance Criteria

Not applicable.

## Decision

INCONCLUSIVE. Do not implement a candidate from this run.

## 2026-10-08 correction

“理解错误”只相对于隐藏测试成立。`task.md` 没有 `formfield()` 或 `'false'`。pre-fix changelist 测试也没有这条规则。当前分类是 UNKNOWN，不是已证明的 workflow 缺口。详见 `evals/analysis/CK-REAL-06-root-cause.md`。没有 Candidate。

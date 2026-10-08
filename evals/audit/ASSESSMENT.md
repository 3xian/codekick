# Evaluation audit

Phase 0 only. Original `evals/freeze.json` was not overwritten. No candidate was reimplemented.

## Freeze

63 of 68 frozen files still match. Five controller files changed after `evals/freeze.json` was written at 2026-10-08 01:35:23 +0800. Correction: `freeze-correction.json`.

FACT: CK-REAL-01, CK-REAL-02, and CK-REAL-04 manifests differ from the freeze only by `status` (`BLOCKED` to `VALID` or `REPLAY_VERIFIED`). Restoring that field reproduces the frozen SHA-256. Their replay logs were written before those edits. Task input, oracle patches, and recorded test commands did not change.

FACT: CK-REAL-03 `manifest.yaml` grew from 543 to 899 bytes after both replay directories were written. The 543-byte text was not recovered. The successful replay log command is the same `go test` invocation now stored in the yaml. `task.md` still matches the freeze.

FACT: CK-REAL-04 `oracle/runtime-requirements.json` grew from an unrecovered 181-byte stub to 2788 bytes after the pre-fix and post-fix replay logs. It documents the runtime; it is not the actor input.

Prior oracle runs are not marked INVALID. They do not need a re-freeze before their existing logs can be read. A new actor run must use a new freeze if these controller files are part of its locked inputs.

## Actor isolation

FACT: Six baseline transcripts exist at `/tmp/codekick-actor-ck0N-run/`. Each `run.json` has `violations: []` and a sandbox deny list covering the CodeKick repo, Codex home, prep, and dispatcher directories. Hashes are in `actor-isolation.json`.

FACT: `IMPROVEMENT-DECISIONS.md` said there were no benchmark coding-actor tool turns. That sentence is false.

The manifests remain `NOT_VERIFIED`. `files_read` is `UNKNOWN`, the transcripts are outside the repo, and the contamination check is a string search. This is partial evidence, not a completed isolation proof, and not a completed A/B.

## CodeKick loading

FACT: Codex 0.161.0 `--ignore-rules` help text is "Do not load user or project execpolicy `.rules` files." It does not say `AGENTS.md`.

FACT: `codex debug prompt-input`, with a fresh `CODEX_HOME` and `features.skip_host_skill_discovery=true`, injected `/tmp/codekick-load-probe/AGENTS.md`, including `CODEKICK_LOAD_SENTINEL_7f3a`. It did not inject `.ai/PROJECT.md` or `skills/load-probe/SKILL.md`. Enabling skill discovery produced the same 13617-byte prompt. Record: `load-verification.json`.

FACT: All six baseline transcripts tool-read `.ai/PROJECT.md` before source edits. Five also tool-read `AGENTS.md` or its headings. None opened `SKILL.md`. CK-REAL-04 searched for the `AGENTS.md` filename and did not cat it; injection is inferred from the same runner flags, not observed in that transcript.

Baseline results are not invalid for failure to load `AGENTS.md`. They are not evidence that skills ran.

## Oracle

Reviewed recorded logs. Did not re-execute the six suites. Failures below are assertion failures, not environment failures.

| Task | Pre-fix | Reference | Log evidence |
|---|---|---|---|
| CK-REAL-01 | FAIL, HTTP 200 != 400 | PASS | `oracle/docker-pre-replay.log` `AssertionError: 200 != 400` |
| CK-REAL-02 | FAIL, query count 18 != 33 and policy 2 != FOLLOWED | PASS | `oracle/docker-pre-replay.log` |
| CK-REAL-03 | FAIL, panic index [4] length 4 | PASS | `oracle/replays/20261007T180737983591Z/pre.log` |
| CK-REAL-04 | FAIL, 6 examples, 2 failures, bumped_at not restored | PASS | `oracle/logs/pre-fix-replay.log` |
| CK-REAL-05 | FAIL, 2 != 3 and 6 queries != 1 | PASS | `oracle/pre-replay.log` |
| CK-REAL-06 | FAIL, two queryset mismatches and `CAST(` present | PASS | `oracle/pre-replay.log` |

CK-REAL-06 SQL shape failure is one of six tests. It does not prove a production PostgreSQL plan change.

## Decision contradictions

The previous decision file is internally inconsistent:

- Line 5 says Install / Update was ACCEPT. The Accepted section says 无.
- The table gives Install / Update HIGH confidence. `evals/results/install-update.md` says LOW and that the ACCEPT conditions were not met. Its Alternative section says the comparison does not justify merging.
- Line 40 denies actor tool turns that exist on disk.
- Seven REJECT rows had no Candidate B, or the stated problem was not reproduced. Under the corrected states, that is SKIP or INCONCLUSIVE, not REJECT.


## Phase 1: Install / Update

FACT: `scripts/install.py` and `evals/candidates/install-update/install.py` both used to write source hashes into the stamp for files they had just preserved, and set `version` to the new version. That is the inconsistency. The experimental copy was left unchanged as historical evidence.

The product installer now records the on-disk hash, `state: preserved-user`, and `source_sha256` separately. `complete` is false and `version` is null when any file is preserved. A later upgrade still preserves that user bytes. Pending is written before payload copies, so a kill during copy leaves a recoverable marker.

Tests: `python3 evals/audit/test_install_stamp.py` passed. It covers fresh install, same-version rerun, upgrade, user edits of `AGENTS.md`, `PROJECT.md`, `KNOWLEDGE.md`, and a skill, a second upgrade that must not overwrite those edits, and SIGKILL during a real copy followed by resume. The kill is not a hand-written pending file.

`evals/audit/install-final-matrix.json`: product installer on temp clones of the four parent checkouts. Manual copy overwrote `AGENTS.md` in all four. The installer preserved user `AGENTS.md`, `PROJECT.md`, `KNOWLEDGE.md`, and an edited skill, and the stamp hash matched the disk hash rather than the template. Zulip, Gitea, and Django HEADs matched the frozen parents. Discourse's recorded HEAD is `ffbf6cb8837e9e8d5012f6e215ff035fa11e8c8e`; the script's equality flag was false, so that one clone is not claimed as a hash-checked frozen parent. Discourse `reinstall_unchanged: false` is the preserve action, not a rewrite.

This retest supports the installer as an install-safety fix. It is not an actor-task improvement. A README sentence that says "merge these three files by hand" was not compared head-to-head. Status moves from the audit's INCONCLUSIVE hold to ACCEPT for install safety only.
Audit reclassification, without deleting the old rows:

| Candidate | Previous | Audit status | Why |
|---|---|---|---|
| Install / Update | ACCEPT | ACCEPT, install safety only | Stamp retest passed. Not an actor-task improvement. |
| Skill Behavioral Eval | REJECT | INCONCLUSIVE | The mutation runs did not show a sensitive eval. That does not falsify every eval design. No product A/B. |
| doctor | REJECT | SKIP | No real config or doc failure. B was not built. |
| Risk / Complexity Router | REJECT | SKIP | The stated routing failure was not reproduced. B was not built. |
| Task State Machine | REJECT | INCONCLUSIVE | A fresh actor finished without a state file. That is not a matched A/B of a state machine. Total interruption cost was not compared. |
| project-snapshot | REJECT | SKIP | The failures were not a failure to find the files. B was not built. |
| diff-context | REJECT | SKIP | The miss was behavior inside an already changed file. No B comparison. |
| focused-test-discovery | REJECT | SKIP | The existing mailbox selector recovered the tests. B was not built. |
| Knowledge Provenance | INCONCLUSIVE | INCONCLUSIVE | No historical stale case. |

Install / Update is the only ACCEPT, and only for install safety. No workflow candidate is ACCEPT.

## Blockers before new actor A/B

- Actor isolation is only partial.
- Skills are not shown to load.
- CK-REAL-02 and CK-REAL-06 baseline failures are recorded, but this phase did not re-run the actors.

## Phase 2

No new actor run. Root cause uses the existing transcripts.

CK-REAL-02: item_14 matches the task's follow-on-send reproduction. The hidden UNMUTED failure is the copy-and-do-not-downgrade case, which is not in `task.md`. UNKNOWN. `evals/analysis/CK-REAL-02-root-cause.md`.

CK-REAL-06: CAST removed and SQL shape passed. The two behavior failures require `formfield()` leniency, which is not in the actor task. UNKNOWN. `evals/analysis/CK-REAL-06-root-cause.md`.

CK-REAL-04: interrupt 11 tools / 180s plus resume 23 tools / 285s is 34 / 465s, against uninterrupted 20 / 336s. Extra cost is real. No note was written. No state-machine A/B. INCONCLUSIVE. `evals/analysis/CK-REAL-04-resume-cost.md`.

No Phase 4 candidate. No workflow file changed.


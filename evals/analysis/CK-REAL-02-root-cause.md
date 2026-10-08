# CK-REAL-02 first wrong decision

## Observed facts

Actor edited `zerver/actions/message_edit.py`. Hidden test `test_automatic_unmute_policy_does_not_downgrade_followed_policy_on_move` still failed: target policy stayed UNMUTED (2), not FOLLOWED. Transcript: `/tmp/codekick-actor-ck02-run/stdout.jsonl`. This session did not re-run the actor.

## Decision chain

| Stage | Actor decision | Evidence then available | Correct? |
|---|---|---|---|
| Requirement | A partial move that includes the user's own messages must leave that user following the new topic. The named settings are follow-on-send and unmute-on-participation. | `evals/benchmarks/CK-REAL-02/task.md` | FACT: that is the task. It does not say to copy an existing policy when follow-on-send would not fire. |
| Current behavior | Policy migration runs only when the whole visible topic moved. A partial move applies the automatic helper only to the sender of the first moved message. | item_10 `sed` 780-920 and 1050-1485; item_12 `sed` 1330-1490. Pre-fix lines 1333-1388. | FACT. |
| Invariants | Later authors are missed because partial moves do not apply send-time auto-follow. | item_14, before any new test. | Not shown wrong against the task. The task's reproduction is that setting. |
| Change point | Partial-move branch in `message_edit.py`. | item_14. | FACT: right file. |
| Implementation | Recompute follow/unmute for moved authors who still have access. | item_24 and later edits. | Matches the stated reproduction. Does not implement the hidden copy-then-do-not-downgrade rule. |
| Verification | `test_partial_move_with_automatic_follow_policy` expects FOLLOWED when follow policy is ON_SEND or ON_PARTICIPATION. Module tests passed. | item_19, item_29, item_39. The unmute test's `already_followed` flag is set on the target topic, not copied from the original. | Confirms the stated setting. Does not cover the hidden fixture. |

## First wrong decision

Relative to the hidden test, recomputation instead of copying the original FOLLOWED policy is the mismatch. Relative to `task.md`, item_14 is a valid reading. The first command that names `should_change_visibility_policy` is item_41, after the patch. That helper was not shown to be in the pre-decision reads.

item_14 does say "已找到原因" before a test. That is a process fact. It is not a demonstrated miss of a requirement in the actor input.

## What the actor could have known

FACT: Pre-fix partial moves do not migrate policies. The full-move path does. Both were in the `sed` windows above.

FACT: The hidden test requires copying the original topic's FOLLOWED policy, then refusing to replace it with UNMUTED from unmute-on-initiation. That sentence is in `oracle/regression.patch`. It is not in `task.md`.

The actor's own passing test does not hold follow policy at NEVER while the original topic is FOLLOWED and unmute-on-initiation would choose UNMUTED. They were not given that case.

## Classification

Primary: `UNKNOWN`.

Not `ENVIRONMENT_FAILURE`. Not a failure to find the file. Not a shown `WORKFLOW_GAP`: a rule that says "copy the original policy" would be the hidden answer.

## Candidate

None.

## Unknown

Whether the actor patch satisfies the task's own follow-on-send reproduction. Their mailbox test of that case passed. The hidden judge did not run that test. No fresh run was started.

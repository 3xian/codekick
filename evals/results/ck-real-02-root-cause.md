# CK-REAL-02 root cause

## Observed Failure

Baseline actor edited `zerver/actions/message_edit.py`. Hidden tests still failed: visibility policy stayed UNMUTED (2), not FOLLOWED, and the query-count guard expected 33 and got 20. Record: `evals/results/baseline-ck-real-02.json`. Transcript: `/tmp/codekick-actor-ck02-run/stdout.jsonl`.

This audit did not re-run the actor.

## Evidence

FACT: `evals/benchmarks/CK-REAL-02/task.md` asks for a partial move that contains the user's own messages to keep the user following the new topic, and to leave the original topic's remaining messages unchanged.

FACT: The actor patch adds a loop over moved-message senders and calls `visibility_policy_for_participation` / `visibility_policy_for_send`. It writes FOLLOWED only if one of those helpers returns FOLLOWED. Patch: `/tmp/codekick-actor-ck02-run/actor.patch`.

FACT: The actor tool-read `.ai/PROJECT.md` and `AGENTS.md` before editing. It did not open `SKILL.md`.

FACT: Pre-fix oracle already fails the same FOLLOWED assertion (`oracle/docker-pre-replay.log`, `2 != FOLLOWED`). The actor did not turn that into a pass.

## Root Cause

INFERENCE: This is an implementation error in the right file, not a failure to find the file. The actor treated "participation policy" as sufficient and did not produce FOLLOWED for the user the hidden test checks.

HYPOTHESIS: The helpers return UNMUTED for that user's settings, so the new branch never writes FOLLOWED. Not re-executed against the hidden test in this audit.

Not a location miss. Not evidence for a router, snapshot, or diff-context helper.

## Existing CodeKick Gap

AGENTS.md was loaded and the actor read project files first. The existing verify rule did not stop a patch whose own tests missed the follow invariant. The hidden tests are not visible to the actor, so `/verify` could not have run them unless the actor reconstructed the same assertion.

## Candidate Fix

None. A workflow change is not justified until a fresh run shows a specific rule that, if followed, would have produced FOLLOWED without leaking the hidden test.

## Simpler Alternative

No new skill. The failure is in the policy implementation.

## Expected Improvement

Not defined. No candidate.

## Acceptance Criteria

Not applicable.

## Decision

INCONCLUSIVE. Do not implement a candidate from this run.

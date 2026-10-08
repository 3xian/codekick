# CK-REAL-04 interruption cost

## Observed Failure

Not a hidden-test failure. The uninterrupted baseline passed. The interrupted run left no task note. A fresh actor on the same workspace also passed.

## Evidence

FACT, from `run.json` files, not from the resume-only comparison:

| Run | Tools | Seconds | Source |
|---|---:|---:|---|
| Uninterrupted baseline | 20 | 336.2 | `evals/results/baseline-ck-real-04.json` |
| Interrupted before a note | 11 | 180.0 | `/tmp/codekick-actor-ck04-int-run/run.json` |
| Fresh resume | 23 | 284.9 | `/tmp/codekick-actor-ck04-resume-run/run.json` |
| Interrupt plus resume | 34 | 464.9 | sum of the two rows above |

The previous REJECT compared resume-only 23/285 with uninterrupted 20/336. That comparison is incomplete. Combined cost is higher: 14 more tool items and about 129 more seconds.

FACT: Resume `run.json` does not record a state file. The earlier decision says the workspace had no note. This audit did not re-list that workspace.

## Root Cause

FACT: Stopping the first actor discarded its in-progress transcript from the second actor. The second actor repeated investigation and still passed the hidden test.

INFERENCE: The extra cost is real. It does not show that a state machine would reduce it. No matched interruption A/B was run.

## Existing CodeKick Gap

There is no persistent task artifact in the product. Whether an actor would read one, and whether a shorter resume prompt would be enough, was not tested.

## Candidate Fix

None in this round. A full state machine is not the first experiment. A one-file note was not tested either.

## Simpler Alternative

A resume prompt that carries the interrupted actor's findings. Not run.

## Expected Improvement

Not defined.

## Acceptance Criteria

Not applicable. Any later experiment must interrupt A and B at the same checkpoint and compare combined cost, not uninterrupted A against interrupted B.

## Decision

INCONCLUSIVE. The extra cost is confirmed. No candidate is implemented.

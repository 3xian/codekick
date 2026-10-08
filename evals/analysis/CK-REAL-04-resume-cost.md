# CK-REAL-04 resume cost

## Observed facts

| Run | Tools | Seconds | Result |
|---|---:|---:|---|
| Uninterrupted | 20 | 336.2 | Hidden test passed |
| Interrupted | 11 | 180.0 | No edit, no note |
| Resume | 23 | 284.9 | Hidden test passed |
| Interrupt plus resume | 34 | 464.9 | Passed, higher cost |

Sources: `evals/results/baseline-ck-real-04.json`, `/tmp/codekick-actor-ck04-int-run/run.json`, `/tmp/codekick-actor-ck04-resume-run/run.json`.

## What was repeated

FACT: Both the interrupted run and the resume run read `.ai/PROJECT.md`, `problem.md`, `.ai/KNOWLEDGE.md`, searched for `AGENTS.md`, and read `lib/post_destroyer.rb`, `app/models/post.rb`, `app/models/topic.rb`, and `spec/lib/post_destroyer_spec.rb`.

FACT: The interrupted transcript ends during those reads. It has no agent message that states a fix, and no `file_change`.

FACT: The resume actor was not given that transcript. It reached "recover does not restore bumped_at" by reading the same files again, then edited `lib/post_destroyer.rb`.

## Persistence

Nothing from the interrupted investigation was written into the workspace. No task artifact existed to ignore. The source files were unchanged, so the resume actor could recover every fact by reading them. The lost item was the search trail, not a decision that the source no longer contained.

## Classification

Primary: no product defect was required to finish the task. The extra cost is real.

`WORKFLOW_GAP` for a note is only a hypothesis. A note of paths already found might have shortened the resume. This was not tested. The interrupted run had not made a decision that source reading could not recover.

A state machine is not indicated. A resume summary was not tested, so it is not implemented.

## Candidate

None. An interruption A/B would compare two interrupted runs at the same checkpoint. It was not started, because the missing data was a search trail and the task still succeeded without it.

## Unknown

How many of the 14 extra tool items a path note would remove. One pair of runs cannot answer that.

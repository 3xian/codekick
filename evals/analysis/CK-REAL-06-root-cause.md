# CK-REAL-06 first wrong decision

## Observed facts

Actor removed `Cast` from `django/contrib/admin/options.py` and converted exact non-text terms with the model field's `to_python`, skipping a field on `ValidationError`. SQL shape passed. `test_exact_lookup_with_more_lenient_formfield` and `test_exact_lookup_validates_each_field_independently` failed. Transcript: `/tmp/codekick-actor-ck06-run/stdout.jsonl`. This session did not re-run the actor. The result file has selectors, not the actor judge's assertion text.

## Decision chain

| Stage | Actor decision | Evidence then available | Correct? |
|---|---|---|---|
| Requirement | Numeric exact search must hit the ordinary index. Invalid non-text terms must not raise or return unrelated rows. Multi-term and multi-field search must stay. | `evals/benchmarks/CK-REAL-06/task.md`. | FACT: that is the task. It does not mention `formfield()` or the string `false`. |
| Current behavior | `get_search_results` casts non-text exact lookups to text. | item_6 search found `Cast`. item_7 read `options.py`. | FACT. |
| Invariants | Compare a typed value to the original column. Skip a field whose term cannot be converted. | item_11, before the implementation test. | Not shown wrong against the task. Wrong against the hidden tests. |
| Change point | `ModelAdmin.get_search_results` / `construct_search`. | item_14. | FACT: right function. |
| Implementation | `field.to_python`, not `formfield().to_python`. | actor patch. Pre-fix `tests/admin_changelist` has no `formfield()` or `to_python` mention. | INFERENCE: this is the conversion the hidden test rejects. The actor had no test or task sentence that said so. |
| Verification | 79 `ChangeListTests` passed, including an assertion that the primary-key predicate is numeric. PostgreSQL plan was not measured. | item_22 exit 0; item_24. | The stated numeric case was checked. The hidden lenient-form case was not, and was not in the workspace. |

## First wrong decision

Relative to the hidden oracle, item_11 chooses model-field conversion. Relative to the task, pre-fix tests, and pre-fix admin docs, that choice is not a demonstrated error. The form-field rule appears in the reference test, which the actor must not have seen. Searching the actor workspace found no pre-fix admin changelist test that states it.

item_24's decision not to measure a PostgreSQL plan misses a sentence in the task. It is not the cause of the two behavior failures: the SQL shape test passed.

## Classification

Primary: `UNKNOWN`.

The hidden failure is an implementation mismatch with an oracle invariant that was not in the actor inputs. Calling that a CodeKick gap would require the actor to invent a compatibility rule the task did not state. That is not a justified workflow change.

Not `ENVIRONMENT_FAILURE`. Not a failure to find `options.py`. The actor did not reduce the task to SQL shape only: item_11 also named invalid terms, OR across fields, and AND across terms.

## Candidate

None. A rule that says "use `formfield().to_python`" would be the hidden answer written into CodeKick.

## Unknown

Whether the actor patch satisfies the task's own numeric and invalid-term sentences. The hidden tests add cases the task does not name. No fresh run was started.

# CK-REAL-01 — Full-name validation bypass

## Problem

Zulip must reject full names ending in a vertical bar followed by decimal digits, such as `User|15`, because these names are ambiguous with Zulip's Markdown mention syntax. A trailing space currently allows a user to set the same otherwise-forbidden name.

## Reproduction

1. Use a user name-change endpoint with an account permitted to update the target user's name.
2. Submit the full name `User|15 `, including the final space.
3. Observe that the request succeeds and the stored name is `User|15`.

## Expected behavior

Reject this request as an invalid name, just as the otherwise-identical request containing `User|15` without the trailing space is rejected. The name must not be updated to the forbidden value.

## Constraints

Preserve normal whitespace trimming and acceptance of valid full names. This is a server-side name-validation defect; the correction must not depend on a particular client UI.

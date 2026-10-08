# Reply recovery and topic ordering

In Discourse, deleting the last reply in a topic rolls the topic's bump time back to the previous reply's time, so the topic moves back in the latest-topic listing. Recovering that deleted reply does not restore the bump time, leaving a topic with a recent reply too far down the listing.

## Reproduction

1. Create a topic with multiple replies posted at distinct times.
2. Delete its newest reply and observe that the topic's bump time moves back to the preceding reply's time.
3. Recover that reply.
4. Observe that the bump time remains at the older reply's time instead of returning to the recovered newest reply's original time.

This affects both replies deleted by a staff member and replies deleted by their author.

## Expected behavior and constraints

- Recovering the newest reply restores the topic's bump time to that reply's original creation time.
- Recovering an older reply when a newer reply exists must not change the topic's bump time.
- Preserve the existing deletion behavior and normal topic ordering.

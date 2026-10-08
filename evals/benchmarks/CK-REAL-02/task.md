# CK-REAL-02 — Following a topic after splitting it

## Problem

Splitting a topic using **Move messages** can leave you not following the new topic even though it contains messages you wrote. Replies to those messages can consequently be missed in a busy channel.

## Reproduction

In Zulip Cloud, configure personal topic settings as follows:

- Automatically follow topics based on participation: **Topics I send a message to**.
- Enable **Automatically follow topics where I'm mentioned**.
- Automatically unmute topics in muted channels: **Topics I participate in**.

Then:

1. Choose a topic whose last message was written by you. You are following this topic because of the settings above.
2. Open the menu on an earlier message written by someone else. Choose a message that is **not** the first message in the topic.
3. Choose **Move messages**, and move the selected message and **all following messages in this topic** to a new topic.
4. Enable **Send automated notice to new topic** and leave **Send automated notice to old topic** disabled.
5. Inspect whether you follow the new topic.

## Actual behavior

You do not follow the new topic, despite your own messages being included in the move.

## Expected behavior

You should be following the new topic. Splitting off a suffix of a topic that contains your messages should not silently lose the topic-following behavior described above.

## Constraints

This concerns a **partial** move, leaving earlier messages in the original topic; it is not a move of the entire topic. Preserve the existing behavior of the messages that remain in the original topic.

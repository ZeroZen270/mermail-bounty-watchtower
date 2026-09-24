# Tools used by mermail-bounty-watchtower

This skill uses a **read + label-only** subset of the Mermail MCP catalog.
Verify exact tool names against the live catalog before first use:

```
node skills/mermail-mcp/scripts/check-connection.mjs   # from the official repo
```

The baseline catalog is 63 tools; additive tools may exist. Tool families this
skill needs:

| Family | Purpose in this skill | Example names seen in merged submissions |
|---|---|---|
| inbox search / list | find unread bounty-platform mail by sender/subject | `mermail_list_emails` |
| read email | fetch full body of each match | `mermail_get_email` |
| label / archive | mark processed mail `bounty/triaged`, `bounty/submitted` | mailbox label tools |

If a family is unavailable in the connected catalog, degrade honestly:
skip that step and tell the user which step was skipped — never substitute a
different tool with side effects.

## Rules

1. **Reads before writes.** Resolve workspace/mailbox IDs with list/get tools;
   prefer the mailbox `public_id` as `mailboxId`.
2. **Labeling is the only mailbox write.** This skill never calls compose, send,
   reply, forward, schedule, transfer, or wallet tools. If a reminder needs to
   reach the user by email, hand the drafted text to the user and let them send
   it via `mermail-compose-email` with explicit approval.
3. **Local files are the working memory.** `bounties/<slug>/BRIEF.md`,
   `SUBMISSION.md`, `STATUS.md`, `INDEX.md`, `DIGEST.md` live on the agent's
   machine, not in the mailbox.
4. **Never request that the user paste an API key into chat.** Auth comes from
   `MERMAIL_API_KEY` in the process environment or platform OAuth.

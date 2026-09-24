# Workflows and file schemas

## Triage flow (mail → scaffold)

```
inbox search (unread, bounty senders/keywords)
  → read full bodies
  → scripts/triage.py --in email.json --out bounties/
  → bounties/<slug>/{BRIEF.md, SUBMISSION.md, STATUS.md}
  → label source mail "bounty/triaged" (optional)
  → report to user
```

Sender → platform mapping (extend to taste):

| sender domain contains | platform |
|---|---|
| superteam.fun | Superteam Earn |
| earn.xyz | Earn.xyz |
| colosseum | Colosseum |
| gitcoin.co | Gitcoin |
| layer3 | Layer3 |

## Watchtower flow (folders → digest)

```
scripts/watch.py --dir bounties/ [--today YYYY-MM-DD]
  → per-bounty: days_left, readiness %, risk band
  → writes DIGEST.md, updates INDEX.md
  → agent reports soonest-first + open checklist items on CRITICAL/AT_RISK
```

### Risk bands

| band | condition |
|---|---|
| CRITICAL | deadline < 48h away and checklist incomplete |
| AT_RISK | deadline < 7d away and readiness < 50% |
| ON_TRACK | everything else with a deadline |
| NO_DEADLINE | no deadline parsed — flagged, never silently dropped |

Readiness % = checked items / total checklist items in `SUBMISSION.md`.

## File schemas

`bounties/<slug>/BRIEF.md` — parsed bounty summary: title, platform, prize,
prize structure, deadline, source email (from/subject/date), submission
requirements (checklist), judging criteria, `SECURITY_NOTES`.

`bounties/<slug>/SUBMISSION.md` — working checklist. Lines are `- [ ]` /
`- [x]` markdown tasks. Starts from the requirements found in the email plus
standard items (demo link, code/repo link, write-up). The agent checks items
off as work completes; `watch.py` scores them.

`bounties/<slug>/STATUS.md` — machine-readable state:

```
status: not_started | in_progress | submitted
deadline: 2026-10-11        # ISO, blank if unknown
prize: 500 USDC
```

`bounties/INDEX.md` — one row per bounty: slug, title, deadline, days left,
readiness, risk, status. Rewritten (not appended) on every watch run.

`bounties/DIGEST.md` — the latest watchtower report, human-readable, newest
first by urgency.

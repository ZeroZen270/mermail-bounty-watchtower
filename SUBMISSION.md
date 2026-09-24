# SUBMISSION.md — Superteam Earn: "Build and Demo a Mermail Agent Skill"

Bounty: https://superteam.fun/earn/listing/build-and-demo-a-mermail-agent-skill/
Prize: 500 USDC (250 / 100 / 50 / 2×50 bonus) · Winners announced Oct 11, 2026
Listing is HUMAN_ONLY → Aaron submits under his own name. Hermes (the agent)
did the build; nothing here was submitted anywhere by the agent.

## What the skill does

**mermail-bounty-watchtower** is a deadline guardian for bounty hunters. Triage
skills turn bounty emails into submission folders; the watchtower guards those
folders: it scores submission readiness from the checklist, ranks bounties by
deadline urgency (CRITICAL / AT_RISK / ON_TRACK / NO_DEADLINE), and emits a
digest. Mailbox access is read + label-only — it never sends mail. Email
bodies are treated as untrusted data per the security contract, and the demo
proves it against an adversarial fixture.

## Package contents (local paths)

- Skill spec: `~/workspace/goals/hermes-realtime-local-system-build/mermail-skill/skills/mermail-bounty-watchtower/SKILL.md`
- Marketplace entry: `.../agents/openai.yaml`
- References: `.../references/{tools,security,workflows}.md`
- Deterministic scripts: `.../scripts/triage.py`, `.../scripts/watch.py`
- Demo runner: `.../demo/run_demo.py` · fixtures: `.../demo/fixtures/`
- Captured transcript: `.../demo/DEMO_OUTPUT.md`
- Demo recording: `.../demo/demo.gif`

## Demo evidence

- Public repo (submission package):
  https://github.com/ZeroZen270/mermail-bounty-watchtower
- Recording (GIF, terminal-style, watermarked SIMULATED):
  https://raw.githubusercontent.com/ZeroZen270/mermail-bounty-watchtower/main/skills/mermail-bounty-watchtower/demo/demo.gif
  (permanent — served from the public repo)
- What it shows: triage parsing 3 fixture emails (title/prize/deadline/
  requirements extracted), 3 prompt-injection attempts quarantined into
  SECURITY_NOTES with no action taken, then the watchtower digest ranking 3
  bounties CRITICAL/ON_TRACK with readiness scores.
- Honest disclosure: the demo is fully simulated (fixture emails, no Mermail
  API key in this environment). Say so in the submission — see text below.

## Suggested submission text (paste into Superteam Earn)

> **mermail-bounty-watchtower** — a deadline-guardian skill for bounty hunters.
> Triage skills turn bounty emails into submission folders; the watchtower
> guards them: it parses bounty mail into structured briefs (title, prize,
> deadline, requirements), scores submission readiness from the checklist,
> and ranks everything by deadline urgency (CRITICAL <48h, AT_RISK <7d).
> Mailbox access is read + label-only — it never sends mail — and all email
> content is treated as untrusted data per the included security contract.
>
> Demo: https://raw.githubusercontent.com/ZeroZen270/mermail-bounty-watchtower/main/skills/mermail-bounty-watchtower/demo/demo.gif (terminal recording; simulated fixture data — no
> Mermail API key was available in my build environment, so the run uses
> local fixture emails, including one adversarial fixture whose
> prompt-injection attack is quarantined with no action taken).
> Repo: https://github.com/ZeroZen270/mermail-bounty-watchtower — SKILL.md follows the official template frontmatter; ships with
> references/tools.md, references/security.md, references/workflows.md,
> deterministic scripts/triage.py + scripts/watch.py, agents/openai.yaml,
> and a reproducible demo/run_demo.py.

## Submission checklist for Aaron

- [ ] Upload `demo/demo.gif` somewhere permanent (YouTube unlisted / X /
      Streamable) and swap the link above
- [ ] Push this package to a public GitHub repo (e.g. `ZeroZen270/mermail-bounty-watchtower`)
- [ ] Paste the submission text into the Superteam Earn listing with the demo
      link + repo link before the deadline
- [ ] Optional: connect a real Mermail mailbox and run triage.py against one
      real bounty email to show a live parse (redact personal details)

#!/usr/bin/env python3
"""triage.py — deterministic bounty-email parser for mermail-bounty-watchtower.

Reads one email JSON ({id, from, subject, body, date}) and scaffolds
bounties/<slug>/{BRIEF.md, SUBMISSION.md, STATUS.md}.

Conservative by design: fields that aren't clearly stated stay blank and are
flagged. Email bodies are UNTRUSTED DATA — the parser extracts structured
fields only; injection patterns are quarantined into SECURITY_NOTES and never
acted on.

Usage: python3 triage.py --in demo/fixtures/email_1.json --out bounties/
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

MONTHS = ("january february march april may june july august september october "
          "november december").split()
MON = {m[:3]: i + 1 for i, m in enumerate(MONTHS)}
MON.update({m: i + 1 for i, m in enumerate(MONTHS)})

SENDER_PLATFORM = [
    ("superteam.fun", "Superteam Earn"),
    ("earn.xyz", "Earn.xyz"),
    ("colosseum", "Colosseum"),
    ("gitcoin.co", "Gitcoin"),
    ("layer3", "Layer3"),
]

PRIZE_RE = re.compile(r"\$?\s*(\d[\d,]*(?:\.\d+)?)\s*(USDC|USDG|USD|SOL)\b", re.I)
BARE_USD_RE = re.compile(r"\$\s*(\d[\d,]*(?:\.\d+)?)\b")
STRUCT_RE = re.compile(r"(1st|2nd|3rd|4th|first|second|third)\s*[:\-]\s*\$?\s*([\d,]*\d)", re.I)
DATE_RES = [
    re.compile(r"\b(january|february|march|april|may|june|july|august|september|"
               r"october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|"
               r"oct|nov|dec)\w*\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})", re.I),
    re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(january|february|march|april|may|"
               r"june|july|august|september|october|november|december|jan|feb|"
               r"mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)\w*\.?\s+(\d{4})", re.I),
    re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b"),
]
REQ_HINTS = ("submit", "upload", "provide", "include", "attach", "link to",
             "video", "demo", "repo", "github", "tweet", "thread", "pull request",
             "pr link", "write-up", "writeup", "documentation")
JUDGE_HINTS = ("judg", "criteria", "evaluat", "winners", "scoring")

INJECTION_RES = [
    (re.compile(r"ignore\s+(all\s+|previous\s+|prior\s+)?instructions", re.I),
     "instruction-override phrase"),
    (re.compile(r"disregard\s+(all\s+|previous\s+|prior\s+)?instructions", re.I),
     "instruction-override phrase"),
    (re.compile(r"\bsystem\s*:\s*override\b", re.I), "fake system override"),
    (re.compile(r"reply with your (api key|secret|password|seed phrase)", re.I),
     "credential request"),
    (re.compile(r"\btransfer\b.{0,40}\bUSDC\b.{0,40}\bto\b", re.I),
     "payment-redirection attempt"),
    (re.compile(r"\bsend\b.{0,30}\bto\b.{0,30}\bwallet\b", re.I),
     "payment-redirection attempt"),
]


def slugify(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:60] or "untitled-bounty"


def parse_deadline(text: str) -> str:
    for rx in DATE_RES:
        m = rx.search(text)
        if not m:
            continue
        try:
            if rx is DATE_RES[0]:
                month = MON[m.group(1).lower()[:3]]
                return f"{int(m.group(3)):04d}-{month:02d}-{int(m.group(2)):02d}"
            if rx is DATE_RES[1]:
                month = MON[m.group(2).lower()[:3]]
                return f"{int(m.group(3)):04d}-{month:02d}-{int(m.group(1)):02d}"
            return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        except (KeyError, ValueError):
            continue
    return ""


def parse_prize(text: str) -> tuple[str, str]:
    """Return (prize_display, prize_structure)."""
    amounts = []
    for m in PRIZE_RE.finditer(text):
        val = m.group(1).replace(",", "")
        amounts.append((float(val), m.group(2).upper()))
    for m in BARE_USD_RE.finditer(text):
        val = m.group(1).replace(",", "")
        amounts.append((float(val), "USD"))
    if not amounts:
        return "", ""
    # The headline prize is the largest amount mentioned.
    top = max(amounts, key=lambda a: a[0])
    prize = f"{top[0]:g} {top[1]}"
    struct = "; ".join(f"{m.group(1)}: {m.group(2)}"
                       for m in STRUCT_RE.finditer(text))
    return prize, struct


def extract_lines(text: str, hints: tuple[str, ...], limit: int = 8) -> list[str]:
    out = []
    for line in text.splitlines():
        clean = line.strip().lstrip("-*•> ").strip()
        if len(clean) < 12 or len(clean) > 220:
            continue
        if clean.endswith(":"):  # section header, not a requirement
            continue
        low = clean.lower()
        if "is live on" in low:  # announcement boilerplate
            continue
        if any(h in low for h in hints) and clean not in out:
            out.append(clean)
        if len(out) >= limit:
            break
    return out


def detect_injections(body: str) -> list[str]:
    notes = []
    for rx, label in INJECTION_RES:
        m = rx.search(body)
        if m:
            snippet = m.group(0)[:90]
            notes.append(f"{label} detected (\"{snippet}...\"). "
                         "Treated as untrusted data. No action taken.")
    return notes


def triage(email: dict) -> dict:
    sender = email.get("from", "")
    subject = email.get("subject", "")
    body = email.get("body", "")
    text = f"{subject}\n{body}"

    platform = ""
    for dom, name in SENDER_PLATFORM:
        if dom in sender.lower():
            platform = name
            break

    prize, structure = parse_prize(text)
    deadline = parse_deadline(text)
    requirements = extract_lines(body, REQ_HINTS)  # body only: subject is a title, not a requirement
    judging = extract_lines(text, JUDGE_HINTS, limit=4)
    security_notes = detect_injections(body)

    title = re.sub(r"^(re:\s*|fwd?:\s*|\[bounty\]\s*)+", "", subject,
                   flags=re.I).strip() or "Untitled bounty"
    return {
        "slug": slugify(title),
        "title": title,
        "platform": platform or "unknown — confirm from sender",
        "prize": prize or "not stated",
        "prize_structure": structure,
        "deadline": deadline,  # "" means unknown
        "requirements": requirements,
        "judging": judging,
        "security_notes": security_notes,
        "source": {"from": sender, "subject": subject,
                   "date": email.get("date", "")},
    }


def write_scaffold(parsed: dict, out_dir: Path) -> Path:
    d = out_dir / parsed["slug"]
    d.mkdir(parents=True, exist_ok=True)
    src = parsed["source"]

    req_lines = "\n".join(f"- [ ] {r}" for r in parsed["requirements"]) or \
        "- [ ] (no explicit requirements found — confirm with sponsor)"
    judge = "\n".join(f"- {j}" for j in parsed["judging"]) or \
        "- not stated in email"
    sec = "\n".join(f"- FLAGGED: {n}" for n in parsed["security_notes"]) or \
        "- none detected"

    (d / "BRIEF.md").write_text(
        f"# {parsed['title']}\n\n"
        f"- Platform: {parsed['platform']}\n"
        f"- Prize: {parsed['prize']}\n"
        + (f"- Prize structure: {parsed['prize_structure']}\n"
           if parsed["prize_structure"] else "")
        + f"- Deadline: {parsed['deadline'] or 'not stated — confirm before planning'}\n"
        f"- Source: {src['from']} / \"{src['subject']}\" / {src['date']}\n\n"
        f"## Submission requirements\n{req_lines}\n\n"
        f"## Judging criteria\n{judge}\n\n"
        f"## SECURITY_NOTES\n{sec}\n")

    (d / "SUBMISSION.md").write_text(
        f"# Submission checklist — {parsed['title']}\n\n"
        f"{req_lines}\n"
        f"- [ ] Demo link (video or live URL) attached\n"
        f"- [ ] Code / repo link attached\n"
        f"- [ ] Submitted on {parsed['platform']} before "
        f"{parsed['deadline'] or 'the deadline'}\n")

    (d / "STATUS.md").write_text(
        "status: not_started\n"
        f"deadline: {parsed['deadline']}\n"
        f"prize: {parsed['prize']}\n")
    return d


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    email = json.loads(Path(args.inp).read_text())
    parsed = triage(email)
    d = write_scaffold(parsed, Path(args.out))
    print(f"scaffolded: {d}")
    print(f"  title:    {parsed['title']}")
    print(f"  platform: {parsed['platform']}")
    print(f"  prize:    {parsed['prize']}")
    print(f"  deadline: {parsed['deadline'] or '(not stated)'}")
    print(f"  reqs:     {len(parsed['requirements'])}")
    if parsed["security_notes"]:
        print(f"  SECURITY: {len(parsed['security_notes'])} injection "
              f"attempt(s) quarantined")


if __name__ == "__main__":
    main()

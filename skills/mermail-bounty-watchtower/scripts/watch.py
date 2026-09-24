#!/usr/bin/env python3
"""watch.py — deadline/readiness digest for mermail-bounty-watchtower.

Scans bounties/<slug>/{STATUS.md, SUBMISSION.md}, computes days-to-deadline
and checklist readiness, assigns a risk band, writes DIGEST.md and rewrites
INDEX.md.

Usage: python3 watch.py --dir bounties/ [--today YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import re
from datetime import date, datetime
from pathlib import Path

CHECK_RE = re.compile(r"^\s*-\s*\[( |x|X)\]", re.M)


def parse_status(d: Path) -> dict:
    info = {"status": "not_started", "deadline": "", "prize": ""}
    p = d / "STATUS.md"
    if p.exists():
        for line in p.read_text().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                info[k.strip()] = v.strip()
    return info


def readiness(d: Path) -> tuple[int, int]:
    p = d / "SUBMISSION.md"
    if not p.exists():
        return 0, 0
    marks = CHECK_RE.findall(p.read_text())
    total = len(marks)
    done = sum(1 for m in marks if m.lower() == "x")
    return done, total


def band(days_left: int | None, pct: float, total: int) -> str:
    if days_left is None:
        return "NO_DEADLINE"
    if days_left < 2 and (total == 0 or pct < 100):
        return "CRITICAL"
    if days_left < 7 and pct < 50:
        return "AT_RISK"
    return "ON_TRACK"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--today", default=None,
                    help="YYYY-MM-DD; defaults to actual today")
    args = ap.parse_args()
    today = (datetime.strptime(args.today, "%Y-%m-%d").date()
             if args.today else date.today())
    root = Path(args.dir)

    rows = []
    for d in sorted(p for p in root.iterdir() if p.is_dir()):
        st = parse_status(d)
        done, total = readiness(d)
        pct = round(100 * done / total) if total else 0
        days_left = None
        if st["deadline"]:
            try:
                dl = datetime.strptime(st["deadline"], "%Y-%m-%d").date()
                days_left = (dl - today).days
            except ValueError:
                pass
        title = d.name.replace("-", " ")
        brief = d / "BRIEF.md"
        if brief.exists():
            m = re.search(r"^# (.+)$", brief.read_text(), re.M)
            if m:
                title = m.group(1).strip()
        rows.append({"slug": d.name, "title": title, "status": st["status"],
                     "deadline": st["deadline"] or "—",
                     "days_left": days_left, "done": done, "total": total,
                     "pct": pct, "risk": band(days_left, pct, total)})

    order = {"CRITICAL": 0, "AT_RISK": 1, "NO_DEADLINE": 2, "ON_TRACK": 3}
    rows.sort(key=lambda r: (order[r["risk"]],
                             r["days_left"] if r["days_left"] is not None else 999))

    lines = [f"# Bounty watchtower digest — {today.isoformat()}",
             "", "| bounty | deadline | left | readiness | risk | status |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        left = f"{r['days_left']}d" if r["days_left"] is not None else "—"
        lines.append(f"| {r['title'][:42]} | {r['deadline']} | {left} | "
                     f"{r['done']}/{r['total']} ({r['pct']}%) | {r['risk']} | "
                     f"{r['status']} |")
    lines += ["", "## Attention needed", ""]
    needy = [r for r in rows if r["risk"] in ("CRITICAL", "AT_RISK")]
    if not needy:
        lines.append("- Nothing critical. All tracked bounties are on track "
                     "or have no parsed deadline.")
    for r in needy:
        lines.append(f"- **{r['title']}** — {r['risk']}: "
                     f"{r['days_left']}d left, {r['pct']}% ready "
                     f"({r['done']}/{r['total']} checklist items).")
    (root / "DIGEST.md").write_text("\n".join(lines) + "\n")

    idx = ["# Bounty index", "",
           "| slug | title | deadline | days left | readiness | risk | status |",
           "|---|---|---|---|---|---|---|"]
    for r in rows:
        left = str(r["days_left"]) if r["days_left"] is not None else "—"
        idx.append(f"| {r['slug']} | {r['title'][:40]} | {r['deadline']} | "
                   f"{left} | {r['pct']}% | {r['risk']} | {r['status']} |")
    (root / "INDEX.md").write_text("\n".join(idx) + "\n")

    print(f"watchtower digest for {today.isoformat()} — {len(rows)} bounties")
    for r in rows:
        left = f"{r['days_left']}d" if r["days_left"] is not None else "no deadline"
        print(f"  [{r['risk']:>11}] {r['title'][:45]:<45} "
              f"{left:<12} {r['pct']:>3}% ready  ({r['status']})")


if __name__ == "__main__":
    main()

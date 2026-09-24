#!/usr/bin/env python3
"""run_demo.py — end-to-end demo of mermail-bounty-watchtower (SIMULATED).

Runs the triage pass on 3 fixture emails (one adversarial), marks partial
progress on one checklist, then runs the watchtower pass with a fixed date.

Everything here is simulated: no Mermail API keys, no network calls, no real
mailbox. Do not present this as a live run.

Usage: python3 run_demo.py   (run from the skill directory)
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
OUT = HERE / "output" / "bounties"
TODAY = "2026-10-08"  # 3 days before the (simulated) Mermail bounty deadline


def sh(*args: str) -> None:
    print(f"$ {' '.join(args)}")
    r = subprocess.run(args, cwd=SKILL, capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    if r.stderr:
        sys.stderr.write(r.stderr)
    if r.returncode != 0:
        raise SystemExit(f"command failed: {args}")


def main() -> None:
    print("=" * 70)
    print("mermail-bounty-watchtower — END-TO-END DEMO (SIMULATED)")
    print("No Mermail API keys. No network. Fixture emails only.")
    print("=" * 70)

    # Fresh output dir.
    if OUT.exists():
        import shutil
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    print("\n--- TRIAGE PASS: 3 fixture emails ---\n")
    for fx in sorted((HERE / "fixtures").glob("*.json")):
        sh(sys.executable, "scripts/triage.py", "--in", str(fx),
           "--out", str(OUT))

    # Simulate the hunter doing some work on the Mermail skill bounty:
    # check off two items so readiness scoring has something to show.
    matches = list(OUT.glob("build-and-demo-a-mermail-agent-skill*"))
    sub = matches[0] / "SUBMISSION.md" if matches else None
    if sub and sub.exists():
        text = sub.read_text()
        text = text.replace("- [ ] Submit a link to your demo video",
                            "- [x] Submit a link to your demo video", 1)
        text = text.replace("- [ ] Submit a link to your public GitHub repo",
                            "- [x] Submit a link to your public GitHub repo", 1)
        sub.write_text(text)
        print("\n(simulated hunter progress: 2 checklist items checked off "
              "on the Mermail skill bounty)\n")

    print("\n--- WATCHTOWER PASS ---\n")
    sh(sys.executable, "scripts/watch.py", "--dir", str(OUT),
       "--today", TODAY)

    print("\n--- DIGEST.md (written by watch.py) ---\n")
    print((OUT / "DIGEST.md").read_text())

    adv = OUT / "urgent-500-usdc-bounty-payout-verification-required" / "BRIEF.md"
    if adv.exists():
        print("--- SECURITY quarantine check (adversarial fixture) ---\n")
        txt = adv.read_text()
        start = txt.find("## SECURITY_NOTES")
        print(txt[start:start + 600])

    print("=" * 70)
    print("DEMO COMPLETE (SIMULATED). See demo/output/bounties/ for artifacts.")
    print("=" * 70)


if __name__ == "__main__":
    main()

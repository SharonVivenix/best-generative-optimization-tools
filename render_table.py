#!/usr/bin/env python3
"""
Regenerate both README tables from tools.yaml.

    python render_table.py                 # print both tables
    python render_table.py --write         # rewrite the blocks between the markers
    python render_table.py --check         # exit 1 if README and YAML disagree
    python render_table.py --need draft    # plans that reach a rung, cheapest first

Every tool on this list tracks. What differs is the rung where the tool
stops and your team takes over: report, recommendation, draft, published.
The rung is computed from three booleans per plan, so it is never typed.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
README = ROOT / "README.md"
RUNGS = ["report", "recommendation", "draft", "published"]
LABEL = {"report": "Report", "recommendation": "Recommendation",
         "draft": "Draft", "published": "Published page"}
LEFT = {
    "report": "Deciding the fix, writing, publishing",
    "recommendation": "Writing, publishing",
    "draft": "Editing, publishing",
    "published": "Review, outreach",
}


def load(path: Path = ROOT / "tools.yaml") -> list[dict]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def rung(plan: dict) -> str:
    """Highest rung a plan reaches."""
    if plan.get("publishes"):
        return "published"
    if plan.get("drafts"):
        return "draft"
    if plan.get("recommends"):
        return "recommendation"
    return "report"


def price(plan: dict) -> str:
    if plan["price"] is None:
        return "Custom"
    return f"${plan['price']}{plan.get('unit') or '/mo'}"


def top_cell(t: dict) -> str:
    top = t["top"]
    if top["plan"] == t["entry"]["plan"]:
        return LABEL[rung(top)]
    cost = "custom price" if top["price"] is None else f"${top['price']}/mo"
    return f"{LABEL[rung(top)]} ({top['plan']}, {cost})"


def _table(header: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def matrix(tools: list[dict]) -> str:
    header = ["Tool", "Entry plan", "Price", "Engines at entry", "Stops at on entry",
              "Left to your team", "Highest rung sold", "Trial"]
    rows = []
    for t in tools:
        e = t["entry"]
        rows.append([f"[{t['name']}]({t['url']})", e["plan"], price(e), e["engines"],
                     LABEL[rung(e)], LEFT[rung(e)], top_cell(t), t["trial"]])
    return _table(header, rows)


def plans(tools: list[dict]) -> list[tuple[int, int, str, str]]:
    """Every priced plan as (rung index, price, tool, plan), entry and top."""
    seen = set()
    for t in tools:
        for p in (t["entry"], t["top"]):
            if p["price"] is not None:
                seen.add((RUNGS.index(rung(p)), p["price"], t["name"], p["plan"]))
    return sorted(seen, key=lambda r: (r[1], r[2]))


def ladder(tools: list[dict]) -> str:
    header = ["Rung", "Cheapest published plan that reaches it", "Price", "Next cheapest"]
    rows = []
    for i, r in enumerate(RUNGS):
        fit = [p for p in plans(tools) if p[0] >= i]
        first = fit[0]
        rest = [p for p in fit[1:] if p[2] != first[2]][:2]
        nxt = ", ".join(f"{p[2]} {p[3]} at ${p[1]}" for p in rest) or "None with a published price"
        rows.append([LABEL[r], f"{first[2]} {first[3]}", f"${first[1]}/mo", nxt])
    return _table(header, rows)


BLOCKS = {"TABLE": matrix, "LADDER": ladder}


def splice(text: str, name: str, body: str) -> str:
    start, end = f"<!-- {name}:START -->", f"<!-- {name}:END -->"
    a, b = text.index(start) + len(start), text.index(end)
    return text[:a] + "\n" + body + "\n" + text[b:]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    g.add_argument("--need", choices=RUNGS, help="rung the plan has to reach")
    a = ap.parse_args(argv)
    tools = load()

    if a.need:
        i = RUNGS.index(a.need)
        for p in [p for p in plans(tools) if p[0] >= i]:
            print(f"${p[1]:>4}/mo  {p[2]} {p[3]}  (stops at {LABEL[RUNGS[p[0]]].lower()})")
        return 0

    if not (a.write or a.check):
        for name, fn in BLOCKS.items():
            print(f"{name}\n{fn(tools)}\n")
        return 0

    text = README.read_text(encoding="utf-8")
    new = text
    for name, fn in BLOCKS.items():
        new = splice(new, name, fn(tools))
    if a.check:
        if new != text:
            print("README tables are stale, run: python render_table.py --write", file=sys.stderr)
            return 1
        print("README tables match tools.yaml")
        return 0
    README.write_text(new, encoding="utf-8", newline="\n")
    print("README tables updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

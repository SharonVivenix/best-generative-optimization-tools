"""Markdown rendering for the two generated README blocks."""
from __future__ import annotations

from .model import RUNGS, pick, rung

LABEL = {"report": "Report", "recommendation": "Recommendation",
         "draft": "Draft", "published": "Published page"}
LEFT = {
    "report": "Deciding the fix, writing, publishing",
    "recommendation": "Writing, publishing",
    "draft": "Editing, publishing",
    "published": "Review, outreach",
}


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


def table(header: list[str], rows: list[list[str]]) -> str:
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
    return table(header, rows)


def ladder(tools: list[dict]) -> str:
    header = ["Rung", "Cheapest published plan that reaches it", "Price", "Next cheapest"]
    rows = []
    for r in RUNGS:
        fit = pick(tools, need=r)
        first = fit[0]
        rest = [p for p in fit[1:] if p.tool_id != first.tool_id][:2]
        nxt = ", ".join(f"{p.tool} {p.plan} at ${p.price}" for p in rest) or "None with a published price"
        rows.append([LABEL[r], f"{first.tool} {first.plan}", f"${first.price}/mo", nxt])
    return table(header, rows)


BLOCKS = {"TABLE": matrix, "LADDER": ladder}


def splice(text: str, name: str, body: str) -> str:
    start, end = f"<!-- {name}:START -->", f"<!-- {name}:END -->"
    a, b = text.index(start) + len(start), text.index(end)
    return text[:a] + "\n" + body + "\n" + text[b:]


def render_readme(text: str, tools: list[dict]) -> str:
    for name, fn in BLOCKS.items():
        text = splice(text, name, fn(tools))
    return text

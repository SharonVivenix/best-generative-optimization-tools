"""Data model. Everything here is pure: no file writes, no network."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "tools.yaml"

RUNGS = ["report", "recommendation", "draft", "published"]
FLAGS = ["recommends", "drafts", "publishes"]

# Which team role a plan replaces once it reaches a rung.
ROLE_TO_RUNG = {"strategist": "recommendation", "writer": "draft", "publisher": "published"}


@dataclass(frozen=True)
class Plan:
    tool: str
    tool_id: str
    plan: str
    tier: str          # "entry" or "top"
    price: int | None  # USD per month, None when quoted by sales
    rung: str
    engines: int

    @property
    def rung_index(self) -> int:
        return RUNGS.index(self.rung)

    def to_dict(self) -> dict:
        return asdict(self)


def load(path: Path | str = DATA) -> list[dict]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def rung(plan: dict) -> str:
    """Highest rung a plan reaches, computed from its three booleans."""
    if plan.get("publishes"):
        return "published"
    if plan.get("drafts"):
        return "draft"
    if plan.get("recommends"):
        return "recommendation"
    return "report"


def plans(tools: list[dict], priced_only: bool = False) -> list[Plan]:
    """Flatten the dataset to one Plan per distinct (tool, plan), cheapest first."""
    out: dict[tuple[str, str], Plan] = {}
    for t in tools:
        entry_engines = t["entry"]["engines_included"]
        for tier in ("entry", "top"):
            p = t[tier]
            if priced_only and p["price"] is None:
                continue
            key = (t["id"], p["plan"])
            out.setdefault(key, Plan(t["name"], t["id"], p["plan"], tier, p["price"], rung(p),
                                     p.get("engines_included", entry_engines)))
    return sorted(out.values(), key=lambda p: (p.price is None, p.price or 0, p.tool))


def pick(tools: list[dict], need: str = "report", budget: int | None = None,
         engines: int = 0, include_custom: bool = False) -> list[Plan]:
    """Plans that reach `need`, fit `budget` and track at least `engines`."""
    floor = RUNGS.index(need)
    fit = []
    for p in plans(tools, priced_only=not include_custom):
        if p.rung_index < floor or p.engines < engines:
            continue
        if budget is not None and p.price is not None and p.price > budget:
            continue
        fit.append(p)
    return fit


def cheapest(tools: list[dict], need: str) -> Plan | None:
    fit = pick(tools, need=need)
    return fit[0] if fit else None


def needed_rung(team: dict) -> str:
    """Lowest rung that covers every role the team does not have."""
    need = "report"
    for role, r in ROLE_TO_RUNG.items():
        if not team.get(role, False) and RUNGS.index(r) > RUNGS.index(need):
            need = r
    return need


def validate(tools: list[dict]) -> list[str]:
    """Return a list of problems. Empty means the dataset is consistent."""
    errors: list[str] = []
    seen: set[str] = set()
    for i, t in enumerate(tools):
        tid = t.get("id", f"#{i}")
        if tid in seen:
            errors.append(f"{tid}: duplicate id")
        seen.add(tid)
        for key in ("id", "name", "url", "entry", "top", "trial"):
            if key not in t:
                errors.append(f"{tid}: missing {key}")
        if "entry" not in t or "top" not in t:
            continue
        if not str(t.get("url", "")).startswith("https://"):
            errors.append(f"{tid}: url must be https")
        for tier in ("entry", "top"):
            p = t[tier]
            for flag in FLAGS:
                if not isinstance(p.get(flag), bool):
                    errors.append(f"{tid}.{tier}: {flag} must be true or false")
            if p.get("price") is not None and not isinstance(p.get("price"), int):
                errors.append(f"{tid}.{tier}: price must be an integer or null")
            if p.get("publishes") and not p.get("drafts"):
                errors.append(f"{tid}.{tier}: publishes without drafts")
        if not isinstance(t["entry"].get("engines_included"), int):
            errors.append(f"{tid}.entry: engines_included must be an integer")
        if RUNGS.index(rung(t["top"])) < RUNGS.index(rung(t["entry"])):
            errors.append(f"{tid}: top plan reaches a lower rung than entry")
        ep, tp = t["entry"].get("price"), t["top"].get("price")
        if isinstance(ep, int) and isinstance(tp, int) and tp < ep:
            errors.append(f"{tid}: top plan is cheaper than entry")
    return errors

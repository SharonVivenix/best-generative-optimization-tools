"""Command line entry point: python -m geopick <command>."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import yaml

from .model import ROOT, RUNGS, load, needed_rung, pick, plans, validate
from .render import BLOCKS, LABEL, render_readme

README = ROOT / "README.md"


def _print_plans(found) -> None:
    for p in found:
        cost = "custom " if p.price is None else f"${p.price:>4}/mo"
        print(f"{cost}  {p.tool} {p.plan}  rung={p.rung}  engines={p.engines}")


def cmd_table(a, tools) -> int:
    for name, fn in BLOCKS.items():
        print(f"{name}\n{fn(tools)}\n")
    return 0


def cmd_write(a, tools) -> int:
    README.write_text(render_readme(README.read_text(encoding="utf-8"), tools),
                      encoding="utf-8", newline="\n")
    print("README tables updated")
    return 0


def cmd_check(a, tools) -> int:
    errors = validate(tools)
    for e in errors:
        print(f"invalid: {e}", file=sys.stderr)
    text = README.read_text(encoding="utf-8")
    stale = render_readme(text, tools) != text
    if stale:
        print("README tables are stale, run: python -m geopick write", file=sys.stderr)
    if errors or stale:
        return 1
    print(f"ok: {len(tools)} tools valid, README tables match tools.yaml")
    return 0


def cmd_pick(a, tools) -> int:
    need = a.need
    if a.team:
        team = yaml.safe_load(Path(a.team).read_text(encoding="utf-8"))
        need = needed_rung(team.get("team", team))
        a.budget = a.budget if a.budget is not None else team.get("budget")
        a.engines = a.engines or team.get("engines", 0)
        print(f"# team needs the tool to reach: {need}", file=sys.stderr)
    found = pick(tools, need=need or "report", budget=a.budget, engines=a.engines,
                 include_custom=a.include_custom)
    if a.json:
        print(json.dumps([p.to_dict() for p in found], indent=2))
    elif found:
        _print_plans(found)
    else:
        print("no published plan fits, loosen --budget or --engines, or add --include-custom")
    return 0 if found else 2


def cmd_export(a, tools) -> int:
    rows = [p.to_dict() for p in plans(tools)]
    if a.format == "json":
        print(json.dumps(rows, indent=2))
    else:
        w = csv.DictWriter(sys.stdout, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="geopick", description=__doc__)
    ap.add_argument("--data", default=None, help="path to a tools.yaml, defaults to the bundled one")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("table", help="print both generated tables").set_defaults(fn=cmd_table)
    sub.add_parser("write", help="rewrite the generated blocks in README.md").set_defaults(fn=cmd_write)
    sub.add_parser("check", help="validate the dataset and fail on a stale README").set_defaults(fn=cmd_check)
    p = sub.add_parser("pick", help="plans that fit a rung, a budget and an engine count")
    p.add_argument("--need", choices=RUNGS, help=f"rung to reach: {', '.join(LABEL)}")
    p.add_argument("--team", help="YAML file describing the roles you already have")
    p.add_argument("--budget", type=int, help="monthly ceiling in USD")
    p.add_argument("--engines", type=int, default=0, help="minimum engines tracked at once")
    p.add_argument("--include-custom", action="store_true", help="include plans quoted by sales")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_pick)
    e = sub.add_parser("export", help="dump every plan as JSON or CSV")
    e.add_argument("--format", choices=["json", "csv"], default="json")
    e.set_defaults(fn=cmd_export)
    return ap


def main(argv: list[str] | None = None) -> int:
    a = build_parser().parse_args(argv)
    tools = load(a.data) if a.data else load()
    return a.fn(a, tools)


if __name__ == "__main__":
    raise SystemExit(main())

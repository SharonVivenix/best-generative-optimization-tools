# Best Generative Optimization Tools

<p align="center">
  <a href="https://aiclicks.io/">
  </a>
</p>

[![checks](https://github.com/SharonVivenix/best-generative-optimization-tools/actions/workflows/checks.yml/badge.svg)](https://github.com/SharonVivenix/best-generative-optimization-tools/actions/workflows/checks.yml)
![python](https://img.shields.io/badge/python-3.9%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

A machine readable dataset of the [best generative engine optimization tools](https://aiclicks.io/blog/best-generative-optimization-tools), plus `geopick`, a small Python CLI that filters it. Eight tools, one YAML file, a JSON Schema, and a test suite that fails the build when the docs drift from the data.

The dataset records one thing other comparisons skip. Every GEO tool tracks prompts and charts mentions. What differs is the point where the software stops and a person takes over, and that point depends on the plan, not the vendor. Each plan here carries three booleans (`recommends`, `drafts`, `publishes`), and the code derives everything else from them.

```console
$ python -m geopick pick --need draft --budget 300
$  59/mo  AIclicks Starter  rung=draft  engines=3
$ 245/mo  Promptwatch Professional  rung=published  engines=14
$ 250/mo  Scrunch AI Core  rung=draft  engines=4
```

## Contents

- [Install](#install)
- [Usage](#usage)
- [Data model](#data-model)
- [The dataset](#the-dataset)
- [Use it as a library](#use-it-as-a-library)
- [Use the data without Python](#use-the-data-without-python)
- [Project layout](#project-layout)
- [Development](#development)
- [Notes per tool](#notes-per-tool)
- [FAQ](#faq)

## Install

There is nothing to build and one dependency.

```bash
git clone https://github.com/SharonVivenix/best-generative-optimization-tools.git
cd best-generative-optimization-tools
pip install -r requirements.txt
python -m geopick check
```

Python 3.9 or newer. The only runtime dependency is PyYAML. `jsonschema` is optional and used by one test.

## Usage

```text
python -m geopick <command> [options]

  table     print both generated tables
  write     rewrite the generated blocks in README.md
  check     validate the dataset and fail on a stale README
  pick      plans that fit a rung, a budget and an engine count
  export    dump every plan as JSON or CSV
```

### pick

| Flag | Type | Meaning |
| --- | --- | --- |
| `--need` | `report`, `recommendation`, `draft`, `published` | Lowest rung the plan has to reach |
| `--team` | path | YAML file listing the roles you already have, replaces `--need` |
| `--budget` | integer | Monthly ceiling in USD |
| `--engines` | integer | Minimum AI engines tracked at once |
| `--include-custom` | flag | Also return plans that are quoted by sales |
| `--json` | flag | Print JSON, for piping into `jq` or another script |

Results are sorted by price. The exit code is `0` when something fits and `2` when nothing does, so the command works inside a shell condition.

### Picking from the best AI tools for generative engine optimization by team shape

Describing your team is usually easier than naming a rung. Copy [examples/team.example.yaml](examples/team.example.yaml) and mark the roles you have.

```yaml
team:
  strategist: false   # decides which page to fix or which source to pitch
  writer: false       # writes the article or the rewrite
  publisher: true     # gets it live in the CMS

budget: 300
engines: 3
```

```console
$ python -m geopick pick --team examples/team.example.yaml
# team needs the tool to reach: draft
$  59/mo  AIclicks Starter  rung=draft  engines=3
$ 245/mo  Promptwatch Professional  rung=published  engines=14
$ 250/mo  Scrunch AI Core  rung=draft  engines=4
```

`geopick` maps every missing role to the rung that replaces it and takes the highest one. No writer means the plan has to draft. No publisher means it has to publish.

### export

```console
$ python -m geopick export --format csv
tool,tool_id,plan,tier,price,rung,engines
Otterly AI,otterly,Lite,entry,29,recommendation,3
AIclicks,aiclicks,Starter,entry,59,draft,3
Peec AI,peec,Starter,entry,95,recommendation,3
Promptwatch,promptwatch,Essential,entry,95,report,14
...
```

## Data model

One list item per tool in [tools.yaml](tools.yaml), validated by [schema/tools.schema.json](schema/tools.schema.json).

```yaml
- id: promptwatch
  name: Promptwatch
  url: https://promptwatch.com
  entry:                      # cheapest paid plan
    plan: Essential
    price: 95                 # integer USD per month, null when quoted by sales
    unit: /mo
    engines: All 14 supported # human readable
    engines_included: 14      # integer, what --engines filters on
    recommends: false
    drafts: false
    publishes: false
  top:                        # cheapest plan that reaches the vendor's highest rung
    plan: Professional
    price: 245
    recommends: true
    drafts: true
    publishes: true
  trial: 7 days
  note: 50 prompts, content writing and crawler logs start on Professional
```

The rung is never stored. `geopick.model.rung()` returns the highest flag that is true.

| Rung | Flag | The plan does this | Your team still does this |
| --- | --- | --- | --- |
| `report` | none | Runs prompts, shows mentions, citations and competitors | Decides the fix, writes it, publishes it |
| `recommendation` | `recommends` | Names the page to change or the source to pitch | Writes it, publishes it |
| `draft` | `drafts` | Writes the article or the page rewrite | Edits it, publishes it |
| `published` | `publishes` | Pushes the content into a CMS | Reviews it, handles outreach |

Validation rules enforced by `python -m geopick check`:

- `id` is unique, `url` is https.
- All three flags are real booleans on both plans.
- `price` is an integer or `null`, never a string and never a guess.
- `publishes` requires `drafts`.
- The `top` plan cannot reach a lower rung or cost less than `entry`.

To get editor autocomplete on the data file, add this as its first line:

```yaml
# yaml-language-server: $schema=./schema/tools.schema.json
```

## The dataset

Both tables below are build output. Do not edit them by hand, run `python -m geopick write`.

<!-- TABLE:START -->
| Tool | Entry plan | Price | Engines at entry | Stops at on entry | Left to your team | Highest rung sold | Trial |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [AIclicks](https://aiclicks.io) | Starter | $59/mo | 3, you pick | Draft | Editing, publishing | Draft | 3 days, card required |
| [Otterly AI](https://otterly.ai) | Lite | $29/mo | 3 of 7 | Recommendation | Writing, publishing | Recommendation | 7 days, no card |
| [Peec AI](https://peec.ai) | Starter | $95/mo | 3 of 6, you pick | Recommendation | Writing, publishing | Recommendation | Yes, length not stated |
| [Semrush AI Visibility Toolkit](https://www.semrush.com) | Toolkit | $99/mo per domain | 4, varies by report | Recommendation | Writing, publishing | Recommendation | 7 days |
| [Promptwatch](https://promptwatch.com) | Essential | $95/mo | All 14 supported | Report | Deciding the fix, writing, publishing | Published page (Professional, $245/mo) | 7 days |
| [Ahrefs Brand Radar](https://ahrefs.com/brand-radar) | One platform | $199/mo per platform | 1 per index, 6 for $699 | Report | Deciding the fix, writing, publishing | Report | None, free checker preview |
| [Scrunch AI](https://scrunch.com) | Core | $250/mo billed annually | 4 (9 on Enterprise) | Draft | Editing, publishing | Draft | 7 days, no card |
| [Profound](https://www.tryprofound.com) | Trial only | Custom | 3 on trial (9 on Enterprise) | Report | Deciding the fix, writing, publishing | Draft (Enterprise, custom price) | 7 days, 50 fixed prompts |
<!-- TABLE:END -->

Cheapest published plan per rung, computed by `geopick.render.ladder()`:

<!-- LADDER:START -->
| Rung | Cheapest published plan that reaches it | Price | Next cheapest |
| --- | --- | --- | --- |
| Report | Otterly AI Lite | $29/mo | AIclicks Starter at $59, Peec AI Starter at $95 |
| Recommendation | Otterly AI Lite | $29/mo | AIclicks Starter at $59, Peec AI Starter at $95 |
| Draft | AIclicks Starter | $59/mo | Promptwatch Professional at $245, Scrunch AI Core at $250 |
| Published page | Promptwatch Professional | $245/mo | None with a published price |
<!-- LADDER:END -->

Facts were read from vendor pages in November 2026. Plans change often, so treat the file as a snapshot and open a PR when a number moves.

## Use it as a library

```python
from geopick import load, pick, cheapest, needed_rung

tools = load()

# every published plan that writes content and tracks 4 or more engines
for p in pick(tools, need="draft", engines=4):
    print(p.tool, p.plan, p.price, p.rung)

# the floor price for a rung
print(cheapest(tools, "published"))

# rung implied by a team with a writer but nobody to plan the work
print(needed_rung({"strategist": False, "writer": True, "publisher": True}))
```

`pick()` returns frozen `Plan` dataclasses with `tool`, `tool_id`, `plan`, `tier`, `price`, `rung` and `engines`. Every function in `geopick.model` is pure, with no file writes and no network calls, so it is safe to import into a notebook or a CI job.

To run it against your own shortlist, pass another file: `python -m geopick --data my-tools.yaml pick --need draft`.

## Use the data without Python

The YAML file is the source of truth and the raw URL is stable.

```bash
curl -sL https://raw.githubusercontent.com/SharonVivenix/best-generative-optimization-tools/main/tools.yaml
```

For JSON, pipe the export through `jq`:

```bash
python -m geopick export | jq '.[] | select(.rung == "recommendation") | {tool, plan, price}'
```

## Project layout

```text
.
├── tools.yaml                  source of truth, one entry per tool
├── schema/tools.schema.json    JSON Schema for tools.yaml
├── geopick/
│   ├── model.py                load, rung, plans, pick, validate
│   ├── render.py               Markdown tables and README splicing
│   ├── cli.py                  argparse commands
│   └── __main__.py             python -m geopick
├── examples/team.example.yaml  input for pick --team
├── tests/test_geopick.py       unittest suite, 12 tests
├── render_table.py             shim kept for the old command
└── .github/workflows/checks.yml
```

## Development

```bash
pip install -r requirements.txt jsonschema
python -m unittest discover -s tests -v
python -m geopick check
```

CI runs three jobs on every push and pull request:

| Job | What fails it |
| --- | --- |
| `data` | An invalid entry in `tools.yaml`, or README tables that no longer match it |
| `tests` | Any unit test, on Python 3.9 and 3.12 |
| `links` | A link to aiclicks.io or github.com in the README that does not return 200 |

To change a fact, edit `tools.yaml`, run `python -m geopick write`, and commit both files. See [CONTRIBUTING.md](CONTRIBUTING.md) for what gets merged.

## Notes per tool

Short context for the rows above. The `note` field in the data file carries the same facts in one line.

| Tool | Where the entry plan stops | Worth knowing before you filter |
| --- | --- | --- |
| AIclicks | Draft. Starter ranks the fixes and writes 5 articles a month | Three models of your choice, one country, one website. GA4, API and MCP start at Pro, $189 |
| Otterly AI | Recommendation. Three a week on Lite, no content writing | Three of seven engines. The next plan is $189 |
| Peec AI | Recommendation, through its Actions feature | Unlimited users. Each extra model adds $30 a month on Starter |
| Semrush AI Visibility Toolkit | Recommendation, inside the Brand Performance report | 25 prompts on one domain. Engine coverage differs per report |
| Promptwatch | Report on Essential | Professional at $245 adds writing, crawler logs and publishing to WordPress, Webflow and Framer |
| Ahrefs Brand Radar | Report. A research index of 551 million prompts | Sold per AI platform. Claude only through custom prompts |
| Scrunch AI | Draft, in small amounts. One page optimization a month | Its Agent Experience Platform is Enterprise only |
| Profound | Report, on a 7 day trial with preset prompts | Nothing is sold between the trial and an Enterprise quote |

For background on the practice itself, see this explainer on [generative engine optimization](https://aiclicks.io/blog/what-is-generative-engine-optimization). The current AIclicks tiers are on its [pricing page](https://aiclicks.io/pricing).

## FAQ

### Why model plans as booleans and not scores?

A score hides the reason behind it and invites argument. A boolean is checkable against one vendor page. Either the plan writes content or it does not, and a reviewer can confirm that in a minute.

### Why does `pick` return Promptwatch Professional for `--need draft`?

Rungs are cumulative. A plan that publishes also drafts, so it satisfies any lower requirement. Sort order is price, which is why it lands between the two draft plans.

### Why are some prices `null`?

The vendor quotes them through sales. `pick` leaves those plans out unless you pass `--include-custom`, because a plan without a number cannot be compared against a budget.

### Can I add a tool that is not on the list?

Yes. Add an entry, run `python -m geopick check`, and open a PR with a link to the vendor page that backs each flag. Affiliate links and review site scores are not accepted.

### How do I track a different set of tools privately?

Keep your own YAML file in the same shape and pass it with `--data`. The package never assumes the bundled file.

## Credits

The shortlist and plan facts started from the AIclicks roundup linked at the top, which covers twelve products. AIclicks is listed first in the data file and is the publisher of that roundup, so weigh the ordering with that in mind. The rung model, the code and the schema are our own. Vendor review scores from the roundup were dropped, and the Promptwatch engine count was corrected against its pricing page.

## License

MIT. See [LICENSE](LICENSE).

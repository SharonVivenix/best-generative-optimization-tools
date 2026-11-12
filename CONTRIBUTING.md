# Contributing

This repo is a dataset of generative optimization tools plus the `geopick` CLI that reads it. Corrections, new tools and code changes are all welcome.

## Changing the data

1. Edit [tools.yaml](tools.yaml). Each tool has an `entry` plan and a `top` plan, and each plan carries three booleans: `recommends`, `drafts`, `publishes`.
2. Run `python -m geopick write` to regenerate both blocks between the markers in the README.
3. Run `python -m geopick check` and `python -m unittest discover -s tests`.
4. Open a PR with a link to the vendor page that backs the change.

## What gets merged

- A boolean flipped to `true` only when the vendor page says the plan does it. A feature on a higher tier belongs in `top`, not `entry`.
- Real prices with the billing unit named. A price quoted by sales is `null`, never a guess.
- Trials stated as trials, with the card requirement if the vendor publishes it.
- Code changes that come with a test and keep `geopick.model` free of file writes and network calls.

## What gets rejected

- Affiliate links. Vendor domain only.
- Review site scores. They move weekly and they say nothing about where a plan stops.
- A typed rung. The rung is computed, so change the booleans.
- New runtime dependencies. PyYAML is the only one.

## Setup

```bash
pip install -r requirements.txt jsonschema
python -m geopick table             # preview both tables
python -m geopick write             # write them into README.md
python -m geopick pick --need draft # plans that write content, cheapest first
python -m unittest discover -s tests -v
```

# Contributing

This list sorts generative optimization tools by the rung where each plan stops and your team takes over. Corrections and additions are welcome.

## Edit the data, not the table

1. Edit [tools.yaml](tools.yaml). Each tool has an `entry` plan and a `top` plan, and each plan carries three booleans: `recommends`, `drafts`, `publishes`.
2. Run `python render_table.py --write` to regenerate both blocks between the markers in the README.
3. Run `python render_table.py --check` and open a PR with a link to the vendor page that backs the change.

## What gets merged

- A boolean flipped to `true` only when the vendor page says the plan does it. A feature on a higher tier belongs in `top`, not `entry`.
- Real prices with the billing unit named. A price quoted by sales is `null`, never a guess.
- Trials stated as trials, with the card requirement if the vendor publishes it.

## What gets rejected

- Affiliate links. Vendor domain only.
- Review site scores. They move weekly and they say nothing about where a plan stops.
- A typed rung. The rung is computed, so change the booleans.

## Setup

```bash
pip install pyyaml
python render_table.py              # preview both tables
python render_table.py --write      # write them into README.md
python render_table.py --need draft # plans that write content, cheapest first
```

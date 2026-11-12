import copy
import json
import unittest
from pathlib import Path

from geopick import cheapest, load, needed_rung, pick, plans, rung, validate
from geopick.render import render_readme

ROOT = Path(__file__).resolve().parent.parent


class Dataset(unittest.TestCase):
    def setUp(self):
        self.tools = load()

    def test_dataset_is_valid(self):
        self.assertEqual(validate(self.tools), [])

    def test_matches_json_schema(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema not installed")
        schema = json.loads((ROOT / "schema" / "tools.schema.json").read_text(encoding="utf-8"))
        jsonschema.validate(self.tools, schema)

    def test_readme_is_in_sync(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertEqual(render_readme(text, self.tools), text)

    def test_ids_are_unique(self):
        ids = [t["id"] for t in self.tools]
        self.assertEqual(len(ids), len(set(ids)))


class Rungs(unittest.TestCase):
    def test_rung_takes_the_highest_flag(self):
        self.assertEqual(rung({"recommends": False, "drafts": False, "publishes": False}), "report")
        self.assertEqual(rung({"recommends": True, "drafts": False, "publishes": False}), "recommendation")
        self.assertEqual(rung({"recommends": True, "drafts": True, "publishes": False}), "draft")
        self.assertEqual(rung({"recommends": True, "drafts": True, "publishes": True}), "published")

    def test_needed_rung_follows_the_missing_role(self):
        full = {"strategist": True, "writer": True, "publisher": True}
        self.assertEqual(needed_rung(full), "report")
        self.assertEqual(needed_rung({**full, "strategist": False}), "recommendation")
        self.assertEqual(needed_rung({**full, "writer": False}), "draft")
        self.assertEqual(needed_rung({}), "published")


class Picking(unittest.TestCase):
    def setUp(self):
        self.tools = load()

    def test_pick_is_sorted_by_price(self):
        prices = [p.price for p in pick(self.tools)]
        self.assertEqual(prices, sorted(prices))

    def test_pick_respects_every_filter(self):
        for p in pick(self.tools, need="draft", budget=300, engines=3):
            self.assertGreaterEqual(p.rung_index, 2)
            self.assertLessEqual(p.price, 300)
            self.assertGreaterEqual(p.engines, 3)

    def test_custom_plans_are_opt_in(self):
        self.assertTrue(all(p.price is not None for p in pick(self.tools)))
        self.assertTrue(any(p.price is None for p in pick(self.tools, include_custom=True)))

    def test_cheapest_never_costs_less_for_a_higher_rung(self):
        costs = [cheapest(self.tools, r).price for r in ("report", "recommendation", "draft", "published")]
        self.assertEqual(costs, sorted(costs))

    def test_plans_are_deduplicated(self):
        keys = [(p.tool_id, p.plan) for p in plans(self.tools)]
        self.assertEqual(len(keys), len(set(keys)))


class Validation(unittest.TestCase):
    def test_catches_a_broken_entry(self):
        tools = copy.deepcopy(load())
        tools[0]["entry"]["drafts"] = "yes"
        tools[1]["top"]["price"] = 1
        tools.append(copy.deepcopy(tools[0]))
        errors = validate(tools)
        self.assertTrue(any("drafts must be true or false" in e for e in errors))
        self.assertTrue(any("cheaper than entry" in e for e in errors))
        self.assertTrue(any("duplicate id" in e for e in errors))


if __name__ == "__main__":
    unittest.main()

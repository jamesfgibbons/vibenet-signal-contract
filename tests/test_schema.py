from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "spec" / "v1" / "schema.json"
SITE_SCHEMA_PATH = ROOT / "site" / "v1" / "schema.json"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class SignalContractSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_json(SCHEMA_PATH)
        cls.site_schema = load_json(SITE_SCHEMA_PATH)
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema)

    def test_site_schema_matches_spec_schema(self):
        self.assertEqual(self.schema, self.site_schema)

    def test_valid_signals_pass(self):
        cases = load_json(ROOT / "tests" / "valid_signals.json")
        for case in cases:
            with self.subTest(case=case["name"]):
                errors = sorted(self.validator.iter_errors(case["payload"]), key=lambda error: list(error.path))
                self.assertEqual(errors, [])

    def test_invalid_signals_fail(self):
        cases = load_json(ROOT / "tests" / "invalid_signals.json")
        for case in cases:
            with self.subTest(case=case["name"]):
                errors = sorted(self.validator.iter_errors(case["payload"]), key=lambda error: list(error.path))
                self.assertTrue(errors, f"expected validation errors for {case['name']}")

    def test_edge_signals_pass(self):
        cases = load_json(ROOT / "tests" / "edge_signals.json")
        for case in cases:
            with self.subTest(case=case["name"]):
                errors = sorted(self.validator.iter_errors(case["payload"]), key=lambda error: list(error.path))
                self.assertEqual(errors, [])

    def test_browser_example_signal_passes(self):
        payload = load_json(ROOT / "examples" / "browser-earcon" / "sample-signal.json")
        errors = sorted(self.validator.iter_errors(payload), key=lambda error: list(error.path))
        self.assertEqual(errors, [])

    def test_python_example_signal_passes(self):
        payload = load_json(ROOT / "examples" / "python-logger" / "sample_signal.json")
        errors = sorted(self.validator.iter_errors(payload), key=lambda error: list(error.path))
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
CORE_SCHEMA_PATH = ROOT / "spec" / "v1" / "schema.json"
SITE_SCHEMA_PATH = ROOT / "site" / "v1" / "schema.json"

PACKS = (
    "adapter-profile",
    "modulation-profile",
    "attention-projection",
)

CORE_REQUIRED = (
    "schema_version",
    "id",
    "occurred_at",
    "producer",
    "entity",
    "event",
    "channel",
    "valence",
    "energy",
    "tension",
    "intensity",
    "hue",
    "pulse",
)


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def profile_root(name: str) -> Path:
    return ROOT / "profiles" / name / "0.1"


def build_validator(schema: dict, *extra_schemas: dict) -> Draft202012Validator:
    registry = Registry()
    for extra in extra_schemas:
        registry = registry.with_resource(extra["$id"], Resource.from_contents(extra))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, registry=registry)


def adapter_semantic_errors(payload: dict, profile: dict) -> list[str]:
    errors = []
    statuses = {rule["status"] for rule in payload.get("rules", [])}
    if "accepted_rule_ids" in payload:
        errors.append("emit_policy")
    if statuses <= set(profile["rule_statuses"]) - set(profile["emit_statuses"]):
        if payload.get("proposal_source") == "browser_assist" and statuses == {"proposed"}:
            return errors
    return errors


def modulation_semantic_errors(payload: dict, profile: dict) -> list[str]:
    errors = []
    receipt = payload.get("derivation_receipt") or {}
    target_channel = receipt.get("target_channel")
    safety = profile["channel_safety"].get(target_channel)
    if safety and payload.get("onset_ms", 0) > safety["max_onset_ms"]:
        if not receipt.get("safety", {}).get("critical_onset_capped"):
            errors.append("channel_safety")
    if payload.get("max_transition_ms", 0) > profile["max_transition_ms_cap"]:
        errors.append("max_transition")
    return errors


def attention_semantic_errors(payload: dict, profile: dict) -> list[str]:
    errors = []
    expected = payload.get("expected_entity_count", 0)
    observed = payload.get("observed_entity_count", 0)
    unobserved = payload.get("unobserved_entity_count", 0)
    named = payload.get("unobserved_entities") or []
    if expected > observed and (unobserved != expected - observed or len(named) != unobserved):
        errors.append("unobserved_policy")
    max_slots = profile["default_policy"]["max_foreground_slots"]
    if payload.get("mode") == "governed" and len(payload.get("foreground_slots") or []) > max_slots:
        errors.append("slot_budget")
    if payload.get("source_signal_count") != len(payload.get("source_signal_ids") or []):
        errors.append("source_count")
    return errors


SEMANTIC = {
    "adapter-profile": adapter_semantic_errors,
    "modulation-profile": modulation_semantic_errors,
    "attention-projection": attention_semantic_errors,
}


class AdjacentProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core_schema = load_json(CORE_SCHEMA_PATH)
        cls.packs = {}
        for name in PACKS:
            root = profile_root(name)
            schema = load_json(root / "profile.schema.json")
            receipt_path = root / "receipt.schema.json"
            receipt_schema = load_json(receipt_path)
            cls.packs[name] = {
                "root": root,
                "profile": load_json(root / "profile.json"),
                "schema": schema,
                "receipt_schema": receipt_schema,
                "validator": build_validator(schema, receipt_schema),
                "receipt_validator": build_validator(receipt_schema),
            }

    def test_core_schema_untouched_and_dual_published(self):
        site = load_json(SITE_SCHEMA_PATH)
        self.assertEqual(self.core_schema, site)
        self.assertEqual(self.core_schema["$id"], "https://vibenet.ai/protocol/v1/schema.json")
        self.assertEqual(self.core_schema["required"], list(CORE_REQUIRED))
        self.assertEqual(self.core_schema["properties"]["schema_version"]["const"], "1.0")

    def test_each_pack_is_adjacent_and_non_breaking(self):
        for name, pack in self.packs.items():
            profile = pack["profile"]
            with self.subTest(profile=name):
                self.assertTrue(profile["adjacent"])
                self.assertFalse(profile["adds_required_sc_fields"])
                self.assertEqual(profile["signal_contract_version"], "1.0")
                self.assertTrue(profile["canonical_question"])
                self.assertNotIn(
                    pack["schema"]["$id"],
                    ["https://vibenet.ai/protocol/v1/schema.json"],
                )
                self.assertNotEqual(pack["schema"].get("allOf"), [{"$ref": self.core_schema["$id"]}])

    def test_valid_fixtures_pass_schema_and_semantics(self):
        for name, pack in self.packs.items():
            fixtures = load_jsonl(pack["root"] / "fixtures" / "valid.jsonl")
            self.assertGreaterEqual(len(fixtures), 2, name)
            checker = SEMANTIC[name]
            for payload in fixtures:
                with self.subTest(profile=name, id=payload.get("profile_id") or payload.get("projection_id") or payload.get("transition_class")):
                    self.assertEqual(list(pack["validator"].iter_errors(payload)), [])
                    self.assertEqual(checker(payload, pack["profile"]), [])

    def test_invalid_fixtures_fail_the_declared_rule(self):
        for name, pack in self.packs.items():
            cases = load_json(pack["root"] / "fixtures" / "invalid.json")
            checker = SEMANTIC[name]
            for case in cases:
                payload = case["payload"]
                with self.subTest(profile=name, case=case["name"]):
                    schema_errors = list(pack["validator"].iter_errors(payload))
                    if case["expected_rule"] == "profile_schema":
                        self.assertTrue(schema_errors)
                    else:
                        self.assertEqual(schema_errors, [])
                        self.assertIn(case["expected_rule"], checker(payload, pack["profile"]))

    def test_receipts_validate(self):
        for name, pack in self.packs.items():
            valid = pack["root"] / "fixtures" / "receipt-valid.json"
            invalid = pack["root"] / "fixtures" / "receipt-invalid.json"
            if not valid.exists():
                continue
            with self.subTest(profile=name, kind="valid"):
                self.assertEqual(
                    list(pack["receipt_validator"].iter_errors(load_json(valid))),
                    [],
                )
            if invalid.exists():
                for case in load_json(invalid):
                    with self.subTest(profile=name, case=case["name"]):
                        self.assertTrue(
                            list(pack["receipt_validator"].iter_errors(case["payload"]))
                        )

    def test_adapter_proposed_rules_cannot_be_emit_status(self):
        profile = self.packs["adapter-profile"]["profile"]
        self.assertEqual(profile["emit_policy"], "accepted_rules_only")
        self.assertEqual(profile["emit_statuses"], ["accepted"])
        self.assertNotIn("proposed", profile["emit_statuses"])
        proposed_only = load_jsonl(profile_root("adapter-profile") / "fixtures" / "valid.jsonl")[1]
        accepted = [rule for rule in proposed_only["rules"] if rule["status"] == "accepted"]
        self.assertEqual(accepted, [])

    def test_modulation_same_state_pair_differs_only_in_arrival(self):
        fixtures = load_jsonl(profile_root("modulation-profile") / "fixtures" / "valid.jsonl")
        self.assertEqual(len(fixtures), 2)
        a, b = fixtures
        self.assertEqual(a["previous_signal_id"], b["previous_signal_id"])
        self.assertEqual(a["target_signal_id"], b["target_signal_id"])
        self.assertEqual(a["valence_curve"]["to"], b["valence_curve"]["to"])
        self.assertEqual(a["energy_curve"]["to"], b["energy_curve"]["to"])
        self.assertEqual(a["tension_curve"]["to"], b["tension_curve"]["to"])
        self.assertNotEqual(a["transition_class"], b["transition_class"])
        self.assertNotEqual(a["interruptibility"], b["interruptibility"])

    def test_attention_governed_budget_and_unobserved(self):
        profile = self.packs["attention-projection"]["profile"]
        self.assertTrue(profile["selection_is_not_truth"])
        self.assertEqual(profile["unobserved_is_not"], ["idle", "nominal"])
        self.assertEqual(profile["default_policy"]["max_foreground_slots"], 4)
        governed = load_jsonl(profile_root("attention-projection") / "fixtures" / "valid.jsonl")[0]
        self.assertEqual(governed["mode"], "governed")
        self.assertLessEqual(len(governed["foreground_slots"]), 4)
        self.assertGreater(governed["unobserved_entity_count"], 0)
        self.assertTrue(any(slot["critical_bypass"] for slot in governed["foreground_slots"]))


if __name__ == "__main__":
    unittest.main()

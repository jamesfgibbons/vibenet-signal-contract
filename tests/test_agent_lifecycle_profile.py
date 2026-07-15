from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
PROFILE_ROOT = ROOT / "profiles" / "agent-lifecycle" / "0.1"
CORE_SCHEMA_PATH = ROOT / "spec" / "v1" / "schema.json"
PROFILE_SCHEMA_PATH = PROFILE_ROOT / "profile.schema.json"
PROFILE_PATH = PROFILE_ROOT / "profile.json"
VALID_FIXTURES_PATH = PROFILE_ROOT / "fixtures" / "valid.jsonl"
INVALID_FIXTURES_PATH = PROFILE_ROOT / "fixtures" / "invalid.json"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def semantic_errors(payload, profile):
    event_rule = profile["events"].get(payload.get("event"))
    if event_rule is None:
        return ["unknown profile event"]

    metadata = payload.get("metadata", {})
    errors = []
    if metadata.get("lifecycle_state") not in event_rule["lifecycle_states"]:
        errors.append("lifecycle_state")
    if payload.get("channel") not in event_rule["channels"]:
        errors.append("channel")
    if metadata.get("requires_action") is not event_rule["requires_action"]:
        errors.append("requires_action")
    if metadata.get("terminal") is not event_rule["terminal"]:
        errors.append("terminal")
    if metadata.get("attention_reason") not in event_rule["attention_reasons"]:
        errors.append("attention_reason")
    return errors


class AgentLifecycleProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core_schema = load_json(CORE_SCHEMA_PATH)
        cls.profile_schema = load_json(PROFILE_SCHEMA_PATH)
        cls.profile = load_json(PROFILE_PATH)
        registry = Registry().with_resource(
            cls.core_schema["$id"], Resource.from_contents(cls.core_schema)
        )
        Draft202012Validator.check_schema(cls.profile_schema)
        cls.core_validator = Draft202012Validator(cls.core_schema)
        cls.profile_validator = Draft202012Validator(
            cls.profile_schema, registry=registry
        )

    def test_profile_is_non_breaking_and_pinned_to_v1(self):
        self.assertEqual(self.profile["profile"], "vibenet.agent-lifecycle/0.1")
        self.assertEqual(self.profile["signal_contract_version"], "1.0")
        self.assertEqual(
            self.profile_schema["allOf"][0]["$ref"], self.core_schema["$id"]
        )

    def test_lifecycle_states_and_precedence_are_exact(self):
        self.assertEqual(
            self.profile["lifecycle_states"],
            ["unobserved", "idle", "running", "needs_input", "complete", "error"],
        )
        self.assertEqual(
            self.profile["precedence"],
            ["error", "needs_input", "running", "complete", "idle"],
        )
        self.assertEqual(self.profile["source_loss_state"], "unobserved")
        self.assertEqual(self.profile["completion_hold_ms"], 3000)

    def test_valid_fixtures_pass_core_profile_and_semantics(self):
        fixtures = load_jsonl(VALID_FIXTURES_PATH)
        self.assertEqual(len(fixtures), 10)
        for payload in fixtures:
            with self.subTest(event=payload["event"]):
                self.assertEqual(list(self.core_validator.iter_errors(payload)), [])
                self.assertEqual(list(self.profile_validator.iter_errors(payload)), [])
                self.assertEqual(semantic_errors(payload, self.profile), [])

    def test_invalid_fixtures_fail_the_declared_profile_rule(self):
        cases = load_json(INVALID_FIXTURES_PATH)
        for case in cases:
            payload = case["payload"]
            with self.subTest(case=case["name"]):
                self.assertEqual(list(self.core_validator.iter_errors(payload)), [])
                if case["expected_rule"] == "profile_schema":
                    self.assertTrue(list(self.profile_validator.iter_errors(payload)))
                else:
                    self.assertEqual(list(self.profile_validator.iter_errors(payload)), [])
                    self.assertTrue(semantic_errors(payload, self.profile))

    def test_metadata_schema_is_a_closed_allowlist(self):
        metadata_schema = self.profile_schema["allOf"][1]["properties"]["metadata"]
        self.assertFalse(metadata_schema["additionalProperties"])
        self.assertEqual(
            set(metadata_schema["required"]), set(metadata_schema["properties"])
        )
        self.assertTrue(metadata_schema["properties"]["content_redacted"]["const"])

    def test_completion_and_interruption_are_distinct(self):
        completed = self.profile["events"]["agent.completed"]
        interrupted = self.profile["events"]["agent.interrupted"]
        self.assertEqual(completed["lifecycle_states"], ["complete"])
        self.assertEqual(completed["channels"], ["nominal"])
        self.assertTrue(completed["terminal"])
        self.assertEqual(interrupted["lifecycle_states"], ["error"])
        self.assertEqual(interrupted["channels"], ["warning"])
        self.assertNotEqual(completed, interrupted)

    def test_recovery_is_a_transition_not_a_seventh_state(self):
        self.assertNotIn("recovery", self.profile["lifecycle_states"])
        recovered = self.profile["events"]["agent.recovered"]
        self.assertEqual(recovered["channels"], ["recovery"])
        self.assertEqual(recovered["lifecycle_states"], ["idle", "running"])


if __name__ == "__main__":
    unittest.main()

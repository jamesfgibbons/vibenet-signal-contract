from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
PROFILE_ROOT = ROOT / "profiles" / "mcp-source" / "0.1"
CORE_SCHEMA_PATH = ROOT / "spec" / "v1" / "schema.json"
PROFILE_SCHEMA_PATH = PROFILE_ROOT / "profile.schema.json"
PROFILE_PATH = PROFILE_ROOT / "profile.json"
VALID_FIXTURES_PATH = PROFILE_ROOT / "fixtures" / "valid.jsonl"
INVALID_FIXTURES_PATH = PROFILE_ROOT / "fixtures" / "invalid.json"
AUTHORITY_PATH = PROFILE_ROOT / "fixtures" / "authority-trace.jsonl"
RECEIPT_SCHEMA_PATH = PROFILE_ROOT / "receipt.schema.json"


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
    if metadata.get("terminal") not in event_rule["terminal_values"]:
        errors.append("terminal")
    if metadata.get("attention_reason") not in event_rule["attention_reasons"]:
        errors.append("attention_reason")
    return errors


class McpSourceProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core_schema = load_json(CORE_SCHEMA_PATH)
        cls.profile_schema = load_json(PROFILE_SCHEMA_PATH)
        cls.profile = load_json(PROFILE_PATH)
        cls.receipt_schema = load_json(RECEIPT_SCHEMA_PATH)
        registry = Registry().with_resource(
            cls.core_schema["$id"], Resource.from_contents(cls.core_schema)
        )
        Draft202012Validator.check_schema(cls.profile_schema)
        Draft202012Validator.check_schema(cls.receipt_schema)
        cls.core_validator = Draft202012Validator(cls.core_schema)
        cls.profile_validator = Draft202012Validator(
            cls.profile_schema, registry=registry
        )

    def test_profile_is_non_breaking_and_pinned(self):
        self.assertEqual(self.profile["profile"], "vibenet.mcp-source/0.1")
        self.assertEqual(self.profile["signal_contract_version"], "1.0")
        self.assertEqual(self.profile["mcp_spec_version"], "2026-07-28")
        self.assertEqual(self.profile["adds_required_sc_fields"], False)
        self.assertEqual(
            self.profile_schema["allOf"][0]["$ref"], self.core_schema["$id"]
        )

    def test_healthy_tools_call_is_silent(self):
        self.assertIn("tools_call_healthy", self.profile["silent_conditions"])
        emit_events = set(self.profile["events"])
        self.assertNotIn("tools.call", emit_events)

    def test_valid_fixtures_pass_core_profile_and_semantics(self):
        fixtures = load_jsonl(VALID_FIXTURES_PATH)
        self.assertEqual(len(fixtures), 8)
        for payload in fixtures:
            with self.subTest(event=payload["event"]):
                self.assertEqual(list(self.core_validator.iter_errors(payload)), [])
                self.assertEqual(list(self.profile_validator.iter_errors(payload)), [])
                self.assertEqual(semantic_errors(payload, self.profile), [])
                self.assertEqual(payload["metadata"]["mcp_spec_version"], "2026-07-28")
                blob = json.dumps(payload)
                self.assertNotIn("SYSTEM:", blob)
                self.assertNotIn("prompt", payload["metadata"])

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
        self.assertEqual(
            metadata_schema["properties"]["mcp_spec_version"]["const"], "2026-07-28"
        )

    def test_authority_trace_handoff_then_recovery(self):
        beats = load_jsonl(AUTHORITY_PATH)
        self.assertEqual([b["event"] for b in beats], [
            "agent.running",
            "agent.input_requested",
            "agent.recovered",
        ])
        self.assertEqual(beats[1]["channel"], "handoff")
        self.assertEqual(beats[1]["metadata"]["cms_verdict"], "UNMEASURED")
        self.assertEqual(beats[2]["channel"], "recovery")
        self.assertEqual(beats[2]["metadata"]["cms_verdict"], "PASS")
        for beat in beats:
            self.assertEqual(list(self.core_validator.iter_errors(beat)), [])
            self.assertEqual(list(self.profile_validator.iter_errors(beat)), [])

    def test_recovery_is_not_a_lifecycle_state(self):
        self.assertNotIn("recovery", self.profile["lifecycle_states"])
        self.assertEqual(self.profile["events"]["agent.recovered"]["channels"], ["recovery"])


if __name__ == "__main__":
    unittest.main()

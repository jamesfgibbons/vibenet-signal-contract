# Adapter Profile 0.1

`vibenet.adapter-profile/0.1` is an adjacent Signal Contract profile. It does
not change Signal Contract v1 and does not add any required top-level fields to
the flat event object.

The profile answers one question: **when may a foreign source event become a
Signal Contract event?**

Observation is not understanding. Understanding is not authorization to render.
Only a **ratified** adapter rule may emit a Signal Contract object.

## Law

1. A source event may be observed without being mapped.
2. A proposed rule may be inspected, compared, and rejected. It MUST NOT emit.
3. The first matching **accepted** rule wins. Later accepted rules do not fire
   for that source event.
4. Ignored classes are trace-only. They MUST NOT emit.
5. Protected fields MUST be stripped before any Signal Contract metadata is
   built. A leak is an invalid mapping, not a warning.
6. An unmapped observation MUST remain silent. Renderers MUST NOT invent a
   channel, event name, or VET state to fill the gap.

## Rule status

| Status | Meaning | May emit SC? |
| --- | --- | --- |
| `proposed` | Human or assist drafted a mapping. Not ratified. | no |
| `accepted` | Ratified. Eligible to emit. | yes, if `when` matches |
| `rejected` | Considered and refused. Kept for audit. | no |

## Reject reasons

When a source event does not become a Signal Contract object, the mapping MUST
name exactly one reason:

| Reason | Meaning |
| --- | --- |
| `malformed` | The source is not an object. |
| `ignored_class` | The source class is listed on the profile as trace-only. |
| `no_accepted_rule` | The profile has no accepted rules. |
| `unmapped` | Observed, but no accepted `when` clause matched. |
| `invalid_signal` | A rule matched and the produced object failed Signal Contract v1 or leaked a protected field. |

`unmapped` is the honest default. It is not `nominal`, not `idle`, and not a
reason to sonify "everything is fine."

## Protected fields

`protected_fields` is a deny-list of source keys that MUST never appear in
emitted Signal Contract `metadata`. Typical members are tokens, prompts, raw
payloads, filesystem paths, and account identifiers.

The listening receipt counts how many times a protected key was present on a
source event (`protected_exclusions`). That count is an audit fact, not a
license to include the values.

## Listening receipt

`foundry.listening-receipt/0.1` records one mapping pass:

- which accepted vs proposed rules were loaded
- how many source events mapped vs rejected
- the reject-reason histogram
- the Signal Contract ids that were actually emitted
- whether browser assist was enabled (assist still cannot emit)

The receipt does not rewrite the source stream or the emitted events.

## Conformance

An adapter profile conforms when it:

1. validates against `profile.schema.json`;
2. matches the status and reject vocabulary in `profile.json`;
3. emits only objects that validate against Signal Contract v1;
4. never copies a protected field into those objects.

A listening receipt conforms when it validates against `receipt.schema.json`
and its `signal_contract_ids` are a subset of the mapping pass.

See `fixtures/` for deterministic synthetic examples. All fixtures are labeled
synthetic. They are not production traces.

# Agent Lifecycle Profile 0.1

`vibenet.agent-lifecycle/0.1` is an additive Signal Contract profile for
renderer-facing agent state. It does not change Signal Contract v1 or add any
required top-level fields.

The profile answers one question: what should a human-perception renderer know
about an agent without receiving the agent's prompt, output, reasoning, command
text, filesystem paths, or private identifiers?

## Lifecycle states

| State | Meaning | Typical public event | Channel |
| --- | --- | --- | --- |
| `unobserved` | The source is disconnected, expired, or not loaded | `agent.unobserved` | `advisory` |
| `idle` | The source is observed and has no active turn | `agent.idle` | `nominal` |
| `running` | A turn is active without a stronger attention state | `agent.running` | `nominal` |
| `needs_input` | Progress is blocked on approval or user input | `agent.approval_requested` or `agent.input_requested` | `handoff` |
| `complete` | A turn completed successfully | `agent.completed` | `nominal` |
| `error` | A turn failed, the system failed, or the turn was interrupted | `agent.failed`, `agent.system_error`, or `agent.interrupted` | `critical` or `warning` |

`agent.recovered` is a transition event, not another lifecycle state. It carries
the trusted state reached after an error and uses the `recovery` channel.

## Reducer rules

When more than one source condition is true, reducers MUST apply this precedence:

```text
error > needs_input > running > complete > idle
```

Source disconnect, expiration, or `notLoaded` MUST invalidate the previous
state and produce `unobserved`. `notLoaded` MUST NOT be treated as `idle`.

Completion is transient. A conforming reducer emits `agent.completed` once,
holds it for 3,000 milliseconds, and then emits `agent.idle` if no stronger
state arrived. An interrupted turn MUST NOT emit completion.

The first trusted transition out of `error` emits `agent.recovered` once. The
event's `metadata.lifecycle_state` records the state reached after recovery.

## Metadata allowlist

Profile events include only these metadata keys:

- `profile`
- `lifecycle_state`
- `attention_reason`
- `requires_action`
- `terminal`
- `source_protocol`
- `source_method`
- `source_version`
- `source_sequence`
- `timestamp_semantics`
- `content_redacted`
- `thread_ref`
- `turn_ref`

All keys are required so that renderers do not infer missing state. Nullable
values use JSON `null` rather than omission.

## Privacy boundary

`content_redacted` MUST be `true`. `thread_ref` and `turn_ref` MUST be opaque,
non-reversible references. Raw source identifiers are not conforming.

Adapters MUST redact before normalization and before diagnostic logging. Profile
events MUST NOT contain prompts, responses, reasoning, command text, approval
questions, paths, diffs, environment values, secrets, account identifiers, or
raw source payloads.

## Codex app-server mapping

The public Codex app-server is the first reference source for this profile. The
mapping is independent and does not imply an official OpenAI integration.

| Source condition | Profile event |
| --- | --- |
| thread `notLoaded`, disconnect, or expired source | `agent.unobserved` |
| thread `idle` | `agent.idle` |
| active thread or turn | `agent.running` |
| `waitingOnApproval` or an approval request | `agent.approval_requested` |
| `waitingOnUserInput`, user-input request, or elicitation | `agent.input_requested` |
| completed turn | `agent.completed`, then `agent.idle` after the hold |
| interrupted turn | `agent.interrupted` |
| failed turn | `agent.failed` |
| thread `systemError` or error notification | `agent.system_error` |
| trusted state after error | `agent.recovered` once |

Unknown source methods MUST be ignored safely. They MUST NOT be guessed into a
lifecycle state.

For an error notification, `willRetry: true` maps to `terminal: false` and
`willRetry: false` maps to `terminal: true`. Both remain in lifecycle state
`error`; retrying does not become a nominal state.

## Conformance

A profile event conforms when it:

1. validates against Signal Contract v1;
2. validates against `profile.schema.json`;
3. matches the event semantics in `profile.json`; and
4. contains no data outside the metadata allowlist.

See `fixtures/valid.jsonl` and `fixtures/invalid.json` for deterministic examples.

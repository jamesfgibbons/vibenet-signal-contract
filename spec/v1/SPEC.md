# VIBEnet Signal Contract v1

## Purpose

Signal Contract standardizes how systems emit renderer-facing awareness when meaningful state changes occur.

The contract is intentionally small:

- producers emit one JSON object
- adapters transport it
- renderers interpret it

This keeps the contract usable across browsers, loggers, earcons, voice systems, haptics, ambient displays, and device surfaces.

## Canonical example

```json
{
  "schema_version": "1.0",
  "id": "sig_demo_001",
  "occurred_at": "2026-04-20T12:00:00Z",
  "producer": "your-agent",
  "entity": "agent.your_system.worker_01",
  "event": "handoff.requested",
  "channel": "handoff",
  "valence": 0.5,
  "energy": 0.6,
  "tension": 0.7,
  "intensity": 0.7,
  "hue": 44,
  "pulse": 0.8
}
```

## Object shape

### Required fields

| Field | Type | Meaning |
| --- | --- | --- |
| `schema_version` | `string` | Published version of the flat public event object; v1 requires `"1.0"` |
| `id` | `string` | Stable event identifier |
| `occurred_at` | `string` | RFC 3339 / ISO 8601 date-time |
| `producer` | `string` | Producer or adapter that emitted the event |
| `entity` | `string` | Stable subject identifier |
| `event` | `string` | Meaningful awareness event |
| `channel` | `string` | Public semantic channel |
| `valence` | `number` | Normalized affective polarity from `0.0` to `1.0` |
| `energy` | `number` | Normalized activity level from `0.0` to `1.0` |
| `tension` | `number` | Normalized instability from `0.0` to `1.0` |
| `intensity` | `number` | Renderer-facing emphasis from `0.0` to `1.0` |
| `hue` | `number` | Renderer-facing hue hint from `0` to `360` |
| `pulse` | `number` | Renderer-facing cadence hint from `0.0` to `1.0` |

### Optional fields

| Field | Type | Meaning |
| --- | --- | --- |
| `confidence` | `number` | Optional producer confidence from `0.0` to `1.0` |
| `ttl_ms` | `integer` | Optional time-to-live in milliseconds |
| `metadata` | `object` | Optional extra context container, allowed to be empty |

## Public channels

Signal Contract v1 uses seven public semantic channels:

- `nominal`
- `advisory`
- `warning`
- `critical`
- `recovery`
- `opportunity`
- `handoff`

Private taxonomies must be mapped to this public set before emission.

## Field semantics

- `valence` describes the polarity of the current state
- `energy` describes activity level
- `tension` describes instability or unresolved uncertainty
- `intensity` is the renderer-facing urgency/emphasis
- `hue` is a renderer-facing color hint
- `pulse` is a renderer-facing temporal/cadence hint

Signal Contract v1 exposes the public state dimensions. It does not expose the internal formulas or renderer logic used to derive or express them.

## Timestamp and TTL

- `occurred_at` records when the producer emitted the event
- `ttl_ms` declares how long downstream consumers may treat the signal as current
- `ttl_ms = 0` means the signal is instantaneous and may be discarded after immediate handling
- consumers may ignore expired signals, degrade them visually, or archive them as history

## Metadata

`metadata` is for non-canonical context such as:

- route identifiers
- source system names
- device hints
- trace references
- renderer-safe contextual details

Renderers must not depend on `metadata` for core protocol validity.

## Renderer stance

Signal Contract is renderer-agnostic. The same object can feed:

- a browser pulse primitive
- a terminal logger
- an audit trail
- a voice agent
- a wearable surface
- a visual or haptic renderer

The contract does not require a shared backend. It only requires a producer and a consumer that agree on the object.

## Relationship to governance

Constitutional CMS governs what agents are permitted to publish. Signal Contract standardizes how systems emit awareness when governed state changes.

## Explicit non-goals in v1

Signal Contract v1 does not define:

- private channel taxonomies
- producer scoring formulas
- transport protocols
- auth schemes
- renderer certification
- hosted validation services
- product-specific backend architecture

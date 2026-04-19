# Signal Contract v1

## Purpose

Signal Contract standardizes how systems emit awareness when meaningful state changes occur.

The contract is intentionally small:

- producers emit one JSON object
- adapters transport it
- renderers interpret it

This keeps the contract usable across browsers, loggers, earcons, audits, voice agents, MCP tools, and device surfaces.

## Canonical example

```json
{
  "entity": "agent.serpradio.route_intelligence",
  "event": "price_volatility_warning",
  "timestamp": "2026-04-19T13:04:00Z",
  "coordinates": {
    "valence": 0.31,
    "energy": 0.66,
    "tension": 0.82
  },
  "channel": "warning",
  "intensity": 0.83,
  "confidence": 0.87,
  "ttl_ms": 12000,
  "metadata": {
    "source": "serpradio",
    "route": "JFK-LHR",
    "producer": "route_intelligence_adapter"
  }
}
```

## Object shape

### Required fields

| Field | Type | Meaning |
| --- | --- | --- |
| `entity` | `string` | Stable subject identifier |
| `event` | `string` | The state change or awareness event |
| `timestamp` | `string` | RFC 3339 / ISO 8601 timestamp in UTC or offset form |
| `coordinates` | `object` | Public VET-style coordinates |
| `channel` | `string` | Public semantic channel |
| `intensity` | `number` | Renderer-facing emphasis from `0.0` to `1.0` |
| `ttl_ms` | `integer` | Time-to-live in milliseconds |
| `metadata` | `object` | Optional extra context container, allowed to be empty |

### Optional fields

| Field | Type | Meaning |
| --- | --- | --- |
| `confidence` | `number` | Producer confidence from `0.0` to `1.0` |

## Coordinates

`coordinates` contains three public dimensions:

- `valence`: approach/avoid quality
- `energy`: quiet/intense quality
- `tension`: resolved/unstable quality

Signal Contract v1 exposes the coordinates, not the formulas that produced them.

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

## Timestamp and TTL

- `timestamp` records when the producer emitted the signal.
- `ttl_ms` declares how long downstream consumers may treat the signal as current.
- `ttl_ms = 0` means the signal is instantaneous and may be discarded after immediate handling.
- Consumers may ignore expired signals, degrade them visually, or archive them as history.

## Metadata

`metadata` is for non-canonical context such as:

- route identifiers
- source system names
- device hints
- trace references
- renderer hints

Renderers must not depend on `metadata` for core protocol validity.

## Renderer stance

Signal Contract is renderer-agnostic. The same object can feed:

- a browser earcon
- a terminal logger
- an audit trail
- a voice agent
- an MCP tool
- a wearable surface

The contract does not require a shared backend. It only requires a producer and a consumer that agree on the object.

## Relationship to governance

Constitutional CMS governs what agents are permitted to publish. Signal Contract standardizes how systems emit awareness when governed state changes.

## Explicit non-goals in v1

Signal Contract v1 does not define:

- private channel taxonomies
- VET formulas
- transport protocols
- auth schemes
- renderer certification
- hosted validation services
- product-specific backend architecture

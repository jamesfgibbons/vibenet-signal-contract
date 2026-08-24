# v1 metadata conventions

Signal Contract v1 keeps extra context inside optional `metadata`. Renderers
must not depend on `metadata` for core protocol validity. These keys are a
convention, not required fields, and they do not change `schema_version`.

This file is the in-repo target for conformance L4. L4 remains **pending**.
Absence of a reserved key is not a validation failure.

## Registered optional keys

These three keys are documented in Signal Contract v1.0.1 and remain the only
ratified metadata convention:

| Metadata key | Type | Meaning |
| --- | --- | --- |
| `publishable` | `boolean` | Whether the event represents content fit for direct human surfacing |
| `indexable` | `boolean` | Whether the event represents content fit for machine citation, caching, or reference accumulation |
| `fallback_reason` | `string` | Optional explanation when an event is not publishable, especially when it remains indexable |

`publishable` and `indexable` are independent. An event may be both
publishable and indexable, publishable but not indexable, indexable but not
publishable, or neither. A fallback state can therefore remain valid evidence
for machines while being withheld from direct human presentation.

Consumers that do not understand this convention should treat absent or ignored
values as equivalent to:

```json
{
  "publishable": true,
  "indexable": true
}
```

Canonical fallback example:

```json
{
  "schema_version": "1.0",
  "id": "sig_route_fallback_001",
  "occurred_at": "2026-04-20T12:00:00Z",
  "producer": "serpradio.route_intelligence",
  "entity": "route.jfk_lhr",
  "event": "snapshot.fallback_served",
  "channel": "advisory",
  "valence": 0.45,
  "energy": 0.3,
  "tension": 0.5,
  "intensity": 0.4,
  "hue": 200,
  "pulse": 0.35,
  "metadata": {
    "publishable": false,
    "indexable": true,
    "fallback_reason": "primary_source_stale",
    "route": "JFK-LHR"
  }
}
```

## Reserved optional keys

The L4 ladder names additional keys that are **not** ratified and **not**
required:

| Metadata key | Status |
| --- | --- |
| `trace_id` | Reserved. A producer MAY include an opaque correlation id. Absence is not a failure. |
| `evidence_uri` | Reserved. A producer MAY include a URI to supporting evidence. Absence is not a failure. |

Do not treat these reserved names as a second schema. Do not fail a renderer
or producer for omitting them. Ratifying them is part of shipping L4, not a
reason to invent required fields now.

## Adjacent profiles

Profile-specific metadata allowlists live next to Signal Contract, not in this
file:

- [`vibenet.agent-lifecycle/0.1`](../../profiles/agent-lifecycle/0.1/)
- [`vibenet.adapter-profile/0.1`](../../profiles/adapter-profile/0.1/)
- [`vibenet.modulation-profile/0.1`](../../profiles/modulation-profile/0.1/)
- [`vibenet.attention-projection/0.1`](../../profiles/attention-projection/0.1/)

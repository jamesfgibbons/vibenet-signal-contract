# Signal Contract

Signal Contract is a public protocol for awareness events emitted by agents, data systems, and devices.

It standardizes one small JSON object that producers can emit and renderers can consume without sharing a backend, framework, or internal taxonomy.

**One JSON object. Many renderers. No shared backend required.**

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

## Positioning

- `constitutional-cms` is governance. It defines what agents are permitted to publish.
- `signal-contract` is awareness protocol. It defines the event object emitted when governed state changes.
- Renderers and adapters are downstream consumers. A browser earcon, a logger, a device surface, a voice agent, or an MCP tool can all consume the same object.

Constitutional CMS governs what agents are permitted to publish. Signal Contract standardizes how systems emit awareness when governed state changes.

## What v1 standardizes

- A renderer-facing JSON object
- Public-safe semantic channels
- VET-style coordinates without exposing formulas
- TTL and confidence semantics
- Schema validation, fixtures, and reference examples

Signal Contract does not prescribe storage, orchestration, authentication, transport, or deployment topology.

## Public channels

Signal Contract v1 uses seven public semantic channels:

- `nominal`
- `advisory`
- `warning`
- `critical`
- `recovery`
- `opportunity`
- `handoff`

If you run a richer private taxonomy, map it to these public channels at the producer boundary.

## Repo layout

- [`spec/v1/SPEC.md`](/Users/jamesfgibbons/Documents/Targeted%20Impressions%20Hub/signal-contract/spec/v1/SPEC.md)
- [`spec/v1/schema.json`](/Users/jamesfgibbons/Documents/Targeted%20Impressions%20Hub/signal-contract/spec/v1/schema.json)
- [`examples/browser-earcon/`](/Users/jamesfgibbons/Documents/Targeted%20Impressions%20Hub/signal-contract/examples/browser-earcon)
- [`examples/python-logger/`](/Users/jamesfgibbons/Documents/Targeted%20Impressions%20Hub/signal-contract/examples/python-logger)
- [`tests/`](/Users/jamesfgibbons/Documents/Targeted%20Impressions%20Hub/signal-contract/tests)
- [`site/`](/Users/jamesfgibbons/Documents/Targeted%20Impressions%20Hub/signal-contract/site)

## Quick start

### Validate the schema

```bash
python3 -m pip install jsonschema
python3 -m unittest tests.test_schema -v
```

### Run the browser earcon example

```bash
python3 -m http.server 8000
```

Then open:

- `http://localhost:8000/examples/browser-earcon/`
- `http://localhost:8000/site/`

### Run the Python logger example

```bash
python3 examples/python-logger/main.py examples/python-logger/sample_signal.json
```

## Scope guardrails

This repo does not include:

- private channel letters
- VET formulas
- Constitutional CMS production contracts
- Soul Bank internals
- Sonafide references
- renderer certification
- hosted validator services
- commercial support surfaces

## License

Apache-2.0

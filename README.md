# VIBEnet Signal Contract

VIBEnet Signal Contract is a flat JSON event object for renderer-facing agent awareness.

**One JSON object. Many renderers. No shared backend required.**

This repo is the public source package for the open protocol served live at [vibenet.ai/protocol](https://vibenet.ai/protocol). It is hosted under the publisher's GitHub account, but the product and protocol brand remain VIBEnet.

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

## The shape

Signal Contract v1 standardizes:

- one flat awareness event object
- six renderer-facing state fields: `valence`, `energy`, `tension`, `intensity`, `hue`, `pulse`
- seven semantic channels: `nominal`, `advisory`, `warning`, `critical`, `recovery`, `opportunity`, `handoff`

The protocol does **not** define transport, auth, storage, orchestration, or renderer internals.

## Browser primitive

The live browser primitive is served from [vibenet.ai/pulse.js](https://vibenet.ai/pulse.js):

```html
<script src="https://vibenet.ai/pulse.js"></script>
<script>
  window.VIBEnetPulse.emit({
    schema_version: "1.0",
    id: "sig_demo_001",
    occurred_at: new Date().toISOString(),
    producer: "your-agent",
    entity: "agent.your_system.worker_01",
    event: "handoff.requested",
    channel: "handoff",
    valence: 0.5,
    energy: 0.6,
    tension: 0.7,
    intensity: 0.7,
    hue: 44,
    pulse: 0.8
  });
</script>
```

## Resources

- [Live protocol reference](https://vibenet.ai/protocol)
- [`spec/v1/schema.json`](spec/v1/schema.json)
- [`spec/v1/SPEC.md`](spec/v1/SPEC.md)
- [`examples/`](examples/)
- [`site/`](site/)

## Quick start

### Validate the schema

```bash
python3 -m pip install jsonschema
python3 -m unittest tests.test_schema -v
```

### Run the browser example

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

## Manual dual-publish rule

For now, the protocol is dual-published:

- this repo contains the public source package
- `vibenet.ai` serves the live schema at `https://vibenet.ai/protocol/v1/schema.json`

Any schema change must update both copies in lockstep:

- [`spec/v1/schema.json`](spec/v1/schema.json)
- [`site/v1/schema.json`](site/v1/schema.json)
- the served copy in `vibenet-frontend/public/protocol/v1/schema.json`

The canonical web URL remains `https://vibenet.ai/protocol/v1/schema.json`.

## Versioning

Signal Contract v1 is additive-stable:

- minor versions may add optional fields
- major versions are required for required-field changes, enum removals, or semantic redefinitions

## Conformance

A producer conforms to v1 when every emitted object validates against `spec/v1/schema.json`. A renderer conforms to v1 when it handles all seven public semantic channels without throwing. Conformance does not require a specific sonic vocabulary.

## License

Apache-2.0

# L1 Conformance — Channel Handling

The first runnable conformance tier. **A renderer is L1-conformant if it accepts one valid event on each of the seven public Signal Contract channels without throwing an error.** A producer is L1-conformant if its emitted events validate against the v1 schema and use only the seven public channels.

## What L1 does NOT require

L1 says nothing about:
- Whether the renderer *expresses* the event audibly/visually/structurally (that's tier-specific renderer policy)
- Whether the renderer handles `ttl_ms` correctly (that's L2)
- Whether the renderer modulates expression based on `confidence` (that's L3)
- Whether the renderer respects metadata conventions (that's L4)
- Whether events flow across multiple renderers unchanged (that's L5)

L1 is deliberately minimal. "Did your renderer accept the event without crashing on any of the seven channels?" That's it.

A renderer that *silently logs* a channel rather than expressing it is L1-conformant for that channel. The deliberate decision (silent vs express) is renderer-side discipline; L1 only asks that the renderer made *some* deliberate decision rather than crashing.

## Running the harness against a renderer

```bash
# From the repo root:
python conformance/l1/run.py --renderer-url http://localhost:9595/event

# Or against a deployed renderer:
python conformance/l1/run.py --renderer-url https://your-host/api/webhook/vibenet-signal

# Write the conformance report to a specific path:
python conformance/l1/run.py \
    --renderer-url http://localhost:9595/event \
    --output conformance-report.json
```

The harness POSTs one event per channel (seven events total, from `events.jsonl`) and records:
- HTTP status code of the response
- Whether the response was received within timeout
- Whether the renderer's response body parses as JSON (optional but informative)

A response status of 2xx for all seven channels is a PASS. Any 5xx, timeout, or connection error is a FAIL.

## Reading the report

```json
{
  "spec_version": "1.0",
  "test_version": "l1.v1",
  "renderer_url": "http://localhost:9595/event",
  "timestamp": "2026-05-12T20:30:00Z",
  "result": "pass",
  "handled_channels": ["nominal", "advisory", "warning", "critical", "recovery", "opportunity", "handoff"],
  "unhandled_channels": [],
  "per_channel_results": [
    {"channel": "nominal", "http_status": 200, "elapsed_ms": 12, "error": null},
    ...
  ]
}
```

## Self-publishing the report

If the run passes, the implementer is encouraged to publish the report at:

```
https://<their-renderer-domain>/.well-known/vibenet/conformance.json
```

This makes the conformance claim verifiable by anyone — they can re-run the harness against the renderer URL and confirm.

## License

Apache-2.0. See repo-root [`LICENSE`](../../LICENSE).

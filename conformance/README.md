# VIBEnet Signal Contract — Conformance

Conformance test suites for VIBEnet Signal Contract v1. Each tier is a runnable test that any producer or renderer can execute to demonstrate conformance at that level. Conformance is **mechanical**, not asserted: a passing run produces a signed JSON report suitable for self-publication at `/.well-known/vibenet/conformance.json` on the implementer's domain.

## Tier ladder

| Tier | What it proves | Status |
|---|---|---|
| **L0** | JSON Schema validation. Every emitted event validates against `spec/v1/schema.json`. Every accepted event passes the same validation before processing. | Schema-only; covered by `spec/v1/schema.json` + existing examples. |
| **L1** | Channel handling. A renderer receives one valid event per public channel and handles all seven without throwing. A producer can emit any of the seven channels and produce schema-valid output. | **Shipped — see [`l1/`](l1/).** |
| **L2** | Timestamp + TTL discipline. A renderer correctly expires events whose `ttl_ms` has elapsed, handles out-of-order replay, and degrades stale events without throwing. | Pending. |
| **L3** | Confidence modulation. A renderer adjusts expression (visual emphasis, audio prosody, structural weight) based on the `confidence` field. Producers populate `confidence` honestly. | Pending. |
| **L4** | Metadata convention discipline. Implementers respect the registered conventions (`publishable`, `indexable`, `trace_id`, `evidence_uri`, etc.) from `spec/v1/metadata-conventions.md`. | Pending registry. |
| **L5** | Cross-renderer interoperability. The same event object flows into two or more renderers (e.g. browser + voice + audit log) without per-renderer transformation. The protocol's "one event, many senses" claim is mechanically demonstrated. | Pending. |

## How conformance works

1. **Self-test.** An implementer runs the harness for the tier they're claiming against their deployment.
2. **Self-publish.** A passing run produces a JSON report. The implementer publishes it at `https://<their-domain>/.well-known/vibenet/conformance.json`.
3. **Verifiable by anyone.** The report includes the test version, the event payloads tested, and the responses received. A third party can re-run the harness against the implementer's URL and confirm the claim.

This is the same shape as ACID compliance claims for databases or USB-C power-delivery tiers: anyone can run the test; the spec defines what passing means. No central registry is required for the first tier. A central registry may emerge later if the ecosystem warrants it; until then, self-claim + verifiable test is sufficient.

## Adoption pattern

A producer or renderer typically starts at L1 (handles the channels), graduates to L2 once event-lifecycle handling is settled, then chases L3+ as the implementation matures. Each tier badge is additive — claiming L3 implies passing L1 and L2 first.

## License

Apache-2.0. See repo-root [`LICENSE`](../LICENSE).

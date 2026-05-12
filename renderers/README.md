# VIBEnet Signal Contract — Reference Renderers

Reference implementations of Signal Contract v1 renderers. Each renderer in this directory is one example of how a particular renderer family can express Signal Contract events. Implementations are Apache-2.0 and intended as starting points — alternative implementations in the same family are welcome and encouraged.

## Current renderers

| Renderer | Family | Channels supported | Conformance |
|---|---|---|---|
| [`google-home-bridge`](google-home-bridge/) | home-voice | warning, critical, recovery, handoff | L1 self-claim |

## Renderer family taxonomy

Renderers are grouped by their target sense + delivery context. Multiple renderers per family are expected:

- **browser-pulse** — visual cue inside an active web tab (favicon, banner, modal)
- **terminal-log** — line-emitted structured log for CLI surfaces
- **audit-trail** — append-only record for compliance and replay
- **home-voice** — ambient voice announcement in a residential space (this directory's `google-home-bridge` reference; Alexa / phone-TTS / Sonos as future siblings)
- **mobile-push** — phone/wearable notification (iOS, Android, Apple Watch, etc.)
- **haptic** — wearable vibration patterns
- **visual-ambient** — smart lighting, e-ink dashboard, glanceable surface

A renderer that handles multiple families (e.g. a Home Assistant config that fans an event out to voice + lights + phone push) declares all relevant families in its manifest.

## Renderer manifest

Every renderer in this directory must publish a `MANIFEST.yaml` declaring:

- `renderer_id` — kebab-case unique identifier
- `renderer_family` — from the taxonomy above
- `schema_version` — Signal Contract version it consumes (`"1.0"` currently)
- `channels_supported` — channels the renderer expresses; subset of the seven public channels
- `channels_ignored_by_design` — channels the renderer deliberately drops (silent handling); subset of the seven public channels
- `conformance_self_claim` — `L0`–`L5` claim, verified by the corresponding test in `conformance/`
- `implementation_paths` — list of routing paths (e.g. `[home-assistant-primary, ifttt-fallback]`)
- `attention_policy` — short description of when the renderer demands human attention vs. logs silently

The intersection of `channels_supported` and `channels_ignored_by_design` must be empty; their union must equal all seven public channels. This forces every renderer to make a deliberate per-channel decision.

## What this directory is NOT

- It is not the schema. The schema lives in [`spec/v1/`](../spec/v1/).
- It is not producer-build guidance. Producer discipline (when to emit which channel, surface_family conventions, retry-loop handling) lives in Constitutional CMS as Incident-Learned Invariants.
- It is not the conformance machinery. The L0–L5 test suites live in [`conformance/`](../conformance/).

This directory is renderers and only renderers. Each is one expression of the protocol; none is the protocol itself.

## License

Apache-2.0. See repo-root [`LICENSE`](../LICENSE).

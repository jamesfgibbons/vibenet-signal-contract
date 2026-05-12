# google-home-bridge

The first reference implementation of a **home-voice** renderer for VIBEnet Signal Contract v1. Subscribes to Signal Contract events, applies an attention policy (which channels warrant speech vs. silent handling), and casts an announcement to a Google Home / Nest device.

## What this is

One example of the home-voice renderer family. The Signal Contract is renderer-agnostic by design — this bridge demonstrates that a contract-compliant event can be expressed as ambient voice without binding the protocol to any voice platform. Alternative home-voice renderers (Alexa, phone-TTS, Sonos cast, Ray-Ban audio, local Whisper-driven TTS) are equally valid and welcome as sibling implementations.

## What this is NOT

- Not a Google-specific protocol dependency. The Signal Contract has no Google in it.
- Not the only voice renderer that can exist. It is the first.
- Not a producer. This consumes Signal Contract events; it does not emit them.

## Architecture

```
┌──────────────────────────┐
│  Producer                │
│  (e.g. SerpClaw worker)  │
└────────────┬─────────────┘
             │  vibenet.signal.v1 event
             ▼
┌──────────────────────────┐
│  signals.jsonl  OR       │
│  webhook endpoint        │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  bridge.py               │
│  - schema validation     │
│  - attention policy      │
│  - announcement format   │
└────────────┬─────────────┘
             │
             ├──[primary]──▶  Home Assistant webhook ──▶  google_cast.tts_speak ──▶ Nest Mini
             │
             └──[fallback]──▶  IFTTT webhook ──▶ Google Assistant Routine ──▶ Nest Mini
```

## Implementation paths

This renderer ships with two routing paths. The manifest declares both; implementers pick at deploy time based on what infrastructure they have running.

### Primary: Home Assistant

Recommended for any non-trivial deployment. Home Assistant runs on a Raspberry Pi, Docker container, or HA Cloud. The bridge POSTs to a Home Assistant webhook trigger; HA routes to `tts.google_say` against a Google Cast media player target.

Advantages:
- Vendor-neutral hub. The same HA can render to lights, MQTT, phone push, Sonos, wearables — adding renderers later is a config change.
- Documented blueprint included: [`ha-blueprint.yaml`](ha-blueprint.yaml).
- Low latency once configured (<2s from event to speech).
- No third-party rate limits.

### Fallback: IFTTT

For deployments that don't have Home Assistant. The bridge POSTs to an IFTTT Webhook trigger; an IFTTT applet triggers a Google Assistant Routine that announces the message.

Trade-offs:
- Free tier is rate-limited; not suitable for high-volume signal streams.
- IFTTT introduces a vendor dependency the rest of the stack avoids.
- Latency is variable (5–15s).
- One-way only.

See [`ifttt-fallback/applet.md`](ifttt-fallback/applet.md) for setup steps.

## Attention policy

The Signal Contract has seven channels. A home-voice renderer is one of the most attention-demanding channels of expression in the human's environment — interrupting a conversation, breaking concentration, waking sleeping inhabitants. The renderer therefore applies a per-channel attention policy:

| Channel | Default action | Reasoning |
|---|---|---|
| `critical` | **Speak** | State requires immediate attention. Voice is the highest-intrusion modality and the right tool. |
| `warning` | **Speak** | Threshold transition warrants ambient awareness. |
| `recovery` | **Speak** | Recovery from a prior critical event closes the loop the user already heard open. Silent recovery is bad UX. |
| `handoff` | **Speak** | An agent is asking for human input — voice is the right surface to surface the ask. |
| `nominal` | Silent | The whole point of "nominal" is that nothing needs attention. Speaking nominal status is noise. |
| `advisory` | Silent | Advisory is "FYI" — not an interrupt. Better surfaced visually or in a passive feed. |
| `opportunity` | Silent | Opportunity is "you could…" — same as advisory, not interrupt-shaped. |

Implementers can override this policy per device or per user. The manifest declares the defaults; the bridge config can suppress or promote any channel. The policy is renderer-side discipline; it is **not** part of the Signal Contract.

## Quick start

```bash
# 1. Install
cd renderers/google-home-bridge
pip install -r requirements.txt

# 2. Configure (either HA primary OR IFTTT fallback)
export HA_WEBHOOK_URL="https://your-ha-host/api/webhook/vibenet-signal"
# OR
export IFTTT_WEBHOOK_URL="https://maker.ifttt.com/trigger/vibenet/with/key/YOUR_KEY"

# 3. Run in tail-file mode (subscribing to a signals.jsonl stream)
python bridge.py --mode tail --source /path/to/signals.jsonl

# OR run as a webhook receiver
python bridge.py --mode webhook --port 9595
```

## Producer side: how SerpClaw emits to this renderer

The canonical producer demo for this renderer is SerpClaw (the SERPRadio Ralph-loop autonomous worker). SerpClaw writes vibenet.signal.v1 events to a `signals.jsonl` file as it processes briefs. To pipe SerpClaw events into this renderer:

```bash
python bridge.py --mode tail \
  --source ~/Documents/Targeted\ Impressions\ Hub/serpradio-cms/briefs/logs/signals.jsonl
```

See [`examples/serpclaw-demo.jsonl`](examples/serpclaw-demo.jsonl) for a canonical event payload — the production event that became the first cross-renderer demo.

## Conformance

This renderer self-claims **L1 conformance**: handles all seven public Signal Contract channels without throwing. To verify:

```bash
# Run the L1 harness against this renderer
cd ../../conformance/l1
python run.py --renderer-url http://localhost:9595/event
```

A passing run produces a report suitable for self-publication at `/.well-known/vibenet/conformance.json` on the renderer's deployment domain.

## License

Apache-2.0. See repo-root [`LICENSE`](../../LICENSE).

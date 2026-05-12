# IFTTT fallback path setup

Use this routing path only when no Home Assistant instance is available. The primary path is [`ha-blueprint.yaml`](../ha-blueprint.yaml); IFTTT is documented here as a fallback because it ties the renderer to a third-party vendor whose free-tier limits and product roadmap are outside our control.

## Setup steps

1. Create an IFTTT account at https://ifttt.com if you don't have one.

2. Connect the **Maker Webhooks** service and the **Google Assistant** service to your IFTTT account.

3. Create a new applet:

   - **If This** (trigger): **Webhooks** → **Receive a web request**
   - **Event name**: `vibenet_signal`
   - **Then That** (action): **Google Assistant** → **Broadcast a message to Google devices**
   - **Message to broadcast**: `{{Value1}}`
   - **Speak to all Google Home devices**: yes (or pick a specific device)

4. Find your webhook key:
   - Go to https://ifttt.com/maker_webhooks → **Documentation**
   - Copy the URL shape: `https://maker.ifttt.com/trigger/vibenet_signal/with/key/YOUR_KEY`

5. Set the bridge environment variable:
   ```bash
   export IFTTT_WEBHOOK_URL="https://maker.ifttt.com/trigger/vibenet_signal/with/key/YOUR_KEY"
   ```

6. Verify with a test event:
   ```bash
   echo '{"schema_version":"1.0","id":"test_001","occurred_at":"2026-05-12T20:00:00Z","producer":"manual-test","entity":"setup.verification","event":"installation.complete","channel":"warning","valence":0.5,"energy":0.5,"tension":0.3,"intensity":0.5,"hue":40,"pulse":0.5}' | python ../bridge.py --mode stdin
   ```

   Your Google Home should announce: *"Warning: manual-test reports installation complete on setup verification"*

## Known trade-offs

- **Rate limits**: IFTTT free tier limits webhook triggers per day. The bridge's attention policy already filters nominal/advisory/opportunity channels at the renderer; the IFTTT path therefore only fires on the four interrupt-shaped channels (critical/warning/recovery/handoff). Even so, a chatty producer can blow through the daily quota.
- **Latency**: 5–15 seconds typical from webhook POST to Google Home speech. Acceptable for ambient awareness; not acceptable for time-sensitive interrupts.
- **Vendor dependency**: IFTTT has changed pricing and product surface several times. If IFTTT goes away or changes its Google Assistant integration, this path breaks. The Home Assistant path is insulated from that.
- **Three values only**: IFTTT webhook payloads carry only `value1`, `value2`, `value3`. The bridge maps `value1=announcement`, `value2=channel`, `value3=event_id`. Richer metadata (provenance, evidence_uri, etc.) is not propagated through this path. The Home Assistant path carries the full event payload.

## When to graduate from IFTTT

You should move to the Home Assistant path as soon as any of these is true:

- You want to render to more than one device family (lights, Sonos, phone push, etc.).
- You hit IFTTT rate limits.
- You need event metadata beyond announcement text in the rendering decision.
- You want quiet-hours or per-room policy that varies by event type.

The bridge.py code is identical for both paths; only the downstream config changes.

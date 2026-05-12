#!/usr/bin/env python3
"""google-home-bridge — home-voice renderer reference for VIBEnet Signal Contract v1.

Consumes vibenet.signal.v1 events, applies an attention policy
(which channels warrant speech), and routes to a Google Home / Nest
device via either Home Assistant (primary) or IFTTT (fallback).

This is one reference implementation of the home-voice renderer family.
Alternative voice renderers (Alexa, phone-TTS, Sonos, Ray-Ban audio,
local Whisper) are welcomed sibling implementations.

Modes:
    --mode tail      Watch a signals.jsonl file, react to each appended line.
    --mode webhook   Listen on a port; accept POST of vibenet.signal.v1 events.
    --mode stdin     Read events from stdin one per line (useful for pipelines).

Routing paths (declared in MANIFEST.yaml):
    HA_WEBHOOK_URL=https://...   Home Assistant primary path.
    IFTTT_WEBHOOK_URL=https://...  IFTTT fallback path.

Exactly one routing env var must be set. If both are set, HA wins.

Attention policy:
    See MANIFEST.yaml attention_policy.default. Override via
    ATTENTION_POLICY_OVERRIDE_<CHANNEL>=speak|silent env vars.
"""
from __future__ import annotations

import argparse
import http.server
import json
import os
import socketserver
import sys
import time
import urllib.request
from typing import Any, Dict, Optional


PUBLIC_CHANNELS = {
    "nominal", "advisory", "warning", "critical",
    "recovery", "opportunity", "handoff",
}

# Renderer-side discipline. Not part of the Signal Contract.
DEFAULT_ATTENTION_POLICY: Dict[str, str] = {
    "critical": "speak",
    "warning": "speak",
    "recovery": "speak",
    "handoff": "speak",
    "nominal": "silent",
    "advisory": "silent",
    "opportunity": "silent",
}


def _resolve_attention_policy() -> Dict[str, str]:
    policy = dict(DEFAULT_ATTENTION_POLICY)
    for channel in PUBLIC_CHANNELS:
        override = os.environ.get(f"ATTENTION_POLICY_OVERRIDE_{channel.upper()}")
        if override in {"speak", "silent"}:
            policy[channel] = override
    return policy


def _validate_event(event: Dict[str, Any]) -> Optional[str]:
    """Minimal Signal Contract v1 shape check. Returns error message or None."""
    required = {"schema_version", "id", "occurred_at", "producer", "entity",
                "event", "channel", "valence", "energy", "tension",
                "intensity", "hue", "pulse"}
    missing = [f for f in required if f not in event]
    if missing:
        return f"missing required fields: {missing}"
    if event.get("schema_version") != "1.0":
        return f"unsupported schema_version: {event.get('schema_version')}"
    channel = event.get("channel")
    if channel not in PUBLIC_CHANNELS:
        return f"unknown channel: {channel}"
    return None


def _format_announcement(event: Dict[str, Any]) -> str:
    """Render an event into a short spoken sentence."""
    channel = event.get("channel", "advisory")
    producer = event.get("producer", "an agent")
    entity = event.get("entity", "an entity")
    event_name = event.get("event", "state change")
    metadata = event.get("metadata") or {}

    # Strip noise: turn dot-paths into spoken form.
    spoken_event = event_name.replace(".", " ").replace("_", " ")
    spoken_entity = entity.replace(".", " ").replace("_", " ")

    detail = metadata.get("voice_detail") or ""
    detail_suffix = f". {detail}" if detail else ""
    return f"{channel.capitalize()}: {producer} reports {spoken_event} on {spoken_entity}{detail_suffix}"


def _post_to_home_assistant(webhook_url: str, payload: Dict[str, Any]) -> int:
    """POST payload to a Home Assistant webhook trigger."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url, data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status
    except Exception as exc:
        sys.stderr.write(f"[bridge] HA webhook error: {exc}\n")
        return 0


def _post_to_ifttt(webhook_url: str, payload: Dict[str, Any]) -> int:
    """POST payload to an IFTTT Maker Webhook (value1=announcement text)."""
    data = json.dumps({
        "value1": payload.get("announcement", ""),
        "value2": payload.get("channel", ""),
        "value3": payload.get("event_id", ""),
    }).encode("utf-8")
    req = urllib.request.Request(
        webhook_url, data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status
    except Exception as exc:
        sys.stderr.write(f"[bridge] IFTTT webhook error: {exc}\n")
        return 0


def _handle_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Process one Signal Contract event. Returns a handling record."""
    err = _validate_event(event)
    if err:
        return {"status": "rejected", "reason": err, "event_id": event.get("id")}

    channel = event["channel"]
    policy = _resolve_attention_policy()
    action = policy.get(channel, "silent")

    record: Dict[str, Any] = {
        "status": "handled",
        "channel": channel,
        "event_id": event.get("id"),
        "action": action,
    }

    if action != "speak":
        return record

    announcement = _format_announcement(event)
    payload = {
        "announcement": announcement,
        "channel": channel,
        "event_id": event.get("id"),
        "raw_event": event,
    }

    ha_url = os.environ.get("HA_WEBHOOK_URL")
    ifttt_url = os.environ.get("IFTTT_WEBHOOK_URL")

    if ha_url:
        status = _post_to_home_assistant(ha_url, payload)
        record["path"] = "home-assistant-primary"
        record["http_status"] = status
    elif ifttt_url:
        status = _post_to_ifttt(ifttt_url, payload)
        record["path"] = "ifttt-fallback"
        record["http_status"] = status
    else:
        record["path"] = "none"
        record["error"] = "no routing path configured; set HA_WEBHOOK_URL or IFTTT_WEBHOOK_URL"

    return record


def _run_tail(source: str) -> None:
    """Tail a signals.jsonl file, handle each newly-appended event."""
    sys.stderr.write(f"[bridge] tailing {source}\n")
    with open(source, "r") as f:
        f.seek(0, 2)  # seek to end
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                sys.stderr.write(f"[bridge] skipping malformed line: {exc}\n")
                continue
            record = _handle_event(event)
            print(json.dumps(record), flush=True)


def _run_stdin() -> None:
    """Read events from stdin, one JSON object per line."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            sys.stderr.write(f"[bridge] skipping malformed line: {exc}\n")
            continue
        record = _handle_event(event)
        print(json.dumps(record), flush=True)


def _run_webhook(port: int) -> None:
    """Listen on port, handle each POSTed event."""
    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # quiet default logging
            pass

        def do_POST(self):
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length)
            try:
                event = json.loads(body)
            except json.JSONDecodeError as exc:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(f"bad json: {exc}".encode())
                return
            record = _handle_event(event)
            if record["status"] == "rejected":
                self.send_response(400)
            else:
                self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(record).encode())
            print(json.dumps(record), flush=True)

    sys.stderr.write(f"[bridge] webhook listening on :{port}\n")
    with socketserver.TCPServer(("", port), Handler) as httpd:
        httpd.serve_forever()


def main() -> int:
    parser = argparse.ArgumentParser(description="google-home-bridge — home-voice renderer for VIBEnet Signal Contract v1")
    parser.add_argument("--mode", choices=("tail", "webhook", "stdin"), default="tail")
    parser.add_argument("--source", help="path to signals.jsonl (tail mode)")
    parser.add_argument("--port", type=int, default=9595, help="port for webhook mode")
    args = parser.parse_args()

    if args.mode == "tail":
        if not args.source:
            parser.error("--source is required for tail mode")
        _run_tail(args.source)
    elif args.mode == "stdin":
        _run_stdin()
    elif args.mode == "webhook":
        _run_webhook(args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())

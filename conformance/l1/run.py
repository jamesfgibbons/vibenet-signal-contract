#!/usr/bin/env python3
"""L1 conformance harness for VIBEnet Signal Contract v1.

Feeds one event per public channel to a renderer-under-test and verifies
the renderer handles all seven without throwing. Writes a JSON report
suitable for self-publication at /.well-known/vibenet/conformance.json.

Usage:
    python run.py --renderer-url http://localhost:9595/event
    python run.py --renderer-url https://host/webhook --output report.json
    python run.py --renderer-url http://localhost:9595/event --pretty
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

from reporter import write_report

EVENTS_PATH = Path(__file__).parent / "events.jsonl"
PUBLIC_CHANNELS = [
    "nominal", "advisory", "warning", "critical",
    "recovery", "opportunity", "handoff",
]
DEFAULT_TIMEOUT_SEC = 8


def load_events() -> List[Dict[str, Any]]:
    """Load the seven canonical L1 events from events.jsonl."""
    events: List[Dict[str, Any]] = []
    with EVENTS_PATH.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            events.append(json.loads(line))
    return events


def validate_event_set(events: List[Dict[str, Any]]) -> None:
    """Confirm the events.jsonl covers each public channel exactly once."""
    channels = [e["channel"] for e in events]
    expected = set(PUBLIC_CHANNELS)
    got = set(channels)
    if got != expected:
        missing = expected - got
        extra = got - expected
        raise SystemExit(f"events.jsonl is malformed: missing={missing} extra={extra}")
    if len(channels) != len(set(channels)):
        raise SystemExit(f"events.jsonl has duplicate channels: {channels}")


def post_event(url: str, event: Dict[str, Any], timeout_sec: int) -> Dict[str, Any]:
    """POST one event to the renderer. Returns a per-channel result record."""
    body = json.dumps(event).encode("utf-8")
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json", "User-Agent": "vibenet-l1-harness/1.0"},
        method="POST",
    )
    start = time.monotonic()
    record: Dict[str, Any] = {
        "channel": event["channel"],
        "event_id": event["id"],
        "http_status": None,
        "elapsed_ms": None,
        "error": None,
        "response_body_excerpt": None,
    }
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            record["http_status"] = resp.status
            record["elapsed_ms"] = int((time.monotonic() - start) * 1000)
            body_bytes = resp.read(512)  # capture first 512 bytes for diagnostics
            record["response_body_excerpt"] = body_bytes.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        record["http_status"] = exc.code
        record["elapsed_ms"] = int((time.monotonic() - start) * 1000)
        record["error"] = f"HTTPError: {exc.reason}"
    except urllib.error.URLError as exc:
        record["elapsed_ms"] = int((time.monotonic() - start) * 1000)
        record["error"] = f"URLError: {exc.reason}"
    except Exception as exc:
        record["elapsed_ms"] = int((time.monotonic() - start) * 1000)
        record["error"] = f"{type(exc).__name__}: {exc}"
    return record


def evaluate(per_channel: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Apply the L1 pass criterion: 2xx response on all seven channels."""
    handled, unhandled = [], []
    for r in per_channel:
        status = r.get("http_status")
        if isinstance(status, int) and 200 <= status < 300 and r.get("error") is None:
            handled.append(r["channel"])
        else:
            unhandled.append(r["channel"])
    return {
        "result": "pass" if not unhandled else "fail",
        "handled_channels": sorted(handled),
        "unhandled_channels": sorted(unhandled),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="VIBEnet Signal Contract v1 — L1 conformance harness")
    parser.add_argument("--renderer-url", required=True, help="URL the harness POSTs events to")
    parser.add_argument("--output", default="-", help="Path to write the report JSON. '-' for stdout (default)")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SEC, help="Per-event timeout in seconds")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print report JSON")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-channel progress logging")
    args = parser.parse_args()

    events = load_events()
    validate_event_set(events)

    per_channel: List[Dict[str, Any]] = []
    for event in events:
        if not args.quiet:
            sys.stderr.write(f"[l1] POST {event['channel']:<12} ({event['id']}) → {args.renderer_url}\n")
        result = post_event(args.renderer_url, event, args.timeout)
        per_channel.append(result)
        if not args.quiet:
            status = result.get("http_status") or "ERR"
            err = result.get("error") or "ok"
            sys.stderr.write(f"[l1]   status={status} elapsed={result.get('elapsed_ms')}ms note={err}\n")

    verdict = evaluate(per_channel)
    report = {
        "spec_version": "1.0",
        "test_version": "l1.v1",
        "renderer_url": args.renderer_url,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "result": verdict["result"],
        "handled_channels": verdict["handled_channels"],
        "unhandled_channels": verdict["unhandled_channels"],
        "per_channel_results": per_channel,
        "harness": {
            "events_file": str(EVENTS_PATH.relative_to(Path(__file__).parent.parent.parent)),
            "timeout_sec": args.timeout,
        },
    }

    write_report(report, args.output, pretty=args.pretty)

    if verdict["result"] == "fail":
        sys.stderr.write(f"\n[l1] RESULT: FAIL — unhandled channels: {verdict['unhandled_channels']}\n")
        return 2
    sys.stderr.write(f"\n[l1] RESULT: PASS — all 7 channels handled\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

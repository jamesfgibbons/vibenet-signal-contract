from __future__ import annotations

import json
import sys
from pathlib import Path


def load_signal(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def describe(signal: dict) -> str:
    confidence = signal.get("confidence")
    confidence_text = f" confidence={confidence:.2f}" if isinstance(confidence, (int, float)) else ""
    ttl_text = f" ttl_ms={signal['ttl_ms']}" if "ttl_ms" in signal else ""
    return (
        f"[{signal['occurred_at']}] "
        f"{signal['channel'].upper()} "
        f"producer={signal['producer']} "
        f"entity={signal['entity']} "
        f"event={signal['event']} "
        f"intensity={signal['intensity']:.2f} "
        f"V={signal['valence']:.2f} "
        f"E={signal['energy']:.2f} "
        f"T={signal['tension']:.2f} "
        f"hue={signal['hue']:.0f} "
        f"pulse={signal['pulse']:.2f}"
        f"{ttl_text}"
        f"{confidence_text}"
    )


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python3 main.py <signal.json>", file=sys.stderr)
        return 1

    signal_path = Path(sys.argv[1]).resolve()
    signal = load_signal(signal_path)
    print(describe(signal))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

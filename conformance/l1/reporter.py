#!/usr/bin/env python3
"""Reporter helper for L1 conformance harness.

Writes the report JSON to a path or stdout. Kept as a separate module
so that future tier harnesses (L2+) can share the same emit pattern.
"""
from __future__ import annotations

import json
import sys
from typing import Any, Dict


def write_report(report: Dict[str, Any], output: str, *, pretty: bool = False) -> None:
    """Write report JSON to `output`. Use '-' for stdout."""
    indent = 2 if pretty else None
    serialized = json.dumps(report, indent=indent, sort_keys=False)
    if output == "-":
        sys.stdout.write(serialized + "\n")
        sys.stdout.flush()
        return
    with open(output, "w") as f:
        f.write(serialized + "\n")
    sys.stderr.write(f"[l1] report written to {output}\n")

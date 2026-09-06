#!/usr/bin/env python3
"""Backward-compatible shim for the publication-safe stabilization launcher.

The earlier wrapper called the historical ``build_closure`` directly, whose
wall-clock budget can return a partial closure.  This shim delegates to
``REPRODUCE/reproduce_stabilization.py`` so a timeout is fail-closed.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAFE = HERE.parent / "reproduce_stabilization.py"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("k", nargs="+", type=int)
    ap.add_argument("--time-budget", type=float, default=300.0)
    ap.add_argument("--output", type=Path, default=Path("build/stabilization"))
    args = ap.parse_args()
    cmd = [
        sys.executable,
        str(SAFE),
        "--k",
        *[str(k) for k in args.k],
        "--max-seconds",
        str(args.time_budget),
        "--output",
        str(args.output),
    ]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Publication-facing launcher for the short-chain compatibility package.

Modes
-----
smoke
    Freshly generate the L=3,4,5 walk families, check their exact equality
    with the archived M0 sets, and re-run the PWC oracle on every generated
    repair.  This is the fast example intended for routine installation tests.

full
    Run all six claim-oriented scripts from the retained upstream package.
    This includes the slower exhaustive lower-size checks.  The upstream
    76-orbit L=5 classification remains a frozen finite input; the full mode
    re-aggregates and audits it but does not claim to regenerate that orbit
    census from first principles.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "REPRODUCE" / "finite_compatibility"
WALK_SCRIPT = PKG / "scripts" / "walk_counts.py"
FULL_SCRIPTS = [
    "walk_counts.py",
    "depth_histogram.py",
    "bridge_lemma.py",
    "disjointness_L3_L5.py",
    "disjointness_L4.py",
    "section6_1_split.py",
]


def load_walk_module():
    sys.path.insert(0, str(PKG / "src"))
    spec = importlib.util.spec_from_file_location("cgta_walk_counts", WALK_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {WALK_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def smoke(output: Path) -> dict:
    m = load_walk_module()
    results = []
    for L in (3, 4, 5):
        initial = m.chain(L)
        generated = m.walk_family(L)
        frozen = m.load_reference(L)
        expected = 4 * 3 ** (L - 1)
        pwc_pass = sum(m.pwc_verdict(initial.symmetric_difference(repair)) for repair in generated)
        row = {
            "L": L,
            "generated_repairs": len(generated),
            "expected_repairs": expected,
            "reference_exact_equality": generated == frozen,
            "pwc_pass": pwc_pass,
        }
        row["pass"] = (
            row["generated_repairs"] == expected
            and row["reference_exact_equality"]
            and row["pwc_pass"] == expected
        )
        if not row["pass"]:
            raise AssertionError(f"short-chain smoke mismatch: {row}")
        results.append(row)

    payload = {
        "mode": "smoke",
        "results": results,
        "claim_boundary": (
            "Fresh walk-family generation and PWC checks for L=3,4,5. "
            "This smoke mode does not independently regenerate the frozen 76-orbit L=5 census."
        ),
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "finite_compatibility_smoke.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return payload


def full(output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    logs = []
    for name in FULL_SCRIPTS:
        proc = subprocess.run(
            [sys.executable, name],
            cwd=PKG / "scripts",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        log_path = output / f"{Path(name).stem}.log"
        log_path.write_text(proc.stdout, encoding="utf-8")
        logs.append({"script": name, "returncode": proc.returncode, "log": str(log_path)})
        print(proc.stdout, end="")
        if proc.returncode != 0:
            raise SystemExit(f"{name} failed with exit code {proc.returncode}")

    payload = {
        "mode": "full",
        "scripts": logs,
        "claim_boundary": (
            "Runs the retained upstream claim-oriented package. The 76-orbit L=5 classification "
            "is audited as a frozen input rather than regenerated from first principles."
        ),
    }
    (output / "finite_compatibility_full.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return payload


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=("smoke", "full"), default="smoke")
    ap.add_argument("--output", type=Path, default=Path("build/finite_compatibility"))
    args = ap.parse_args()
    payload = smoke(args.output) if args.mode == "smoke" else full(args.output)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Compare regenerated publication artifacts with the archived reference outputs."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def check_stabilization(build: Path) -> dict:
    p = build / "stabilization_reproduction.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    checks = {}
    for r in data["results"]:
        k = r["k"]
        checks[f"k{k}_reference_checks"] = bool(r["reference_checks"]["all"])
        checks[f"k{k}_closure_complete"] = bool(r["closure_complete"])
    return checks


def check_local(build: Path) -> dict:
    ref = ROOT / "LOCAL_DECISION_DATA"
    return {
        "rule_table": read_csv(build / "rule_table_117_keys.csv") == read_csv(ref / "rule_table_117_keys.csv"),
        "four_mixed_keys": read_csv(build / "four_mixed_keys.csv") == read_csv(ref / "four_mixed_keys.csv"),
        "coverage_and_totals": json.loads((build / "coverage_and_totals.json").read_text())
        == json.loads((ref / "coverage_and_totals.json").read_text()),
    }


def check_finite(build: Path) -> dict:
    smoke = json.loads((build / "finite_compatibility_smoke.json").read_text())
    ref_rows = read_csv(ROOT / "FINITE_COMPATIBILITY_DATA" / "walk_counts.csv")
    ref = {int(r["L"]): int(r["M0_size"]) for r in ref_rows}
    return {
        f"L{r['L']}_M0_size": r["generated_repairs"] == ref[r["L"]] and r["pass"]
        for r in smoke["results"]
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stabilization", type=Path)
    ap.add_argument("--local-decision", type=Path)
    ap.add_argument("--finite-compatibility", type=Path)
    args = ap.parse_args()

    groups = {}
    if args.stabilization:
        groups["stabilization"] = check_stabilization(args.stabilization)
    if args.local_decision:
        groups["local_decision"] = check_local(args.local_decision)
    if args.finite_compatibility:
        groups["finite_compatibility"] = check_finite(args.finite_compatibility)
    if not groups:
        ap.error("at least one build directory must be supplied")

    ok = all(all(v.values()) for v in groups.values())
    payload = {"checks": groups, "pass": ok}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

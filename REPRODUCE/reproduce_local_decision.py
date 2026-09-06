#!/usr/bin/env python3
"""Regenerate the publication local-decision tables from the certified B7 registry.

This is a deterministic *registry-to-publication-table* reproduction layer.  It
starts from the shipped integrated B7 finite-domain record and regenerates the
117-key table, the four exceptional keys, and aggregate totals.  It does not
claim to rebuild the 37,058-class D1 census from the ten historical source roots.
The latter requires the predecessor archives documented in ``REPRODUCE/provenance``.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "REPRODUCE" / "frozen_d1" / "02C20D_B7_FULL_DECISION_RULE.json"
REFERENCE_DIR = ROOT / "LOCAL_DECISION_DATA"


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_rule_table(rows: list[dict], path: Path) -> None:
    fields = ["rho_R_multiset_key", "rule", "class_count", "geometry_false", "geometry_true"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({
                "rho_R_multiset_key": r["rho_R_multiset_key"],
                "rule": r["rule"],
                "class_count": r["class_count"],
                "geometry_false": r["b4_geometry_false"],
                "geometry_true": r["b4_geometry_true"],
            })


def write_exception_table(rows: list[dict], path: Path) -> None:
    fields = ["exception_key", "rho_R_multiset_key", "classes", "geometry_false", "geometry_true"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for i, r in enumerate(rows, 1):
            w.writerow({
                "exception_key": f"M{i}",
                "rho_R_multiset_key": r["rho_R_multiset_key"],
                "classes": r["class_count"],
                "geometry_false": r["b4_geometry_false"],
                "geometry_true": r["b4_geometry_true"],
            })
        w.writerow({
            "exception_key": "total",
            "rho_R_multiset_key": "",
            "classes": sum(r["class_count"] for r in rows),
            "geometry_false": sum(r["b4_geometry_false"] for r in rows),
            "geometry_true": sum(r["b4_geometry_true"] for r in rows),
        })


def semantic_compare_json(a: Path, b: Path) -> bool:
    return json.loads(a.read_text(encoding="utf-8")) == json.loads(b.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--output", type=Path, default=Path("build/local_decision"))
    args = ap.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    rows = data["rule_table"]
    mixed = [r for r in rows if r["rule"] == "adjacency_saturation"]
    constant = [r for r in rows if r["rule"] == "constant_false"]

    checks = {
        "keys_117": len(rows) == 117,
        "constant_113": len(constant) == 113,
        "mixed_4": len(mixed) == 4,
        "classes_37058": sum(r["class_count"] for r in rows) == 37058,
        "constant_classes_36765": sum(r["class_count"] for r in constant) == 36765,
        "dynamic_classes_293": sum(r["class_count"] for r in mixed) == 293,
        "geometry_false_37018": sum(r["b4_geometry_false"] for r in rows) == 37018,
        "geometry_true_40": sum(r["b4_geometry_true"] for r in rows) == 40,
        "dynamic_mismatch_zero": data["dynamic_branch_regression"]["mismatch"] == 0,
    }
    if not all(checks.values()):
        raise AssertionError(f"B7 registry invariants failed: {checks}")

    args.output.mkdir(parents=True, exist_ok=True)
    rule_path = args.output / "rule_table_117_keys.csv"
    mixed_path = args.output / "four_mixed_keys.csv"
    totals_path = args.output / "coverage_and_totals.json"

    write_rule_table(rows, rule_path)
    write_exception_table(mixed, mixed_path)
    totals = {
        "scope": data["scope"],
        "coverage": data["coverage"],
        "predicted_totals": data["predicted_totals"],
        "source": "Certified finite local-decision data included in Online Resource 1.",
    }
    totals_path.write_text(json.dumps(totals, indent=2) + "\n", encoding="utf-8")

    comparisons = {
        "rule_table_semantic_equal": load_csv(rule_path) == load_csv(REFERENCE_DIR / rule_path.name),
        "mixed_table_semantic_equal": load_csv(mixed_path) == load_csv(REFERENCE_DIR / mixed_path.name),
        "totals_semantic_equal": semantic_compare_json(totals_path, REFERENCE_DIR / totals_path.name),
    }
    if not all(comparisons.values()):
        raise AssertionError(f"publication-table comparison failed: {comparisons}")

    summary = {
        "pipeline": "certified B7 registry -> publication local-decision tables",
        "claim_boundary": (
            "This layer does not regenerate the ten-source-root D1 census. "
            "Full raw rebuild requires the exact predecessor archives recorded under REPRODUCE/provenance."
        ),
        "checks": checks,
        "reference_comparisons": comparisons,
    }
    (args.output / "local_decision_reproduction.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

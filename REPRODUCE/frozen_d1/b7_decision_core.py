#!/usr/bin/env python3
from __future__ import annotations
from typing import Any


def l1(a, b) -> int:
    return sum(abs(int(x)-int(y)) for x, y in zip(a, b))


def frame_adjacency_saturated(frame: dict[str, Any]) -> bool:
    boundary = [[0, 0, 0], *frame.get("ordered_q_R", []), frame["endpoint_span"]]
    return all(l1(a, b) == 1 for a, b in zip(boundary, boundary[1:]))


def saturated_pair_exists(class_row: dict[str, Any]) -> bool:
    return any(frame_adjacency_saturated(f) for f in class_row.get("span_ordered_q_R_set", []))


def build_rule_table(b4: dict[str, Any]) -> list[dict[str, Any]]:
    rows=[]
    for b in b4["buckets"]:
        mixed=bool(b["mixed_geometry"])
        rows.append({
            "rho_R_multiset_key": b["rho_R_multiset_key"],
            "class_count": int(b["class_count"]),
            "b4_geometry_false": int(b["geometry_false"]),
            "b4_geometry_true": int(b["geometry_true"]),
            "rule": "adjacency_saturation" if mixed else "constant_false",
        })
    return sorted(rows, key=lambda r:r["rho_R_multiset_key"])


def decide_from_rule(rule: str, class_row: dict[str, Any] | None = None) -> bool:
    if rule == "constant_false":
        return False
    if rule == "adjacency_saturation":
        if class_row is None:
            raise ValueError("adjacency_saturation requires a class geometry row")
        return saturated_pair_exists(class_row)
    raise ValueError(f"unknown rule: {rule}")

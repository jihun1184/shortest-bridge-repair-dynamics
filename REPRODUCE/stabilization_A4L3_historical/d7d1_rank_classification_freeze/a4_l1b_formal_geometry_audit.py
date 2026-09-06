"""A4-L1b symbolic geometry audit; does not enumerate any closure."""

from __future__ import annotations

from collections import Counter, deque
import json
from pathlib import Path

from anchor_windowed_quotient_v2 import CORE


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "a4_l1a_signature_table_results.json"
OUTPUT = HERE / "a4_l1b_formal_geometry_results.json"
REPAIR = (-1, -1, 0)


def neighbors6(point):
    x, y, z = point
    for dx, dy, dz in (
        (1, 0, 0),
        (-1, 0, 0),
        (0, 1, 0),
        (0, -1, 0),
        (0, 0, 1),
        (0, 0, -1),
    ):
        yield x + dx, y + dy, z + dz


def components6(points):
    unseen = set(points)
    components = []
    while unseen:
        start = unseen.pop()
        component = {start}
        queue = deque((start,))
        while queue:
            point = queue.popleft()
            for neighbor in neighbors6(point):
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    component.add(neighbor)
                    queue.append(neighbor)
        components.append(frozenset(component))
    return components


def connected(points):
    points = frozenset(points)
    return bool(points) and len(components6(points)) == 1


def decode_points(rows):
    return frozenset(tuple(point) for point in rows)


def infer_law(lengths):
    triple = tuple(lengths[str(k)] for k in (6, 7, 8))
    laws = {
        (2, 3, 4): ("k-4", lambda k: k - 4, -4),
        (0, 0, 0): ("0", lambda k: 0, None),
        (0, 1, 2): ("k-6", lambda k: k - 6, -6),
    }
    if triple not in laws:
        raise AssertionError(f"unrecognized corridor-length triple: {triple}")
    return laws[triple]


def build_satellite(template, k, length):
    satellite = (-k, 2, 0)
    d = tuple(template["line_offset"])
    attachment = decode_points(template["attachment_shape"])
    patch = decode_points(template["patch_shape"])
    start = tuple(satellite[i] + d[i] for i in range(3))
    endpoint = (start[0] + length, start[1], start[2])
    satellite_piece = {
        tuple(satellite[i] + point[i] for i in range(3))
        for point in attachment
    }
    corridor = {
        (start[0] + j, start[1], start[2]) for j in range(length + 1)
    }
    core_piece = {
        tuple(endpoint[i] + point[i] for i in range(3)) for point in patch
    }
    return satellite, start, endpoint, frozenset(
        satellite_piece | corridor | core_piece
    )


def main(k_min=6, k_max=100):
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    templates = {row["template_id"]: row for row in source["templates"]}
    failures = []

    # Local conditions are the finite hypotheses used in the connectivity proof.
    template_checks = []
    for template_id, template in sorted(templates.items()):
        d = tuple(template["line_offset"])
        attachment = decode_points(template["attachment_shape"])
        patch = decode_points(template["patch_shape"])
        checks = {
            "origin_in_attachment": (0, 0, 0) in attachment,
            "line_start_in_attachment": d in attachment,
            "attachment_6_connected": connected(attachment),
            "endpoint_patch_6_connected": connected(patch | {(0, 0, 0)}),
        }
        if not all(checks.values()):
            failures.append({"template_id": template_id, "checks": checks})
        template_checks.append({"template_id": template_id, **checks})

    law_counts = Counter()
    class_results = []
    total_cases = 0
    for row in source["classes"]:
        class_id = row["class_id"]
        if len(row["compatible_template_ids"]) != 1:
            raise AssertionError(f"{class_id} does not have a unique template")
        template_id = row["selected_template_id"]
        template = templates[template_id]
        lengths = {
            str(k): row["selected_template_witnesses"][str(k)]["corridor_length"]
            for k in (6, 7, 8)
        }
        law_name, length_at, fixed_endpoint_x = infer_law(lengths)
        law_counts[law_name] += 1

        if law_name == "0" and template_id != "T12":
            failures.append({"class_id": class_id, "unexpected_zero_template": template_id})
        if law_name == "k-6" and (class_id, template_id) != ("C050", "T14"):
            failures.append(
                {"class_id": class_id, "unexpected_k_minus_6_template": template_id}
            )

        remainder = decode_points(row["fixed_remainder"])
        remainder_x_bound = all(point[0] >= -4 for point in remainder)
        if not remainder_x_bound:
            failures.append({"class_id": class_id, "remainder_x_bound": False})

        boundary_at_6 = None
        class_failures = []
        for k in range(k_min, k_max + 1):
            length = length_at(k)
            if length < 0:
                class_failures.append({"k": k, "negative_length": length})
                continue
            satellite, start, endpoint, satellite_component = build_satellite(
                template, k, length
            )
            candidate = remainder | satellite_component
            overlap = remainder & satellite_component
            components = components6(candidate)
            containing = next(component for component in components if satellite in component)
            root = frozenset(CORE | {satellite, REPAIR})
            core_facing_boundary = frozenset(
                point for point in satellite_component if point[0] >= -5
            )
            if k == 6:
                boundary_at_6 = core_facing_boundary

            checks = {
                "nonnegative_length": length >= 0,
                "satellite_contained": satellite in satellite_component,
                "satellite_component_connected": connected(satellite_component),
                "remainder_overlap_empty": not overlap,
                "no_component_leak": containing == satellite_component,
                "root_subset": root <= candidate,
                "core_boundary_fixed": core_facing_boundary == boundary_at_6,
            }
            if fixed_endpoint_x is not None:
                checks["endpoint_x_fixed"] = endpoint[0] == fixed_endpoint_x
            if not all(checks.values()):
                class_failures.append({"k": k, "checks": checks})
            total_cases += 1

        if class_failures:
            failures.append({"class_id": class_id, "cases": class_failures})
        class_results.append(
            {
                "class_id": class_id,
                "template_id": template_id,
                "corridor_law": law_name,
                "fixed_endpoint_x": fixed_endpoint_x,
                "remainder_x_ge_minus_4": remainder_x_bound,
                "tested_k_range": [k_min, k_max],
                "regression_failures": class_failures,
            }
        )

    expected_laws = {"k-4": 30, "0": 22, "k-6": 1}
    if dict(law_counts) != expected_laws:
        failures.append(
            {"corridor_law_counts": dict(law_counts), "expected": expected_laws}
        )

    result = {
        "scope": (
            "symbolic local-condition audit plus finite regression; no closure enumeration"
        ),
        "claim_boundary": (
            "Defines and proves the formal all-k voxel geometry only; reachability and "
            "behavioral-class membership for k>8 remain open."
        ),
        "template_count": len(templates),
        "class_count": len(source["classes"]),
        "corridor_law_counts": dict(law_counts),
        "special_family": {"class_id": "C050", "template_id": "T14"},
        "template_local_checks": template_checks,
        "regression_k_range": [k_min, k_max],
        "regression_class_k_cases": total_cases,
        "failures": failures,
        "classes": class_results,
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        raise AssertionError(f"A4-L1b audit failures: {len(failures)}; see {OUTPUT}")
    print(
        json.dumps(
            {key: result[key] for key in (
                "scope",
                "template_count",
                "class_count",
                "corridor_law_counts",
                "special_family",
                "regression_k_range",
                "regression_class_k_cases",
                "failures",
                "claim_boundary",
            )},
            indent=2,
        )
    )
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()

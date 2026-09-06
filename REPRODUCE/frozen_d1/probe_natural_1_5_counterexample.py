from __future__ import annotations

import json

from run_02c15_geometry_instrumentation import (
    aset,
    monotone_segment_reachable,
    oriented_coordinates,
    residual_chain,
)
from s2comp02c15_env import env02c12


ACTOR = frozenset({(-4, -1, -1), (-4, 0, -1), (-4, 0, 0)})
TARGET = frozenset({(-4, -1, -1), (-4, 0, -1), (-4, 1, -1)})


def probe():
    with env02c12() as (frozen_env, _, _):
        with frozen_env() as outer:
            with outer.frozen.frozen_env() as env:
                import c07d3e_component_viability as cv

                rows = outer.domains.load_d7b_rows(env)
                initial = frozenset(tuple(p) for p in rows[1]["state"])
                first = env.api.atomic_actions(initial)[0]
                parent = frozenset(initial | {tuple(p) for p in first["additions"]})
                parent_certs = tuple(
                    c for c in env.pred["extract_certificates"](parent, env.api)
                    if c.predicate == "N2_facet_connectivity"
                )
                actions = tuple(
                    a for a in env.pred["canonical_actions"](parent, env.api, parent_certs)
                    if "N2" in a.roles
                )
                actor_hits = [a for a in actions if aset(a) == ACTOR]
                target_hits = [a for a in actions if aset(a) == TARGET]
                if len(actor_hits) != 1 or len(target_hits) != 1:
                    raise AssertionError("exact natural negative-control actions not found")
                child = frozenset(parent | ACTOR)
                residual = frozenset(TARGET - ACTOR)
                certs = tuple(
                    c for c in env.pred["extract_certificates"](child, env.api)
                    if c.predicate == "N2_facet_connectivity"
                )
                allowed = child | residual
                all_pairs = []
                for cert in certs:
                    left, right = cert.carrier
                    distance, pairs = cv.shortest_endpoint_pairs(
                        frozenset(left), frozenset(right)
                    )
                    for s, t in pairs:
                        chain = residual_chain(residual, s, t)
                        if chain is None:
                            all_pairs.append({
                                "certificate": cert.snapshot_id,
                                "s": list(s), "t": list(t), "distance": distance,
                                "residual_chainable": False,
                            })
                            continue
                        required = (s,) + tuple(chain) + (t,)
                        profile = [
                            bool(monotone_segment_reachable(u, v, allowed))
                            for u, v in zip(required, required[1:])
                        ]
                        q_rows = [list(oriented_coordinates(p, s, t)) for p in chain]
                        span = [abs(t[i] - s[i]) for i in range(3)]
                        boundary = [[0, 0, 0], *q_rows, span]
                        gaps = [
                            sum(abs(v[i] - u[i]) for i in range(3))
                            for u, v in zip(boundary, boundary[1:])
                        ]
                        all_pairs.append({
                            "certificate": cert.snapshot_id,
                            "s": list(s), "t": list(t), "distance": distance,
                            "residual_chainable": True,
                            "ordered_residual": [list(p) for p in chain],
                            "endpoint_span": span,
                            "ordered_q_R": q_rows,
                            "segment_l1_lengths": gaps,
                            "segment_reachable": profile,
                            "fully_monotone_reachable": all(profile),
                        })
    chainable = [row for row in all_pairs if row["residual_chainable"]]
    return {
        "source_state_index": 1,
        "actor": [list(v) for v in sorted(ACTOR)],
        "target": [list(v) for v in sorted(TARGET)],
        "residual": [list(v) for v in sorted(residual)],
        "shortest_endpoint_pair_count": len(all_pairs),
        "residual_chainable_pair_count": len(chainable),
        "fully_monotone_reachable_pair_count": sum(
            row["fully_monotone_reachable"] for row in chainable
        ),
        "chainable_pairs": chainable,
    }


if __name__ == "__main__":
    print(json.dumps(probe(), indent=2, sort_keys=True))

#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/"STABILIZATION_DATA"
def load(n): return json.loads((ROOT/n).read_text())
def empty(v):
    if isinstance(v,list): return len(v)==0
    if isinstance(v,dict): return all(empty(x) for x in v.values())
    return not v
l1a=load('base_signature_table.json'); l1b=load('representative_geometry.json')
conn=load('connected_tail.json'); iso=load('isolated_bridge_quotient.json')
reach=load('parametric_reachability.json'); k9=load('k9_exhaustiveness.json')
checks={
 'base_sizes':l1a['closure_sizes']=={'6':9524,'7':21963,'8':45939},
 'classes_53':l1a['common_behavioral_classes']==53 and len(l1a['classes'])==53,
 'templates_18':l1a['witnessed_template_count']==18 and len(l1a['templates'])==18,
 'corridor_laws':l1b['corridor_law_counts']=={'0':22,'k-4':30,'k-6':1},
 'connected_31':conn['connected_class_count']==31,
 'connected_counts':conn['descendant_states_audited']==2869 and conn['action_edges_audited']==4035,
 'isolated_22_737':iso['t12_formal_classes']==22 and iso['isolated_states']==737,
 'k9_counts':k9['root_closure_state_count']==87517 and k9['root_closure_edge_count']==148722,
 'reach_tree':reach['tree_node_count']==54 and reach['tree_edge_count']==53,
 'reach_53':reach['k6_reachable_formal_classes']==53 and reach['k9_reachable_formal_classes']==53,
 'no_failures':empty(l1a['fixed_remainder_failures']) and empty(l1a['component_reconstruction_failures']) and empty(l1b['failures']) and empty(conn['failures']) and empty(iso['failures']) and empty(reach['failures']) and empty(k9['failures']),
}
print(json.dumps({'pass':all(checks.values()),'checks':checks},indent=2,sort_keys=True))
raise SystemExit(0 if all(checks.values()) else 1)

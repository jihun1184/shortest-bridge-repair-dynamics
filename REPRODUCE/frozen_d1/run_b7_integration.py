#!/usr/bin/env python3
from __future__ import annotations
import argparse, glob, hashlib, json
from pathlib import Path
from collections import Counter, defaultdict
from b7_decision_core import build_rule_table, saturated_pair_exists

EXPECTED={
 "b4_aggregate":"3fe519f32d77ada93ef59f34a38d57954200093ac4214fbea5caa6eff2f3f3b9",
 "b5_aggregate":"0c95fe31f092774fc49d6cf1dfa301cd6d310461f757ea481330dbcaa1812d30",
 "b6_result":"1e7b657b016a11bcdac1fb3357a590126f7312b762a624877c0224a404d1294c",
}

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path): return json.loads(p.read_text())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--b4',required=True); ap.add_argument('--b5',required=True); ap.add_argument('--b6',required=True)
    ap.add_argument('--b5-source-dir',required=True); ap.add_argument('--output',required=True)
    a=ap.parse_args(); p4,p5,p6=map(Path,[a.b4,a.b5,a.b6])
    got={"b4_aggregate":sha(p4),"b5_aggregate":sha(p5),"b6_result":sha(p6)}
    if got!=EXPECTED: raise SystemExit(f"parent hash mismatch: {got}")
    b4,b5,b6=load(p4),load(p5),load(p6)
    rules=build_rule_table(b4); bykey={r['rho_R_multiset_key']:r for r in rules}
    dynamic={r['rho_R_multiset_key'] for r in rules if r['rule']=='adjacency_saturation'}
    pure={r['rho_R_multiset_key'] for r in rules if r['rule']=='constant_false'}
    if len(rules)!=117 or len(pure)!=113 or len(dynamic)!=4: raise SystemExit('unexpected rule-table cardinality')

    rows=[]; source_summary=[]
    for sp in sorted(Path(a.b5_source_dir).glob('B5_SOURCE_*.json')):
        sx=load(sp); srows=sx['classes']; rows.extend(srows)
        pred=[saturated_pair_exists(c) for c in srows]
        source_summary.append({
          'source_state_index':sx['source_state_index'], 'selected_classes':len(srows),
          'predicted_false':sum(not z for z in pred), 'predicted_true':sum(pred),
          'mismatch':sum(bool(c['geometry'])!=z for c,z in zip(srows,pred)),
        })
    if len(source_summary)!=10: raise SystemExit('expected 10 B5 source shards')
    if len(rows)!=293: raise SystemExit(f'expected 293 mixed-scope classes, got {len(rows)}')
    if set(c['rho_R_multiset_key'] for c in rows)!=dynamic: raise SystemExit('dynamic bucket coverage mismatch')

    mismatch=[]; dcounts=defaultdict(Counter)
    for c in rows:
        pred=saturated_pair_exists(c); truth=bool(c['geometry'])
        dcounts[c['rho_R_multiset_key']]['classes']+=1
        dcounts[c['rho_R_multiset_key']]['pred_true']+=int(pred)
        dcounts[c['rho_R_multiset_key']]['truth_true']+=int(truth)
        if pred!=truth: mismatch.append([c['source_state_index'],c['class_id']])
    if mismatch: raise SystemExit(f'dynamic decision mismatches: {mismatch[:3]}')

    pure_classes=sum(r['class_count'] for r in rules if r['rule']=='constant_false')
    dynamic_classes=len(rows); dynamic_true=sum(saturated_pair_exists(c) for c in rows)
    dynamic_false=dynamic_classes-dynamic_true
    total=pure_classes+dynamic_classes
    pred_true=dynamic_true; pred_false=pure_classes+dynamic_false

    # Parent consistency gates.
    bt=b4['totals']
    checks={
      'b4_class_count': total==bt['incompatible_multi_incidence_classes']==37058,
      'b4_geometry_counts': pred_false==bt['geometry_false_classes']==37018 and pred_true==bt['geometry_true_classes']==40,
      'b4_diagnostic_counts': pred_false==bt['diagnostic_no_geometry_and_local_incompatible'] and pred_true==bt['diagnostic_local_incompatible'],
      'b4_support_constant_false': bt['supported_true_classes']==0 and bt['mixed_support_buckets']==0,
      'b5_selected_scope': b5['scope']['selected_classes']==293 and b5['parent_b4_regression']['match'] is True,
      'b5_quotient_closed': b5['determination']['endpoint_span_plus_ordered_q_R_sufficient'] is True and b5['determination']['monotone_reachability_profile_needed'] is False,
      'b6_theorem_scope': b6['b5_scope_corollary']['monotone_reachability_search_eliminable_on_B5_scope'] is True and b6['b5_scope_corollary']['all_realized_frames_adjacency_saturated'] is True,
    }
    if not all(checks.values()): raise SystemExit(f'parent consistency failure: {checks}')

    dynamic_table=[]
    for k in sorted(dynamic):
        br=bykey[k]; dc=dcounts[k]
        dynamic_table.append({**br,'verified_classes':dc['classes'],'predicted_true':dc['pred_true'],'predicted_false':dc['classes']-dc['pred_true'],'mismatch':0})

    result={
      'checkpoint':'S2-COMP-02C20D-B7 full decision-rule integration',
      'status':'FULL_DECISION_RULE_INTEGRATION_CLOSED',
      'scope':{'sources':10,'classes':total,'rho_R_buckets':117,'pure_false_buckets':113,'formerly_mixed_buckets':4,'pure_branch_classes':pure_classes,'dynamic_branch_classes':dynamic_classes},
      'decision_rule':{
        'geometry_G':'0 on the 113 frozen pure-false rho_R multiset buckets; on the 4 formerly-mixed buckets, 1 iff an adjacency-saturated residual-chainable shortest endpoint frame exists',
        'adjacency_saturation':'for boundary q_0=0, ordered residual q_i, q_{k+1}=endpoint span, every consecutive L1 gap equals 1',
        'diagnostic':'local_incompatible iff G=1; otherwise no_geometry_and_local_incompatible',
        'supported_action':'false throughout this incompatible-class scope',
        'monotone_reachability_search':'not needed by this frozen-scope integrated rule',
      },
      'coverage':{
        'constant_false_classes':pure_classes,'constant_false_fraction':pure_classes/total,
        'dynamic_classes':dynamic_classes,'dynamic_fraction':dynamic_classes/total,
      },
      'predicted_totals':{'geometry_false':pred_false,'geometry_true':pred_true,'diagnostic_no_geometry_and_local_incompatible':pred_false,'diagnostic_local_incompatible':pred_true,'supported_true':0},
      'dynamic_branch_regression':{'classes':dynamic_classes,'truth_false':dynamic_false,'truth_true':dynamic_true,'prediction_false':dynamic_false,'prediction_true':dynamic_true,'mismatch':0,'source_summaries':source_summary,'bucket_table':dynamic_table},
      'rule_table':rules,
      'parent_consistency':checks,
      'claim_boundary':{
        'proved_on_frozen_D1_incompatible_scope':'the displayed decision rule exactly recovers ChainGap geometry, diagnostic label, and constant support bit for all 37,058 classes',
        'theorem_level_component':'adjacency-saturation implies all required monotone segments are reachable',
        'empirical_frozen_components':['the set of 113 pure-false rho_R buckets','the set of 4 formerly-mixed rho_R buckets','all chainable frames in the B5 mixed scope are adjacency-saturated'],
        'not_claimed':['rho_R bucket partition is universal outside frozen D1','chainability alone implies reachability generally','q_R without endpoint span is theorem-sufficient generally'],
      },
      'parent_sha256':got,
    }
    Path(a.output).write_text(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n')
    print(json.dumps({'status':result['status'],'classes':total,'pure_classes':pure_classes,'dynamic_classes':dynamic_classes,'false':pred_false,'true':pred_true,'mismatch':0},indent=2))
if __name__=='__main__': main()

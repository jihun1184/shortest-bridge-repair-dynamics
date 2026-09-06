#!/usr/bin/env python3
import json
from pathlib import Path
x=json.loads(Path('02C20D_B7_FULL_DECISION_RULE.json').read_text())
assert x['status']=='FULL_DECISION_RULE_INTEGRATION_CLOSED'
assert x['scope']=={'sources':10,'classes':37058,'rho_R_buckets':117,'pure_false_buckets':113,'formerly_mixed_buckets':4,'pure_branch_classes':36765,'dynamic_branch_classes':293}
assert x['predicted_totals']=={'geometry_false':37018,'geometry_true':40,'diagnostic_no_geometry_and_local_incompatible':37018,'diagnostic_local_incompatible':40,'supported_true':0}
assert x['dynamic_branch_regression']['mismatch']==0
assert len(x['rule_table'])==117
assert sum(r['rule']=='constant_false' for r in x['rule_table'])==113
assert sum(r['rule']=='adjacency_saturation' for r in x['rule_table'])==4
assert all(x['parent_consistency'].values())
assert sum(s['mismatch'] for s in x['dynamic_branch_regression']['source_summaries'])==0
print('PASS: B7 full decision-rule integration 37,058/37,058')

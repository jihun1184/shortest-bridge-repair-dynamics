#!/usr/bin/env python3
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'LOCAL_DECISION_DATA'
rows=list(csv.DictReader((ROOT/'rule_table_117_keys.csv').open()))
exc=list(csv.DictReader((ROOT/'four_mixed_keys.csv').open()))
exc=[r for r in exc if r['exception_key']!='total']
cov=json.loads((ROOT/'coverage_and_totals.json').read_text())
constant=[r for r in rows if r['rule']=='constant_false']
mixed=[r for r in rows if r['rule']!='constant_false']
checks={
 'keys_117':len(rows)==117,
 'constant_113':len(constant)==113,
 'mixed_4':len(mixed)==4 and len(exc)==4,
 'constant_classes_36765':sum(int(r['class_count']) for r in constant)==36765,
 'mixed_classes_293':sum(int(r['classes']) for r in exc)==293,
 'mixed_false_true':sum(int(r['geometry_false']) for r in exc)==253 and sum(int(r['geometry_true']) for r in exc)==40,
 'totals':cov['scope']['classes']==37058 and cov['predicted_totals']['geometry_false']==37018 and cov['predicted_totals']['geometry_true']==40,
}
print(json.dumps({'pass':all(checks.values()),'checks':checks},indent=2,sort_keys=True))
raise SystemExit(0 if all(checks.values()) else 1)

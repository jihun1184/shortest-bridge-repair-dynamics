#!/usr/bin/env python3
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'FINITE_COMPATIBILITY_DATA'
def rows(n): return list(csv.DictReader((ROOT/n).open()))
w=rows('walk_counts.csv'); d=rows('depth_histogram.csv'); s=rows('support_separation.csv')
checks={
 'walk_counts':[(int(r['L']),int(r['M0_size'])) for r in w]==[(3,36),(4,108),(5,324)],
 'depth_totals':d[-1]['depth']=='total' and int(d[-1]['class_count'])==76 and int(d[-1]['pair_count'])==528,
 'depth3':any(r['depth']=='3' and int(r['class_count'])==4 and int(r['pair_count'])==12 for r in d),
 'support_total':s[-1]['chain_length_L']=='total' and int(s[-1]['instances_checked'])==21 and int(s[-1]['leaks_found'])==0,
}
print(json.dumps({'pass':all(checks.values()),'checks':checks},indent=2,sort_keys=True))
raise SystemExit(0 if all(checks.values()) else 1)

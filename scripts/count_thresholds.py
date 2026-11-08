# the counts in the post ("five of six on MOF alone, four of six strict") use thresholds I picked:
# any gap at all for MOF alone, and more than $5bn of non-US selling by all residents for the strict
# count. this reruns both counts at every threshold from $0bn to $60bn so you can see where they break.
import os, csv
from common import RESULTS, write_csv

ig = list(csv.DictReader(open(os.path.join(RESULTS, 'intervention_gaps.csv'))))
mof = [-float(r['gap_mof_only']) for r in ig]               # positive = MOF sold more than US data find
strict = [-float(r['non_us_all_residents']) for r in ig]    # positive = residents sold non-US debt
rows = []
for x in range(0, 61, 5):
    a = sum(v > x for v in mof); b = sum(v > x for v in strict)
    a24 = sum(v > x for r, v in zip(ig, mof) if r['month'] >= '2024'); b24 = sum(v > x for r, v in zip(ig, strict) if r['month'] >= '2024')
    rows.append([x, a, b, a24, b24])
    print(f"threshold {x:2d}bn: MOF alone {a} of 6, strict {b} of 6 | since 2024: {a24} of 4 and {b24} of 4")
print(f"\nMOF alone stays at 5 of 6 up to {min(v for v in mof if v > 0):.1f}bn; strict stays at 4 of 6 up to "
      f"{sorted(v for v in strict if v > 0)[-4]:.1f}bn")
write_csv('count_thresholds.csv', ['threshold_bn', 'mof_alone_of_6', 'strict_of_6', 'mof_alone_since_2024_of_4', 'strict_since_2024_of_4'], rows)

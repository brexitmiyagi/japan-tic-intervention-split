# the August gap is a leftover: MOF's securities drop minus what US data can find. leftovers are
# where measurement error lives, so for each way the gap could be an error I work out how big that
# error would have to be to close all of it, and put it next to what the data say.
#
# two facts about TIC that matter here, from the notes to SLT table 3 and the Fed staff note of
# 15 October 2025 (federalreserve.gov/econres/notes/feds-notes/measuring-u-s-cross-border-
# securities-flows-out-with-the-old-in-with-the-new-20251015.html):
#   - since February 2023 long-term net flows come from reported purchases and sales on the SLT
#     form, not from holdings minus an estimated price change. the old Form S was dropped after
#     January 2023.
#   - bill net flows are the month-over-month change in bill holdings, with no valuation change.
#     so a bill that matures and isn't replaced counts as a "sale".
import os, csv
import subprocess, sys
from common import DATA, RESULTS, tic_table3, write_csv
subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'custody_centres.py')], check=True, capture_output=True)

t = tic_table3(); jp = t['Japan']
gap = list(csv.DictReader(open(os.path.join(RESULTS, 'august_gap.csv'))))
aug = [r for r in gap if r['month'] == '2026-08'][0]
G = -float(aug['gap_vs_all_us_debt'])                         # 49.7, the size to explain
val = float(aug['implied_valuation'])
lt_jul = jp['2026-07']['lt_pos']; st_jul = jp['2026-07']['st_pos']

# biggest seller in August after Japan and the aggregates
skip = ('Japan', 'Grand Total', 'Of Which: Foreign Official', 'Total')
others = sorted(((k, v['2026-08']['lt_net'] + (v['2026-08']['st_net'] or 0)) for k, v in t.items()
                 if '2026-08' in v and v['2026-08'].get('lt_net') is not None and not k.startswith(skip)
                 and 'Total' not in k and k != 'International'), key=lambda x: x[1])
big_name, big_val = others[0]
cust = {k: t[k]['2026-08']['lt_net'] + t[k]['2026-08']['st_net'] for k in ('Belgium', 'Luxembourg', 'United Kingdom')}
off = t['Of Which: Foreign Official']['2026-08']; off_tot = off['lt_net'] + off['st_net']

cc = list(csv.DictReader(open(os.path.join(RESULTS, 'custody_centres.csv'))))
cc_net = sum(float(r['net_bn']) for r in cc if r['group'] == 'custody centre')
cc_fall = sum(float(r['falling_lines_bn']) for r in cc if r['group'] == 'custody centre')
oth = sum(float(r['net_bn']) for r in cc if r['group'] == 'other net seller')
fe = {r['item']: float(r['value']) for r in csv.DictReader(open(os.path.join(RESULTS, 'fefsa_composition.csv')))}
swap = [r for r in csv.DictReader(open(os.path.join(RESULTS, 'intervention_gaps.csv'))) if r['month'] == '2026-08'][0]
rows = [
    ['Price change on MOF holdings', f"{G:.1f}bn of price loss in August",
     f"BoP transactions vs stock: valuation about {val:+.1f}bn", 'ruled out'],
    ['Error in TIC long-term figures', f"{G / lt_jul * 100:.1f}% of Japan's {lt_jul:,.0f}bn long-term holdings, in one month",
     'reported purchases and sales since Feb 2023', 'very unlikely'],
    ['Error in TIC bill figures', f"{G / st_jul * 100:.0f}% of Japan's {st_jul:.1f}bn end-July bills",
     'holdings change; maturities count as sales, which raises dollars just the same', 'very unlikely'],
    ['Treasuries in custody outside Japan', f"other country rows selling about {G:.0f}bn between them",
     f"custody centres net {cc_net:+.1f}bn; every falling bill or bond line among them {cc_fall:.1f}bn; every other net-selling country {oth:.1f}bn (biggest {big_name} {big_val:+.1f}bn)",
     'unlikely: needs nearly every falling line outside Japan to be MOF'],
    ['Timing (trades settling outside August)', f"about {G:.0f}bn of trades settling in July or September",
     'window ended 26 Aug, MOF zero from 27 Aug, end-July reserves flat', 'ruled out'],
    ['Interest income inside the BoP figure', 'would need to be a large negative',
     f"coupons add about ${fe['interest_usd_bn_per_month']:.1f}bn a month to reserves (FEFSA FY2024 accounts)", 'wrong sign, widens the gap'],
    ['Private Japanese swapping non-US bonds into Treasuries', f"{G:.0f}bn of private Treasury buying matched by non-US selling",
     f"needs Y{swap['swap_needed_yen_tn']}tn, {swap['swap_pct_of_real_money_acq']}% of real-money gross foreign-bond buying that month (Y{swap['real_money_gross_lt_acq_yen_tn']}tn); survey has no currency split",
     'strained, can\'t rule out; non-US selling by Japanese residents is the same either way'],
]
for r in rows:
    print(' | '.join(r))
write_csv('error_band.csv', ['source', 'size needed to close the gap', 'what the data say', 'verdict'], rows)

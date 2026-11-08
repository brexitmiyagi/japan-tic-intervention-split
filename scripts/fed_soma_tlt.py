# how much of TLT's basket the Fed owns, and whether it's shrinking.
# the New York Fed publishes SOMA holdings by CUSIP every week, with each line's share of the amount
# outstanding. I match TLT's 47 bonds on 4 Nov 2026 and look back a year. the Fed's 28 October
# implementation note says it rolls over at auction all principal from its Treasuries, so its long bonds
# only change when its maturing coupons get rolled into new 20- and 30-year auctions. nothing runs off.
# careful: "outstanding" here is implied from SOMA's own percent-of-outstanding column.
import os, csv, json
from common import DATA, write_csv

tlt = {r['cusip']: float(r['par_value_usd_k']) * 1e3 for r in csv.DictReader(open(os.path.join(DATA, 'tlt_holdings_2026-11-04.csv'))) if r['cusip'].startswith('912810')}
note = {r['item']: r['text'] for r in csv.DictReader(open(os.path.join(DATA, 'fomc_implementation_note_2026-10-28.csv')))}
assert note['treasury_rollover'].startswith('Roll over at auction all principal payments')
rows = []
for d in ('2025-11-05', '2025-12-31', '2026-07-29', '2026-11-04'):
    h = {x['cusip']: x for x in json.load(open(os.path.join(DATA, f'nyfed_soma_tsy_{d}.json')))['soma']['holdings']}
    m = [c for c in tlt if c in h]
    par = sum(float(h[c]['parValue']) for c in m) / 1e9
    out = sum(float(h[c]['parValue']) / float(h[c]['percentOutstanding']) for c in m if float(h[c]['percentOutstanding']) > 0) / 1e9
    nb = sum(float(x['parValue']) for x in h.values() if x['securityType'] == 'NotesBonds') / 1e9
    rows.append([d, len(m), round(par, 1), round(out, 1), round(par / out * 100, 1), round(nb, 1)])
    print(f"{d}: Fed holds {len(m)} of TLT's bonds, ${par:.1f}bn par, {par / out * 100:.1f}% of their ${out:.1f}bn outstanding; all Fed notes and bonds ${nb:.1f}bn")
tp = sum(tlt.values()) / 1e9
print(f"TLT's own par in the same bonds: ${tp:.1f}bn, so the Fed holds {rows[-1][2] / tp:.1f} times what TLT holds")
print(f"change in the Fed's holdings of TLT's bonds over the year: ${rows[-1][2] - rows[0][2]:+.1f}bn")
write_csv('fed_soma_tlt.csv', ['as_of', 'tlt_bonds_held', 'fed_par_bn', 'outstanding_bn', 'fed_share_pct', 'fed_notes_bonds_bn'], rows + [['tlt_par', None, round(tp, 1), None, None, None]])

# where the year's increase came from: bonds first sold during the year, or more of the old ones
h0 = {x['cusip']: float(x['parValue']) for x in json.load(open(os.path.join(DATA, 'nyfed_soma_tsy_2025-11-05.json')))['soma']['holdings']}
h1 = {x['cusip']: float(x['parValue']) for x in json.load(open(os.path.join(DATA, 'nyfed_soma_tsy_2026-11-04.json')))['soma']['holdings']}
new = [c for c in tlt if c in h1 and c not in h0]
old = [c for c in tlt if c in h0 and c in h1]
nv, ov = sum(h1[c] for c in new) / 1e9, sum(h1[c] - h0[c] for c in old) / 1e9
print(f"of the change: ${nv:.1f}bn is the Fed's share of {len(new)} bonds first sold during the year, ${ov:+.1f}bn in the other {len(old)}")
write_csv('fed_soma_tlt_split.csv', ['part', 'bonds', 'change_bn'], [['new bonds', len(new), round(nv, 1)], ['bonds held a year ago', len(old), round(ov, 1)]])

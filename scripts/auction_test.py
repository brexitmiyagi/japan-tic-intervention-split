# did Japan step back from the long end at auction? every 20- and 30-year nominal bond auction since 2022.
# indirect bidders are where foreign central banks bid (through the New York Fed), alongside foreign
# private accounts and domestic funds bidding through dealers. if MOF or other official buyers stepped back
# during or after a defense, the indirect share of the competitive award should drop, and dealers, who take
# what's left, should end up with more.
# windows: "during and the month after" runs from the first intervention day to 30 calendar days after the
# last. "the refill months" runs from day 31 to day 120, when Japan was rebuilding bills after 2024.
# each auction is compared with every auction of the same tenor since 2022 that sits outside all windows.
# careful: indirect isn't only central banks, and Treasury doesn't split it. the usual tail measure needs the
# 1pm when-issued yield, which isn't free, so I don't use tails. the sample is small: one or two auctions per
# tenor per window.
import os, csv, datetime as dt
from common import DATA, write_csv

A = []
for r in csv.DictReader(open(os.path.join(DATA, 'treasury_bond_auctions_2021_2026.csv'))):
    d = dt.date.fromisoformat(r['auction_date'])
    comp = float(r['indirect_competitive_awarded']) + float(r['direct_competitive_awarded']) + float(r['dealer_competitive_awarded'])
    if d < dt.date(2022, 1, 1) or comp == 0:
        continue
    A.append({'d': d, 'ten': r['tenor'], 'ind': float(r['indirect_competitive_awarded']) / comp * 100,
              'dlr': float(r['dealer_competitive_awarded']) / comp * 100, 'btc': float(r['bid_to_cover']),
              'dir': float(r['direct_competitive_awarded']) / comp * 100, 'ind_usd': float(r['indirect_competitive_awarded']), 'comp': comp})
episodes = [
    ('Sep 2022', [dt.date(2022, 9, 22)]),
    ('Oct 2022', [dt.date(2022, 10, 21), dt.date(2022, 10, 24)]),
    ('Apr-May 2024', [dt.date(2024, 4, 29), dt.date(2024, 5, 1)]),
    ('Jul 2024', [dt.date(2024, 7, 11), dt.date(2024, 7, 12)]),
    ('Apr-May 2026', [dt.date(2026, 4, 30), dt.date(2026, 5, 4), dt.date(2026, 5, 6)]),
    ('Jul 2026', [dt.date(2026, 7, 30), dt.date(2026, 7, 31)]),
]
def window(a, e, part):
    s, l = e[1][0], e[1][-1]
    if part == 'during':
        return s <= a['d'] <= l + dt.timedelta(30)
    return l + dt.timedelta(31) <= a['d'] <= l + dt.timedelta(120)
inside = lambda a: any(window(a, e, p) for e in episodes for p in ('during', 'refill'))
base = {t: [a for a in A if a['ten'] == t and not inside(a)] for t in ('20', '30')}
def pct(a, key):
    b = [x[key] for x in base[a['ten']]]
    return round(sum(x <= a[key] for x in b) / len(b) * 100)
print(f"{len(A)} auctions since 2022; outside all windows: 20y {len(base['20'])}, 30y {len(base['30'])}")
for t in ('20', '30'):
    b = sorted(x['ind'] for x in base[t])
    print(f"  {t}y indirect share outside windows: median {b[len(b) // 2]:.1f}%, 10th-90th {b[len(b) // 10]:.1f}% to {b[len(b) * 9 // 10]:.1f}%")
rows, low = [], 0
for name, days in episodes:
    for part in ('during', 'refill'):
        for a in [x for x in A if window(x, (name, days), part)]:
            pi, pdl = pct(a, 'ind'), pct(a, 'dlr')
            low += pi <= 10
            rows.append([name, part, a['d'].isoformat(), a['ten'] + 'y', round(a['ind'], 1), pi, round(a['dlr'], 1), pdl, a['btc']])
            print(f"{name:13s} {part:6s} {a['d']} {a['ten']}y  indirect {a['ind']:5.1f}% (pct {pi:3d})  dealers {a['dlr']:5.1f}% (pct {pdl:3d})  btc {a['btc']:.2f}")
# windows overlap (Sep and Oct 2022, the 2024 pair), so count each auction once
seen = {}
for r in sorted(rows, key=lambda r: r[1] != 'during'):   # an auction inside any "during" window counts as during
    seen.setdefault((r[2], r[3]), r)
u = list(seen.values())
for part in ('during', 'refill'):
    rr = [r for r in u if r[1] == part]
    print(f"  {part}: {len(rr)} auctions, median indirect percentile {sorted(r[5] for r in rr)[len(rr) // 2]}, "
          f"median dealer percentile {sorted(r[7] for r in rr)[len(rr) // 2]}, indirect at or below 10th pct: {sum(r[5] <= 10 for r in rr)}")
print(f"  all: {len(u)} distinct auctions, indirect at or below 10th pct: {sum(r[5] <= 10 for r in u)} (about {len(u) / 10:.0f} by chance)")

# the long end as a whole: indirect dollars over competitive dollars across the 20y and 30y in each month
mon = {}
for a in A:
    m = mon.setdefault((a['d'].year, a['d'].month), {'ind': 0.0, 'comp': 0.0, 'n': 0, 'inside': False})
    m['ind'] += a['ind_usd']; m['comp'] += a['comp']; m['n'] += 1; m['inside'] |= inside(a)
full = {k: v['ind'] / v['comp'] * 100 for k, v in mon.items() if v['n'] == 2}
outm = [full[k] for k in full if not mon[k]['inside']]
mrows = []
print("\nboth long auctions together, months after the July 2026 defense:")
for k in [(2026, 8), (2026, 9), (2026, 10)]:
    pc = round(sum(x <= full[k] for x in outm) / len(outm) * 100)
    print(f"  {k[0]}-{k[1]:02d}: indirect {full[k]:.1f}% of the competitive award, percentile {pc} of {len(outm)} months outside windows")
    mrows.append([f"{k[0]}-{k[1]:02d}", round(full[k], 1), pc])
for d in ('2026-09-15', '2026-10-21'):
    a = [x for x in A if x['d'].isoformat() == d][0]
    print(f"  20y {d}: indirect {a['ind']:.1f}%, direct {a['dir']:.1f}%, dealers {a['dlr']:.1f}%")
    b = sorted(x['dir'] for x in base['20'])
    print(f"     direct share percentile {round(sum(x <= a['dir'] for x in b) / len(b) * 100)}")
write_csv('auction_test.csv', ['episode', 'window', 'auction_date', 'tenor', 'indirect_share_pct', 'indirect_percentile',
                               'dealer_share_pct', 'dealer_percentile', 'bid_to_cover'], rows)
write_csv('auction_test_monthly.csv', ['month', 'indirect_share_20y_30y_pct', 'percentile'], mrows)

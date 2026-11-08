# why did indirect bidders take so little of the September and October 2026 20-year auctions?
# two cheap explanations, both checked here.
# 1. price: if the 20-year were rich against the 30-year, buyers skipping it would make sense. the 20s30s
#    spread (30-year yield minus 20-year, FRED constant maturity) on each auction day says which.
# 2. plumbing: FIMA (foreign central banks bidding non-competitively) or SOMA add-ons taking a slice. SOMA
#    add-ons sit outside the offering amount, so they can't change the competitive shares, and FIMA
#    non-competitive awards have been zero at every bond auction since 2021.
import os, csv, datetime as dt
from common import DATA, fred, write_csv

y20, y30 = dict(fred('DGS20')), dict(fred('DGS30'))
A = [r for r in csv.DictReader(open(os.path.join(DATA, 'treasury_bond_auctions_2021_2026.csv')))
     if r['tenor'] == '20' and r['auction_date'] >= '2022-01-01']
rows = []
for r in A:
    d = dt.date.fromisoformat(r['auction_date'])
    if d not in y20 or d not in y30:
        continue
    comp = sum(float(r[k]) for k in ('indirect_competitive_awarded', 'direct_competitive_awarded', 'dealer_competitive_awarded'))
    rows.append([r['auction_date'], round((y30[d] - y20[d]) * 100), round(float(r['indirect_competitive_awarded']) / comp * 100, 1),
                 int(float(r['fima_noncomp_awarded'] or 0)), int(float(r['soma_awarded'] or 0))])
spr = sorted(x[1] for x in rows)
for d in ('2026-09-15', '2026-10-21'):
    r = [x for x in rows if x[0] == d][0]
    print(f"{d}: 20s30s {r[1]:+d}bp (percentile {round(sum(s <= r[1] for s in spr) / len(spr) * 100)} of {len(spr)} 20-year auction days), "
          f"indirect {r[2]}%, FIMA non-comp ${r[3]:,}, SOMA ${r[4]:,}")
inv = [x for x in rows if x[1] < 0]
print(f"20s30s inverted (20-year cheaper) on {len(inv)} of {len(rows)} 20-year auction days since 2022")
# does a cheaper 20-year normally go with a lower indirect share? a simple correlation across auctions
n = len(rows); mx = sum(x[1] for x in rows) / n; my = sum(x[2] for x in rows) / n
cov = sum((x[1] - mx) * (x[2] - my) for x in rows); vx = sum((x[1] - mx) ** 2 for x in rows); vy = sum((x[2] - my) ** 2 for x in rows)
print(f"correlation of 20s30s with indirect share across {n} auctions: {cov / (vx * vy) ** 0.5:+.2f}")
print(f"FIMA non-competitive awards at any bond auction since 2021: {sum(1 for r in csv.DictReader(open(os.path.join(DATA, 'treasury_bond_auctions_2021_2026.csv'))) if float(r['fima_noncomp_awarded'] or 0) > 0)}")
write_csv('auction_20y_check.csv', ['auction_date', 'spread_20s30s_bp', 'indirect_share_pct', 'fima_noncomp', 'soma_awarded'], rows)
# how much of the low share does price explain? a straight-line fit of indirect share on 20s30s
b = cov / vx; a = my - b * mx
res = sorted(x[2] - (a + b * x[1]) for x in rows)
spr_med = spr[len(spr) // 2]
print(f"median 20s30s on 20-year auction days: {spr_med:+d}bp")
for d in ('2026-09-15', '2026-10-21'):
    r = [x for x in rows if x[0] == d][0]; fit = a + b * r[1]; e = r[2] - fit
    print(f"{d}: fit says {fit:.1f}%, actual {r[2]}%, shortfall {e:+.1f} points, "
          f"residual percentile {round(sum(z <= e for z in res) / len(res) * 100)}")

# where September and October rank among every 20-year auction since 2022, and how unusual it is for two
# of the weakest three to come back to back. if the order were random, the chance that some adjacent pair
# of auctions both sit in the bottom three is worked out exactly below.
from itertools import combinations
order = sorted(rows, key=lambda x: x[0])
ranked = sorted(range(len(order)), key=lambda i: order[i][2])
for d in ('2026-09-15', '2026-10-21'):
    i = [k for k, x in enumerate(order) if x[0] == d][0]
    print(f"{d}: indirect share rank {ranked.index(i) + 1} lowest of {len(order)} 20-year auctions since 2022")
bottom3 = sorted(ranked[:3])
print(f"the three lowest: {', '.join(order[i][0] for i in bottom3)}")
n = len(order)
adj = sum(1 for c in combinations(range(n), 3) if c[1] - c[0] == 1 or c[2] - c[1] == 1)
tot = n * (n - 1) * (n - 2) // 6
print(f"chance that a random order puts two of the bottom three back to back: {adj / tot:.1%}")
write_csv('auction_20y_rank.csv', ['item', 'value'], [['n', n], ['rank_2026_09_15', ranked.index([k for k, x in enumerate(order) if x[0] == '2026-09-15'][0]) + 1],
          ['rank_2026_10_21', ranked.index([k for k, x in enumerate(order) if x[0] == '2026-10-21'][0]) + 1], ['p_adjacent_bottom3', round(adj / tot, 3)]])

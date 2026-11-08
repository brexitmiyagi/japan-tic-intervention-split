# sold, or left to run off? TIC counts a bill that matures and isn't replaced as a sale, so it
# can't tell the two apart. Treasury's auction allotments by investor class can. for every bill
# auction since October 2009 they say how much went to "foreign and international" buyers, which
# includes central banks bidding through the New York Fed (and foreign private buyers too).
# run-off at auction, per month = what foreign and international buyers were allotted in bills
# issued that month, minus what they had been allotted in bills maturing that month.
# careful: this only sees auctions. a bill bought at auction and sold before it matures, or bought
# in the market, doesn't show. and the category isn't only central banks.
import os, csv, datetime as dt
from common import DATA, tic_table3, write_csv

iss, mat = {}, {}
win = {'May 2026': (dt.date(2026, 4, 28), dt.date(2026, 5, 29)), 'Aug 2026': (dt.date(2026, 7, 29), dt.date(2026, 8, 28))}
w_iss = {k: 0.0 for k in win}; w_mat = {k: 0.0 for k in win}
for r in csv.DictReader(open(os.path.join(DATA, 'treasury_ic_bills_allotments.csv'))):
    if not r['fi']:
        continue
    fi = float(r['fi']); i = dt.date.fromisoformat(r['issue'][:10]); m = dt.date.fromisoformat(r['maturity'][:10])
    iss[i.strftime('%Y-%m')] = iss.get(i.strftime('%Y-%m'), 0) + fi
    mat[m.strftime('%Y-%m')] = mat.get(m.strftime('%Y-%m'), 0) + fi
    for k, (a, b) in win.items():
        if a <= i <= b: w_iss[k] += fi
        if a <= m <= b: w_mat[k] += fi
months = sorted(k for k in iss if '2010-01' <= k <= '2026-09')
net = {m: iss[m] - mat.get(m, 0) for m in months}
order = sorted(months, key=lambda m: net[m])
off = tic_table3()['Of Which: Foreign Official']; jp = tic_table3()['Japan']
rows = []
for m in months:
    rows.append([m, round(iss[m], 1), round(mat.get(m, 0), 1), round(net[m], 1), order.index(m) + 1])
print(f"{len(months)} months, January 2010 to September 2026. biggest run-offs:")
for m in order[:10]:
    print(f"  {m}: issued {iss[m]:.1f}, maturing {mat.get(m, 0):.1f}, net {net[m]:+.1f}bn")
for m in ['2022-10', '2024-05', '2024-07', '2026-05', '2026-06', '2026-08']:
    tic = f"; TIC bills: foreign official {off[m]['st_net']:+.1f}, Japan {jp[m]['st_net']:+.1f}" if m in off and off[m]['st_net'] is not None else ''
    print(f"{m}: run-off at auction {net[m]:+.1f}bn, rank {order.index(m) + 1} of {len(months)}{tic}")
for k in win:
    print(f"{k} window by issue date: issued {w_iss[k]:.1f}, maturing {w_mat[k]:.1f}, net {w_iss[k] - w_mat[k]:+.1f}bn")
print(f"May 2026 run-off as a share of the TIC fall in foreign official bills: {net['2026-05'] / off['2026-05']['st_net'] * 100:.0f}%; "
      f"August: {net['2026-08'] / off['2026-08']['st_net'] * 100:.0f}%")
write_csv('auction_runoff.csv', ['month', 'fi_allotted_in_bills_issued_bn', 'fi_allotted_in_bills_maturing_bn', 'net_bn', 'rank_most_negative'], rows)

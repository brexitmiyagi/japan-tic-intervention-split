# TLT's own positioning: money in and out of the fund, short interest, and the latest payout.
# flows: iShares' daily shares outstanding times NAV. a creation adds shares, a redemption removes them,
# so the daily change in shares times that day's NAV is about the money that came in or went out.
# short interest: FINRA's mid-month and month-end counts (Nasdaq carries the same file), against
# shares outstanding on the same settlement date.
# careful: TLT short interest includes market makers' hedges and people shorting TLT against bonds they
# own, so it isn't all bearish bets. and iShares' shares outstanding can lag a creation by a day.
import os, csv, json, datetime as dt
from common import DATA, write_csv

h = []
for r in csv.DictReader(open(os.path.join(DATA, 'ishares_tlt_history_2026-11-05.csv'))):
    h.append((dt.date.fromisoformat(r['date']), float(r['nav_usd']), float(r['ex_dividend_usd'] or 0), float(r['shares_outstanding'])))
h.sort()
def flow(a, b):
    tot = 0.0
    for (d0, n0, _, s0), (d1, n1, _, s1) in zip(h, h[1:]):
        if a < d1 <= b:
            tot += (s1 - s0) * n1
    return tot / 1e9
def so(d):
    return [x for x in h if x[0] <= d][-1][3]
rows = []
for name, a, b in [('2026 to date', dt.date(2025, 12, 31), dt.date(2026, 11, 5)),
                   ('Japan April-May defense through end-May', dt.date(2026, 4, 28), dt.date(2026, 5, 29)),
                   ('Japan July defense through end-August', dt.date(2026, 7, 29), dt.date(2026, 8, 31)),
                   ('September', dt.date(2026, 8, 31), dt.date(2026, 9, 30)),
                   ('October to 5 Nov', dt.date(2026, 9, 30), dt.date(2026, 11, 5))]:
    f = flow(a, b)
    print(f"{name:42s}: shares {so(a) / 1e6:6.1f}m -> {so(b) / 1e6:6.1f}m, net flow about ${f:+.1f}bn")
    rows.append([name, a.isoformat(), b.isoformat(), round(so(a) / 1e6, 1), round(so(b) / 1e6, 1), round(f, 1)])
si = json.load(open(os.path.join(DATA, 'nasdaq_tlt_short_interest_2026-11-06.json')))['data']['shortInterestTable']['rows']
finra = json.load(open(os.path.join(DATA, 'finra_tlt_short_interest_2026-10-15.json')))[0]
assert int(si[0]['interest'].replace(',', '')) == finra['currentShortPositionQuantity']
for r in si[:1] + [x for x in si if x['settlementDate'] in ('07/31/2026', '12/31/2025')]:
    d = dt.datetime.strptime(r['settlementDate'], '%m/%d/%Y').date(); n = int(r['interest'].replace(',', ''))
    print(f"short interest {d}: {n / 1e6:.1f}m shares, {n / so(d) * 100:.1f}% of shares outstanding, {float(r['daysToCover']):.1f} days to cover")
    rows.append([f'short interest {d}', None, d.isoformat(), round(n / 1e6, 1), round(n / so(d) * 100, 1), round(float(r['daysToCover']), 1)])
d, nav, div, _ = [x for x in h if x[2]][-1]
print(f"latest payout: ${div} ex {d}, {div * 12 / nav * 100:.2f}% a year at that NAV (SEC yield 5.28%, trailing 12m 4.78%)")
rows.append(['latest monthly payout annualised', d.isoformat(), None, div, round(div * 12 / nav * 100, 2), None])
write_csv('tlt_flows.csv', ['item', 'from', 'to', 'a', 'b', 'c'], rows)

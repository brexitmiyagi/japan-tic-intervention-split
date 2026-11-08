# TLT's price against its NAV on every MOF intervention day since 2022. if Japan's selling hit the long end
# hard, the ETF would trade at a discount first, because buyers of TLT can step back faster than bond
# dealers can reprice the basket.
# close: Nasdaq, checked against Yahoo (they agree on every day). NAV: iShares' daily history.
# careful: the NAV and the 4pm close aren't struck on exactly the same prices, so a few basis points
# either way is normal noise. what matters is whether intervention days sit in the tail.
import os, csv, datetime as dt
from common import DATA, fred, write_csv

px = {dt.date.fromisoformat(r['date']): float(r['close_usd']) for r in csv.DictReader(open(os.path.join(DATA, 'nasdaq_tlt_close_2022_2026.csv')))}
y = {dt.date.fromisoformat(r['date']): float(r['close_usd']) for r in csv.DictReader(open(os.path.join(DATA, 'yahoo_tlt_close_2022_2026.csv')))}
assert all(abs(px[d] - y[d]) < 0.011 for d in px if d in y)
nav = {dt.date.fromisoformat(r['date']): float(r['nav_usd']) for r in csv.DictReader(open(os.path.join(DATA, 'ishares_tlt_history_2026-11-05.csv')))}
days = sorted(d for d in px if d in nav)
# days the stock market traded but the bond market didn't (Columbus Day, Veterans Day) carry a stale NAV,
# so I keep only days with a FRED 30-year yield, which is missing when the bond market is shut
bond_open = {d for d, _ in fred('DGS30')}
days = [d for d in days if d in bond_open]
prem = {d: (px[d] / nav[d] - 1) * 10000 for d in days}   # basis points
allv = sorted(prem.values())
def pctile(v):
    return round(sum(x <= v for x in allv) / len(allv) * 100)
episodes = [
    ('Sep 2022', [dt.date(2022, 9, 22)]),
    ('Oct 2022', [dt.date(2022, 10, 21), dt.date(2022, 10, 24)]),
    ('Apr-May 2024', [dt.date(2024, 4, 29), dt.date(2024, 5, 1)]),
    ('Jul 2024', [dt.date(2024, 7, 11), dt.date(2024, 7, 12)]),
    ('Apr-May 2026', [dt.date(2026, 4, 30), dt.date(2026, 5, 4), dt.date(2026, 5, 6)]),
    ('Jul 2026', [dt.date(2026, 7, 30), dt.date(2026, 7, 31)]),
]
print(f"{len(days)} bond-market days since 2022: TLT close vs NAV median {allv[len(allv) // 2]:+.1f}bp, "
      f"5th-95th {allv[len(allv) // 20]:+.1f} to {allv[len(allv) * 19 // 20]:+.1f}bp, worst {allv[0]:+.1f}bp on {min(prem, key=prem.get)}")
rows, tail = [], 0
for name, ds in episodes:
    last = days.index(max(d for d in days if d <= ds[-1]))
    wk = [d for d in days if ds[0] <= d] [:len([d for d in days if ds[0] <= d <= ds[-1]]) + 5]
    for d in wk:
        p = prem[d]; pc = pctile(p); tail += pc <= 5
        rows.append([name, d.isoformat(), 'intervention' if d in ds else 'settlement week', round(p, 1), pc])
    v = [prem[d] for d in wk]
    print(f"  {name:13s}: {len(wk)} days, close vs NAV {min(v):+.1f} to {max(v):+.1f}bp, lowest percentile {min(pctile(x) for x in v)}")
print(f"{len(rows)} intervention and settlement days, {tail} in the bottom 5% (about {len(rows) / 20:.0f} by chance)")
write_csv('tlt_premium.csv', ['episode', 'date', 'window', 'close_vs_nav_bp', 'percentile_since_2022'], rows +
          [['all days', None, 'median', round(allv[len(allv) // 2], 1), 50], ['all days', None, 'p5', round(allv[len(allv) // 20], 1), 5],
           ['all days', None, 'p95', round(allv[len(allv) * 19 // 20], 1), 95]])

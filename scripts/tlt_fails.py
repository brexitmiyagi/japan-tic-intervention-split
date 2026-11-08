# fails to deliver in TLT around each intervention, from the SEC's twice-monthly files (2022 to mid-October 2026).
# if market makers were creating TLT shares and shorting them faster than they could deliver, the
# way an ETF short gets built in a hurry, fails would spike. a flat line around intervention days closes that.
# the SEC lists a security on a day only when there's a fail balance, so a missing day counts as zero.
# careful: fails are reported by settlement date, a day or two after the trade, so I look at the ten
# bond-market days from the first intervention day.
import os, csv, datetime as dt
from common import DATA, fred, write_csv

f = {dt.date.fromisoformat(r['settlement_date']): int(r['fails_shares']) for r in csv.DictReader(open(os.path.join(DATA, 'sec_ftd_tlt_2022_2026.csv')))}
so = {dt.date.fromisoformat(r['date']): float(r['shares_outstanding']) for r in csv.DictReader(open(os.path.join(DATA, 'ishares_tlt_history_2026-11-05.csv')))}
days = [d for d, _ in fred('DGS30') if dt.date(2022, 1, 3) <= d <= max(f)]
def share(d):
    s = so[max(x for x in so if x <= d)]
    return f.get(d, 0) / s * 100
allv = sorted(share(d) for d in days)
pct = lambda v: round(sum(x <= v for x in allv) / len(allv) * 100)
print(f"{len(days)} days, fails as % of shares outstanding: median {allv[len(allv) // 2]:.3f}%, 95th {allv[len(allv) * 19 // 20]:.3f}%, "
      f"99th {allv[len(allv) * 99 // 100]:.3f}%, max {allv[-1]:.2f}% on {max(days, key=share)}")
episodes = [('Sep 2022', dt.date(2022, 9, 22)), ('Oct 2022', dt.date(2022, 10, 21)), ('Apr-May 2024', dt.date(2024, 4, 29)),
            ('Jul 2024', dt.date(2024, 7, 11)), ('Apr-May 2026', dt.date(2026, 4, 30)), ('Jul 2026', dt.date(2026, 7, 30))]
rows, hi = [], 0
for name, s in episodes:
    w = [d for d in days if d >= s][:10]
    v = [share(d) for d in w]; top = max(v); pc = pct(top); hi += pc >= 95
    rows.append([name, w[0].isoformat(), w[-1].isoformat(), round(top, 3), pc, max(f.get(d, 0) for d in w)])
    print(f"  {name:13s}: biggest fail in the ten days {max(f.get(d, 0) for d in w):>9,} shares, {top:.3f}% of shares, percentile {pc}")
print(f"{hi} of 6 episodes with a ten-day peak at or above the 95th percentile of single days")
# the fair yardstick for a ten-day peak is other ten-day peaks, not single days
peaks = sorted(max(share(d) for d in days[i:i + 10]) for i in range(len(days) - 10))
for r in rows:
    r.append(round(sum(x <= r[3] for x in peaks) / len(peaks) * 100))
print('  ten-day peak percentile against every ten-day window: ' + ', '.join(f"{r[0]} {r[6]}" for r in rows))
write_csv('tlt_fails.csv', ['episode', 'from', 'to', 'peak_fail_pct_of_shares', 'pctile_vs_days', 'peak_fail_shares', 'pctile_vs_10day_windows'], rows)

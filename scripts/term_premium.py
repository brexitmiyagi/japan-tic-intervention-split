# how much extra the market is charging to hold long bonds, on two public models.
# ACM is the New York Fed's daily 10-year term premium; Kim-Wright is the Fed Board's, via FRED.
# they're built differently and don't agree on the level, so I quote both and only lean on the moves.
# neither covers 30 years. the 10-year term premium is the closest public measure for TLT's end of the curve.
import os, csv, datetime as dt
from common import DATA, write_csv

def load(fn, col):
    out = {}
    for r in csv.DictReader(open(os.path.join(DATA, fn))):
        k = [c for c in r if 'date' in c.lower()][0]
        if r[col] not in ('', '.'):
            out[dt.date.fromisoformat(r[k][:10])] = float(r[col])
    return out
rows = []
for name, s in [('ACM (NY Fed)', load('nyfed_acm_tp10_daily.csv', 'ACMTP10')), ('Kim-Wright (Fed Board)', load('fred_THREEFYTP10.csv', 'THREEFYTP10'))]:
    last = max(s); v = s[last]
    def at(d): return s[max(x for x in s if x <= d)]
    since = [x for d, x in s.items() if d >= dt.date(2007, 1, 1)]
    pct = round(sum(x <= v for x in since) / len(since) * 100)
    y26 = [x for d, x in s.items() if d.year == 2026]
    print(f"{name}: {v:.2f} on {last}; end-2025 {at(dt.date(2025, 12, 31)):.2f}; 2026 range {min(y26):.2f} to {max(y26):.2f}; "
          f"percentile since 2007 {pct}")
    rows.append([name, last.isoformat(), round(v, 2), round(at(dt.date(2025, 12, 31)), 2), round(min(y26), 2), round(max(y26), 2), pct])
write_csv('term_premium.csv', ['model', 'latest_date', 'tp10_pct', 'end_2025', 'min_2026', 'max_2026', 'pctile_since_2007'], rows)

# was the 2024 refill really absorbed, or did the Fed rally hide it?
# from end-May to end-September 2024 Japan's row sold $88.1bn of notes and bonds and the 30-year fell 51bp.
# but the Fed started cutting on 18 September 2024 (50bp, to 4-3/4 to 5 percent), and the 2-year fell
# much more. so I ask what the 30-year usually does, given the 2-year, over four months.
# every month-end to month-end four-month window since 1977 (FRED DGS2 and DGS30, full history; Treasury
# didn't publish a 30-year from 2002 to 2006, so those windows drop out). straight-line fit of the 30-year
# change on the 2-year change, then where 2024's residual sits. a second fit uses only windows where the
# 2-year fell at least 75bp, which is what easing cycles look like. the ACM 10-year term premium is the
# third read, since supply indigestion should show up there.
import os, csv, datetime as dt
from common import DATA, write_csv

def load(fn, col):
    out = {}
    for r in csv.DictReader(open(os.path.join(DATA, fn))):
        if r[col] not in ('', '.'):
            out[dt.date.fromisoformat(r['observation_date'])] = float(r[col])
    return out
y2, y30 = load('fred_DGS2_full.csv', 'DGS2'), load('fred_DGS30_full.csv', 'DGS30')
acm = {dt.date.fromisoformat(r['DATE']): float(r['ACMTP10']) for r in csv.DictReader(open(os.path.join(DATA, 'nyfed_acm_tp10_daily.csv')))}
def month_ends(s):
    m = {}
    for d in sorted(s):
        m[(d.year, d.month)] = d
    return m
me2, me30 = month_ends(y2), month_ends(y30)
keys = sorted(set(me2) & set(me30))
W = []
for i, k in enumerate(keys):
    j = i + 4
    if j >= len(keys):
        break
    k2 = keys[j]
    if (k2[0] * 12 + k2[1]) - (k[0] * 12 + k[1]) != 4:
        continue   # skips the 2002-2006 gap
    a, b = me30[k], me30[k2]
    W.append((k, k2, (y2[me2[k2]] - y2[me2[k]]) * 100, (y30[b] - y30[a]) * 100))
def fit(ws):
    n = len(ws); mx = sum(w[2] for w in ws) / n; my = sum(w[3] for w in ws) / n
    b = sum((w[2] - mx) * (w[3] - my) for w in ws) / sum((w[2] - mx) ** 2 for w in ws)
    return my - b * mx, b
tgt = [w for w in W if w[0] == (2024, 5)][0]
print(f"end-May to end-Sep 2024: 2-year {tgt[2]:+.0f}bp, 30-year {tgt[3]:+.0f}bp, 2s30s {tgt[3] - tgt[2]:+.0f}bp")
rows = []
for name, ws in [('all four-month windows since 1977', [w for w in W if w is not tgt]),
                 ('windows where the 2-year fell 75bp or more', [w for w in W if w[2] <= -75 and w is not tgt])]:
    a, b = fit(ws)
    pred = a + b * tgt[2]; res = tgt[3] - pred
    rs = sorted(w[3] - (a + b * w[2]) for w in ws)
    pc = round(sum(x <= res for x in rs) / len(rs) * 100)
    print(f"  {name} (n={len(ws)}): 30y = {a:+.1f} + {b:.2f} x 2y; predicted {pred:+.0f}bp, actual {tgt[3]:+.0f}bp, "
          f"30-year {res:+.0f}bp worse than usual, residual percentile {pc}")
    rows.append([name, len(ws), round(b, 2), round(pred), round(tgt[3]), round(res), pc])
def at(s, d):
    return s[max(x for x in s if x <= d)]
tp = (at(acm, dt.date(2024, 9, 30)) - at(acm, dt.date(2024, 5, 31))) * 100
ad = sorted(acm); tps = []
for k, k2, *_ in W:
    if k[0] < 2000:
        continue
    da, db = dt.date(k[0], k[1], 28), dt.date(k2[0], k2[1], 28)
    tps.append((at(acm, db) - at(acm, da)) * 100)
pc_tp = round(sum(x <= tp for x in tps) / len(tps) * 100)
print(f"ACM 10-year term premium, end-May to end-Sep 2024: {tp:+.0f}bp, percentile {pc_tp} of four-month changes since 2000")
rows.append(['ACM term premium change', len(tps), None, None, round(tp), None, pc_tp])
write_csv('refill_2024_control.csv', ['test', 'n', 'beta', 'predicted_30y_bp', 'actual_30y_bp', 'residual_bp', 'percentile'], rows)

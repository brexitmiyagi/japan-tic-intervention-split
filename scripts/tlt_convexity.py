# TLT's convexity, from the fund's own holdings on 4 Nov 2026.
# iShares publishes effective duration (14.90) but not convexity on the page I used, so I rebuild it:
# every bond in the fund is repriced from its own yield, with each yield moved up and down the same
# amount, and the fund's value is the market-value-weighted sum. cash is left at its value.
# the check that this is the same fund: the duration it gives should land close to iShares' 14.90.
# careful: a parallel shift in every yield is the simplest case. the long end rarely moves exactly
# in parallel, and this ignores the fund's turnover over a year.
import os, csv, datetime as dt
from common import DATA, write_csv

SETTLE = dt.date(2026, 11, 5)
def add_months(d, m):
    y, mo = divmod(d.month - 1 + m, 12)
    return dt.date(d.year + y, mo + 1, 15)

def dirty(cpn, mat, y):
    # cash flows every six months back from maturity, discounted at y/2 per half-year
    dates, d = [], mat
    while d > SETTLE:
        dates.append(d); d = add_months(d, -6)
    prev = d; nxt = dates[-1]
    frac = (nxt - SETTLE).days / (nxt - prev).days
    v = 0.0
    for k, cd in enumerate(sorted(dates)):
        cf = cpn / 2 + (100 if cd == mat else 0)
        v += cf / (1 + y / 200) ** (frac + k)
    return v

bonds, cash = [], 0.0
for r in csv.DictReader(open(os.path.join(DATA, 'tlt_holdings_2026-11-04.csv'))):
    mv = float(r['market_value_usd_k'])
    if not r['maturity']:
        cash += mv; continue
    bonds.append((mv, float(r['coupon_pct']), dt.date.fromisoformat(r['maturity']), float(r['ytm_pct'])))
total = sum(b[0] for b in bonds) + cash

def fund_change(bp):
    # % change in the fund's value if every bond yield moves by bp
    v = cash
    for mv, c, m, y in bonds:
        v += mv * dirty(c, m, y + bp / 100) / dirty(c, m, y)
    return (v / total - 1) * 100

h = 1  # 1bp for the derivatives
up, dn = fund_change(h), fund_change(-h)
dur = (dn - up) / (2 * h / 100)
conv_y2 = (up + dn) / 100 / (h / 10000) ** 2   # years squared: dP/P = -D dy + C dy^2 / 2, dy in decimals
print(f"{len(bonds)} bonds, cash {cash / total * 100:.2f}% of the fund")
print(f"duration from the holdings: {dur:.2f} years (iShares effective duration 14.90)")
print(f"convexity: {conv_y2:.0f} (years squared)")
# why 15.10 and not 14.90: iShares' own holdings file carries two measures for every bond. weighted by
# market value, its duration column is the fund's 14.90 effective duration and its modified duration
# column is 15.10, the same as this rebuild. effective duration comes from iShares' curve model, modified
# duration from each bond's own yield, and for these bonds the first runs about 0.2 years lower.
ish = list(csv.DictReader(open(os.path.join(DATA, 'tlt_holdings_2026-11-04.csv'))))
mvt = sum(float(r['market_value_usd_k']) for r in ish)
eff = sum(float(r['market_value_usd_k']) * float(r['ishares_duration']) for r in ish) / mvt
mod = sum(float(r['market_value_usd_k']) * float(r['ishares_mod_duration']) for r in ish) / mvt
print(f"iShares' own columns, market-value weighted: duration {eff:.2f}, modified duration {mod:.2f}")
rows = []
for bp in (-150, -100, -50, 50, 100, 150):
    full = fund_change(bp); lin = -dur * bp / 100
    rows.append([bp, round(lin, 2), round(full, 2), round(full - lin, 2)])
    print(f"  {bp:+4d}bp: duration only {lin:+6.2f}%, with convexity {full:+6.2f}%, convexity adds {full - lin:+.2f} points")
write_csv('tlt_convexity.csv', ['shift_bp', 'duration_only_pct', 'full_reprice_pct', 'convexity_adds_pts'], rows +
          [['duration_years', None, round(dur, 2), None], ['convexity_years_sq', None, round(conv_y2, 1), None],
           ['ishares_effective_duration_weighted', None, round(eff, 2), None], ['ishares_modified_duration_weighted', None, round(mod, 2), None]])

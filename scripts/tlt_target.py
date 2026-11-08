# the 12-month target for TLT, and why it's a hold.
# I'm not forecasting long yields, and nothing in this research gives me a reason to. so the target
# sits on the market's own path, the forward curve. if yields follow the forwards, every Treasury
# earns about the 1-year rate over the year (that's what forward rates mean), so TLT's total return
# is the 1-year yield less its fee. TLT pays out its income, so the price return is the total return
# less the income, and I use the 30-day SEC yield for the income. the second case keeps the curve
# where it is: TLT earns its yield to maturity less the fee, and roll-down adds little because the
# 20-to-30-year part of the curve is close to flat.
# the rule is the same as in my other pieces: a target within 15% of the price is a hold.
# the income is the 30-day SEC yield (5.28%), which is what the fund's bonds are earning now. the
# trailing 12-month yield (4.78%) is what it paid out over the last year from bonds bought at lower
# yields, so it understates next year's income. the YTM (5.33%) is the same idea as the SEC yield
# before costs.
# the yield moves use convexity from tlt_convexity.py (321, years squared), so a rally adds more than
# a selloff of the same size takes away.
# careful: this treats par yields as if they were zero-coupon yields, and ignores the fund's own
# turnover. both small next to a 15% band.
import os, csv, math
from common import DATA, RESULTS, write_csv

tlt = {r['item']: float(r['value']) for r in csv.DictReader(open(os.path.join(DATA, 'tlt_2026-11-04.csv')))}
curve = {}
for r in csv.DictReader(open(os.path.join(DATA, 'treasury_par_curve_2026-11.csv'))):
    if r['Date'] == '11/04/2026':
        curve = {k: float(v) for k, v in r.items() if k != 'Date' and v}
P, D = tlt['close_usd'], tlt['effective_duration_years']
y1, y20, y30 = curve['1 Yr'], curve['20 Yr'], curve['30 Yr']
fee, inc, ytm = tlt['expense_ratio_pct'], tlt['sec_yield_30d_pct'], tlt['avg_yield_to_maturity_pct']
assert tlt['close_usd'] == tlt['close_usd_second_source']
print(f"TLT {P} on 4 Nov 2026 (SA and iShares agree); duration {D}; YTM {ytm}%; SEC yield {inc}%; fee {fee}%")
print(f"Treasury par curve 4 Nov: 1y {y1}%, 20y {y20}%, 30y {y30}% (20s30s {100 * (y30 - y20):+.0f}bp)")
rows = []
for name, total in [('forward curve', y1 - fee), ('unchanged curve', ytm - fee)]:
    price_ret = total - inc
    rows.append([name, round(total, 2), inc, round(price_ret, 2), round(P * (1 + price_ret / 100), 2)])
    print(f"{name:16s}: total return {total:.2f}%, income {inc}%, price {price_ret:+.2f}% -> ${P * (1 + price_ret / 100):.2f}")
target = round(rows[0][4])
lo, hi = target / 1.15, target / 0.85
C = float([r for r in csv.DictReader(open(os.path.join(RESULTS, 'tlt_convexity.csv'))) if r['shift_bp'] == 'convexity_years_sq'][0]['full_reprice_pct'])
def move(dy_bp):
    dy = dy_bp / 10000
    return 1 - D * dy + C * dy * dy / 2
def bp_for(ratio):
    # solve 1 - D dy + C dy^2 / 2 = ratio for the root nearest zero
    a, b, c = C / 2, -D, 1 - ratio
    r1 = (-b - math.sqrt(b * b - 4 * a * c)) / (2 * a)
    r2 = (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a)
    return min((r1, r2), key=abs) * 10000
print(f"target ${target} ({(target / P - 1) * 100:+.1f}% vs price): HOLD while TLT is between ${lo:.2f} and ${hi:.2f}")
print(f"  the band in long yields, duration {D} and convexity {C:.0f}: about {bp_for(lo / P):+.0f}bp to a Buy, {bp_for(hi / P):+.0f}bp to a Sell")
print(f"  (duration alone would say {(1 - lo / P) * 100 / D * 100:+.0f}bp and {-(hi / P - 1) * 100 / D * 100:+.0f}bp)")
print(f"each 10bp on long yields is about {D * 0.1:.2f}% on TLT")
for dy in (-100, -50, 50, 100):
    print(f"  long yields {dy:+d}bp over the year: price about ${P * move(dy) * (1 + (ytm - fee - inc) / 100):.2f}"
          f" (duration alone ${P * (1 - D * dy / 10000) * (1 + (ytm - fee - inc) / 100):.2f})")
write_csv('tlt_target.csv', ['case', 'total_return_pct', 'income_pct', 'price_return_pct', 'price_in_12m_usd'], rows +
          [['target', None, None, round((target / P - 1) * 100, 2), target], ['buy_below', None, None, None, round(lo, 2)], ['sell_above', None, None, None, round(hi, 2)]])

# the old scenario weights are gone. tlt_band_history.py asks history how often the band breaks instead.

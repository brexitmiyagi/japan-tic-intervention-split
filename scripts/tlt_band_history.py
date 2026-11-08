# how often would history have flipped the rating? every 12-month change in the 30-year since FRED's series
# starts (February 1977), run through TLT's numbers today: price $81.76, duration 14.90, convexity 321
# (tlt_convexity.py) and a year of carry. each move gives a TLT price a year out, which lands in the Buy
# zone (below $70.43), the Hold band, or the Sell zone (above $95.29). I also count how often it lands in the
# tighter band I score on my ledger, $72.90 to $89.10.
# careful: windows overlap, so they aren't independent draws; today's duration, convexity and carry are
# applied to every year, which flatters the 1980s; and Treasury published no 30-year from 2002 to 2006, so
# those windows drop out.
import os, csv, datetime as dt, bisect
from common import DATA, RESULTS, write_csv

y = {}
for r in csv.DictReader(open(os.path.join(DATA, 'fred_DGS30_full.csv'))):
    if r['DGS30'] not in ('', '.'):
        y[dt.date.fromisoformat(r['observation_date'])] = float(r['DGS30'])
tlt = {r['item']: float(r['value']) for r in csv.DictReader(open(os.path.join(DATA, 'tlt_2026-11-04.csv')))}
P, D = tlt['close_usd'], tlt['effective_duration_years']
carry = (tlt['avg_yield_to_maturity_pct'] - tlt['expense_ratio_pct'] - tlt['sec_yield_30d_pct']) / 100
C = float([r for r in csv.DictReader(open(os.path.join(RESULTS, 'tlt_convexity.csv'))) if r['shift_bp'] == 'convexity_years_sq'][0]['full_reprice_pct'])
def price(bp):
    dy = bp / 10000
    return P * (1 - D * dy + C * dy * dy / 2) * (1 + carry)
buy, sell, lo10, hi10 = 81 / 1.15, 81 / 0.85, 81 * 0.9, 81 * 1.1
days = sorted(y)
moves = []
for d in days:
    e = dt.date(d.year + 1, d.month, min(d.day, 28)) if d.month == 2 and d.day == 29 else dt.date(d.year + 1, d.month, d.day)
    i = bisect.bisect_right(days, e) - 1
    if i < 0 or days[i] <= d or (e - days[i]).days > 7:
        continue          # no observation within a week of the end date (the 2002-2006 gap)
    moves.append((d, (y[days[i]] - y[d]) * 100))
rows = []
for name, start in [('since 1977', dt.date(1977, 1, 1)), ('since 2000', dt.date(2000, 1, 1)), ('since 2010', dt.date(2010, 1, 1))]:
    m = [bp for d, bp in moves if d >= start]
    px = [price(bp) for bp in m]; n = len(px)
    b = sum(p < buy for p in px) / n * 100; s = sum(p > sell for p in px) / n * 100; h = 100 - b - s
    led = sum(lo10 <= p <= hi10 for p in px) / n * 100
    big = sum(abs(bp) > 100 for bp in m) / n * 100
    avg = sum(px) / n
    print(f"{name:10s} ({n} windows): Buy {b:4.1f}%, Hold {h:4.1f}%, Sell {s:4.1f}%; ledger band {led:4.1f}%; "
          f"30-year moved more than 100bp {big:4.1f}%; average TLT price ${avg:.2f}")
    rows.append([name, n, round(b, 1), round(h, 1), round(s, 1), round(led, 1), round(big, 1), round(avg, 2)])
write_csv('tlt_band_history.csv', ['sample', 'windows', 'buy_pct', 'hold_pct', 'sell_pct', 'ledger_band_pct', 'moved_over_100bp_pct', 'avg_price'], rows)

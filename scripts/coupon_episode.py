# the one time Japan paid for a defense with notes and bonds: July 2024.
# since February 2023 TIC long-term flows are reported trades, so I can tell bill-funded and coupon-funded
# defenses apart for the four episodes since 2024. in the settlement month, July 2024 is the one where the
# Japan row sold more notes and bonds ($10.9bn) than it ran down bills ($3.0bn), and it kept selling coupons
# in August ($22.3bn). the 2022 episodes come from before that switch, so they stay unclassified.
# this script pulls every check for July 2024 and sets it against the three bill-funded episodes.
# confounds to keep in view: the June CPI release came out on 11 July 2024, the day MOF stepped in, and the
# carry-trade unwind hit on 5 August 2024, three days before the August 30-year auction.
import os, csv
from common import RESULTS, tic_table3, write_csv

t = tic_table3()['Japan']
eps = {'Apr-May 2024': '2024-05', 'Jul 2024': '2024-07', 'Apr-May 2026': '2026-05', 'Jul 2026': '2026-08'}
kind = {}
for e, m in eps.items():
    st, lt = t[m]['st_net'], t[m]['lt_net']
    kind[e] = 'coupons' if lt < 0 and -lt > -st else 'bills'
    print(f"{e:13s} settlement month {m}: bills {st:+.1f}bn, notes and bonds {lt:+.1f}bn -> {kind[e]}")
assert [e for e in kind if kind[e] == 'coupons'] == ['Jul 2024']
at = list(csv.DictReader(open(os.path.join(RESULTS, 'auction_test.csv'))))
rows = []
print('\nlong-bond auctions during each window (indirect percentile / dealer percentile):')
for e in eps:
    a = [r for r in at if r['episode'] == e and r['window'] == 'during']
    s = ', '.join(f"{r['auction_date']} {r['tenor']} {r['indirect_percentile']}/{r['dealer_percentile']}" for r in a)
    print(f"  {e:13s} ({kind[e]}): {s}")
    for r in a:
        rows.append([e, kind[e], 'auction', r['auction_date'] + ' ' + r['tenor'], r['indirect_percentile'], r['dealer_percentile']])
d30 = [r for r in at if r['window'] == 'during' and r['tenor'] == '30y']
lo = min(d30, key=lambda r: int(r['indirect_percentile'])); hi = max(d30, key=lambda r: int(r['dealer_percentile']))
print(f"weakest 30-year indirect share in any defense window: {lo['auction_date']} ({lo['episode']}), percentile {lo['indirect_percentile']}")
print(f"highest 30-year dealer share in any defense window:  {hi['auction_date']} ({hi['episode']}), percentile {hi['dealer_percentile']}")
es = [r for r in csv.DictReader(open(os.path.join(RESULTS, 'event_study.csv'))) if r['measure'] == '30-year Treasury (bp)' and r['episode'] in eps]
seen = set()
print('\n30-year yield (bp, percentile vs normal windows):')
for r in es:
    k = (r['episode'], r['window'])
    if k in seen:
        continue
    seen.add(k)
    print(f"  {r['episode']:13s} {r['window']:10s} {float(r['change']):+.0f}bp, percentile {r['percentile_vs_normal']}")
    rows.append([r['episode'], kind[r['episode']], '30y ' + r['window'], r['change'], r['percentile_vs_normal'], None])
pr = [r for r in csv.DictReader(open(os.path.join(RESULTS, 'tlt_premium.csv'))) if r['episode'] in eps]
fa = {r['episode']: r for r in csv.DictReader(open(os.path.join(RESULTS, 'tlt_fails.csv')))}
print('\nTLT plumbing (lowest close vs NAV, bp and percentile; fails ten-day peak percentile):')
for e in eps:
    v = [r for r in pr if r['episode'] == e]; m = min(v, key=lambda r: float(r['close_vs_nav_bp']))
    print(f"  {e:13s}: {float(m['close_vs_nav_bp']):+.1f}bp (pct {m['percentile_since_2022']}), fails {fa[e]['pctile_vs_10day_windows']}")
    rows.append([e, kind[e], 'plumbing', m['close_vs_nav_bp'], m['percentile_since_2022'], fa[e]['pctile_vs_10day_windows']])
write_csv('coupon_episode.csv', ['episode', 'funded_by', 'check', 'value', 'percentile', 'second_percentile'], rows)

# is "weakest of any defense window" more than luck? 13 auctions sit inside defense windows. if each one's
# percentile were a random draw, the chance that at least one lands at or below the 12th percentile is
# 1 - 0.88^13, and at least one at or above the 98th for dealers is 1 - 0.98^13.
n_win = len(set((r['auction_date'], r['tenor']) for r in at if r['window'] == 'during'))
p_low = 1 - (1 - int(lo['indirect_percentile']) / 100) ** n_win
p_hi = 1 - (int(hi['dealer_percentile']) / 100) ** n_win
print(f"\nby chance alone, across {n_win} defense-window auctions: at least one indirect reading this low {p_low:.0%}, "
      f"at least one dealer reading this high {p_hi:.0%}")
# and who sold: the Japan row mixes MOF with private investors. treasury_share.py bounds MOF's own part.
tb = {r['settlement_month']: r for r in csv.DictReader(open(os.path.join(RESULTS, 'treasury_share_bounds.csv')))}
b = tb['2024-07']
print(f"July 2024: MOF sold ${float(b['mof_securities_sold_bn']):.1f}bn of securities; the Japan row's Treasury sales were "
      f"${float(b['japan_row_treasuries_sold_bn']):.1f}bn, of which MOF's own share is ${float(b['mof_treasury_sales_low_bn']):.1f}bn to "
      f"${float(b['mof_treasury_sales_high_bn']):.1f}bn ({b['share_low_pct']}% to {b['share_high_pct']}% of what MOF sold)")
write_csv('coupon_episode_odds.csv', ['item', 'value'], [['window_auctions', n_win], ['p_indirect_this_low', round(p_low, 2)],
          ['p_dealer_this_high', round(p_hi, 2)], ['mof_tsy_low_bn', b['mof_treasury_sales_low_bn']], ['mof_tsy_high_bn', b['mof_treasury_sales_high_bn']],
          ['share_low_pct', b['share_low_pct']], ['share_high_pct', b['share_high_pct']], ['mof_securities_sold_bn', b['mof_securities_sold_bn']]])

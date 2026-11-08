# MOF's foreign securities fell another $17.9bn in September 2026, with MOF out of the market since
# 27 August. was that selling or price? Japan's September BoP isn't out yet (last year's came on
# 11 November), so this is a price estimate to hold until it is.
#
# the estimate: MOF's maturity mix from its annual FX fund breakdown (31 March 2025: 30.5% within a
# year, 37.7% one to five years, 31.8% over five), a duration range for each bucket, and the
# September change in Treasury yields (4-week bill, 2-year, 10-year). then a euro piece: MOF
# publishes no currency split, so I let anywhere from 0% to 20% of the securities be in euros and
# mark them by EUR/USD. the 20% is my assumption, not a number MOF gives.
# careful: Treasury yields stand in for every currency's yields, the maturity mix is 18 months old,
# and the durations are ranges I chose. it says whether price can plausibly explain the fall, not
# that it does. the BoP will.
import os, csv
from common import RESULTS, fred, on_or_before, mof_reserves, write_csv

res = mof_reserves()
sec_aug, sec_sep = res['2026-08']['securities_musd'], res['2026-09']['securities_musd']
fall = sec_sep - sec_aug
fe = {r['item']: float(r['value']) for r in csv.DictReader(open(os.path.join(RESULTS, 'fefsa_composition.csv')))}
w = [fe['maturity_up_to_1y_share'], fe['maturity_1_to_5y_share'], fe['maturity_over_5y_share']]

def chg(series):
    r = fred(series)
    return on_or_before(r, '2026-09-30')[1] - on_or_before(r, '2026-08-31')[1]
dy = [chg('DTB4WK') / 100, chg('DGS2') / 100, chg('DGS10') / 100]
eur = fred('DEXUSEU'); eur_chg = on_or_before(eur, '2026-09-30')[1] / on_or_before(eur, '2026-08-31')[1] - 1
print(f"MOF securities end-Aug {sec_aug:.1f}bn, end-Sep {sec_sep:.1f}bn, change {fall:+.1f}bn")
print(f"September yield changes: 4-week bill {dy[0] * 1e4:+.0f}bp, 2-year {dy[1] * 1e4:+.0f}bp, 10-year {dy[2] * 1e4:+.0f}bp; EUR/USD {eur_chg * 100:+.1f}%")

durations = {'low': [0.25, 2.0, 6.0], 'high': [0.75, 3.5, 10.0]}
rows = []
for case, d in durations.items():
    rate = -sum(wi * di * yi for wi, di, yi in zip(w, d, dy))
    for share in (0.0, 0.20):
        price = rate * sec_aug + eur_chg * share * sec_aug
        rows.append([case, share, round(rate * 100, 2), round(price, 1)])
        print(f"durations {case} {d}, euro share {share:.0%}: price and FX {price:+.1f}bn")
lo, hi = min(r[3] for r in rows), max(r[3] for r in rows)
print(f"price and FX range {lo:+.1f}bn to {hi:+.1f}bn against an actual fall of {fall:+.1f}bn; "
      f"interest adds about +{fe['interest_usd_bn_per_month']:.1f}bn a month the other way")
print('inside the range' if lo <= fall <= hi else 'outside the range')
write_csv('sept_securities.csv', ['duration_case', 'euro_share', 'treasury_price_change_pct', 'price_and_fx_bn'],
          rows + [['actual', None, None, round(fall, 1)]])

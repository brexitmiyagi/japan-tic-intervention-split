# lines up each MOF intervention with the month it settles in, then asks three sources what
# happened that month: MOF's own reserve report, the TIC row for Japan, and TIC for all
# foreign official holders. dollar sales settle T+2, so the 30 April trade lands in May and
# the 30/31 July trades land in August. MOF's end-April and end-July reserves confirm it:
# neither moved.
import csv, os
from common import DATA, tic_table3, fred, on_or_before, mof_reserves, mof_interventions, write_csv

usdjpy = fred('DEXJPUS')
t = tic_table3()
jp, off = t['Japan'], t['Of Which: Foreign Official']
res = mof_reserves()

# Q2 2026 has a daily breakdown, so convert day by day at the noon NY rate (FRED DEXJPUS)
q2 = list(csv.DictReader(open(os.path.join(DATA, 'mof_intervention_days_2026q2.csv'))))
q2_usd = sum(float(r['yen_bn']) / on_or_before(usdjpy, r['trade_date'])[1] for r in q2)
# Q3's daily split is not published yet. MOF says 30 July to 26 August. bracket it with the
# 30 and 31 July rates.
q3_yen = 15399.3
q3_lo, q3_hi = q3_yen / on_or_before(usdjpy, '2026-07-30')[1], q3_yen / on_or_before(usdjpy, '2026-07-31')[1]
q3_usd = (q3_lo + q3_hi) / 2

def prev_month(m):
    y, mm = int(m[:4]), int(m[5:])
    return f"{y-1}-12" if mm == 1 else f"{y}-{mm-1:02d}"

rows = []
raw = []
for m, usd, yen in [('2026-05', q2_usd, 11734.9), ('2026-08', q3_usd, q3_yen)]:
    p = prev_month(m)
    fx = res[m]['foreign_currency_reserves_musd'] - res[p]['foreign_currency_reserves_musd']
    sec = res[m]['securities_musd'] - res[p]['securities_musd']
    dep = res[m]['deposits_musd'] - res[p]['deposits_musd']
    j = jp[m]; o = off[m]
    raw.append((usd, fx, sec, j['st_net'], j['lt_net'], j['net']))
    rows.append([m, yen, round(usd, 1), round(fx, 1), round(sec, 1), round(dep, 1),
                 round(j['st_net'], 1), round(j['lt_net'], 1), round(j['net'], 1),
                 round(o['st_net'], 1), round(o['lt_net'], 1)])
    print(f"{m}: intervention Y{yen:,.1f}bn = ${usd:,.1f}bn | MOF FX reserves {fx:,.1f} (securities {sec:,.1f}, deposits {dep:,.1f})")
    print(f"        TIC Japan: bills {j['st_net']:,.1f}, bonds {j['lt_net']:,.1f}, total {j['net']:,.1f} | "
          f"TIC all foreign official: bills {o['st_net']:,.1f}, bonds {o['lt_net']:,.1f}")

print(f"\nQ3 conversion range ${q3_lo:,.1f}bn to ${q3_hi:,.1f}bn")
tot_usd, tot_fx, tot_sec, tot_bills, tot_bonds, tot_net = [sum(x[i] for x in raw) for i in range(6)]
print(f"both windows: yen bought for about ${tot_usd:,.1f}bn | MOF FX reserves {tot_fx:,.1f} | MOF securities {tot_sec:,.1f}")
print(f"  TIC Japan bills {tot_bills:,.1f} | bonds {tot_bonds:+,.1f} | total net {tot_net:,.1f}")
print(f"  bills as a share of the dollars raised: {-tot_bills/tot_usd:.0%}")
print(f"  MOF securities fall that the Japan TIC row does not show: {tot_sec - tot_net:,.1f}bn")
print(f"  total yen spent: Y{11734.9+q3_yen:,.1f}bn")

write_csv('intervention_windows.csv',
          ['settle_month', 'yen_bn', 'usd_bn_est', 'mof_fx_reserves_chg', 'mof_securities_chg', 'mof_deposits_chg',
           'tic_japan_bills', 'tic_japan_bonds', 'tic_japan_total', 'tic_official_bills', 'tic_official_bonds'], rows)

# what was left after August
a = res['2026-09']
print(f"\nend-Sep MOF: securities ${a['securities_musd']:,.1f}bn, deposits ${a['deposits_musd']:,.1f}bn; "
      f"TIC Japan bills end-Aug ${jp['2026-08']['st_pos']:.1f}bn")
print(f"USDJPY: before Apr action {on_or_before(usdjpy,'2026-04-29')[1]}, before Jul action {on_or_before(usdjpy,'2026-07-29')[1]}, latest {usdjpy[-1][0]} {usdjpy[-1][1]}")

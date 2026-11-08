# the yen side of the trade. MOF's foreign exchange fund (FEFSA) carries its dollars at old
# exchange rates, so selling them at 157-159 books a gain in yen even if the bonds are under
# water in dollars. JRI puts the fund's break-even near 115 yen, from FEFSA's own accounts.
# that break-even is their estimate, not an MOF number, and it averages the whole portfolio.
# the cost basis of dollars rolled into bills is not public and the last audited balance sheet
# is 31 March 2025, so I run a range around it and treat the answer as a model.
import csv, os
from common import DATA, write_csv

fe = {r['item']: float(r['value']) for r in csv.DictReader(open(os.path.join(DATA, 'fefsa.csv')))}
print(f"FEFSA at 31 Mar 2025: net assets Y{fe['FEFSA assets less liabilities at 31 Mar 2025']/1e6:.2f}tn, "
      f"of which FX translation gain Y{fe['FEFSA cumulative FX translation gain at 31 Mar 2025']/1e6:.2f}tn")

ops = [('Apr-May 2026', 11734.9, 74.9), ('Jul-Aug 2026', 15399.3, 96.7)]   # yen bn, $bn from intervention_match.py
rows = []
for be in (110, 115, 120):
    total = 0
    for label, yen, usd in ops:
        rate = yen / usd
        gain = usd * (rate - be)          # yen bn
        total += gain
        if be == 115:
            print(f"{label}: Y{yen:,.1f}bn for ${usd}bn = {rate:.1f} yen per dollar; gain at {be} break-even Y{gain/1000:.2f}tn")
    rows.append([be, round(total / 1000, 2)])
    print(f"break-even {be}: realized gain on both operations Y{total/1000:.2f}tn")
write_csv('yen_gains.csv', ['breakeven_usdjpy', 'realized_gain_yen_tn'], rows)

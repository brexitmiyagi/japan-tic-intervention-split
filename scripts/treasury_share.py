# the Treasury share: of what MOF actually sold in an intervention's settlement month, how much
# shows up as Treasuries sold in TIC's Japan row. the usual reading assumes 100%.
#   Treasury share = Japan-row Treasury net sales (bills + notes and bonds) / MOF securities sold
# "MOF securities sold" is the BoP reserve-asset outflow less the change in deposits, so it's a
# transaction, the same basis as the rest of the work. price moves don't get in.
# I also print the version on the reserves report's stock fall, which is the number people
# actually read. the two differ by price: July 2024 is 43% on transactions and 81% on the stock.
# timing: MOF's reserves come out early in the month after settlement, so the denominator is known
# then. the numerator needs TIC, about six weeks after month-end. so each reading lands with the TIC.
# the Japan row includes private investors, so a big private flow in the same month moves it.
import os, csv
from common import RESULTS, write_csv

ig = list(csv.DictReader(open(os.path.join(RESULTS, 'intervention_gaps.csv'))))
rows = []
for r in ig:
    drop = -float(r['mof_securities_stock_chg']); sold = -float(r['mof_securities_sold_tx']); tsy = -float(r['japan_treasuries_net'])
    rows.append([r['month'], round(sold, 1), round(drop, 1), round(tsy, 1), round(tsy / sold * 100), round(tsy / drop * 100)])
    print(f"{r['month']}: Treasury share {tsy / sold * 100:.0f}% of what MOF sold ({sold:.1f}bn); "
          f"{tsy / drop * 100:.0f}% of the stock fall in the reserves report ({drop:.1f}bn)")
since = [x for x in rows if x[0] >= '2024']
print(f"since 2024: {min(x[4] for x in since)}% to {max(x[4] for x in since)}% of what MOF sold, so the reading "
      f"that treats it all as Treasuries was {100 - max(x[4] for x in since)} to {100 - min(x[4] for x in since)} points too high; "
      f"on the stock fall {min(x[5] for x in since)}% to {max(x[5] for x in since)}%")
print(f"under 100% in {sum(x[4] < 100 for x in rows)} of {len(rows)} months on transactions")
write_csv('treasury_share.csv', ['settlement_month', 'mof_securities_sold_bn', 'mof_securities_stock_fall_bn', 'tic_japan_treasuries_sold_bn',
                                 'treasury_share_pct', 'treasury_share_of_stock_fall_pct'], rows)

# bounds. the Japan row mixes MOF with private Japanese investors. MOF's survey gives private
# Japanese net flows into all foreign debt but not how much of it was Treasuries. so, as in the
# strict count, assume private flows went anywhere from none to all into Treasuries. that gives a
# low and a high for MOF's own Treasury selling, and for the share. it doesn't cover a private swap
# (private buying Treasuries while selling other foreign bonds), which would push the share higher.
# this is a diagnostic, after the fact. it moves too much month to month to use as a multiplier.
brows = []
print('\nMOF-only Treasury share, bounded by private Japanese flows:')
for r in ig:
    sold = -float(r['mof_securities_sold_tx']); T = float(r['japan_treasuries_net']); P = float(r['private_foreign_debt_net'])
    lo_sales, hi_sales = sorted([-T, -(T - P)])
    lo, hi = round(lo_sales / sold * 100), round(hi_sales / sold * 100)
    brows.append([r['month'], round(sold, 1), round(-T, 1), round(P, 1), round(lo_sales, 1), round(hi_sales, 1), lo, hi])
    print(f"{r['month']}: MOF Treasury sales {lo_sales:.1f} to {hi_sales:.1f} of {sold:.1f} sold, share {lo}% to {hi}%")
below = [b for b in brows if b[7] < 100]
print(f"under 100% even at the high bound in {len(below)} of {len(brows)} months ({', '.join(b[0] for b in below)})")
write_csv('treasury_share_bounds.csv', ['settlement_month', 'mof_securities_sold_bn', 'japan_row_treasuries_sold_bn',
          'private_japanese_foreign_debt_net_bn', 'mof_treasury_sales_low_bn', 'mof_treasury_sales_high_bn',
          'share_low_pct', 'share_high_pct'], brows)

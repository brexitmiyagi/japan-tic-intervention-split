# the reading everyone uses: MOF's foreign securities fell by X, so Japan sold X of Treasuries.
# this puts that reading next to what TIC's Japan row actually shows for Treasuries, for every
# intervention month since 2022, and splits the difference into price (from the BoP) and the rest.
#
# careful: the Japan row is every Japanese resident, so private flows can push it either way.
# the 2022 TIC flows were estimates, not reported trades.
import os, csv
from common import RESULTS, write_csv

ig = list(csv.DictReader(open(os.path.join(RESULTS, 'intervention_gaps.csv'))))
rows = []
for r in ig:
    m = r['month']
    headline = -float(r['mof_securities_stock_chg'])          # what the reserves report shows, as a sale
    price = -float(r['implied_valuation'])                    # positive = price loss inside the drop
    sold = -float(r['mof_securities_sold_tx'])                # what MOF actually sold
    tic = -float(r['japan_treasuries_net'])                   # Treasuries the Japan row sold
    over = (headline - tic) / headline * 100
    share = tic / headline * 100
    rows.append([m, round(headline, 1), round(price, 1), round(sold, 1), round(tic, 1), round(share), round(over)])
    print(f"{m}: headline reading {headline:.1f} of Treasury sales; price inside it {price:+.1f}; MOF actually sold {sold:.1f}; "
          f"TIC Japan-row Treasuries sold {tic:.1f}; Treasuries were {share:.0f}% of the headline, so {over:.0f} points of the headline weren't Treasuries")

since24 = [r for r in rows if r[0] >= '2024']
lo, hi = min(r[6] for r in since24), max(r[6] for r in since24)
slo, shi = min(r[5] for r in since24), max(r[5] for r in since24)
print(f"\nsince 2024 the headline reading overstated Japan's Treasury selling in all {len(since24)} intervention months, by {lo} to {hi} points of the headline; "
      f"Treasuries were {slo}% to {shi}% of the reserves drop")
write_csv('headline_vs_actual.csv', ['month', 'headline_treasury_sales_bn', 'price_loss_inside_bn', 'mof_actually_sold_bn',
                                     'tic_japan_treasuries_sold_bn', 'treasuries_pct_of_headline', 'headline_overstated_pct'], rows)

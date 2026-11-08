# how big is the bill shortfall next to what Treasury actually sells? I put the 65.4 billion
# that bills can't cover against two months of note and bond auctions, August and September 2026
# (October is left out because the end-of-month auctions weren't in the file when I pulled it).
import os, json
from common import DATA, write_csv

d = json.load(open(os.path.join(DATA, 'treasury_coupon_auctions_2026-08_10.json')))['data']
amt = lambda r: float(r['offering_amt']) / 1e9
aug_sep = [r for r in d if r['auction_date'][:7] in ('2026-08', '2026-09')]
coupons = sum(amt(r) for r in aug_sep)
long_bonds = sum(amt(r) for r in aug_sep if r['security_type'] == 'Bond')
per_month = coupons / 2

shortfall = 96.7 - 31.3
print(f"notes and bonds auctioned Aug-Sep 2026: {coupons:.0f} bn ({len(aug_sep)} auctions), {per_month:.0f} bn a month")
print(f"of which 20-year and longer: {long_bonds:.0f} bn")
print(f"shortfall bills can't cover: {shortfall:.1f} bn = {shortfall/per_month*100:.0f}% of one month of coupon auctions,"
      f" {shortfall/coupons*100:.0f}% of two months, {shortfall/long_bonds*100:.0f}% of two months of 20y+ bonds")
write_csv('coupon_supply.csv', ['item', 'bn'], [['coupon_auctions_aug_sep', round(coupons)], ['per_month', round(per_month)],
                                               ['bonds_20y_plus_aug_sep', round(long_bonds)], ['shortfall', round(shortfall, 1)]])

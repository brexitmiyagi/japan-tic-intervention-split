# who is positioned in long Treasury futures: the CFTC's Traders in Financial Futures report,
# futures only, positions as of 27 October 2026 (released 30 October). two contracts carry the long
# end, the classic Treasury bond and the Ultra bond, both $100,000 face. leveraged funds short and
# asset managers long is usually read as the cash-futures basis trade more than a view on yields.
import os, re
from common import DATA, write_csv

t = re.sub(r'<[^>]+>', '', open(os.path.join(DATA, 'cftc_tff_futures_2026-10-27.htm'), encoding='utf-8', errors='ignore').read())
assert 'Positions as of October 27, 2026' in t
rows = []
for label, key in [('UST bond', 'UST BOND - CHICAGO BOARD OF TRADE'), ('Ultra UST bond', 'ULTRA UST BOND - CHICAGO BOARD OF TRADE')]:
    seg = t[t.find(key):t.find(key) + 900]
    oi = int(re.search(r'Open Interest is ([\d,]+)', seg).group(1).replace(',', ''))
    n = [int(x.replace(',', '')) for x in re.findall(r'-?[\d,]+', seg.split('Positions', 1)[1].split('Changes')[0])]
    dealer, am, lev = n[0] - n[1], n[3] - n[4], n[6] - n[7]
    rows.append([label, oi, dealer, am, lev])
    print(f"{label:15s} open interest {oi:,}: dealers net {dealer:+,}, asset managers net {am:+,}, leveraged funds net {lev:+,}")
lev = sum(r[4] for r in rows)
print(f"leveraged funds net across both: {lev:+,} contracts, about ${-lev * 100000 / 1e9:.1f}bn of face value short")
write_csv('cftc_positioning.csv', ['contract', 'open_interest', 'dealer_net', 'asset_manager_net', 'leveraged_net'], rows)

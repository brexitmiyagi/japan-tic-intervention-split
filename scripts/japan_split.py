# splits the fall in Japan's Treasury holdings, end-Feb to end-Aug 2026, into what was sold
# (bills vs bonds) and what was just price.
from common import tic_table3, write_csv

MONTHS = ['2026-03', '2026-04', '2026-05', '2026-06', '2026-07', '2026-08']

t = tic_table3()
jp = t['Japan']

start, end = jp['2026-02']['pos'], jp['2026-08']['pos']
bills = sum(jp[m]['st_net'] for m in MONTHS)
bonds = sum(jp[m]['lt_net'] for m in MONTHS)
price = sum(jp[m]['lt_val'] for m in MONTHS)
change = end - start
other = change - bills - bonds - price

print(f"Japan holdings end-Feb {start:,.1f}bn, end-Aug {end:,.1f}bn, change {change:,.1f}bn")
print(f"  bills run down (net)      {bills:,.1f}")
print(f"  bonds and notes sold (net) {bonds:,.1f}")
print(f"  price change on bonds     {price:,.1f}")
print(f"  other / rounding          {other:,.1f}")
print(f"  bills share of the fall   {bills/change:.0%}")
print(f"Japan bill holdings end-Feb {jp['2026-02']['st_pos']:.1f}bn -> end-Aug {jp['2026-08']['st_pos']:.1f}bn "
      f"({jp['2026-08']['st_pos']/jp['2026-02']['st_pos']-1:.0%})")
print(f"Bills as a share of Japan's holdings, end-Aug: {jp['2026-08']['st_pos']/end:.1%}")

rows = []
prev = '2026-02'
for m in MONTHS:
    r = jp[m]
    rows.append([m, round(r['st_net'], 1), round(r['lt_net'], 1), round(r['lt_val'], 1),
                 round(r['pos'] - jp[prev]['pos'], 1)])
    prev = m
write_csv('japan_monthly.csv', ['month', 'bills_net_bn', 'bonds_net_bn', 'bond_price_change_bn', 'holdings_change_bn'], rows)
write_csv('japan_waterfall.csv', ['piece', 'bn'],
          [['Bills run down', round(bills, 1)], ['Price change on bonds', round(price, 1)],
           ['Bonds and notes sold', round(bonds, 1)], ['Other', round(other, 1)], ['Total change', round(change, 1)]])

# same split for the two others people quote
for name in ['China, Mainland', 'Of Which: Foreign Official', 'Grand Total']:
    c = t[name]
    ch = c['2026-08']['pos'] - c['2026-02']['pos']
    b = sum(c[m]['st_net'] for m in MONTHS); l = sum(c[m]['lt_net'] for m in MONTHS); v = sum(c[m]['lt_val'] for m in MONTHS)
    print(f"{name}: change {ch:,.1f} | bills {b:,.1f} | bonds {l:,.1f} | price {v:,.1f} | other {ch-b-l-v:,.1f}")

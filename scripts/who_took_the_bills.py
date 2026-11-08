# who ended up holding the bills. end-Feb to end-Aug 2026.
# supply = new bills Treasury issued (MSPD) + bills foreign official holders sold (TIC).
# the Fed number is SOMA bill holdings (FRED WSHOBL, Wednesday levels, nearest to month end).
# the Fed bought these in two ways: reserve management purchases (RMPs) and reinvesting its
# MBS paydowns into bills. RMPs ran $40bn a month to mid-April, $10bn a month to 13 August,
# then zero from 14 August.
from common import tic_table3, fred, nearest, mspd_bills, write_csv

MONTHS = ['2026-03', '2026-04', '2026-05', '2026-06', '2026-07', '2026-08']
t = tic_table3()
off = t['Of Which: Foreign Official']; jp = t['Japan']
bills = mspd_bills()
soma = fred('WSHOBL')

new_bills = bills['2026-08'] - bills['2026-02']
official_sold = -sum(off[m]['st_net'] for m in MONTHS)
japan_sold = -sum(jp[m]['st_net'] for m in MONTHS)
fed = (nearest(soma, '2026-08-26')[1] - nearest(soma, '2026-02-25')[1]) / 1000.0
needed_a_home = new_bills + official_sold
private = needed_a_home - fed

print(f"new bills, end-Feb to end-Aug (MSPD): {new_bills:,.1f}bn")
print(f"bills run down by foreign official holders (TIC): {official_sold:,.1f}bn, of which Japan row {japan_sold:,.1f}bn")
print(f"bills that needed a new owner: {needed_a_home:,.1f}bn")
print(f"Fed bill holdings change, 25 Feb to 26 Aug (WSHOBL): {fed:+,.1f}bn = {fed/needed_a_home:.0%} of it, "
      f"from {nearest(soma, '2026-02-25')[1] / 1000:.1f}bn to {nearest(soma, '2026-08-26')[1] / 1000:.1f}bn")
print(f"Fed buying vs official selling: {fed/official_sold:.2f}x")
print(f"left for everyone else: {private:,.1f}bn")

for a, b, label in [('2026-04-29', '2026-05-27', 'May window'), ('2026-07-29', '2026-08-26', 'Aug window')]:
    ch = (nearest(soma, b)[1] - nearest(soma, a)[1]) / 1000.0
    print(f"Fed bills {label} ({a} to {b}): {ch:+.1f}bn")

# monthly lines for the chart: Japan bill holdings vs Fed bill holdings
rows = []
for m in ['2025-12', '2026-01', '2026-02'] + MONTHS:
    y, mm = int(m[:4]), int(m[5:])
    import calendar, datetime as dt
    me = dt.date(y, mm, calendar.monthrange(y, mm)[1])
    rows.append([m, round(jp[m]['st_pos'], 1), round(nearest(soma, me)[1] / 1000.0, 1)])
write_csv('japan_bills_vs_fed_bills.csv', ['month_end', 'japan_tbills_bn', 'fed_tbills_bn'], rows)
write_csv('who_took_the_bills.csv', ['piece', 'bn'],
          [['New bills issued', round(new_bills, 1)], ['Sold by foreign official holders', round(official_sold, 1)],
           ['Bought by the Fed', round(fed, 1)], ['Left for private buyers', round(private, 1)]])

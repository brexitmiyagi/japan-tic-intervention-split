# same test on the 2024 intervention. MOF sold dollars on 29 April and 1 May 2024
# (Y9,788.5bn, MOF quarterly release). both settle in May 2024.
from common import tic_table3, fred, on_or_before
jp = tic_table3()['Japan']
usdjpy = fred('DEXJPUS')
usd = 5918.5 / on_or_before(usdjpy, '2024-04-29')[1] + 3870.0 / on_or_before(usdjpy, '2024-05-01')[1]
for m in ['2024-04', '2024-05', '2024-06']:
    r = jp[m]
    print(f"{m}: Japan bills {r['st_net']:+.1f}bn, bonds {r['lt_net']:+.1f}bn, bill holdings {r['st_pos']:.1f}bn")
print(f"2024 intervention about ${usd:,.1f}bn")

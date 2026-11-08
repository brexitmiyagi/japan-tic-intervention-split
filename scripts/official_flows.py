# the same check for any central bank: reserves change = transactions + price, and the transactions
# set against that country's row in TIC. this file holds the general version and a first screen.
#
#   securities sold (transactions) = BoP reserve-asset outflow - change in deposits
#   US debt the country row sold   = TIC Treasuries (bills + notes and bonds) + agencies + corporates
#   not in US data                 = securities sold - US debt sold
#
# only Japan has every input monthly and in this repo. data/country_data_map.csv says what exists
# for Korea, Taiwan, Switzerland and India and what still has to be confirmed. the screen below
# is TIC alone, so it shows what each row sold, not whether it matches the central bank.
import os, csv
from common import DATA, tic_table3, write_csv

def decompose(bop_outflow, deposits_change, tic_treasuries, tic_agencies_corporates):
    sold = bop_outflow - deposits_change
    us = tic_treasuries + tic_agencies_corporates
    return {'securities_sold': sold, 'us_debt': us, 'not_in_us_data': sold - us}

if __name__ == '__main__':
    t = tic_table3()
    ms = ['2026-03', '2026-04', '2026-05', '2026-06', '2026-07', '2026-08']
    rows = []
    for c in ['Japan', 'Korea, South', 'Taiwan', 'Switzerland', 'India']:
        v = t[c]
        b = sum(v[m]['st_net'] for m in ms); l = sum(v[m]['lt_net'] for m in ms); p = sum(v[m]['lt_val'] for m in ms)
        rows.append([c, round(b, 1), round(l, 1), round(p, 1), round(v['2026-02']['pos'], 1), round(v['2026-08']['pos'], 1)])
        print(f"{c}: Mar-Aug 2026 TIC bills {b:+.1f}, notes and bonds {l:+.1f}, price {p:+.1f}; holdings {v['2026-02']['pos']:.1f} -> {v['2026-08']['pos']:.1f}")
    write_csv('official_flows_screen.csv', ['country', 'bills_net', 'notes_bonds_net', 'price_change', 'holdings_feb', 'holdings_aug'], rows)
    for r in csv.DictReader(open(os.path.join(DATA, 'country_data_map.csv'))):
        print(f"  {r['country']}: {r['status_5_nov_2026']}")

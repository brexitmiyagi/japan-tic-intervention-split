# how many August-sized defenses can MOF fund before it has to sell notes and bonds?
# the liquid pool: Japan's bills (TIC, end-August), MOF's deposits (end-September reserves) and the
# Fed's FIMA repo cap. an August-sized defense is the July 30 to August 26 window, Y15.40tn, at
# today's rate. some of each defense comes from paper outside the US (24% to 56% since 2024), so
# only the rest has to come out of the liquid pool.
#
# careful, this cuts both ways:
#   - deposits aren't all spendable. from March 2024 to September 2026 they stayed between about
#     $155bn and $162bn, even through four interventions, which suggests most of them are a floor MOF doesn't spend.
#     I show the count with no deposits, half and all of them.
#   - FIMA is a loan against Treasuries, repaid later. it buys time, it doesn't fund anything.
#   - the other way: bills get refilled between defenses (that's call #1 in the post), which raises the count.
#   - the dates don't line up: bills are end-August, deposits end-September.
import os, csv
from common import DATA, tic_table3, write_csv, mof_reserves

rates = {r['KEY']: float(r['OBS_VALUE']) for r in csv.DictReader(open(os.path.join(DATA, 'ecb_reference_rates_latest.csv')))}
usdjpy = rates['EXR.D.JPY.EUR.SP00.A'] / rates['EXR.D.USD.EUR.SP00.A']
bills = tic_table3()['Japan']['2026-08']['st_pos']
dep = mof_reserves()['2026-09']['deposits_musd']
fima = 60.0
august = 15399.3 / usdjpy                      # Y bn / (Y per $) = $bn
print(f"USD/JPY {usdjpy:.2f}; bills {bills:.1f}bn; deposits {dep:.1f}bn; FIMA cap {fima:.0f}bn; August-sized defense {august:.1f}bn")
rows = []
for label, pool in [('bills only', bills), ('bills + FIMA', bills + fima), ('bills + FIMA + half of deposits', bills + fima + dep / 2),
                    ('bills + FIMA + all deposits', bills + fima + dep)]:
    out = [label, round(pool, 1)]
    for s in (0.0, 0.24, 0.56):
        out.append(round(pool / (august * (1 - s)), 1))
    rows.append(out)
    print(f"{label:32s} {pool:6.1f}bn -> defenses before coupons: {out[2]} (no outside-US paper), {out[3]} (24%), {out[4]} (56%)")
write_csv('capacity_countdown.csv', ['liquid_pool', 'pool_bn', 'defenses_if_outside_us_0pct', 'defenses_if_outside_us_24pct',
                                     'defenses_if_outside_us_56pct'], rows)

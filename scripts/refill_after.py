# what Japan did in the months after it stopped intervening. 2024 is the only recent case with
# country-level flows (TIC table 3 reports n.a. for Japan's 2022 flows).
# the pattern to look for: bills going back up while long-term Treasuries are sold.
from common import tic_table3, write_csv

t = tic_table3()
jp, off = t['Japan'], t['Of Which: Foreign Official']

def run(label, months, who=jp):
    b = sum(who[m]['st_net'] for m in months); l = sum(who[m]['lt_net'] for m in months)
    print(f"{label} {months[0]} to {months[-1]}: bills {b:+.1f}bn, bonds {l:+.1f}bn, "
          f"bill holdings {who[months[0]]['st_pos'] - who[months[0]]['st_net']:.1f} -> {who[months[-1]]['st_pos']:.1f}bn")
    return b, l

# 2024 had two interventions: 29 Apr and 1 May (settled May), then 11 and 12 July (settled July).
# an earlier version of this script called June to September a quiet refill. July wasn't quiet.
print('2024: interventions settled in May 2024 and July 2024 (see intervention_history.py)')
run('  Japan, first intervention month', ['2024-05'])
run('  Japan, June, no intervention', ['2024-06'])
run('  Japan, second intervention month', ['2024-07'])
run('  Japan, August and September, no intervention', ['2024-08', '2024-09'])
qb = sum(jp[m]['st_net'] for m in ['2024-06', '2024-08', '2024-09']); ql = sum(jp[m]['lt_net'] for m in ['2024-06', '2024-08', '2024-09'])
print(f"  Japan, the three quiet months (Jun, Aug, Sep 2024): bills {qb:+.1f}bn, bonds {ql:+.1f}bn")
b24, l24 = run('  Japan, June to September together', ['2024-06', '2024-07', '2024-08', '2024-09'])
run('  all foreign official, June to September', ['2024-06', '2024-07', '2024-08', '2024-09'], off)
rr = __import__('common').mof_reserves()
print(f"  MOF securities Jun to Jul 2024 {rr['2024-07']['securities_musd'] - rr['2024-06']['securities_musd']:+.1f}bn, "
      f"Japan row Treasuries in July {jp['2024-07']['st_net'] + jp['2024-07']['lt_net']:+.1f}bn")
print('2026: first intervention settled in May 2026, second in August')
run('  Japan, the month between', ['2026-07'])

rows = [[m, round(jp[m]['st_net'], 1), round(jp[m]['lt_net'], 1), round(jp[m]['st_pos'], 1)]
        for m in ['2024-03', '2024-04', '2024-05', '2024-06', '2024-07', '2024-08', '2024-09', '2024-10']]
write_csv('refill_2024.csv', ['month', 'japan_bills_net_bn', 'japan_bonds_net_bn', 'japan_bill_holdings_bn'], rows)

# MOF's own reserve report over the 2024 refill. if MOF was swapping bonds for bills, its total
# securities should barely move even while bills go up.
from common import mof_reserves
r = mof_reserves()
print(f"MOF securities end-May 2024 {r['2024-05']['securities_musd']:.1f}bn -> end-Sep 2024 {r['2024-09']['securities_musd']:.1f}bn "
      f"({r['2024-09']['securities_musd']-r['2024-05']['securities_musd']:+.1f}), deposits {r['2024-05']['deposits_musd']:.1f} -> {r['2024-09']['deposits_musd']:.1f}")
for a, b in [('2026-04', '2026-05'), ('2026-07', '2026-08')]:
    print(f"MOF deposits {a} {r[a]['deposits_musd']:.1f} -> {b} {r[b]['deposits_musd']:.1f}")

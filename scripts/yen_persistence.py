# does the yen move stick? event_study.py stops five business days after MOF's last trade. this
# carries the same six episodes to 20 and 60 business days after the last trade, measured from the
# close before the first trade, and asks how much of the settlement-week move is still there.
# each change is again set against every window of the same length from 2022 to October 2026 that
# doesn't start or end inside an episode.
#
# careful with overlaps. 60 business days is about three months, so some windows run into the
# next thing: Apr-May 2024 runs into the July 2024 intervention, Jul 2024 runs into the 5 August
# 2024 carry unwind, and Apr-May 2026 runs into the July 2026 intervention. I flag those rather
# than drop them, and the summary prints the clean ones separately.
import datetime as dt
from common import fred, write_csv

jpy = dict(fred('DEXJPUS')); eur = dict(fred('DEXUSEU'))
y30 = dict(fred('DGS30'))
cal = sorted(set(jpy) & set(eur) & set(y30))

episodes = [
    ('Sep 2022', dt.date(2022, 9, 22), dt.date(2022, 9, 22)),
    ('Oct 2022', dt.date(2022, 10, 21), dt.date(2022, 10, 24)),
    ('Apr-May 2024', dt.date(2024, 4, 29), dt.date(2024, 5, 1)),
    ('Jul 2024', dt.date(2024, 7, 11), dt.date(2024, 7, 12)),
    ('Apr-May 2026', dt.date(2026, 4, 30), dt.date(2026, 5, 6)),
    ('Jul 2026', dt.date(2026, 7, 30), dt.date(2026, 7, 31)),
]
overlap = {('Apr-May 2024', 60): 'runs into the July 2024 intervention',
           ('Jul 2024', 60): 'runs into the 5 Aug 2024 carry unwind',
           ('Jul 2024', 20): 'runs into the 5 Aug 2024 carry unwind',
           ('Apr-May 2026', 60): 'runs into the July 2026 intervention'}

def idx(d):
    return cal.index(max(x for x in cal if x <= d))

measures = {'USD/JPY (%)': lambda d: jpy[d], 'EUR/JPY (%)': lambda d: jpy[d] * eur[d]}

blocked = set()
for e, a, b in episodes:
    i0, i1 = idx(a) - 1, idx(b) + 5
    blocked |= set(cal[i0:i1 + 1])

def baseline(f, n):
    out = []
    for i in range(len(cal) - n):
        a, b = cal[i], cal[i + n]
        if a in blocked or b in blocked or b > dt.date(2026, 10, 30):
            continue
        out.append((f(b) / f(a) - 1) * 100)
    return out

rows = []
for e, a, b in episodes:
    i0, i1 = idx(a) - 1, idx(b)
    for name, f in measures.items():
        start = cal[i0]
        settle = (f(cal[i1 + 5]) / f(start) - 1) * 100
        for k in (5, 20, 60):
            if i1 + k >= len(cal):
                continue
            end = cal[i1 + k]
            ch = (f(end) / f(start) - 1) * 100
            n = i1 + k - i0
            base = baseline(f, n)
            pct = round(sum(x <= ch for x in base) / len(base) * 100)
            kept = round(ch / settle * 100) if settle else None
            rows.append([e, name, k, start.isoformat(), end.isoformat(), round(ch, 2), pct, kept, overlap.get((e, k), '')])
            print(f"{e:13s} {name:12s} +{k:2d}bd to {end}: {ch:+6.2f}%  percentile {pct:3d}  kept {kept}% of settlement week  {overlap.get((e, k), '')}")

write_csv('yen_persistence.csv', ['episode', 'measure', 'business_days_after_last_trade', 'from', 'to', 'change_pct',
                                  'percentile_vs_normal', 'pct_of_settlement_week_move_kept', 'overlap'], rows)

# solo or joint. July 2026 is the only episode here where the US Treasury bought yen alongside MOF
# (MOF statement, 3 August 2026; ESF August statement). the others were MOF alone. one joint case
# can't separate "joint" from "biggest", since July 2026 was also the largest at Y15.40tn.
print('\nsolo against joint, USD/JPY, % of the settlement-week move left:')
for e in ('Apr-May 2024', 'Apr-May 2026', 'Jul 2026'):
    k20 = [r for r in rows if r[0] == e and r[1] == 'USD/JPY (%)' and r[2] == 20][0]
    k60 = [r for r in rows if r[0] == e and r[1] == 'USD/JPY (%)' and r[2] == 60][0]
    print(f"  {e:13s} {'joint' if e == 'Jul 2026' else 'solo ':5s}  +20bd {k20[7]}% left (pct {k20[6]}), +60bd {k60[7]}% left {('(' + k60[8] + ')') if k60[8] else ''}")

print('\nsince 2024, USD/JPY:')
for k in (20, 60):
    rs = [r for r in rows if r[1] == 'USD/JPY (%)' and r[2] == k and r[0] in ('Apr-May 2024', 'Jul 2024', 'Apr-May 2026', 'Jul 2026')]
    clean = [r for r in rs if not r[8]]
    print(f"  +{k}bd: changes {', '.join(f'{r[0]} {r[5]:+.2f}% ({r[7]}% kept, pct {r[6]})' for r in rs)}")
    print(f"         clean windows only: {', '.join(f'{r[0]} {r[5]:+.2f}% ({r[7]}% kept)' for r in clean) or 'none'}")

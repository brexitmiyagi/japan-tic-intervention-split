# the yen test with more cases, and a fairer yardstick.
# cases: every yen-buying episode in MOF's file since 1991, plus July 2026 (not in the file yet).
# solo or joint: June 1998 and July 2026 are the two where the US Treasury bought yen alongside MOF
# (New York Fed's 1998 Q2 FX report; MOF's 3 August 2026 statement). the rest are MOF alone, as far
# as I've checked. 1991-92 is left out: about two dozen small operations, none above Y0.08tn a day, so
# close together that every window runs into the next one, and I haven't checked US involvement.
#
# the fairer yardstick: MOF steps in after the yen has already fallen hard, and some bounce-back
# after a hard fall is normal. so as well as every same-length window since 1991, I compare each
# episode with windows that start after a USD/JPY rise over the previous 20 business days at least
# as big as the one before that episode. if there are fewer than 30 of those, I take the 30 biggest.
import os, csv, io, datetime as dt
from common import DATA, write_csv

px = {}
for r in csv.DictReader(open(os.path.join(DATA, 'fred_DEXJPUS_1971.csv'))):
    if r['DEXJPUS'] not in ('', '.'):
        px[dt.date.fromisoformat(r['observation_date'])] = float(r['DEXJPUS'])
cal = sorted(d for d in px if d >= dt.date(1990, 1, 1))
pos = {d: i for i, d in enumerate(cal)}
def at(d):
    return max(x for x in cal if x <= d)

raw = open(os.path.join(DATA, 'mof_intervention_history.csv'), 'rb').read().decode('shift_jis')
days, year, month = [], None, None
MON = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
for r in csv.reader(io.StringIO(raw)):
    if len(r) < 9 or not r[5].strip().isdigit() or not r[6].strip():
        continue
    if r[3].strip().isdigit():
        year = int(r[3])
    if r[4].strip():
        month = MON[r[4].strip()]
    if 'yen (bought)' in r[8] and year >= 1997:
        days.append((dt.date(year, month, int(r[5])), int(r[6].replace(',', '')) / 10000))
days.append((dt.date(2026, 7, 30), 15.3993)); days.append((dt.date(2026, 7, 31), 0.0))   # window total on the first day
days.sort()

# group days within 10 business days of each other into one episode
eps = []
for d, y in days:
    if eps and pos[at(d)] - pos[at(eps[-1]['days'][-1])] <= 10:
        eps[-1]['days'].append(d); eps[-1]['yen_tn'] += y
    else:
        eps.append({'days': [d], 'yen_tn': y})
JOINT = {dt.date(1998, 6, 17), dt.date(2026, 7, 30)}
for e in eps:
    e['name'] = e['days'][0].strftime('%b %Y') if len(e['days']) == 1 or e['days'][0].month == e['days'][-1].month else \
        f"{e['days'][0].strftime('%b')}-{e['days'][-1].strftime('%b %Y')}"
    e['joint'] = bool(JOINT & set(e['days']))
    e['i0'] = pos[at(e['days'][0])] - 1          # close before the first trade
    e['i1'] = pos[at(e['days'][-1])]             # close of the last trade

blocked = set()
for e in eps:
    blocked |= set(range(e['i0'] - 20, e['i1'] + 61))

def chg(i, j):
    return (px[cal[j]] / px[cal[i]] - 1) * 100

rows = []
for e in eps:
    pre = chg(e['i0'] - 20, e['i0'])                       # the yen fall going in (USD/JPY rise, %)
    settle = chg(e['i0'], e['i1'] + 5)
    for k in (5, 20, 60):
        j = e['i1'] + k
        if j >= len(cal):
            continue
        ch = chg(e['i0'], j); n = j - e['i0']
        allw, cond = [], []
        for i in range(20, len(cal) - n):
            if i in blocked or i + n in blocked or cal[i + n] > dt.date(2026, 10, 30):
                continue
            c = chg(i, i + n); allw.append(c)
            cond.append((chg(i - 20, i), c))
        big = [c for p, c in cond if p >= pre]
        if len(big) < 30:
            big = [c for p, c in sorted(cond, reverse=True)[:30]]
        p_all = round(sum(x <= ch for x in allw) / len(allw) * 100)
        p_cond = round(sum(x <= ch for x in big) / len(big) * 100)
        kept = round(ch / settle * 100) if settle else None
        nxt = [f['name'] for f in eps if f is not e and e['i0'] < f['i0'] <= j]
        rows.append([e['name'], 'joint' if e['joint'] else 'solo', round(e['yen_tn'], 2), round(pre, 2), k, round(ch, 2),
                     kept, p_all, p_cond, len(big), '; '.join(nxt)])
        print(f"{e['name']:13s} {'joint' if e['joint'] else 'solo ':5s} Y{e['yen_tn']:5.2f}tn  fall going in {pre:+5.1f}%  +{k:2d}bd {ch:+6.2f}%  "
              f"kept {kept}%  pct vs all {p_all:3d}, vs after-a-fall {p_cond:3d} (n={len(big)}) {('runs into ' + ', '.join(nxt)) if nxt else ''}")
write_csv('yen_history.csv', ['episode', 'solo_or_joint', 'yen_tn', 'usdjpy_rise_20bd_before_pct', 'business_days_after',
                              'usdjpy_change_pct', 'pct_of_settlement_week_kept', 'percentile_vs_all', 'percentile_vs_after_a_fall',
                              'n_after_a_fall', 'runs_into'], rows)

print('\nafter 20 business days, clean windows only (no later episode inside):')
for side in ('solo', 'joint'):
    rs = [r for r in rows if r[1] == side and r[4] == 20 and not r[10]]
    print(f"  {side}: " + ', '.join(f"{r[0]} kept {r[6]}% (pct vs after-a-fall {r[8]})" for r in rs))

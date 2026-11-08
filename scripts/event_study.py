# what moves when MOF intervenes, by how much, and how fast.
# six episodes: Sep 2022, Oct 2022, Apr-May 2024, Jul 2024, Apr-May 2026, Jul 2026.
# two windows per episode:
#   "days"        close the day before the first trade to close of the last trade day
#   "settlement"  close the day before the first trade to five business days after the last
# each change is set against every other window of the same length from 2022 to October 2026
# (event windows left out), so a move can be read as normal or not. sizes are MOF's own.
#
# careful with three things. the sample is six episodes, so this can rule out big effects better
# than it can prove small ones. MOF often moves on days that carry other news: 1 May 2024 was an
# FOMC decision day and 11 July 2024 was the June CPI release. and MOF hasn't published the daily
# split for July-August 2026 yet, so that episode is dated 30-31 July from the window it reported
# and the US Treasury's ESF statement, with the window's full Y15.40tn as its size. if some of it
# was traded later in August, that episode's per-$10bn numbers are too small.
# the euro-area minus US 10-year spread takes out the part of euro yields that just follows Treasuries.
import os, csv, io, statistics, datetime as dt
from common import DATA, fred, write_csv

def series(name):
    return dict(fred(name))
y30, y10, y2, b4, sofr, jpy, eur = (series(s) for s in ('DGS30', 'DGS10', 'DGS2', 'DTB4WK', 'SOFR', 'DEXJPUS', 'DEXUSEU'))
bund = {}
for line in open(os.path.join(DATA, 'bundesbank_bund10y_daily.csv'), encoding='utf-8-sig'):
    p = line.strip().split(',')
    if len(p) >= 2 and p[0][:2] == '20' and p[1] not in ('.', ''):
        bund[dt.date.fromisoformat(p[0])] = float(p[1])
ea = {dt.date.fromisoformat(r['date']): float(r['yield_pct']) for r in csv.DictReader(open(os.path.join(DATA, 'ecb_euro_govt_10y_daily.csv')))}

measures = {
    '30-year Treasury (bp)': (lambda d: y30[d] * 100, [y30]),
    '2s10s (bp)': (lambda d: (y10[d] - y2[d]) * 100, [y10, y2]),
    '1-month bill minus SOFR (bp)': (lambda d: (b4[d] - sofr[d]) * 100, [b4, sofr]),
    'USD/JPY (%)': (lambda d: jpy[d], [jpy]),
    'EUR/JPY (%)': (lambda d: jpy[d] * eur[d], [jpy, eur]),
    'Bund 10-year (bp)': (lambda d: bund[d] * 100, [bund]),
    'Euro-area govt 10-year, all issuers (bp)': (lambda d: ea[d] * 100, [ea]),
    'Euro-area govt 10-year minus US 10-year (bp)': (lambda d: (ea[d] - y10[d]) * 100, [ea, y10]),
}
pct = {'USD/JPY (%)', 'EUR/JPY (%)'}

# MOF's own trade dates and yen amounts
raw = open(os.path.join(DATA, 'mof_intervention_history.csv'), 'rb').read().decode('shift_jis')
days, year, month = {}, None, None
MON = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
for r in csv.reader(io.StringIO(raw)):
    if len(r) < 9 or not r[5].strip().isdigit() or not r[6].strip():
        continue
    if r[3].strip().isdigit():
        year = int(r[3])
    if r[4].strip():
        month = MON[r[4].strip()]
    if year >= 2022:
        days[dt.date(year, month, int(r[5]))] = int(r[6].replace(',', '')) / 10000   # yen tn

episodes = [
    ('Sep 2022', [dt.date(2022, 9, 22)]),
    ('Oct 2022', [dt.date(2022, 10, 21), dt.date(2022, 10, 24)]),
    ('Apr-May 2024', [dt.date(2024, 4, 29), dt.date(2024, 5, 1)]),
    ('Jul 2024', [dt.date(2024, 7, 11), dt.date(2024, 7, 12)]),
    ('Apr-May 2026', [dt.date(2026, 4, 30), dt.date(2026, 5, 4), dt.date(2026, 5, 6)]),
    ('Jul 2026', [dt.date(2026, 7, 30), dt.date(2026, 7, 31)]),
]
size_yen = {e: sum(days.get(d, 0) for d in ds) for e, ds in episodes}
size_yen['Jul 2026'] = 15.3993                               # MOF monthly window, 30 Jul to 26 Aug

# a common trading calendar: days where the US series all exist
cal = sorted(set(y30) & set(jpy) & set(eur) & set(y10) & set(y2) & set(b4) & set(sofr))
def on_or_before(d):
    return max(x for x in cal if x <= d)
def index_of(d):
    return cal.index(on_or_before(d))

def value(f, deps, d):
    # latest date on or before d (within a week) where every input exists, so European holidays
    # fall back to the previous Frankfurt close
    for k in range(8):
        x = d - dt.timedelta(days=k)
        if all(x in s for s in deps):
            return f(x)
    raise KeyError(d)

def change(name, a, b):
    f, deps = measures[name]
    va, vb = value(f, deps, a), value(f, deps, b)
    return (vb / va - 1) * 100 if name in pct else vb - va

windows = {}
for e, ds in episodes:
    i0 = index_of(ds[0]) - 1
    i1 = index_of(ds[-1])
    windows[e] = {'days': (cal[i0], cal[i1]), 'settlement': (cal[i0], cal[min(i1 + 5, len(cal) - 1)])}

# baseline: every window of the same length, excluding anything overlapping an episode
blocked = set()
for e in windows:
    a, b = windows[e]['settlement']
    blocked |= {x for x in cal if a <= x <= b}
_cache = {}
def baseline(name, n):
    if (name, n) in _cache:
        return _cache[(name, n)]
    out = []
    for i in range(len(cal) - n):
        a, b = cal[i], cal[i + n]
        if a in blocked or b in blocked or b > dt.date(2026, 10, 30):
            continue
        try:
            out.append(change(name, a, b))
        except KeyError:
            pass
    _cache[(name, n)] = out
    return out

rows = []
print('episode, window, measure: change | percentile among same-length windows | per $10bn')
for e, ds in episodes:
    a, b = windows[e]['days']
    usd = size_yen[e] * 1000 / value(lambda d: jpy[d], [jpy], ds[0])
    for w in ('days', 'settlement'):
        a, b = windows[e][w]
        n = cal.index(b) - cal.index(a)
        for name in measures:
            ch = change(name, a, b)
            base = baseline(name, n)
            pctile = sum(x <= ch for x in base) / len(base) * 100
            sd = statistics.pstdev(base)
            rows.append([e, w, name, a.isoformat(), b.isoformat(), round(size_yen[e], 2), round(usd, 1),
                         round(ch, 2), round(ch / usd * 10, 2), round(pctile), round(ch / sd, 2) if sd else None])
    print(f"{e}: Y{size_yen[e]:.2f}tn, about ${usd:.1f}bn")
write_csv('event_study.csv', ['episode', 'window', 'measure', 'from', 'to', 'yen_tn', 'usd_bn', 'change',
                              'change_per_10bn', 'percentile_vs_normal', 'z_vs_normal'], rows)

# summary across the six episodes, per measure and window
print('\nacross six episodes (median change, median per $10bn, how many outside the 10th-90th percentile, sign split):')
summ = []
for w in ('days', 'settlement'):
    for name in measures:
        rs = [r for r in rows if r[1] == w and r[2] == name]
        chg = [r[7] for r in rs]; per = [r[8] for r in rs]; pc = [r[9] for r in rs]
        unusual = sum(p < 10 or p > 90 for p in pc)
        up = sum(c > 0 for c in chg)
        summ.append([w, name, round(statistics.median(chg), 2), round(statistics.median(per), 2), unusual, up, len(rs) - up])
        print(f"  {w:10s} {name:42s} median {statistics.median(chg):+7.2f}, per $10bn {statistics.median(per):+6.2f}, "
              f"unusual {unusual}/6, up {up} down {len(rs) - up}")
write_csv('event_study_summary.csv', ['window', 'measure', 'median_change', 'median_per_10bn', 'episodes_outside_10_90', 'episodes_up', 'episodes_down'], summ)

# since 2024 only. partly because the Sep 2022 intervention came the day after a Fed hike (FOMC 20-21 Sep 2022)
print('\nsince 2024 (four episodes): range of changes, range of percentiles, range per $10bn')
s24 = []
for w in ('days', 'settlement'):
    for name in measures:
        rs = [r for r in rows if r[1] == w and r[2] == name and r[0] in ('Apr-May 2024', 'Jul 2024', 'Apr-May 2026', 'Jul 2026')]
        c = [r[7] for r in rs]; p = [r[9] for r in rs]; k = [r[8] for r in rs]
        s24.append([w, name, round(min(c), 2), round(max(c), 2), min(p), max(p), round(min(k), 2), round(max(k), 2)])
        print(f"  {w:10s} {name:42s} {min(c):+6.2f} to {max(c):+6.2f}; percentile {min(p)} to {max(p)}; per $10bn {min(k):+.2f} to {max(k):+.2f}")
write_csv('event_study_since_2024.csv', ['window', 'measure', 'min_change', 'max_change', 'min_percentile', 'max_percentile',
                                         'min_per_10bn', 'max_per_10bn'], s24)

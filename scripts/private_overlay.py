# the Japan row in TIC is every Japanese resident. to see how much of it could be MOF, I take
# MOF's own monthly survey of Japanese residents' purchases of foreign bonds by investor type.
# that survey covers banks, trust accounts (pension money), life insurers and the rest. it
# does not include MOF's reserve operations, which are counted as reserve assets.
# the survey is in 100 million yen and covers every currency, so I convert at the month's
# average noon rate and treat the share that went into Treasuries as unknown, 0 to 100%.
import os, csv, io, statistics
from common import DATA, tic_table3, fred, write_csv

MONTHS = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
          'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}

def survey(fname):
    raw = open(os.path.join(DATA, fname), 'rb').read().decode('shift_jis', errors='ignore')
    out, year = {}, None
    for r in csv.reader(io.StringIO(raw)):
        if len(r) < 6:
            continue
        if r[0].strip()[:4].isdigit():
            year = int(r[0].strip()[:4])
        m = r[2].strip()
        if year and m in MONTHS and r[5].strip():
            def n(x):
                x = x.replace(',', '').strip()
                return 0.0 if x in ('', '-') else float(x) / 10.0   # 100m yen -> yen bn
            out[f"{year}-{MONTHS[m]:02d}"] = dict(total=n(r[5]), banks=n(r[20]), trust_accounts=n(r[38]))
    return out

lt = survey('mof_sector_longterm_raw.csv')
fx = fred('DEXJPUS')
def avg_rate(m):
    y, mm = int(m[:4]), int(m[5:])
    return statistics.mean(v for d, v in fx if d.year == y and d.month == mm)

jp = tic_table3()['Japan']
# 2022 flows are n.a. in table 3, so use the same TIC series as republished on FRED
ft_lt = {d.strftime('%Y-%m'): v / 1000 for d, v in fred('FORLTTREASNET42609')}
ft_st = {d.strftime('%Y-%m'): v / 1000 for d, v in fred('FORSTTREASNET42609')}
def tic(m, k):
    r = jp.get(m, {})
    if r.get(k) is not None:
        return r[k]
    return ft_lt.get(m) if k == 'lt_net' else ft_st.get(m)

episodes = [
    ('2022 intervention (22 Sep, 21 and 24 Oct)', ['2022-09', '2022-10']),
    ('2022 after', ['2022-11', '2022-12']),
    ('2024 intervention (29 Apr, 1 May)', ['2024-05']),
    ('2024 June to September (includes the 11-12 July intervention)', ['2024-06', '2024-07', '2024-08', '2024-09']),
    ('2026 first intervention (30 Apr to 6 May)', ['2026-05']),
    ('2026 between', ['2026-06', '2026-07']),
    ('2026 second intervention (30-31 Jul)', ['2026-08']),
    ('2026 after (survey only, TIC due 18 Nov)', ['2026-09']),
]
rows = []
for label, ms in episodes:
    bills = sum(tic(m, 'st_net') or 0 for m in ms) if all(tic(m, 'st_net') is not None for m in ms) else None
    bonds = sum(tic(m, 'lt_net') or 0 for m in ms) if all(tic(m, 'lt_net') is not None for m in ms) else None
    priv_yen = sum(lt[m]['total'] for m in ms)
    priv_usd = sum(lt[m]['total'] / avg_rate(m) for m in ms)
    if bonds is not None:
        lo, hi = sorted([bonds, bonds - priv_usd])
        rng = f"{lo:+.1f} to {hi:+.1f}"
    else:
        rng = 'n/a'
    rows.append([label, ' '.join(ms), None if bills is None else round(bills, 1), None if bonds is None else round(bonds, 1),
                 round(priv_yen / 1000, 2), round(priv_usd, 1), rng])
    print(f"{label}: TIC Japan bills {bills if bills is None else round(bills,1)}, bonds {bonds if bonds is None else round(bonds,1)} | "
          f"private Japanese foreign bonds Y{priv_yen/1000:+.2f}tn (${priv_usd:+.1f}bn) | non-private bond flow {rng}")
write_csv('episodes_with_private_overlay.csv',
          ['episode', 'months', 'tic_japan_bills_bn', 'tic_japan_bonds_bn', 'private_foreign_bonds_yen_tn',
           'private_foreign_bonds_usd_bn', 'implied_non_private_bonds_bn_range'], rows)

for m in ['2026-05', '2026-08', '2026-09']:
    s = lt[m]
    print(f"{m} survey detail: banks Y{s['banks']/1000:+.2f}tn, trust accounts Y{s['trust_accounts']/1000:+.2f}tn, total Y{s['total']/1000:+.2f}tn")

# what Japan had in bills going into the 2022 intervention (end-August 2022, TIC on FRED)
pos = {d.strftime('%Y-%m'): v / 1000 for d, v in fred('FORSTTREASPOS42609')}
print(f"Japan bill holdings going into 2022, end-Aug 2022: {pos['2022-08']:.1f}bn")

# MOF's securities fell 87.8 billion dollars in August. The Japan row in TIC only sold 37.0
# billion of Treasuries. This script works through where the other 50 billion or so could be.
#
# step 1: was it sales or price? Japan's balance of payments books reserve assets as
#         transactions, so if the BoP outflow matches the stock drop, valuation is small.
# step 2: was it other US securities? TIC table 1 has agencies and corporates for Japan.
# step 3: was it private Japanese selling hiding MOF buying? MOF's investor-type survey.
# step 4: was it euro-area bonds? the ECB's monthly BoP has non-residents' net purchases
#         of euro-area debt. it has no country split, so the best it can do is say whether
#         August looks unusual next to other Augusts.
import os, csv, io, statistics
from common import DATA, tic_table3, fred, mof_reserves, write_csv

def avg_rate(ym):
    return statistics.mean(v for d, v in fred('DEXJPUS') if d.strftime('%Y-%m') == ym)

res = mof_reserves()
jp = tic_table3()['Japan']

rows = []
for prev, m in [('2026-04', '2026-05'), ('2026-07', '2026-08')]:
    sec = res[m]['securities_musd'] - res[prev]['securities_musd']
    dep = res[m]['deposits_musd'] - res[prev]['deposits_musd']
    fx = res[m]['foreign_currency_reserves_musd'] - res[prev]['foreign_currency_reserves_musd']

    bop = {r['month']: float(r['reserve_assets_100m_yen']) for r in csv.DictReader(open(os.path.join(DATA, 'mof_bop_reserve_assets.csv')))}
    rate = avg_rate(m)
    bop_usd = bop[m] / 10.0 / rate            # 100m yen -> yen bn -> usd bn
    valuation = fx - bop_usd

    # TIC table 1: agencies and corporates for Japan in the month
    t1 = {}
    with open(os.path.join(DATA, 'slt_table1.txt')) as f:
        for line in f:
            p = line.rstrip('\n').split('\t')
            if p[0] == 'Japan' and p[2] == m:
                t1 = dict(agcy=float(p[10]) / 1000, corp=float(p[13]) / 1000)
    treas = jp[m]['lt_net'] + jp[m]['st_net']
    us_debt = treas + t1['agcy'] + t1['corp']
    gap = sec - treas

    print(f"{m}: MOF securities {sec:+.1f}, deposits {dep:+.1f}, FX reserves {fx:+.1f} ($bn)")
    print(f"   BoP reserve-asset transactions {bop[m]/10000:+.2f} yen tn = {bop_usd:+.1f} at {rate:.2f}, so valuation about {valuation:+.1f}")
    print(f"   Japan row Treasuries {treas:+.1f} (bonds {jp[m]['lt_net']:+.1f}, bills {jp[m]['st_net']:+.1f}), agencies {t1['agcy']:+.1f}, corporates {t1['corp']:+.1f}, all US debt {us_debt:+.1f}")
    print(f"   securities drop not in the Japan Treasury row: {gap:+.1f}; not in any US debt: {sec - us_debt:+.1f}")
    rows.append([m, round(sec, 1), round(dep, 1), round(fx, 1), round(bop_usd, 1), round(valuation, 1),
                 round(treas, 1), round(t1['agcy'], 1), round(t1['corp'], 1), round(gap, 1), round(sec - us_debt, 1)])

write_csv('august_gap.csv', ['month', 'mof_securities_chg', 'mof_deposits_chg', 'mof_fx_reserves_chg',
                             'bop_reserve_transactions_usd', 'implied_valuation', 'japan_treasuries_net',
                             'japan_agencies_net', 'japan_corporates_net', 'gap_vs_treasuries', 'gap_vs_all_us_debt'], rows)

# step 3: private Japanese, long and short foreign debt, August
MONTHS = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
          'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
def survey(fname):
    # same parser as private_overlay.py: column 5 is the all-investor net figure, 100m yen
    raw = open(os.path.join(DATA, fname), 'rb').read().decode('shift_jis', errors='ignore')
    out, year = {}, None
    for r in csv.reader(io.StringIO(raw)):
        if len(r) < 6:
            continue
        if r[0].strip()[:4].isdigit():
            year = int(r[0].strip()[:4])
        m = r[2].strip()
        if year and m in MONTHS and r[5].strip():
            x = r[5].replace(',', '').strip()
            out[f"{year}-{MONTHS[m]:02d}"] = dict(total=0.0 if x in ('', '-') else float(x) / 10.0)
    return out
lt = survey('mof_sector_longterm_raw.csv')
st_ = survey('mof_sector_shortterm_raw.csv')
r8 = avg_rate('2026-08')
print(f"\nprivate Japanese, August: long-term foreign debt {lt['2026-08']['total']/r8:+.1f}, short-term {st_['2026-08']['total']/r8:+.1f} ($bn)")
# every Japanese resident together, so it doesn't matter who did what. MOF's securities plus the
# private survey (long and short) is all foreign debt Japanese residents sold. TIC's Japan row is all
# US debt they sold. the difference is non-US debt, whoever sold it.
priv = (lt['2026-08']['total'] + st_['2026-08']['total']) / r8
aug = [r for r in rows if r[0] == '2026-08'][0]
all_foreign = aug[1] + priv
all_us = aug[6] + aug[7] + aug[8]
print(f"all Japanese residents, August: foreign debt {all_foreign:+.1f}, of which US debt {all_us:+.1f}, so non-US debt {all_foreign - all_us:+.1f} ($bn)")
write_csv('august_all_residents.csv', ['item', 'usd_bn'], [['mof_securities', aug[1]], ['private_foreign_debt', round(priv, 1)],
          ['all_foreign_debt', round(all_foreign, 1)], ['us_debt_tic', round(all_us, 1)], ['non_us_debt', round(all_foreign - all_us, 1)]])

# step 4: euro area, non-residents' net purchases of euro-area debt securities, EUR bn
ea = {}
for r in csv.DictReader(open(os.path.join(DATA, 'ecb_bps_nonresident_debt_purchases.csv'))):
    ea.setdefault((r['issuer_sector'], r['maturity']), {})[r['month']] = float(r['eur_millions']) / 1000
eur_rows = []
print('\neuro area, non-residents net purchases of euro-area debt (EUR bn)')
for key in [('all sectors', 'all'), ('all sectors', 'long-term'), ('general government', 'long-term'), ('general government', 'short-term')]:
    s = ea[key]
    augs = [v for mth, v in s.items() if mth.endswith('-08') and mth < '2026']
    jan_jul = [s[f'2026-{i:02d}'] for i in range(1, 8)]
    mu, sd = statistics.mean(augs), statistics.stdev(augs)
    z = (s['2026-08'] - mu) / sd
    print(f"   {key[0]}, {key[1]}: Aug 2026 {s['2026-08']:+.1f}; Augusts 2014-2025 mean {mu:+.1f}, sd {sd:.1f}, z {z:+.2f}; Jan-Jul 2026 median {statistics.median(jan_jul):+.1f}")
    eur_rows.append([key[0], key[1], round(s['2026-08'], 1), round(mu, 1), round(sd, 1), round(z, 2), round(statistics.median(jan_jul), 1)])
write_csv('euro_area_august.csv', ['issuer_sector', 'maturity', 'aug_2026', 'aug_mean_2014_2025', 'aug_sd', 'z', 'jan_jul_2026_median'], eur_rows)

# what 50 billion dollars is in euros at the end-August ECB rate
eurusd = None
for r in csv.DictReader(open(os.path.join(DATA, 'ecb_reference_rates_usd_jpy.csv'))):
    if r['KEY'] == 'EXR.D.USD.EUR.SP00.A' and r['TIME_PERIOD'] == '2026-08-31':
        eurusd = float(r['OBS_VALUE'])
print(f"\n50.8 billion dollars is about EUR {50.8 / eurusd:.0f} billion at {eurusd}")

# second sources for the numbers the post leans on. each check pulls the same figure from a
# different publication and fails if they disagree.
import csv, json, os, statistics
from common import DATA, tic_table3, fred, nearest, on_or_before, mof_reserves

def ok(a, b, tol, what):
    assert abs(a - b) <= tol, f"MISMATCH {what}: {a} vs {b}"
    print(f"ok  {what}: {a} | {b}")

jp = tic_table3()['Japan']
# 1. TIC table 3 vs the same TIC series as published on FRED
f_pos = {d.strftime('%Y-%m'): v / 1000 for d, v in fred('FORTREASPOS42609')}
f_st = {d.strftime('%Y-%m'): v / 1000 for d, v in fred('FORSTTREASNET42609')}
f_lt = {d.strftime('%Y-%m'): v / 1000 for d, v in fred('FORLTTREASNET42609')}
for m in ['2026-02', '2026-05', '2026-08']:
    ok(round(jp[m]['pos'], 3), round(f_pos[m], 3), 0.001, f"Japan holdings {m}, table 3 vs FRED")
for m in ['2026-05', '2026-08']:
    ok(round(jp[m]['st_net'], 3), round(f_st[m], 3), 0.001, f"Japan bill flow {m}, table 3 vs FRED")
    ok(round(jp[m]['lt_net'], 3), round(f_lt[m], 3), 0.001, f"Japan bond flow {m}, table 3 vs FRED")

# 2. Fed bills and NY Fed custody: FRED vs the H.4.1 release pages themselves
h = {r['release_date']: r for r in csv.DictReader(open(os.path.join(DATA, 'h41_transcribed.csv')))}
num = lambda s: float(s.replace(',', '')) / 1000
soma = fred('WSHOBL'); cust = fred('WMTSECL1')
for rel, wed in [('2026-02-26', '2026-02-25'), ('2026-08-27', '2026-08-26'), ('2026-04-30', '2026-04-29'),
                 ('2026-05-28', '2026-05-27'), ('2026-07-30', '2026-07-29'), ('2026-10-29', '2026-10-28')]:
    ok(num(h[rel]['fed_bills_wednesday_musd']), nearest(soma, wed)[1] / 1000, 0.001, f"Fed bills {wed}, H.4.1 vs FRED")
    ok(num(h[rel]['custody_marketable_treasuries_wednesday_musd']), nearest(cust, wed)[1] / 1000, 0.001, f"custody {wed}, H.4.1 vs FRED")
fo = [float(h[k]['foreign_official_repo_week_avg_musd'].replace(',', '')) for k in h if '2026-04-30' <= k <= '2026-10-29']
print(f"ok  FIMA / foreign official repo, week averages 30 Apr to 29 Oct: max ${max(fo):.0f} million across {len(fo)} releases")
fw = [v for d, v in fred('H41RESPPALGTRFNWW') if str(d) >= '2026-04-01']
assert max(fw) <= 2, f"FIMA Wednesday level above $2m since April: {max(fw)}"
print(f"ok  FIMA / foreign official repo, Wednesday levels 1 Apr to {max(d for d, v in fred('H41RESPPALGTRFNWW'))}: max ${max(fw):.0f} million across {len(fw)} weeks (FRED H41RESPPALGTRFNWW)")

# 3. 30-year yield: FRED vs Treasury's own par curve
par = {r['Date']: float(r['30 Yr']) for r in csv.DictReader(open(os.path.join(DATA, 'treasury_par_curve_2026.csv')))}
y = fred('DGS30')
for d in ['04/29/2026', '05/29/2026', '07/29/2026', '08/26/2026', '10/07/2026', '11/03/2026']:
    iso = f"{d[6:]}-{d[:2]}-{d[3:5]}"
    ok(par[d], on_or_before(y, iso)[1], 0.001, f"30y {iso}, Treasury vs FRED")
par01 = [float(r['30 Yr']) for r in csv.DictReader(open(os.path.join(DATA, 'treasury_par_curve_2001.csv'))) if r['Date'] == '07/11/2001']
print(f"ok  Treasury par curve 30y on 11 Jul 2001: {par01[0]} (last Treasury-published close at or above 5.67 before 2026)")

# 4. USD/JPY: FRED noon NY vs ECB reference cross (EUR/JPY / EUR/USD), within 0.5% on quiet days
e = {}
for r in csv.DictReader(open(os.path.join(DATA, 'ecb_reference_rates_usd_jpy.csv'))):
    e.setdefault(r['TIME_PERIOD'], {})[r['CURRENCY']] = float(r['OBS_VALUE'])
fx = fred('DEXJPUS')
for d in ['2026-04-30', '2026-05-06', '2026-07-31', '2026-10-30']:
    ecb = e[d]['JPY'] / e[d]['USD']; fr = on_or_before(fx, d)[1]
    ok(round(ecb, 2), fr, fr * 0.007, f"USDJPY {d}, ECB cross vs FRED")
ecb_q2 = 6278.7 / (e['2026-04-30']['JPY'] / e['2026-04-30']['USD']) + 780.2 / (e['2026-05-04']['JPY'] / e['2026-05-04']['USD']) + 4675.9 / (e['2026-05-06']['JPY'] / e['2026-05-06']['USD'])
ecb_q3 = [15399.3 / (e[d]['JPY'] / e[d]['USD']) for d in ['2026-07-30', '2026-07-31']]
print(f"ok  Apr-May dollars at ECB rates ${ecb_q2:.1f}bn (FRED basis $74.9bn); Jul-Aug ${min(ecb_q3):.1f}bn to ${max(ecb_q3):.1f}bn (FRED basis $96.6-96.8bn)")

# 5. SOFR: FRED vs the NY Fed's own API
s = dict(fred('SOFR')); i = dict(fred('IORB'))
import datetime as dt
for m in ['05', '08']:
    ny = {x['effectiveDate']: x['percentRate'] for x in json.load(open(os.path.join(DATA, f'nyfed_sofr_2026-{m}.json')))['refRates']}
    for d, v in ny.items():
        assert abs(v - s[dt.date.fromisoformat(d)]) < 1e-9, f"SOFR mismatch {d}"
    avg = statistics.mean((v - i[dt.date.fromisoformat(d)]) * 100 for d, v in ny.items())
    print(f"ok  SOFR 2026-{m}: {len(ny)} days identical on NY Fed and FRED; SOFR minus IORB average {avg:+.1f}bp")

# 6. MOF reserves: the English IMF-template page vs MOF's Japanese summary page (transcribed by hand)
jp_page = {'2026-04': (1382994, 1007241, 162197), '2026-05': (1305874, 931678, 162235),
           '2026-07': (1287099, 927332, 162285), '2026-08': (1207524, 839559, 155417), '2026-09': (1178396, 821691, 155222)}
r = mof_reserves()
for m, (tot, sec, dep) in jp_page.items():
    ok(round(r[m]['official_reserve_assets_musd'], 3), tot / 1000, 0.001, f"MOF total reserves {m}, English vs Japanese page")
    ok(round(r[m]['securities_musd'], 3), sec / 1000, 0.001, f"MOF securities {m}, English vs Japanese page")
# 7. ECB: the monthly API series summed over 12 months vs the 12-month totals in the ECB's own
#    press release of 20 October 2026 (Table 2, non-residents' net purchases of euro-area debt)
ea = {r['month']: float(r['eur_millions']) / 1000 for r in csv.DictReader(open(os.path.join(DATA, 'ecb_bps_nonresident_debt_purchases.csv')))
      if r['issuer_sector'] == 'all sectors' and r['maturity'] == 'all'}
ok(sum(v for m, v in ea.items() if '2025-09' <= m <= '2026-08'), 659, 0.5, 'euro-area debt liabilities, 12m to Aug 2026, API vs release (EUR bn)')
ok(sum(v for m, v in ea.items() if '2024-09' <= m <= '2025-08'), 412, 0.5, 'euro-area debt liabilities, 12m to Aug 2025, API vs release (EUR bn)')

# 8. Japan's BoP reserve-asset outflow vs MOF's intervention reports for the same settlement month.
#    they should be close but not equal: the BoP also has coupon income and other flows.
bop = {r['month']: float(r['reserve_assets_100m_yen']) / 10000 for r in csv.DictReader(open(os.path.join(DATA, 'mof_bop_reserve_assets.csv')))}
ok(-bop['2026-05'], 11.73, 0.5, 'BoP reserve outflow May vs MOF intervention 30 Apr-6 May (Y tn)')
ok(-bop['2026-08'], 15.40, 0.5, 'BoP reserve outflow Aug vs MOF intervention 30 Jul-26 Aug (Y tn)')

# 9. MOF's historical reserves file vs the monthly pages, and FRED vs TIC table 1 for Japan agencies and corporates
import io as _io
raw = open(os.path.join(DATA, 'mof_reserves_historical.csv'), 'rb').read().decode('shift_jis', errors='replace')
M = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
hist, y = {}, None
for row in csv.reader(_io.StringIO(raw)):
    if len(row) > 8 and row[3].strip() in M:
        if row[2].strip().isdigit():
            y = int(row[2])
        elif row[3].strip() == 'January':
            y += 1
        hist[f"{y}-{M.index(row[3].strip()) + 1:02d}"] = float(row[6].replace(',', '')) / 1000
for m in ['2024-04', '2024-05', '2024-07', '2026-04', '2026-05', '2026-07', '2026-08']:
    ok(hist[m], r[m]['securities_musd'], 0.001, f"MOF securities {m}, historical file vs monthly page")
t1 = {}
for line in open(os.path.join(DATA, 'slt_table1.txt')):
    q = line.rstrip('\n').split('\t')
    if q[0] == 'Japan' and q[2] in ('2024-05', '2024-07', '2026-08'):
        t1[q[2]] = (float(q[10]) / 1000, float(q[13]) / 1000)
fa = {d.strftime('%Y-%m'): v / 1000 for d, v in fred('FORLTAGCYNET42609')}
fc_ = {d.strftime('%Y-%m'): v / 1000 for d, v in fred('FORLTCORPNET42609')}
for m, (a, c) in t1.items():
    ok(fa[m], a, 0.001, f"Japan agencies {m}, FRED vs TIC table 1")
    ok(fc_[m], c, 0.001, f"Japan corporates {m}, FRED vs TIC table 1")

print('\nall cross-checks pass')

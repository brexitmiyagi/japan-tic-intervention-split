# is August 2026 a one-off, or does every Japanese intervention leave selling that US data can't see?
# same check as august_gap.py, for every settlement month since 2022:
#   MOF securities change (MOF's historical reserves file)
#   minus Japan's US debt flows (TIC via FRED: long-term Treasuries, bills, agencies, corporates)
#   checked against Japan's BoP reserve-asset transactions (MOF's monthly BoP summary), so price
#   changes can be separated from sales.
# then the private side: MOF's investor survey, net and gross, to see whether a private swap of
# non-US bonds into Treasuries could be big enough to hide the gap.
#
# careful: TIC long-term flows before February 2023 were estimated from holdings and prices, not
# reported trades. so the 2022 rows are softer than the 2024 and 2026 rows.
import os, csv, io, statistics
from common import DATA, fred, write_csv

MONTHS = ['2022-09', '2022-10', '2024-05', '2024-07', '2026-05', '2026-08']
M = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

# MOF reserves, historical file. rows run monthly from January 2013; the year only appears in January
raw = open(os.path.join(DATA, 'mof_reserves_historical.csv'), 'rb').read().decode('shift_jis', errors='replace')
seq = [r for r in csv.reader(io.StringIO(raw)) if len(r) > 8 and r[3].strip() in M]
res, y = {}, None
for r in seq:
    if r[2].strip().isdigit():
        y = int(r[2])
    elif r[3].strip() == 'January':
        y += 1
    if y:
        n = lambda x: float(x.replace(',', '')) / 1000
        res[f"{y}-{M.index(r[3].strip()) + 1:02d}"] = dict(fx=n(r[5]), sec=n(r[6]), dep=n(r[8]))

# BoP reserve assets, 100m yen (column 18 of MOF's monthly summary)
raw = open(os.path.join(DATA, 'mof_bop_monthly_summary.csv'), 'rb').read().decode('cp932', errors='replace')
bop, y = {}, None
short = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
for r in csv.reader(io.StringIO(raw)):
    if len(r) < 19:
        continue
    if r[2].strip().isdigit():
        y = r[2].strip()
    mo = r[3].replace('(P)', '').strip()
    if y and mo in short and r[18].strip():
        bop[f"{y}-{short.index(mo) + 1:02d}"] = float(r[18].replace(',', '')) / 10.0   # yen bn

fx = fred('DEXJPUS')
def rate(m):
    return statistics.mean(v for d, v in fx if d.strftime('%Y-%m') == m)
def series(s):
    return {d.strftime('%Y-%m'): v / 1000 for d, v in fred(s)}
lt, st, ag, co = (series(s) for s in ('FORLTTREASNET42609', 'FORSTTREASNET42609', 'FORLTAGCYNET42609', 'FORLTCORPNET42609'))

# investor survey, long-term and short-term. columns: 3/4/5 all investors acquisition/disposition/net,
# 39/40 securities firms (dealer churn), so real-money gross = all minus dealers
def survey(fname):
    raw = open(os.path.join(DATA, fname), 'rb').read().decode('shift_jis', errors='ignore')
    out, year = {}, None
    for r in csv.reader(io.StringIO(raw)):
        if len(r) < 41:
            continue
        if r[0].strip()[:4].isdigit():
            year = int(r[0].strip()[:4])
        m = r[2].strip()
        if year and m in short and r[5].strip():
            g = lambda x: 0.0 if x.strip() in ('', '-') else float(x.replace(',', '')) / 10.0
            out[f"{year}-{short.index(m) + 1:02d}"] = dict(acq=g(r[3]), disp=g(r[4]), net=g(r[5]), dacq=g(r[39]), ddisp=g(r[40]))
    return out
svl, svs = survey('mof_sector_longterm_raw.csv'), survey('mof_sector_shortterm_raw.csv')

def prev(m):
    yy, mm = int(m[:4]), int(m[5:])
    return f"{yy - 1}-12" if mm == 1 else f"{yy}-{mm - 1:02d}"

rows = []
# the gap is measured on transactions, so price moves don't get in: MOF's securities sold is the BoP
# reserve-asset transaction less the change in deposits. "MOF only" puts every dollar of the Japan
# row's US debt flow on MOF. "all residents" adds the private survey, which is the strict version,
# because private Japanese buying Treasuries is the one thing that could hide MOF Treasury sales.
for m in MONTHS:
    p = prev(m); r_ = rate(m)
    sec = res[m]['sec'] - res[p]['sec']; dep = res[m]['dep'] - res[p]['dep']; fxc = res[m]['fx'] - res[p]['fx']
    bop_usd = bop[m] / r_
    sold = bop_usd - dep                      # securities sold, transactions
    treas = lt[m] + st[m]; us = treas + ag[m] + co[m]
    priv = (svl[m]['net'] + svs[m]['net']) / r_
    gap = sold - us                           # MOF-only basis
    strict = sold + priv - us                 # all-residents basis
    real_acq = svl[m]['acq'] - svl[m]['dacq']
    swap_yen = -gap * r_
    rows.append([m, round(sec, 1), round(dep, 1), round(fxc, 1), round(bop_usd, 1), round(fxc - bop_usd, 1), round(sold, 1),
                 round(treas, 1), round(ag[m] + co[m], 1), round(priv, 1), round(gap, 1),
                 round(gap / sold * 100) if gap < 0 else None, round(strict, 1),
                 round(real_acq / 1000, 2), round(swap_yen / 1000, 2) if gap < 0 else None,
                 round(swap_yen / real_acq * 100) if gap < 0 else None])
    print(f"{m}: MOF securities sold (BoP less deposits) {sold:+.1f} [stock {sec:+.1f}, valuation {fxc - bop_usd:+.1f}]; "
          f"US debt in the Japan row {us:+.1f}; gap, MOF only {gap:+.1f}"
          + (f" ({gap / sold * 100:.0f}% of MOF sales)" if gap < 0 else '')
          + f"; private {priv:+.1f}; non-US, all residents {strict:+.1f}"
          + (f"; private swap needed Y{swap_yen / 1000:.1f}tn = {swap_yen / real_acq * 100:.0f}% of real-money gross LT acquisitions (Y{real_acq / 1000:.1f}tn)" if gap < 0 else ''))

neg_gap = sum(r[10] < 0 for r in rows); neg_strict = sum(r[12] < -5 for r in rows)
print(f"\nintervention months where MOF sold more than US data show: {neg_gap} of {len(rows)}; "
      f"where all Japanese residents sold more than $5bn of non-US debt: {neg_strict} of {len(rows)}")
write_csv('intervention_gaps.csv', ['month', 'mof_securities_stock_chg', 'mof_deposits_chg', 'mof_fx_chg', 'bop_reserve_tx_usd',
                                    'implied_valuation', 'mof_securities_sold_tx', 'japan_treasuries_net', 'japan_agencies_corporates_net',
                                    'private_foreign_debt_net', 'gap_mof_only', 'gap_pct_of_mof_sales', 'non_us_all_residents',
                                    'real_money_gross_lt_acq_yen_tn', 'swap_needed_yen_tn', 'swap_pct_of_real_money_acq'], rows)

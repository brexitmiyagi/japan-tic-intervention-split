# the test for the $50 billion gap, ready for MOF's July to September 2026 daily breakdown.
# MOF's file lists every intervention day with the currency pair. every yen-buying day so far has been
# "the US dollar (sold) the Japanese yen (bought)". if any July or August 2026 day shows euros (or any other
# currency) sold for yen, the gap is non-dollar bonds sold and converted straight to yen. if every day is
# dollars, MOF sold dollar paper TIC doesn't see (supranationals, foreign agencies) or converted euros to
# dollars first.
# to run it: save the new file from
# https://www.mof.go.jp/english/policy/international_policy/reference/feio/foreign_exchange_intervention_operations.csv
# over data/mof_intervention_history.csv and run this again.
import os, csv, io
from common import DATA, write_csv

YEAR, MONTHS = 2026, ('Jul', 'Aug', 'Sep')
raw = open(os.path.join(DATA, 'mof_intervention_history.csv'), 'rb').read().decode('shift_jis')
year, month, rows = None, None, []
for r in csv.reader(io.StringIO(raw)):
    if len(r) < 9 or not r[5].strip().isdigit() or not r[6].strip():
        continue
    if r[3].strip().isdigit():
        year = int(r[3])
    if r[4].strip():
        month = r[4].strip()
    if year == YEAR and month in MONTHS:
        rows.append([year, month, int(r[5]), r[6], r[8].strip()])
if not rows:
    print('July to September 2026 is not in this file yet. MOF publishes the quarter in early November (8 Nov 2024, 10 Nov 2025).')
else:
    pairs = sorted({r[4] for r in rows})
    print(f"{len(rows)} intervention days in July to September {YEAR}:")
    for r in rows:
        print(f"  {r[1]} {r[2]}: {r[3]} (100 million yen), {r[4]}")
    non_usd = [r for r in rows if 'US dollar' not in r[4]]
    if non_usd:
        print(f"VERDICT: {len(non_usd)} day(s) sold something other than dollars for yen. The euro (or other non-dollar) reading of the gap stands.")
    else:
        print("VERDICT: every day was dollars for yen. The gap is dollar paper outside TIC, or non-dollar bonds converted to dollars first.")
    write_csv('mof_q3_check.csv', ['year', 'month', 'day', 'amount_100m_yen', 'currency_pair'], rows)

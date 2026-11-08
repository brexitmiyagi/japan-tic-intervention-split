# MOF's own record of every intervention since April 1991, straight from its CSV.
# I use it for the 2022 and 2024 amounts so they come from MOF, not from wire reports.
import os, csv, io
from common import DATA, write_csv

raw = open(os.path.join(DATA, 'mof_intervention_history.csv'), 'rb').read().decode('shift_jis')
rows, year, month = [], None, None
for r in csv.reader(io.StringIO(raw)):
    if len(r) < 9 or not r[5].strip().isdigit() or not r[6].strip():
        continue
    if r[3].strip().isdigit():
        year = int(r[3])
    if r[4].strip():
        month = r[4].strip()
    rows.append([year, month, int(r[5]), int(r[6].replace(',', '')) / 10000, r[8].strip()])   # 100m yen -> yen tn

out = [x for x in rows if x[0] in (2022, 2024, 2026)]
for y in (2022, 2024, 2026):
    days = [x for x in out if x[0] == y]
    print(f"{y}: " + ', '.join(f"{m} {d} {a:.2f}" for _, m, d, a, _ in days) + f"  total yen {sum(x[3] for x in days):.2f} tn; pairs: {set(x[4] for x in days)}")
write_csv('intervention_history.csv', ['year', 'month', 'day', 'yen_tn', 'currency_pair'], out)

# every yen-buying day in the file, and what MOF sold to buy the yen
yen_bought = [x for x in rows if 'yen (bought)' in x[4]]
print(f"yen-buying days since April 1991: {len(yen_bought)}; currencies sold: {sorted(set(x[4].split(' (sold)')[0] for x in yen_bought))}")

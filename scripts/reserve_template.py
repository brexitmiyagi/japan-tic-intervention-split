# MOF's monthly reserves file is the IMF's full reserves template, not just the headline. most
# people read section I (reserves). this reads the rest, to check for channels that could fund a
# defense without showing up as securities sold:
#   section II   forwards and futures against the yen (a forward sale of dollars would show here)
#   section III  contingent liabilities
#   section IV   securities lent or on repo (a private repo would show here), derivatives marked
#                to market
# plus gold, which moves total reserves without anything being sold.
# columns are by position in MOF's historical.csv, labels from its own header rows. US$ millions in
# the file, billions here.
import os, csv, io
from common import DATA, write_csv

raw = open(os.path.join(DATA, 'mof_reserves_historical.csv'), 'rb').read().decode('cp932', errors='ignore')
rows = list(csv.reader(io.StringIO(raw)))
COL = {'total_reserves': 4, 'fx_reserves': 5, 'securities': 6, 'deposits': 8, 'gold': 16,
       'fwd_net': 30, 'fwd_short': 34, 'fwd_long': 38,
       'contingent': 47,
       'lent_repo_total': 127, 'lent_repo_in_section_I': 128, 'borrowed_not_in_section_I': 131,
       'derivatives_net': 132}
for k, c in COL.items():
    lab = ' | '.join(rows[i][c].strip() for i in range(7, 16) if c < len(rows[i]) and rows[i][c].strip())
    print(f"  col {c:3d} {k:26s} {lab[:110]}")

# the year sits in the first column as a Japanese era year (Heisei or Reiwa), only on the first row
# of each year; the month is in the second column as "N月". MOF's English month labels vary
# ("Apr", "April", even "Feburuary"), so I don't use them.
import re
ERA = {'平成': 1988, '令和': 2018}
out, year = [], None
for r in rows:
    if len(r) < 140:
        continue
    era = re.match(r'(平成|令和)(\d+|元)年', r[0].strip())
    if era:
        year = ERA[era.group(1)] + (1 if era.group(2) == '元' else int(era.group(2)))
    mm = re.match(r'(\d+)月', r[1].strip())
    if not (year and mm and r[4].strip()):
        continue
    m = f"{year}-{int(mm.group(1)):02d}"
    def v(c):
        x = r[c].replace(',', '').strip()
        return float(x) / 1000 if x not in ('', '-') else 0.0
    out.append([m] + [round(v(c), 2) for c in COL.values()])

hdr = ['month'] + list(COL)
write_csv('reserve_template.csv', hdr, out)
idx = {h: i for i, h in enumerate(hdr)}
print('\nmonth    reserves securities   gold  fwd long fwd short  lent/repo borrowed  deriv')
for r in out:
    if r[0] >= '2024-01':
        print(f"{r[0]}  {r[idx['total_reserves']]:8.1f} {r[idx['securities']]:9.1f} {r[idx['gold']]:6.1f} {r[idx['fwd_long']]:8.2f} "
              f"{r[idx['fwd_short']]:8.3f} {-r[idx['lent_repo_in_section_I']]:9.1f} {r[idx['borrowed_not_in_section_I']]:8.1f} {r[idx['derivatives_net']]:6.2f}")

byM = {r[0]: r for r in out}
def d(m0, m1, k):
    return byM[m1][idx[k]] - byM[m0][idx[k]]
for m0, m1 in [('2026-04', '2026-05'), ('2026-07', '2026-08'), ('2026-08', '2026-09')]:
    print(f"\n{m0} to {m1}: total {d(m0, m1, 'total_reserves'):+.1f}, securities {d(m0, m1, 'securities'):+.1f}, deposits {d(m0, m1, 'deposits'):+.1f}, "
          f"gold {d(m0, m1, 'gold'):+.1f}, forwards long {d(m0, m1, 'fwd_long'):+.2f}, forwards short {d(m0, m1, 'fwd_short'):+.3f}, "
          f"lent/repo {-d(m0, m1, 'lent_repo_in_section_I'):+.1f}, borrowed {d(m0, m1, 'borrowed_not_in_section_I'):+.1f}, derivatives {d(m0, m1, 'derivatives_net'):+.2f}")
s24 = [r for r in out if r[0] >= '2024-01']
print(f"\nsince Jan 2024: forwards long {min(r[idx['fwd_long']] for r in s24):.1f} to {max(r[idx['fwd_long']] for r in s24):.1f}bn; "
      f"most negative short {min(r[idx['fwd_short']] for r in s24):.3f}bn; lent/repo {min(-r[idx['lent_repo_in_section_I']] for r in s24):.1f} to "
      f"{max(-r[idx['lent_repo_in_section_I']] for r in s24):.1f}bn; derivatives {min(r[idx['derivatives_net']] for r in s24):+.2f} to {max(r[idx['derivatives_net']] for r in s24):+.2f}bn")

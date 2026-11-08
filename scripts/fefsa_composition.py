# what MOF tells us about the make-up of its foreign securities. once a year, in early November, MOF
# publishes a breakdown of the FX fund's foreign-currency assets (gaitametokkai xlsx). it gives the
# split by maturity and between government and non-government bonds. it does not give a currency
# split, so it can't cap how much euro or other non-dollar paper MOF holds.
# two things it does give me:
#   - 26% of the securities are not government bonds. that bucket includes US agencies (which TIC
#     table 1 sees) and supranational or foreign-agency bonds (which TIC never sees, even in dollars).
#     so "outside US data" doesn't have to mean "outside the dollar".
#   - annual interest, which sizes the interest-income effect in the BoP check.
import os, statistics
import openpyxl
from common import DATA, fred, write_csv

ws = openpyxl.load_workbook(os.path.join(DATA, 'mof_fefsa_assets_fy2024.xlsx'), data_only=True).worksheets[0]
cells = [[c for c in row] for row in ws.iter_rows(values_only=True)]
def find(label):
    # labels sit in column B or C; values follow to the right. match the whole label, not a prefix
    for r in cells:
        for c in r[:3]:
            if c is not None and str(c).replace('\u3000', '').strip() == label:
                return [v for v in r[3:] if isinstance(v, (int, float))]
    raise KeyError(label)

sec_total = find('外貨証券')[0]                       # million yen, FY2024 year-end
gov = find('国債')[:2]; nongov = find('国債以外の証券')[:2]
mat = {k: find(k)[:2] for k in ('1年以下', '1年超5年以下', '5年超')}
interest = find('外貨証券利子')[0] + find('外貨預け金利子')[0]   # million yen, FY2024

print(f"FEFSA foreign securities at 31 Mar 2025: Y{sec_total / 1e6:.2f}tn")
print(f"  government bonds {gov[1] * 100:.0f}%, non-government {nongov[1] * 100:.0f}% (Y{nongov[0] / 1e6:.2f}tn)")
names = {'1年以下': 'up to 1 year', '1年超5年以下': '1 to 5 years', '5年超': 'over 5 years'}
print('  maturity: ' + ', '.join(f"{names[k]} {v[1] * 100:.1f}%" for k, v in mat.items()))
rate = statistics.mean(v for d, v in fred('DEXJPUS') if d.strftime('%Y-%m') == '2026-08')
monthly_usd = interest / 12 / 1000 / rate
print(f"  interest on securities and deposits FY2024 Y{interest / 1e6:.2f}tn, about ${monthly_usd:.1f}bn a month at August 2026's rate")
print("  currency split: not published")
write_csv('fefsa_composition.csv', ['item', 'value'], [['securities_yen_tn', round(sec_total / 1e6, 2)],
          ['government_share', round(gov[1], 3)], ['non_government_share', round(nongov[1], 3)],
          ['interest_yen_tn_fy2024', round(interest / 1e6, 2)], ['interest_usd_bn_per_month', round(monthly_usd, 1)],
          ['maturity_up_to_1y_share', round(mat['1年以下'][1], 3)], ['maturity_1_to_5y_share', round(mat['1年超5年以下'][1], 3)],
          ['maturity_over_5y_share', round(mat['5年超'][1], 3)]])

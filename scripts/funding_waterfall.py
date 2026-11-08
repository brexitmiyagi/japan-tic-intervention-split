# the next defense: if MOF does Y5tn, Y10tn or Y15tn, where do the dollars come from?
# I replay each past episode's actual mix (shares of the dollars MOF raised in the settlement month)
# at today's rate, and cap bills at what Japan still holds. whatever the bill cap blocks has to come
# from somewhere else: deposits, the Fed's FIMA line, coupons, or more paper outside the US.
#
# mix per episode, from intervention_gaps.csv (all shares of the BoP reserve outflow):
#   deposits      change in MOF deposits
#   bills         TIC Japan-row bill run-down
#   coupons       TIC Japan-row net sales of notes and bonds
#   agencies/corp TIC Japan-row agencies and corporates
#   outside US    the rest: MOF securities sold that US data can't find
# Sep 2022 is left out because private selling swamped the Japan row that month. Oct 2022 is kept
# but its TIC flows were estimates.
# where each piece shows up first:
#   bills          NY Fed custody in the Thursday H.4.1, then TIC about six weeks after month-end
#   deposits       MOF's reserve report, early the following month
#   FIMA           the H.4.1 foreign official repo line, every Thursday
#   coupons        custody falling faster than bills explain, then TIC
#   outside US     MOF's securities line against TIC, and the BoP; currency only in MOF's quarterly
#                  breakdown or the IMF's COFER
import os, csv
from common import RESULTS, DATA, tic_table3, write_csv

ig = {r['month']: r for r in csv.DictReader(open(os.path.join(RESULTS, 'intervention_gaps.csv')))}
jp = tic_table3()['Japan']
from common import fred
lt = {d.strftime('%Y-%m'): v / 1000 for d, v in fred('FORLTTREASNET42609')}
st = {d.strftime('%Y-%m'): v / 1000 for d, v in fred('FORSTTREASNET42609')}

# today's rate: ECB reference rates, 4 November 2026 (JPY per EUR / USD per EUR)
rates = {}
for r in csv.DictReader(open(os.path.join(DATA, 'ecb_reference_rates_latest.csv'))):
    rates[r['KEY']] = float(r['OBS_VALUE'])
usdjpy = rates['EXR.D.JPY.EUR.SP00.A'] / rates['EXR.D.USD.EUR.SP00.A']
bills_left = jp['2026-08']['st_pos']

mixes = {}
for m in ['2022-10', '2024-05', '2024-07', '2026-05', '2026-08']:
    r = ig[m]; out = -float(r['bop_reserve_tx_usd'])
    mixes[m] = {
        'deposits': -float(r['mof_deposits_chg']) / out,
        'bills': -st[m] / out,
        'coupons': -lt[m] / out,
        'agencies_corporates': -float(r['japan_agencies_corporates_net']) / out,
        'outside_us': -float(r['gap_mof_only']) / out,
    }
    print(m, ' '.join(f"{k} {v * 100:+.0f}%" for k, v in mixes[m].items()), f"(sum {sum(mixes[m].values()) * 100:.0f}%)")

print(f"\nUSD/JPY {usdjpy:.2f} (ECB, 4 Nov 2026); Japan's bills at end-August {bills_left:.1f}bn")
# replaying the Japan-row mixes one-for-one would copy private flows into MOF's plan (the negative
# agencies in Oct 2022 and coupons in Aug 2026 are private buying). so the forward model uses the
# ranges the 2024-2026 episodes give for the MOF-driven pieces, and treats coupons as what's left:
#   bills         up to what Japan still holds (bills first held in three of the four since 2024)
#   outside US    24% to 56% of the dollars, the 2024-26 range
#   deposits      0% to 7%, the 2024-26 range
#   coupons/FIMA  whatever is left. FIMA is capped at $60bn and has never been drawn
# and a July-2024-style case, where MOF barely touched bills and sold coupons (34% of the dollars).
since = [m for m in mixes if m >= '2024']
o_lo, o_hi = min(mixes[m]['outside_us'] for m in since), max(mixes[m]['outside_us'] for m in since)
d_lo, d_hi = max(0.0, min(mixes[m]['deposits'] for m in since)), max(mixes[m]['deposits'] for m in since)
c_jul = mixes['2024-07']['coupons']
print(f"ranges since 2024: outside US {o_lo * 100:.0f}% to {o_hi * 100:.0f}%, deposits {d_lo * 100:.0f}% to {d_hi * 100:.0f}%; July 2024 coupons {c_jul * 100:.0f}%")
rows = []
for yen in (5, 10, 15):
    usd = yen * 1000 / usdjpy
    bills = min(bills_left, usd)
    left_light = max(0.0, usd - bills - o_hi * usd - d_hi * usd)     # everything else at its biggest
    left_heavy = max(0.0, usd - bills - o_lo * usd - d_lo * usd)     # everything else at its smallest
    jul = c_jul * usd
    rows.append([yen, round(usd, 1), round(bills, 1), round(o_lo * usd, 1), round(o_hi * usd, 1), round(d_hi * usd, 1),
                 round(left_light, 1), round(left_heavy, 1), round(jul, 1), round(left_heavy / 60 * 100)])
    print(f"Y{yen}tn = ${usd:.1f}bn: bills up to {bills:.1f}; outside US {o_lo * usd:.1f} to {o_hi * usd:.1f}; deposits up to {d_hi * usd:.1f}; "
          f"left for coupons or FIMA {left_light:.1f} to {left_heavy:.1f}; July-2024-style coupons {jul:.1f}")
write_csv('funding_waterfall.csv', ['yen_tn', 'usd_bn', 'bills_up_to', 'outside_us_low', 'outside_us_high', 'deposits_up_to',
                                    'coupons_or_fima_low', 'coupons_or_fima_high', 'july_2024_style_coupons', 'high_case_pct_of_fima_cap'], rows)
write_csv('funding_mixes.csv', ['episode', 'deposits', 'bills', 'coupons', 'agencies_corporates', 'outside_us'],
          [[m] + [round(v * 100, 1) for v in mix.values()] for m, mix in mixes.items()])

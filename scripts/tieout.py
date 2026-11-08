# checks that the pieces add back to the totals I quote, and that the numbers in the post
# are the ones the data gives. if anything here fails, the post is wrong somewhere.
from common import tic_table3, mof_reserves, fred, on_or_before, nearest, mspd_bills

MONTHS = ['2026-03', '2026-04', '2026-05', '2026-06', '2026-07', '2026-08']
t = tic_table3(); jp = t['Japan']; off = t['Of Which: Foreign Official']; g = t['Grand Total']

def close(a, b, tol, what):
    assert abs(a - b) <= tol, f"FAILED {what}: {a:.2f} vs {b:.2f}"
    print(f"ok  {what}: {a:,.1f}")

# 1. each month, holdings change = net flow + bond price change, within a few billion
for m, p in zip(MONTHS, ['2026-02'] + MONTHS[:-1]):
    ch = jp[m]['pos'] - jp[p]['pos']
    close(ch, jp[m]['net'] + jp[m]['lt_val'], 7.0, f"Japan {m} holdings change vs flows + price")
    close(jp[m]['net'], jp[m]['lt_net'] + jp[m]['st_net'], 0.05, f"Japan {m} total flow = bills + bonds")

# 2. the headline split
close(jp['2026-08']['pos'] - jp['2026-02']['pos'], -171.0, 0.05, 'Japan fall end-Feb to end-Aug')
close(sum(jp[m]['st_net'] for m in MONTHS), -120.4, 0.05, 'Japan bills run down')
close(sum(jp[m]['lt_net'] for m in MONTHS), -12.8, 0.05, 'Japan bonds sold')
close(sum(jp[m]['lt_val'] for m in MONTHS), -34.7, 0.05, 'Japan price change')
close(sum(off[m]['lt_net'] for m in MONTHS), 14.4, 0.05, 'foreign official bonds, net bought')
close(sum(off[m]['st_net'] for m in MONTHS), -141.1, 0.05, 'foreign official bills run down')
close(sum(off[m]['lt_val'] for m in MONTHS), -103.5, 0.05, 'foreign official price change')
close(sum(g[m]['lt_net'] for m in MONTHS), 231.8, 0.05, 'all foreigners, bonds net bought')

# 3. MOF's own reserve report should fall by about what MOF spent
r = mof_reserves()
fx = (r['2026-05']['foreign_currency_reserves_musd'] - r['2026-04']['foreign_currency_reserves_musd']) + \
     (r['2026-08']['foreign_currency_reserves_musd'] - r['2026-07']['foreign_currency_reserves_musd'])
close(fx, -170.2, 0.05, 'MOF FX reserves, May + Aug')
close(fx, -171.6, 3.0, 'MOF FX reserves vs dollars spent (within $3bn)')
# end-April and end-July reserves did not drop, so the trades settled the month after
assert r['2026-04']['foreign_currency_reserves_musd'] >= r['2026-03']['foreign_currency_reserves_musd']
assert abs(r['2026-07']['foreign_currency_reserves_musd'] - r['2026-06']['foreign_currency_reserves_musd']) < 2
print('ok  end-April and end-July reserves flat: settlement in May and August')

# 4. Fed and bill supply
soma = fred('WSHOBL'); b = mspd_bills()
close((nearest(soma, '2026-08-26')[1] - nearest(soma, '2026-02-25')[1]) / 1000, 212.7, 0.05, 'Fed bills, 25 Feb to 26 Aug')
close(b['2026-08'] - b['2026-02'], 440.0, 0.05, 'new bills, end-Feb to end-Aug')

# 5. the long end
y = fred('DGS30')
close((on_or_before(y, '2026-10-07')[1] - on_or_before(y, '2026-08-26')[1]) * 100, 49, 0.5, '30y bp, 26 Aug to 7 Oct')

# 6. the cross-checks added on 5 November
import subprocess, sys, os, csv as _csv
here = os.path.dirname(os.path.abspath(__file__))
for script in ['private_overlay.py', 'custody_check.py', 'funding_check.py']:
    subprocess.run([sys.executable, os.path.join(here, script)], check=True, capture_output=True)
res = os.path.join(here, '..', 'results')
ep = {r['episode']: r for r in _csv.DictReader(open(os.path.join(res, 'episodes_with_private_overlay.csv')))}
close(float(ep['2026 second intervention (30-31 Jul)']['private_foreign_bonds_usd_bn']), -0.9, 0.05, 'private Japanese foreign bonds, Aug 2026 ($bn)')
close(float(ep['2026 first intervention (30 Apr to 6 May)']['private_foreign_bonds_usd_bn']), 19.5, 0.05, 'private Japanese foreign bonds, May 2026 ($bn)')
close(float(ep['2022 intervention (22 Sep, 21 and 24 Oct)']['tic_japan_bonds_bn']), -67.5, 0.05, 'Japan bonds, Sep-Oct 2022')
close(float(ep['2024 June to September (includes the 11-12 July intervention)']['private_foreign_bonds_usd_bn']), 35.8, 0.05, 'private Japanese foreign bonds, Jun-Sep 2024 ($bn)')
cu = list(_csv.DictReader(open(os.path.join(res, 'custody_check.csv'))))
close(float(cu[0]['fed_custody_change_bn']), -55.4, 0.05, 'Fed custody, May window')
close(float(cu[1]['fed_custody_change_bn']), -41.4, 0.05, 'Fed custody, Aug window')
close(float(cu[2]['fed_custody_change_bn']), -46.6, 0.05, 'Fed custody, 26 Aug to 28 Oct')
sf = {r['month']: r for r in _csv.DictReader(open(os.path.join(res, 'sofr_minus_iorb_2026.csv')))}
close(float(sf['2026-05']['avg_bp']), -6.4, 0.05, 'SOFR minus IORB, May average (bp)')
close(float(sf['2026-08']['avg_bp']), -0.8, 0.05, 'SOFR minus IORB, Aug average (bp)')
# what a second August would need from a $31.3bn bill pile
close(96.7 - jp['2026-08']['st_pos'], 65.4, 0.1, 'August-sized defense not covered by bills ($bn)')

# 7. yen side and FIMA (added in the third pass)
subprocess.run([sys.executable, os.path.join(here, 'yen_gains.py')], check=True, capture_output=True)
yg = {r['breakeven_usdjpy']: float(r['realized_gain_yen_tn']) for r in _csv.DictReader(open(os.path.join(res, 'yen_gains.csv')))}
close(yg['115'], 7.40, 0.005, 'realized yen gain at 115 break-even (Y tn)')
h41 = list(_csv.DictReader(open(os.path.join(here, '..', 'data', 'h41_transcribed.csv'))))
fima = max(float(r['foreign_official_repo_week_avg_musd'].replace(',', '')) for r in h41 if '2026-04-30' <= r['release_date'] <= '2026-10-29')
close(fima, 1, 0.5, 'max FIMA week average 30 Apr to 29 Oct ($ million)')
close(31.3 + 60.0, 91.3, 0.05, 'bills plus the whole FIMA cap ($bn)')

# 8. the August gap, the euro area, coupon supply, the funding confound, MOF's own history
for script in ['august_gap.py', 'coupon_supply.py', 'intervention_history.py']:
    subprocess.run([sys.executable, os.path.join(here, script)], check=True, capture_output=True)
ag = {r['month']: r for r in _csv.DictReader(open(os.path.join(res, 'august_gap.csv')))}
close(float(ag['2026-08']['mof_securities_chg']), -87.8, 0.05, 'MOF securities, August ($bn)')
close(float(ag['2026-08']['gap_vs_treasuries']), -50.8, 0.05, 'MOF securities drop not in the Japan Treasury row, August ($bn)')
close(float(ag['2026-08']['gap_vs_all_us_debt']), -49.7, 0.05, 'not in any US debt, August ($bn)')
close(float(ag['2026-08']['bop_reserve_transactions_usd']), -95.0, 0.05, 'BoP reserve-asset transactions, August ($bn)')
assert abs(float(ag['2026-08']['implied_valuation'])) < 2, 'August valuation should be small'
print('ok  August reserve drop is transactions, valuation under $2bn')
ea = {(r['issuer_sector'], r['maturity']): r for r in _csv.DictReader(open(os.path.join(res, 'euro_area_august.csv')))}
close(float(ea[('all sectors', 'all')]['aug_2026']), 2.2, 0.05, 'euro area, non-residents net debt purchases, Aug 2026 (EUR bn)')
assert all(abs(float(r['z'])) < 1 for r in ea.values()), 'some euro-area August series is more than 1 sd from normal'
print('ok  every euro-area August series is within 1 sd of other Augusts')
cs = {r['item']: float(r['bn']) for r in _csv.DictReader(open(os.path.join(res, 'coupon_supply.csv')))}
close(cs['coupon_auctions_aug_sep'], 722, 0.5, 'notes and bonds auctioned Aug-Sep 2026 ($bn)')
close(cs['bonds_20y_plus_aug_sep'], 84, 0.5, '20-year and longer auctioned Aug-Sep 2026 ($bn)')
tg = list(_csv.DictReader(open(os.path.join(res, 'tga_and_reserves_windows.csv'))))
close(float(tg[0]['tga_change_bn']), -152, 0.5, 'TGA, May window ($bn)')
close(float(tg[0]['reserves_change_bn']), 148, 0.5, 'bank reserves, May window ($bn)')
ih = list(_csv.DictReader(open(os.path.join(res, 'intervention_history.csv'))))
close(sum(float(r['yen_tn']) for r in ih if r['year'] == '2022'), 9.19, 0.005, 'MOF 2022 interventions (Y tn)')
close(sum(float(r['yen_tn']) for r in ih if r['year'] == '2024' and r['month'] == 'Jul'), 5.53, 0.01, 'MOF July 2024 intervention (Y tn)')
close(sum(float(r['yen_tn']) for r in ih if r['year'] == '2026'), 11.73, 0.005, 'MOF April-May 2026 (Y tn, Q3 2026 not yet in the file)')

# 9. all Japanese residents together, and the error band (added after the critic read)
for script in ['fefsa_composition.py', 'intervention_gaps.py', 'error_band.py']:
    subprocess.run([sys.executable, os.path.join(here, script)], check=True, capture_output=True)
ar = {r['item']: float(r['usd_bn']) for r in _csv.DictReader(open(os.path.join(res, 'august_all_residents.csv')))}
close(ar['non_us_debt'], -57.1, 0.05, 'non-US debt sold by all Japanese residents, August ($bn)')
eb = list(_csv.DictReader(open(os.path.join(res, 'error_band.csv'))))
assert len(eb) == 7 and sum(r['verdict'] == 'ruled out' for r in eb) == 2
print('ok  error band: 7 sources, 2 ruled out outright')

# 10. every intervention since 2022, on transactions (added in the sixth pass)
ig = {r['month']: r for r in _csv.DictReader(open(os.path.join(res, 'intervention_gaps.csv')))}
assert sum(float(r['gap_mof_only']) < 0 for r in ig.values()) == 5, 'MOF-only gap should be negative in 5 of 6 months'
assert sum(float(r['non_us_all_residents']) < -5 for r in ig.values()) == 4, 'all-resident non-US selling should exceed $5bn in 4 of 6'
print('ok  MOF sold more than US data show in 5 of 6 intervention months; all residents sold >$5bn non-US in 4 of 6')
close(float(ig['2026-08']['gap_mof_only']), -50.0, 0.05, 'Aug 2026 gap on transactions ($bn)')
close(float(ig['2024-05']['gap_mof_only']), -32.0, 0.05, 'May 2024 gap on transactions ($bn)')
close(float(ig['2024-07']['gap_mof_only']), -17.2, 0.05, 'Jul 2024 gap on transactions ($bn)')
close(float(ig['2022-10']['gap_mof_only']), -15.5, 0.05, 'Oct 2022 gap on transactions ($bn)')
close(float(ig['2026-05']['gap_mof_only']), -17.4, 0.05, 'May 2026 gap on transactions ($bn)')
close(float(ig['2026-08']['swap_pct_of_real_money_acq']), 74, 0.5, 'Aug 2026 private swap as % of real-money gross buying')
fc = {r['item']: float(r['value']) for r in _csv.DictReader(open(os.path.join(res, 'fefsa_composition.csv')))}
close(fc['non_government_share'], 0.26, 0.0005, 'FEFSA non-government share of securities')
close(fc['interest_usd_bn_per_month'], 1.7, 0.05, 'FEFSA interest, $bn a month')

# 11. the headline reading vs TIC, and the count without 2022 (added in the seventh pass)
subprocess.run([sys.executable, os.path.join(here, 'headline_vs_actual.py')], check=True, capture_output=True)
hv = {r['month']: r for r in _csv.DictReader(open(os.path.join(res, 'headline_vs_actual.csv')))}
s24 = [float(r['headline_overstated_pct']) for m, r in hv.items() if m >= '2024']
assert len(s24) == 4 and min(s24) == 17 and max(s24) == 58, s24
print('ok  since 2024 the reserves-drop reading overstated Japan-row Treasury selling in 4 of 4 months, by 17 to 58 points of the headline')
x = [r for m, r in ig.items() if m >= '2024']
assert sum(float(r['gap_mof_only']) < 0 for r in x) == 4 and sum(float(r['non_us_all_residents']) < -5 for r in x) == 3
print('ok  without 2022: 4 of 4 on MOF alone, 3 of 4 on the strict count')

# 12. price impact, the next defense, the Treasury share (added in the eighth pass)
for script in ['event_study.py', 'treasury_share.py', 'funding_waterfall.py']:
    subprocess.run([sys.executable, os.path.join(here, script)], check=True, capture_output=True)
ev = {(r['window'], r['measure']): r for r in _csv.DictReader(open(os.path.join(res, 'event_study_since_2024.csv')))}
assert float(ev[('settlement', 'USD/JPY (%)')]['max_change']) < 0, 'yen should strengthen in every settlement week since 2024'
assert int(ev[('settlement', '30-year Treasury (bp)')]['min_percentile']) >= 10 and int(ev[('settlement', '30-year Treasury (bp)')]['max_percentile']) <= 90
assert int(ev[('days', '30-year Treasury (bp)')]['min_percentile']) >= 10 and int(ev[('days', '30-year Treasury (bp)')]['max_percentile']) <= 90
assert float(ev[('settlement', '1-month bill minus SOFR (bp)')]['min_change']) > 0
assert float(ev[('settlement', 'Euro-area govt 10-year, all issuers (bp)')]['max_change']) < 0
sp = ev[('settlement', 'Euro-area govt 10-year minus US 10-year (bp)')]
assert float(sp['min_change']) < 0 < float(sp['max_change']) and int(sp['min_percentile']) >= 10 and int(sp['max_percentile']) <= 90
print('ok  since 2024: yen up every settlement week, 30-year inside its 10th-90th percentile every time, bills cheaper vs SOFR every settlement week, euro-area yields down every settlement week, but no consistent sign against the US 10-year')
ts = {r['settlement_month']: r for r in _csv.DictReader(open(os.path.join(res, 'treasury_share.csv')))}
tx = {k: float(r['treasury_share_pct']) for k, r in ts.items()}
st = {k: float(r['treasury_share_of_stock_fall_pct']) for k, r in ts.items()}
assert [tx[k] for k in sorted(tx)] == [262, 96, 41, 43, 87, 42], tx
assert [st[k] for k in sorted(st) if k >= '2024'] == [47, 81, 83, 42], st
print('ok  Treasury share on transactions: 262, 96, 41, 43, 87, 42; under 100% in 5 of 6; on the stock fall since 2024: 47, 81, 83, 42')
fw = {int(r['yen_tn']): r for r in _csv.DictReader(open(os.path.join(res, 'funding_waterfall.csv')))}
close(float(fw[15]['coupons_or_fima_high']), 40.7, 0.05, 'Y15tn: most left for coupons or FIMA ($bn)')
close(float(fw[10]['coupons_or_fima_high']), 16.7, 0.05, 'Y10tn: most left for coupons or FIMA ($bn)')
close(float(fw[5]['coupons_or_fima_high']), 0.0, 0.05, 'Y5tn: left for coupons or FIMA ($bn)')

# 13. the tenth pass: custody centres, the August bond buying, and numbers new to the text
subprocess.run([sys.executable, os.path.join(here, 'custody_centres.py')], check=True, capture_output=True)
cc = list(_csv.DictReader(open(os.path.join(res, 'custody_centres.csv'))))
close(sum(float(r['net_bn']) for r in cc if r['group'] == 'custody centre'), 21.4, 0.05, 'custody centres net, August ($bn)')
close(sum(float(r['falling_lines_bn']) for r in cc if r['group'] == 'custody centre'), -22.8, 0.05, 'falling lines among custody centres ($bn)')
close(sum(float(r['net_bn']) for r in cc if r['group'] == 'other net seller'), -28.5, 0.05, 'every other net-selling country ($bn)')
from common import tic_table3 as _t3
_j = _t3()['Japan']
close(_j['2026-08']['lt_net'], 11.9, 0.05, 'Japan row notes and bonds, August ($bn)')
close(_j['2026-07']['lt_pos'], 1024, 0.5, 'Japan long-term holdings, end-July ($bn)')
for m, v in [('2024-06', 12.0), ('2024-08', 19.2), ('2024-09', 12.3)]:
    close(_j[m]['st_net'], v, 0.05, f'Japan bills {m} ($bn)')
close(float(ig['2026-05']['private_foreign_debt_net']), 18.3, 0.05, 'private Japanese foreign debt, May 2026 ($bn)')
close(float(ig['2026-08']['private_foreign_debt_net']), -7.3, 0.05, 'private Japanese foreign debt, August 2026 ($bn)')

# 14. the eleventh pass: Treasury share bounds, threshold check, yen persistence, capacity
for script in ['fefsa_composition.py', 'treasury_share.py', 'count_thresholds.py', 'yen_persistence.py', 'capacity_countdown.py']:
    subprocess.run([sys.executable, os.path.join(here, script)], check=True, capture_output=True)
fc = {r['item']: float(r['value']) for r in _csv.DictReader(open(os.path.join(res, 'fefsa_composition.csv')))}
close(fc['maturity_up_to_1y_share'], 0.305, 0.0005, 'FEFSA securities maturing within a year (share)')
tb = {r['settlement_month']: r for r in _csv.DictReader(open(os.path.join(res, 'treasury_share_bounds.csv')))}
assert [(int(tb[m]['share_low_pct']), int(tb[m]['share_high_pct'])) for m in sorted(tb)] == \
    [(162, 262), (54, 96), (41, 64), (14, 43), (87, 112), (34, 42)], tb
print('ok  Treasury share bounds: 162-262, 54-96, 41-64, 14-43, 87-112, 34-42; under 100% at the high bound in 4 of 6')
ct = {int(r['threshold_bn']): r for r in _csv.DictReader(open(os.path.join(res, 'count_thresholds.csv')))}
assert all(ct[x]['mof_alone_of_6'] == '5' and ct[x]['strict_of_6'] == '4' for x in (0, 5, 10, 15))
assert ct[20]['mof_alone_of_6'] == '2' and ct[20]['strict_of_6'] == '3'
print('ok  counts hold at 5 of 6 and 4 of 6 for any threshold up to $15bn, and break at $20bn')
yp = {(r['episode'], r['measure'], r['business_days_after_last_trade']): r for r in _csv.DictReader(open(os.path.join(res, 'yen_persistence.csv')))}
kept20 = [int(yp[(e, 'USD/JPY (%)', '20')]['pct_of_settlement_week_move_kept']) for e in ('Apr-May 2024', 'Apr-May 2026', 'Jul 2026')]
assert kept20 == [45, 11, 62], kept20
pc20 = [int(yp[(e, 'USD/JPY (%)', '20')]['percentile_vs_normal']) for e in ('Apr-May 2024', 'Apr-May 2026', 'Jul 2026')]
assert pc20 == [29, 34, 16], pc20
close(float(yp[('Jul 2026', 'USD/JPY (%)', '60')]['change_pct']), -3.66, 0.005, 'USD/JPY, Jul 2026 episode, +60 business days (%)')
print('ok  yen after 20 business days, clean episodes since 2024: 45%, 11%, 62% of the settlement-week move kept; percentiles 29, 34, 16')
cc2 = {r['liquid_pool']: r for r in _csv.DictReader(open(os.path.join(res, 'capacity_countdown.csv')))}
close(float(cc2['bills + FIMA + all deposits']['pool_bn']), 246.5, 0.05, 'liquid pool, bills + FIMA + all deposits ($bn)')
close(float(cc2['bills only']['defenses_if_outside_us_24pct']), 0.4, 0.05, 'August-sized defenses from bills, 24% outside US')
close(float(cc2['bills + FIMA']['defenses_if_outside_us_24pct']), 1.2, 0.05, 'August-sized defenses from bills + FIMA, 24% outside US')
close(float(cc2['bills + FIMA + all deposits']['defenses_if_outside_us_24pct']), 3.3, 0.05, 'August-sized defenses, everything, 24% outside US')

# 15. the twelfth pass: September's securities fall
subprocess.run([sys.executable, os.path.join(here, 'sept_securities.py')], check=True, capture_output=True)
ss = list(_csv.DictReader(open(os.path.join(res, 'sept_securities.csv'))))
est = [float(r['price_and_fx_bn']) for r in ss if r['duration_case'] != 'actual']
act = [float(r['price_and_fx_bn']) for r in ss if r['duration_case'] == 'actual'][0]
close(act, -17.9, 0.05, 'MOF securities, September 2026 ($bn)')
close(min(est), -24.6, 0.05, 'September price and FX, widest loss ($bn)')
close(max(est), -12.2, 0.05, 'September price and FX, smallest loss ($bn)')
assert min(est) <= act <= max(est)
print('ok  September fall sits inside the price-and-FX range')

# 16. the thirteenth pass: the reserve template, auction run-off, Fed lines, the longer yen test
for script in ['reserve_template.py', 'auction_runoff.py', 'fed_lines.py', 'yen_history.py']:
    subprocess.run([sys.executable, os.path.join(here, script)], check=True, capture_output=True)
rt = {r['month']: r for r in _csv.DictReader(open(os.path.join(res, 'reserve_template.csv')))}
s24 = [r for m, r in rt.items() if m >= '2024-01']
assert all(abs(float(r['fwd_long']) - 20.0) < 0.01 for r in s24), 'forward long position should be $20bn every month since 2024'
assert min(float(r['fwd_short']) for r in s24) > -0.01
close(-float(rt['2026-08']['lent_repo_in_section_I']), 188.9, 0.05, 'securities lent or on repo, end-Aug 2026 ($bn)')
close(-float(rt['2026-08']['lent_repo_in_section_I']) + float(rt['2026-07']['lent_repo_in_section_I']), 2.2, 0.05, 'change in lent/repo book, August ($bn)')
close(float(rt['2026-08']['derivatives_net']) - float(rt['2026-07']['derivatives_net']), 0.18, 0.005, 'change in derivatives, August ($bn)')
close(float(rt['2026-08']['gold']), 124.1, 0.05, 'gold, end-Aug ($bn)'); close(float(rt['2026-09']['gold']), 113.6, 0.05, 'gold, end-Sep ($bn)')
ar2 = {r['month']: r for r in _csv.DictReader(open(os.path.join(res, 'auction_runoff.csv')))}
close(float(ar2['2026-05']['net_bn']), -73.9, 0.05, 'foreign and international run-off at auction, May 2026 ($bn)')
assert ar2['2026-05']['rank_most_negative'] == '1' and ar2['2026-08']['rank_most_negative'] == '9' and ar2['2026-06']['rank_most_negative'] == '3'
close(float(ar2['2026-08']['net_bn']), -25.2, 0.05, 'run-off at auction, August 2026 ($bn)')
fl = {(r['line'], r['window']): r for r in _csv.DictReader(open(os.path.join(res, 'fed_lines.csv')))}
for w in ('May window', 'Aug window'):
    r = fl[('foreign repo pool', w)]
    assert float(r['p5_bn']) < float(r['change_bn']) < float(r['p95_bn'])
close(float(fl[('foreign repo pool', 'May window')]['change_bn']), -17.8, 0.05, 'foreign repo pool, May window ($bn)')
close(float(fl[('foreign repo pool', 'Aug window')]['change_bn']), 19.1, 0.05, 'foreign repo pool, Aug window ($bn)')
yh = {(r['episode'], r['business_days_after']): r for r in _csv.DictReader(open(os.path.join(res, 'yen_history.csv')))}
assert [int(yh[(e, '20')]['percentile_vs_after_a_fall']) for e in ('Jun 1998', 'Jul 2026')] == [14, 19]
assert [int(yh[(e, '20')]['percentile_vs_after_a_fall']) for e in ('Dec 1997', 'Apr 1998', 'Apr-May 2024', 'Apr-May 2026')] == [17, 51, 37, 48]
close(float(yh[('Jun 1998', '20')]['yen_tn']), 0.23, 0.005, 'June 1998 joint intervention (Y tn)')
print('ok  template, auction run-off, Fed lines and the 1997-2026 yen test')

# 17. the fourteenth pass: TLT target and CFTC positioning
for script in ['tlt_target.py', 'cftc_positioning.py']:
    subprocess.run([sys.executable, os.path.join(here, script)], check=True, capture_output=True)
tt = {r['case']: r for r in _csv.DictReader(open(os.path.join(res, 'tlt_target.csv')))}
close(float(tt['forward curve']['price_in_12m_usd']), 80.91, 0.005, 'TLT on the forward curve in 12 months ($)')
close(float(tt['unchanged curve']['price_in_12m_usd']), 81.68, 0.005, 'TLT on an unchanged curve ($)')
assert float(tt['target']['price_in_12m_usd']) == 81
close(float(tt['buy_below']['price_in_12m_usd']), 70.43, 0.005, 'TLT Buy below ($)'); close(float(tt['sell_above']['price_in_12m_usd']), 95.29, 0.005, 'TLT Sell above ($)')
cp = {r['contract']: r for r in _csv.DictReader(open(os.path.join(res, 'cftc_positioning.csv')))}
assert int(cp['Ultra UST bond']['leveraged_net']) == -805828 and int(cp['UST bond']['leveraged_net']) == -150393
assert int(cp['Ultra UST bond']['asset_manager_net']) == 858168 and int(cp['UST bond']['asset_manager_net']) == 383981
print('ok  TLT target $81 (forward curve $80.91, unchanged $81.68), Hold band $70.43-$95.29; CFTC positioning 27 Oct')
from common import fred as _fred, on_or_before as _oob
_d30 = _fred('DGS30')
close((_oob(_d30, '2024-09-30')[1] - _oob(_d30, '2024-05-31')[1]) * 100, -51, 0.5, '30-year, end-May to end-Sep 2024, during the 2024 refill (bp)')

# 18. the fifteenth pass: convexity, scenarios, TLT's own positioning, supply and term premium
for script in ['tlt_convexity.py', 'tlt_target.py', 'tlt_flows.py', 'tlt_options.py', 'term_premium.py']:
    subprocess.run([sys.executable, os.path.join(here, script)], check=True, capture_output=True)
cv = {r['shift_bp']: r for r in _csv.DictReader(open(os.path.join(res, 'tlt_convexity.csv')))}
close(float(cv['convexity_years_sq']['full_reprice_pct']), 321, 1, 'TLT convexity rebuilt from holdings (years squared)')
close(float(cv['duration_years']['full_reprice_pct']), 14.90, 0.25, 'holdings duration vs iShares effective duration')
tf = {r['item']: r for r in _csv.DictReader(open(os.path.join(res, 'tlt_flows.csv')))}
close(float(tf['Japan July defense through end-August']['c']), 5.4, 0.05, 'TLT net creations, 29 Jul to end-Aug ($bn)')
close(float(tf['short interest 2026-10-15']['b']), 18.6, 0.05, 'TLT short interest, % of shares, 15 Oct')
close(float(tf['short interest 2025-12-31']['b']), 26.3, 0.05, 'TLT short interest, % of shares, end-2025')
to = {r['item']: r['value'] for r in _csv.DictReader(open(os.path.join(res, 'tlt_options.csv')))}
close(float(to['put_call_open_interest']), 0.51, 0.005, 'TLT put/call open interest, 5 Nov')
close(float(to['30d_skew_vol_pts']), -0.9, 0.05, 'one-month 25-delta skew (vol points)')
tp = {r['model']: r for r in _csv.DictReader(open(os.path.join(res, 'term_premium.csv')))}
close(float(tp['ACM (NY Fed)']['tp10_pct']), 0.68, 0.005, 'ACM 10-year term premium, 3 Nov')
close(float(tp['Kim-Wright (Fed Board)']['tp10_pct']), 0.91, 0.005, 'Kim-Wright 10-year term premium, 30 Oct')
rf = {r['item']: r['value'] for r in _csv.DictReader(open(os.path.join(here, '..', 'data', 'treasury_refunding_2026-11-04.csv')))}
long_new = sum(float(v) for k, v in rf.items() if k.startswith('bond_'))
close(long_new, 111, 0.5, 'new 20- and 30-year bonds, Nov 2026 to Jan 2027 ($bn)')
assert 'at least' in rf['guidance_aug'] and 'at least' not in rf['guidance_nov']
print('ok  refunding: $111bn of 20s and 30s over three months; "at least" dropped on 4 Nov')
print('ok  convexity 321, TLT flows, short interest, options, term premium')

# 19. the sixteenth pass: auctions, buybacks, ETF plumbing, the Fed's long bonds, NAV and duration
for script in ['auction_test.py', 'buybacks_tlt.py', 'tlt_premium.py', 'tlt_fails.py', 'fed_soma_tlt.py', 'tlt_convexity.py', 'mof_q3_check.py']:
    subprocess.run([sys.executable, os.path.join(here, script)], check=True, capture_output=True)
at = list(_csv.DictReader(open(os.path.join(res, 'auction_test.csv'))))
u = {}
for r in sorted(at, key=lambda r: r['window'] != 'during'):
    u.setdefault((r['auction_date'], r['tenor']), r)
dur = sorted(int(r['indirect_percentile']) for r in u.values() if r['window'] == 'during')
ref = sorted(int(r['indirect_percentile']) for r in u.values() if r['window'] == 'refill')
assert len(u) == 35 and len(dur) == 13 and dur[len(dur) // 2] == 52 and min(dur) > 10 and ref[len(ref) // 2] == 80
a20 = {r['auction_date']: r for r in at if r['tenor'] == '20y'}
close(float(a20['2026-09-15']['indirect_share_pct']), 52.5, 0.05, '20-year indirect share, 15 Sep 2026 (%)')
close(float(a20['2026-10-21']['indirect_share_pct']), 58.2, 0.05, '20-year indirect share, 21 Oct 2026 (%)')
am = {r['month']: r for r in _csv.DictReader(open(os.path.join(res, 'auction_test_monthly.csv')))}
assert am['2026-09']['percentile'] == '82' and am['2026-10']['percentile'] == '55'
bb = list(_csv.DictReader(open(os.path.join(res, 'buybacks_tlt.csv'))))
close(sum(float(r['accepted_bn']) for r in bb), 65.1, 0.05, 'long-bucket buybacks accepted since June 2024 ($bn)')
close(sum(float(r['accepted_in_tlt_cusips_bn']) for r in bb), 57.3, 0.05, 'of which in bonds TLT holds ($bn)')
late = [r for r in bb if r['operation_date'] >= '2026-09-24']
assert len(late) == 3 and all(1.7 < float(r['offered_to_accepted']) < 2.6 for r in late)
pr = list(_csv.DictReader(open(os.path.join(res, 'tlt_premium.csv'))))
ev = [float(r['close_vs_nav_bp']) for r in pr if r['episode'] != 'all days']
assert len(ev) == 45; close(min(ev), -3.4, 0.05, 'lowest TLT close vs NAV on intervention days (bp)'); close(max(ev), 28.7, 0.05, 'highest (bp)')
assert sum(int(r['percentile_since_2022']) <= 5 for r in pr if r['episode'] != 'all days') == 2
fa = {r['episode']: r for r in _csv.DictReader(open(os.path.join(res, 'tlt_fails.csv')))}
assert [fa[e]['pctile_vs_10day_windows'] for e in ('Apr-May 2026', 'Jul 2026', 'Apr-May 2024')] == ['26', '31', '95']
fs = {r['as_of']: r for r in _csv.DictReader(open(os.path.join(res, 'fed_soma_tlt.csv')))}
close(float(fs['2026-11-04']['fed_par_bn']), 566.9, 0.05, "Fed's holdings of TLT's bonds ($bn)")
close(float(fs['2026-11-04']['fed_share_pct']), 19.0, 0.05, "Fed's share of their outstanding (%)")
close(float(fs['2026-11-04']['fed_par_bn']) - float(fs['2025-11-05']['fed_par_bn']), 36.3, 0.05, 'change over the year ($bn)')
cv2 = {r['shift_bp']: r for r in _csv.DictReader(open(os.path.join(res, 'tlt_convexity.csv')))}
close(float(cv2['ishares_effective_duration_weighted']['full_reprice_pct']), 14.90, 0.005, "iShares duration column, weighted")
close(float(cv2['ishares_modified_duration_weighted']['full_reprice_pct']), 15.10, 0.005, "iShares modified duration column, weighted")
tl = {r['item']: r['value'] for r in _csv.DictReader(open(os.path.join(here, '..', 'data', 'tlt_2026-11-04.csv')))}
close(float(tl['net_assets_usd']) / 597.1e6, float(tl['nav_usd']), 0.0005, 'NAV = net assets / shares outstanding, 4 Nov')
close((float(tl['close_usd']) / float(tl['nav_usd']) - 1) * 100, 0.03, 0.005, "premium on 4 Nov vs iShares' published 0.03% (%)")
print('ok  auctions, buybacks, TLT plumbing, Fed SOMA, duration columns and the 4 Nov NAV')

# 20. the seventeenth pass: the 20-year anomaly, the Fed's new bonds, buyback offers
for script in ['auction_20y_check.py', 'fed_soma_tlt.py', 'buybacks_tlt.py']:
    subprocess.run([sys.executable, os.path.join(here, script)], check=True, capture_output=True)
a2 = {r['auction_date']: r for r in _csv.DictReader(open(os.path.join(res, 'auction_20y_check.csv')))}
assert a2['2026-09-15']['spread_20s30s_bp'] == '-4' and a2['2026-10-21']['spread_20s30s_bp'] == '-5'
assert all(r['fima_noncomp'] == '0' for r in a2.values())
sp = sorted(int(r['spread_20s30s_bp']) for r in a2.values()); assert sp[len(sp) // 2] == -8
fsp = {r['part']: r for r in _csv.DictReader(open(os.path.join(res, 'fed_soma_tlt_split.csv')))}
assert fsp['new bonds']['bonds'] == '4' and abs(float(fsp['bonds held a year ago']['change_bn'])) < 0.05
bb2 = [r for r in _csv.DictReader(open(os.path.join(res, 'buybacks_tlt.csv')))]
summ = [float(r['offered_bn']) for r in bb2 if '2026-06-01' <= r['operation_date'] <= '2026-08-31']
late2 = [float(r['offered_bn']) for r in bb2 if r['operation_date'] >= '2026-09-24']
offs = sorted(float(r['offered_bn']) for r in bb2)
close(min(summ), 19.9, 0.05, 'smallest summer buyback offer ($bn)'); close(max(summ), 30.5, 0.05, 'largest summer offer ($bn)')
close(min(late2), 10.5, 0.05, 'smallest offer since 24 Sep ($bn)'); close(max(late2), 14.9, 0.05, 'largest since 24 Sep ($bn)')
assert all(x < offs[len(offs) // 2] for x in late2), 'every offer since 24 Sep should sit below the median'
print('ok  20-year check (spread -4/-5bp, FIMA zero), the Fed rise is all new bonds, buyback offers below median')

# 21. the eighteenth pass: the coupon-funded defense, the 2024 refill control, the band on history
for script in ['coupon_episode.py', 'refill_2024_control.py', 'tlt_band_history.py']:
    subprocess.run([sys.executable, os.path.join(here, script)], check=True, capture_output=True)
ce = list(_csv.DictReader(open(os.path.join(res, 'coupon_episode.csv'))))
assert {r['episode'] for r in ce if r['funded_by'] == 'coupons'} == {'Jul 2024'}
j = {r['value']: r for r in ce if r['episode'] == 'Jul 2024' and r['check'] == 'auction'}
assert j['2024-07-11 30y']['percentile'] == '12' and j['2024-08-08 30y']['second_percentile'] == '98' and j['2024-07-17 20y']['percentile'] == '98'
rc = {r['test']: r for r in _csv.DictReader(open(os.path.join(res, 'refill_2024_control.csv')))}
allw = rc['all four-month windows since 1977']
assert allw['predicted_30y_bp'] == '-67' and allw['actual_30y_bp'] == '-51' and allw['residual_bp'] == '16' and allw['percentile'] == '68'
ease = rc['windows where the 2-year fell 75bp or more']
assert ease['residual_bp'] == '19' and ease['percentile'] == '60'
assert rc['ACM term premium change']['actual_30y_bp'] == '-12'
th = {r['sample']: r for r in _csv.DictReader(open(os.path.join(res, 'tlt_band_history.csv')))}
close(float(th['since 2000']['hold_pct']), 86.2, 0.05, 'TLT in the Hold band on 12-month 30-year moves since 2000 (%)')
close(float(th['since 2000']['ledger_band_pct']), 69.5, 0.05, 'in the ledger band since 2000 (%)')
close(float(th['since 1977']['hold_pct']), 73.3, 0.05, 'in the Hold band since 1977 (%)')
print('ok  July 2024 coupon defense, the 2024 refill against the front end, the Hold band on history')

# 22. the nineteenth pass: luck odds, MOF's part of the July 2024 selling, the 20-year ranks
for script in ['coupon_episode.py', 'auction_20y_check.py']:
    subprocess.run([sys.executable, os.path.join(here, script)], check=True, capture_output=True)
od = {r['item']: r['value'] for r in _csv.DictReader(open(os.path.join(res, 'coupon_episode_odds.csv')))}
assert od['window_auctions'] == '13' and od['p_indirect_this_low'] == '0.81' and od['p_dealer_this_high'] == '0.23'
assert od['share_low_pct'] == '14' and od['share_high_pct'] == '43'
close(float(od['mof_tsy_low_bn']), 4.4, 0.05, "MOF's own Treasury sales, July 2024, low ($bn)")
rk = {r['item']: r['value'] for r in _csv.DictReader(open(os.path.join(res, 'auction_20y_rank.csv')))}
assert rk['n'] == '58' and rk['rank_2026_09_15'] == '1' and rk['rank_2026_10_21'] == '3'
close(float(rk['p_adjacent_bottom3']), 0.102, 0.0005, 'chance two of the bottom three come back to back')
print('ok  July 2024 within luck (81%, 23%), MOF 14-43% of it; 20-year ranks 1 and 3 of 58, back to back 10%')

print('\nall tie-outs pass')

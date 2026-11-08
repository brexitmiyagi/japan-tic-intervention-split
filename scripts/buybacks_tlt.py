# Treasury's liquidity buybacks in the 20-to-30-year bucket, and how much of what it bought back sits in TLT.
# holders offer bonds, Treasury picks the cheapest up to a cap and retires them. the amount offered is a
# direct read of how much long-bond supply wanted out at that moment. Treasury publishes the total offered
# per operation, and what it accepted per CUSIP, so I can match acceptances to TLT's 4 Nov holdings but not
# offers. the offered amount is capped by how many offers each dealer may submit, so it isn't the whole
# market's wish to sell.
import os, csv, datetime as dt
from common import DATA, write_csv

ops = [r for r in csv.DictReader(open(os.path.join(DATA, 'treasury_buybacks_operations.csv')))
       if r['security_type'] == 'Nominal Coupons' and r['maturity_bucket'] == '20Y to 30Y' and r['operation_type'] == 'Liquidity Support']
det = list(csv.DictReader(open(os.path.join(DATA, 'treasury_buybacks_security_details.csv'))))
tlt = {r['cusip'] for r in csv.DictReader(open(os.path.join(DATA, 'tlt_holdings_2026-11-04.csv'))) if r['cusip'].startswith('912810')}
windows = [('Apr-May 2024', dt.date(2024, 4, 29), dt.date(2024, 5, 1)), ('Jul 2024', dt.date(2024, 7, 11), dt.date(2024, 7, 12)),
           ('Apr-May 2026', dt.date(2026, 4, 30), dt.date(2026, 5, 6)), ('Jul 2026', dt.date(2026, 7, 30), dt.date(2026, 7, 31))]
rows = []
for o in ops:
    d = dt.date.fromisoformat(o['operation_date'])
    off, acc = float(o['total_par_amt_offered']) / 1e9, float(o['total_par_amt_accepted']) / 1e9
    a_tlt = sum(float(x['par_amt_accepted']) for x in det if x['operation_date'] == o['operation_date']
                and x['operation_start_time_est'] == o['operation_start_time_est'] and x['cusip_nbr'] in tlt) / 1e9
    tag = next((n for n, s, l in windows if s <= d <= l + dt.timedelta(30)), '')
    rows.append([o['operation_date'], round(off, 2), round(acc, 2), round(off / acc, 2) if acc else None, round(a_tlt, 2), tag])
offers = [r[1] for r in rows]
print(f"{len(rows)} long-bucket liquidity buybacks, {rows[0][0]} to {rows[-1][0]}")
print(f"offered per operation: median ${sorted(offers)[len(offers) // 2]:.1f}bn, max ${max(offers):.1f}bn on {rows[offers.index(max(offers))][0]}")
for r in rows:
    if r[5] or r[0] >= '2026-06-01':
        pc = round(sum(x <= r[1] for x in offers) / len(offers) * 100)
        print(f"  {r[0]}: offered ${r[1]:5.1f}bn, accepted ${r[2]:.1f}bn ({r[3]}x), in TLT bonds ${r[4]:.2f}bn, offer pctile {pc} {r[5]}")
since = [r for r in rows if r[0] >= '2024-05-01']
acc_all, acc_tlt = sum(r[2] for r in since), sum(r[4] for r in since)
print(f"since May 2024 Treasury bought back ${acc_all:.1f}bn in this bucket, ${acc_tlt:.1f}bn ({acc_tlt / acc_all * 100:.0f}%) in bonds TLT holds now")
write_csv('buybacks_tlt.csv', ['operation_date', 'offered_bn', 'accepted_bn', 'offered_to_accepted', 'accepted_in_tlt_cusips_bn', 'intervention_window'], rows)

# lead with what holders offered, not the ratio: the ratio fell mostly because Treasury tripled what it takes
summer = [r for r in rows if '2026-06-01' <= r[0] <= '2026-08-31']
late = [r for r in rows if r[0] >= '2026-09-24']
pc = lambda v: round(sum(x <= v for x in offers) / len(offers) * 100)
print(f"offers, June to August 2026: ${min(r[1] for r in summer):.1f}bn to ${max(r[1] for r in summer):.1f}bn, Treasury took ${summer[0][2]:.1f}bn each")
print(f"offers since 24 Sep: ${min(r[1] for r in late):.1f}bn to ${max(r[1] for r in late):.1f}bn (percentiles {', '.join(str(pc(r[1])) for r in late)}), "
      f"Treasury took ${min(r[2] for r in late):.1f}bn to ${max(r[2] for r in late):.1f}bn")

# a weekly cross-check that doesn't come from TIC: Treasuries the New York Fed holds in custody
# for foreign official accounts (H.4.1, FRED WMTSECL1, Wednesday levels). it's every central
# bank that custodies at the Fed, so it's a check on the official total, not on Japan alone.
from common import fred, nearest, tic_table3, write_csv

c = fred('WMTSECL1')
off = tic_table3()['Of Which: Foreign Official']
rows = []
for label, a, b, m in [('May window', '2026-04-29', '2026-05-27', '2026-05'),
                       ('Aug window', '2026-07-29', '2026-08-26', '2026-08')]:
    ch = (nearest(c, b)[1] - nearest(c, a)[1]) / 1000
    rows.append([label, a, b, round(ch, 1), round(off[m]['st_net'], 1), round(off[m]['net'], 1)])
    print(f"{label}: Fed custody {a} to {b} {ch:+.1f}bn | TIC official bills {off[m]['st_net']:+.1f}bn, total {off[m]['net']:+.1f}bn")
after = (nearest(c, '2026-10-28')[1] - nearest(c, '2026-08-26')[1]) / 1000
print(f"after Japan stopped, 26 Aug to 28 Oct: Fed custody {after:+.1f}bn (no MOF intervention in this stretch)")
rows.append(['after, no intervention', '2026-08-26', '2026-10-28', round(after, 1), None, None])
write_csv('custody_check.csv', ['window', 'start', 'end', 'fed_custody_change_bn', 'tic_official_bills_bn', 'tic_official_total_bn'], rows)

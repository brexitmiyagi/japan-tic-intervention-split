# two more H.4.1 lines that could show a defense being funded some other way:
#   the foreign repo pool (reverse repos with foreign official accounts, FRED WREPOFOR), where
#   central banks park dollars overnight. raising dollars early and parking them would push it up.
#   custody holdings of agency debt and MBS for foreign official accounts (FRED WFASECL1). selling
#   agencies held at the Fed would pull it down.
# plus foreign official deposits at the Fed (FRED WDFOL). each window is four Wednesdays, set against
# every four-week change since 2023. all of these cover every foreign central bank, not just Japan.
from common import fred, nearest, write_csv

rows = []
for s, label in [('WREPOFOR', 'foreign repo pool'), ('WFASECL1', 'agency and MBS custody'), ('WDFOL', 'foreign official deposits at the Fed')]:
    x = fred(s)
    ch = sorted((x[i + 4][1] - x[i][1]) / 1000 for i in range(len(x) - 4))
    p5, p50, p95 = ch[int(0.05 * len(ch))], ch[len(ch) // 2], ch[int(0.95 * len(ch))]
    for name, a, b in [('May window', '2026-04-29', '2026-05-27'), ('Aug window', '2026-07-29', '2026-08-26'), ('after, no MOF', '2026-08-26', '2026-10-28')]:
        c = (nearest(x, b)[1] - nearest(x, a)[1]) / 1000
        rows.append([label, name, a, b, round(c, 1), round(p5, 1), round(p50, 1), round(p95, 1)])
        print(f"{label:38s} {name:13s} {c:+6.1f}bn  (normal four weeks since 2023: 5th pct {p5:+.1f}, median {p50:+.1f}, 95th {p95:+.1f})")
write_csv('fed_lines.csv', ['line', 'window', 'from', 'to', 'change_bn', 'p5_bn', 'median_bn', 'p95_bn'], rows)

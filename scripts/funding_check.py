# did Japan's bill selling squeeze US funding? if it did, SOFR should have risen relative to the
# rate the Fed pays on reserves (IORB) in the weeks the trades settled.
#
# careful: this test is confounded. after April tax day the Treasury's cash account (TGA) runs
# down and that cash lands in bank reserves. so May had a big reserve tailwind at exactly the time
# Japan was dumping bills. August is a cleaner month (TGA rising, reserves falling), but the Fed was
# still buying bills until 14 August. I print the TGA and reserves next to the spread so nobody
# reads the calm as proof of anything.
import statistics
from common import fred, nearest, write_csv

s = dict(fred('SOFR')); i = dict(fred('IORB'))
tga = fred('WTREGEN'); res = fred('WRESBAL')
rows = []
for m in range(1, 11):
    xs = [(s[d] - i[d]) * 100 for d in s if d.year == 2026 and d.month == m and d in i]
    rows.append([f"2026-{m:02d}", round(statistics.mean(xs), 1), round(max(xs))])
    print(f"2026-{m:02d}: SOFR minus IORB average {statistics.mean(xs):+.1f}bp, max {max(xs):+.0f}bp")
latest = max(s)
print(f"latest {latest}: {(s[latest]-i[latest])*100:+.0f}bp")
write_csv('sofr_minus_iorb_2026.csv', ['month', 'avg_bp', 'max_bp'], rows)

# the two settlement windows, Wednesday levels, $bn
out = []
for label, a, b in [('May window', '2026-04-29', '2026-05-27'), ('August window', '2026-07-29', '2026-08-26')]:
    t0, t1 = nearest(tga, a)[1] / 1000, nearest(tga, b)[1] / 1000
    r0, r1 = nearest(res, a)[1] / 1000, nearest(res, b)[1] / 1000
    print(f"{label}: TGA {t0:.0f} to {t1:.0f} ({t1-t0:+.0f}), reserves {r0:.0f} to {r1:.0f} ({r1-r0:+.0f})")
    out.append([label, a, b, round(t1 - t0), round(r1 - r0)])
write_csv('tga_and_reserves_windows.csv', ['window', 'from', 'to', 'tga_change_bn', 'reserves_change_bn'], out)

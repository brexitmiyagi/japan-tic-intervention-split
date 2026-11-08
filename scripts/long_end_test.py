# if Japan's selling was what pushed the long end up, the 30-year should rise in the months
# Japan intervened. it should not rise much in the months it did nothing.
from common import fred, on_or_before, write_csv

y = fred('DGS30')
windows = [
    ('intervention, Apr-May', '2026-04-29', '2026-05-29'),
    ('intervention, Jul-Aug', '2026-07-29', '2026-08-26'),
    ('no intervention, 27 Aug to 7 Oct', '2026-08-26', '2026-10-07'),
]
rows = []
for label, a, b in windows:
    ya, yb = on_or_before(y, a)[1], on_or_before(y, b)[1]
    bp = round((yb - ya) * 100)
    rows.append([label, a, ya, b, yb, bp])
    print(f"{label}: {a} {ya:.2f}% -> {b} {yb:.2f}%  = {bp:+d}bp")

peak = max(y, key=lambda x: x[1])
print(f"2026 peak {peak[0]} {peak[1]:.2f}%, latest {y[-1][0]} {y[-1][1]:.2f}%")
write_csv('long_end_test.csv', ['window', 'start', 'start_yield', 'end', 'end_yield', 'change_bp'], rows)
write_csv('dgs30_2026.csv', ['date', 'dgs30'], [[d.isoformat(), v] for d, v in y if d.year == 2026])

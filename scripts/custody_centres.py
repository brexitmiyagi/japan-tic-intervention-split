# could MOF's missing $50 billion be Treasuries it held through a custodian outside Japan?
# if so, the sale shows up in TIC under the custodian's country, not Japan's.
# two tests for August 2026, both from SLT table 3:
#   1. the usual custody centres. their net flow, and the bigger number: every bill or bond line
#      that fell among them, added up, as if all of it were MOF selling and nobody else bought.
#   2. every country in the table that was a net seller of Treasuries in August, Japan left out.
# the custody list is my call. it's the centres the TIC literature usually treats as custody
# locations: the UK, the big euro custodians, Switzerland, Ireland, the Caribbean centres,
# Hong Kong, Singapore, plus Guernsey and Jersey.
from common import tic_table3, write_csv

t = tic_table3()
M = '2026-08'
centres = ['United Kingdom', 'Belgium', 'Luxembourg', 'Switzerland', 'Ireland', 'Guernsey', 'Jersey',
           'Cayman Islands', 'Bermuda', 'Bahamas', 'British Virgin Islands', 'Barbados', 'Curacao',
           'Hong Kong', 'Singapore']
aggregates = {'Total Europe', 'Memo: Euro Area', 'Memo: European Union', 'Total Latin America', 'Total Caribbean',
              'Total Asia', 'Total Africa', 'Total Other', 'All Countries', 'International', 'Total Regional Orgs.',
              'Total IROs', 'Grand Total', 'Of Which: Foreign Official', 'Of Which: Foreign Non-Official'}

rows = []
net_sum = falls = 0.0
for c in centres:
    r = t[c][M]
    lt, st = r['lt_net'] or 0.0, r['st_net'] or 0.0
    fell = min(lt, 0) + min(st, 0)
    net_sum += lt + st
    falls += fell
    rows.append(['custody centre', c, round(lt, 2), round(st, 2), round(lt + st, 2), round(fell, 2)])
    print(f"{c:25s} notes and bonds {lt:+6.2f}  bills {st:+6.2f}  net {lt + st:+6.2f}")
sellers = [c for c in t if c not in centres and c not in aggregates and c != 'Japan' and t[c].get(M) and (t[c][M]['net'] or 0) < 0]
print(f"\ncustody centres together, August: net {net_sum:+.1f}bn")
print(f"every falling bill or bond line among them added up: {falls:.1f}bn (the most that could hide there, if nobody else bought)")
centre_sellers = sum(min((t[c][M]['lt_net'] or 0) + (t[c][M]['st_net'] or 0), 0) for c in centres)
print(f"custody centres that were net sellers: {centre_sellers:.1f}bn")
seller_sum = sum(t[c][M]['net'] for c in sellers)
for c in sorted(sellers, key=lambda c: t[c][M]['net']):
    rows.append(['other net seller', c, round(t[c][M]['lt_net'], 2), round(t[c][M]['st_net'], 2), round(t[c][M]['net'], 2), None])
print(f"every other country that was a net seller in August, Japan left out ({len(sellers)} of them): {seller_sum:.1f}bn, "
      f"biggest {min(sellers, key=lambda c: t[c][M]['net'])} at {min(t[c][M]['net'] for c in sellers):.1f}")
print(f"the August gap to explain: 50.0bn")
write_csv('custody_centres.csv', ['group', 'country', 'notes_bonds_net_bn', 'bills_net_bn', 'net_bn', 'falling_lines_bn'], rows)

# the widest bound: every falling bill or bond line in every country row, Japan left out
widest = sum(min(t[c][M]['lt_net'] or 0, 0) + min(t[c][M]['st_net'] or 0, 0)
             for c in t if c not in aggregates and c != 'Japan' and t[c].get(M))
print(f"custody-centre falling lines plus every other net-selling country: {falls + seller_sum:.1f}bn")
print(f"widest bound, every falling bill or bond line in every country row except Japan: {widest:.1f}bn")

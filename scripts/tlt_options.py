# TLT options at the 5 Nov 2026 close, from Cboe's delayed quotes: who is paying for protection which way.
# two numbers. put/call open interest across every listed expiry. and skew: implied volatility of the
# put with delta closest to -0.25 against the call with delta closest to +0.25, for the expiry nearest
# 30 and nearest 90 calendar days out. positive skew means downside protection costs more.
# careful: open interest doesn't say who's long or short the option, and TLT puts are a standard
# hedge for people who own bonds, so a high put/call isn't a bearish bet by itself.
import os, json, datetime as dt, re
from common import DATA, write_csv

d = json.load(open(os.path.join(DATA, 'cboe_tlt_options_2026-11-05.json')))['data']
asof = dt.date(2026, 11, 5)
opts = []
for o in d['options']:
    m = re.match(r'TLT(\d{6})([CP])(\d{8})', o['option'])
    exp = dt.datetime.strptime(m.group(1), '%y%m%d').date()
    opts.append({'exp': exp, 'cp': m.group(2), 'k': int(m.group(3)) / 1000, 'oi': o['open_interest'] or 0,
                 'vol': o['volume'] or 0, 'iv': o['iv'], 'delta': o['delta']})
poi = sum(o['oi'] for o in opts if o['cp'] == 'P'); coi = sum(o['oi'] for o in opts if o['cp'] == 'C')
pv = sum(o['vol'] for o in opts if o['cp'] == 'P'); cv = sum(o['vol'] for o in opts if o['cp'] == 'C')
print(f"open interest: puts {poi:,.0f}, calls {coi:,.0f}, put/call {poi / coi:.2f}")
print(f"5 Nov volume: puts {pv:,.0f}, calls {cv:,.0f}, put/call {pv / cv:.2f}")
rows = [['put_call_open_interest', round(poi / coi, 2)], ['put_call_volume', round(pv / cv, 2)]]
exps = sorted({o['exp'] for o in opts})
for target in (30, 90):
    e = min(exps, key=lambda x: abs((x - asof).days - target))
    ch = [o for o in opts if o['exp'] == e and o['iv'] and 0.01 < abs(o['delta']) < 0.99]
    p = min((o for o in ch if o['cp'] == 'P'), key=lambda o: abs(o['delta'] + 0.25))
    c = min((o for o in ch if o['cp'] == 'C'), key=lambda o: abs(o['delta'] - 0.25))
    atm = min((o for o in ch if o['cp'] == 'C'), key=lambda o: abs(o['delta'] - 0.5))
    sk = (p['iv'] - c['iv']) * 100
    print(f"{e} ({(e - asof).days}d): 25d put {p['k']} iv {p['iv'] * 100:.1f}%, 25d call {c['k']} iv {c['iv'] * 100:.1f}%, "
          f"skew {sk:+.1f} vol points; at-the-money iv {atm['iv'] * 100:.1f}%")
    rows += [[f'{target}d_expiry', e.isoformat()], [f'{target}d_25d_put_iv_pct', round(p['iv'] * 100, 1)],
             [f'{target}d_25d_call_iv_pct', round(c['iv'] * 100, 1)], [f'{target}d_skew_vol_pts', round(sk, 1)],
             [f'{target}d_atm_iv_pct', round(atm['iv'] * 100, 1)]]
write_csv('tlt_options.csv', ['item', 'value'], rows)

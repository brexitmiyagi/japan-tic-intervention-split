# shared loaders. everything reads from ../data so the scripts run from anywhere.
import os, csv, json, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
RESULTS = os.path.join(HERE, '..', 'results')
os.makedirs(RESULTS, exist_ok=True)


def tic_table3():
    """Treasury TIC SLT table 3. returns {country: {month: dict}} in billions of dollars.
    columns: holdings, net flow (total), LT holdings, LT net flow, LT valuation change,
    ST (bills) holdings, ST net flow. a positive flow is a foreign purchase."""
    out = {}
    with open(os.path.join(DATA, 'slt_table3.txt'), encoding='utf-8', errors='ignore') as f:
        for line in f:
            r = line.rstrip('\n').split('\t')
            if len(r) < 10 or not r[2][:2] == '20':
                continue
            def num(x):
                x = x.strip()
                return None if x in ('', 'n.a.', 'null') else float(x) / 1000.0
            out.setdefault(r[0], {})[r[2]] = dict(
                pos=num(r[3]), net=num(r[4]), lt_pos=num(r[5]), lt_net=num(r[6]),
                lt_val=num(r[7]), st_pos=num(r[8]), st_net=num(r[9]))
    return out


def fred(series):
    rows = []
    with open(os.path.join(DATA, f'fred_{series}.csv')) as f:
        for r in csv.reader(f):
            if r[0][:2] == '20' and r[1] not in ('', '.'):
                rows.append((dt.date.fromisoformat(r[0]), float(r[1])))
    return rows


def nearest(rows, day):
    day = dt.date.fromisoformat(day) if isinstance(day, str) else day
    return min(rows, key=lambda x: abs((x[0] - day).days))


def on_or_before(rows, day):
    day = dt.date.fromisoformat(day) if isinstance(day, str) else day
    return [x for x in rows if x[0] <= day][-1]


def mof_reserves():
    with open(os.path.join(DATA, 'mof_reserves.csv')) as f:
        return {r['month_end']: {k: (float(v) / 1000.0 if v else None) for k, v in r.items() if k.endswith('musd')}
                for r in csv.DictReader(f)}


def mof_interventions():
    with open(os.path.join(DATA, 'mof_interventions.csv')) as f:
        return list(csv.DictReader(f))


def mspd_bills():
    d = json.load(open(os.path.join(DATA, 'mspd_bills.json')))['data']
    return {r['record_date'][:7]: float(r['total_mil_amt']) / 1000.0 for r in d}


def write_csv(name, header, rows):
    with open(os.path.join(RESULTS, name), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

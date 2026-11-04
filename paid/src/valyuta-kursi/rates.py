"""Official exchange rates from the Central Bank of Uzbekistan (cbu.uz) + converter + history CSV.
Usage:
  python rates.py                 # today's main rates
  python rates.py 100 USD         # convert 100 USD to UZS
  python rates.py 1500000 UZS EUR # convert UZS to EUR
  python rates.py --save          # append today's rates to rates_history.csv
"""
import csv, datetime, json, pathlib, sys, urllib.request

URL = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"
MAIN = ["USD", "EUR", "RUB", "KZT", "CNY", "GBP", "TRY"]


def fetch(url=URL):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 rates-script"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return parse(json.loads(r.read().decode("utf-8")))


def parse(data):
    """Return {code: (rate_in_uzs_per_1_unit, diff, date)} from cbu.uz JSON."""
    out = {}
    for x in data:
        nominal = float(x.get("Nominal", 1) or 1)
        out[x["Ccy"]] = (float(x["Rate"]) / nominal, float(x.get("Diff", 0) or 0), x.get("Date", ""))
    return out


def convert(rates, amount, src, dst="UZS"):
    src, dst = src.upper(), dst.upper()
    uzs = amount if src == "UZS" else amount * rates[src][0]
    return uzs if dst == "UZS" else uzs / rates[dst][0]


def main(argv):
    rates = fetch()
    if "--save" in argv:
        f = pathlib.Path("rates_history.csv"); new = not f.exists()
        with f.open("a", newline="", encoding="utf-8") as fh:
            wr = csv.writer(fh)
            if new:
                wr.writerow(["date"] + MAIN)
            wr.writerow([datetime.date.today().isoformat()] + [rates[c][0] for c in MAIN if c in rates])
        print("Saqlandi:", f); return
    if len(argv) >= 2:
        amount, src = float(argv[0].replace(" ", "")), argv[1]
        dst = argv[2] if len(argv) > 2 else "UZS"
        res = convert(rates, amount, src, dst)
        print(f"{amount:,.2f} {src.upper()} = {res:,.2f} {dst.upper()}".replace(",", " ")); return
    date = next(iter(rates.values()))[2]
    print(f"Markaziy bank kursi ({date}):")
    for c in MAIN:
        if c in rates:
            r, d, _ = rates[c]
            print(f"  1 {c} = {r:,.2f} so'm ({'+' if d >= 0 else ''}{d})".replace(",", " "))


if __name__ == "__main__":
    main(sys.argv[1:])

"""Offline test with a saved sample of the cbu.uz response format."""
import json, rates
sample = json.load(open("sample.json", encoding="utf-8"))
r = rates.parse(sample)
assert "USD" in r and r["USD"][0] > 1000
usd = r["USD"][0]
assert abs(rates.convert(r, 100, "USD") - 100 * usd) < 1e-6
assert abs(rates.convert(r, 100 * usd, "UZS", "USD") - 100) < 1e-6
print("TEST OK: 1 USD =", usd)

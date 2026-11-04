# CSV → chiroyli Excel hisobot (grafik bilan)

Kassadan, marketpleysdan yoki Google Sheets'dan olingan sotuv ro'yxatini (CSV) 1 soniyada tayyor hisobotga aylantiradi:
- «Ma'lumot» varag'i: formulali jadval
- «Mahsulotlar» varag'i: har bir mahsulot tushumi + ustunli grafik
- «Oylar» varag'i: oyma-oy tushum

## O'rnatish
```
pip install openpyxl
```

## Ishlatish
```
python report.py sales.csv report.xlsx
```
`sales.csv` namunasi papkada bor. O'z faylingizda ustunlar shunday bo'lsin: `date,product,quantity,price` (sana YYYY-MM-DD ko'rinishida).

💡 Google Sheets'dan: Fayl → Yuklab olish → CSV.

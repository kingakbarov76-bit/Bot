# Markaziy bank valyuta kursi + konvertor (Python)

O'zbekiston Markaziy banki (cbu.uz) rasmiy kurslarini oladi, summani istalgan valyutaga o'giradi va kurslar tarixini CSV faylga yig'adi.

## Ishlatish (Python 3.8+, qo'shimcha kutubxona kerak emas)
```
python rates.py                  # bugungi asosiy kurslar
python rates.py 100 USD          # 100 dollar necha so'm
python rates.py 1500000 UZS EUR  # 1,5 mln so'm necha yevro
python rates.py --save           # bugungi kursni rates_history.csv ga qo'shish
```
💡 Har kuni avtomatik saqlash: Windows «Task Scheduler» yoki Linux `cron` orqali `--save` ni kuniga bir marta ishga tushiring, keyin CSV'ni Excel'da grafikka aylantiring.

`python test_rates.py` internetsiz test (namuna fayl bilan).

⚠️ cbu.uz sayti O'zbekiston ichidan ishonchli ochiladi. Skriptni chet eldagi serverda ishlatsangiz, sayt javob bermasligi mumkin; bunday holatda uni o'z kompyuteringizda ishlating.

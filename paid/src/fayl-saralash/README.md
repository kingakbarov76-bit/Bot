# «Yuklab olinganlar» papkasini avtomatik tartiblash

Yuzlab aralash faylni turiga qarab papkalarga ajratadi: Rasmlar, Videolar, Hujjatlar, Jadvallar, Arxivlar, Dasturlar, Kod, Musiqa, Boshqa.

**Xavfsiz:**
- `--dry-run` avval nima bo'lishini ko'rsatadi, hech narsani ko'chirmaydi;
- bir xil nomli fayl ustidan yozmaydi (`fayl (1).pdf` qiladi);
- `--undo` hammasini joyiga qaytaradi.

## Ishlatish (Python 3.8+, qo'shimcha kutubxona kerak emas)
```
python organize.py "C:/Users/Ism/Downloads" --dry-run
python organize.py "C:/Users/Ism/Downloads"
python organize.py "C:/Users/Ism/Downloads" --undo
```
💡 Toifalarni `TYPES` ro'yxatida o'zgartirasiz.

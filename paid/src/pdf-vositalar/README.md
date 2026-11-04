# PDF vositalari: birlashtirish, bo'lish, sahifa ajratish, aylantirish, parol

Onlayn saytlarga hujjat yuklamasdan (maxfiylik!), o'z kompyuteringizda PDF bilan ishlash.

## O'rnatish
```
pip install pypdf cryptography
```

## Buyruqlar
| Vazifa | Buyruq |
|---|---|
| Bir nechta PDF'ni bitta qilish | `python pdftool.py merge natija.pdf 1.pdf 2.pdf` |
| Har sahifani alohida faylga | `python pdftool.py split kitob.pdf sahifalar/` |
| Kerakli sahifalarni olish | `python pdftool.py extract kitob.pdf 3-7,10 qism.pdf` |
| Aylantirish (90/180/270) | `python pdftool.py rotate skan.pdf 90 tuzatilgan.pdf` |
| Parol qo'yish | `python pdftool.py protect hujjat.pdf parol123 himoyali.pdf` |
| Ma'lumot | `python pdftool.py info hujjat.pdf` |

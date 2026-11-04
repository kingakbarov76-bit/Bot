# Rasmlarni ommaviy kichraytirish + logo yozuvi + format o'zgartirish

Yuzlab mahsulot rasmini bir buyruq bilan:
- kerakli kenglikka kichraytiradi (masalan 1080 px, Instagram uchun),
- burchagiga brend yozuvini (watermark) qo'shadi,
- JPG / PNG / WEBP ga aylantiradi (WEBP sayt uchun 3 baravar yengil).

## O'rnatish
```
pip install pillow
```

## Ishlatish
```
python images.py rasmlar natija --width 1080 --watermark "@dokonim" --format jpg
```
- `rasmlar` - asl rasmlar papkasi
- `natija` - tayyor rasmlar shu yerga tushadi (asl rasmlar o'zgarmaydi)
- `--quality 85` - sifat (60-95)

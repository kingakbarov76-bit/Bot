"""Batch image tool: resize, add a text watermark and convert (JPG/PNG/WEBP) every image in a folder.
Usage: python images.py INPUT_DIR OUTPUT_DIR --width 1080 --watermark "@mybrand" --format webp
"""
import argparse, pathlib
from PIL import Image, ImageDraw, ImageFont, ImageOps

EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def load_font(size):
    for name in ("DejaVuSans-Bold.ttf", "arialbd.ttf", "Arial Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def process(path, out_dir, width, mark, fmt, quality):
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGBA")
    if width and im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    if mark:
        layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        font = load_font(max(18, im.width // 28))
        box = d.textbbox((0, 0), mark, font=font)
        tw, th = box[2] - box[0], box[3] - box[1]
        x, y = im.width - tw - im.width // 40, im.height - th - im.height // 30
        d.text((x + 2, y + 2), mark, font=font, fill=(0, 0, 0, 110))
        d.text((x, y), mark, font=font, fill=(255, 255, 255, 190))
        im = Image.alpha_composite(im, layer)
    out = out_dir / (path.stem + "." + fmt)
    if fmt in ("jpg", "jpeg"):
        im.convert("RGB").save(out, "JPEG", quality=quality, optimize=True)
    elif fmt == "webp":
        im.save(out, "WEBP", quality=quality)
    else:
        im.save(out, "PNG", optimize=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input"); ap.add_argument("output")
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--watermark", default="")
    ap.add_argument("--format", default="jpg", choices=["jpg", "png", "webp"])
    ap.add_argument("--quality", type=int, default=85)
    a = ap.parse_args()
    out = pathlib.Path(a.output); out.mkdir(parents=True, exist_ok=True)
    files = [p for p in sorted(pathlib.Path(a.input).iterdir()) if p.suffix.lower() in EXT]
    for p in files:
        r = process(p, out, a.width, a.watermark, a.format, a.quality)
        print("✓", r.name)
    print(f"Tayyor: {len(files)} ta rasm → {out}")


if __name__ == "__main__":
    main()

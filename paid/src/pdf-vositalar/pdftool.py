"""PDF toolbox: merge, split, extract pages, rotate, protect with password, show info.
Examples:
  python pdftool.py merge out.pdf a.pdf b.pdf c.pdf
  python pdftool.py split book.pdf parts/
  python pdftool.py extract book.pdf 3-7,10 out.pdf
  python pdftool.py rotate scan.pdf 90 out.pdf
  python pdftool.py protect doc.pdf secret123 out.pdf
  python pdftool.py info doc.pdf
"""
import pathlib, sys
from pypdf import PdfReader, PdfWriter


def pages_from_spec(spec, n):
    result = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-"); result += list(range(int(a), int(b) + 1))
        else:
            result.append(int(part))
    bad = [p for p in result if p < 1 or p > n]
    if bad:
        raise SystemExit(f"Bunday sahifa yo'q: {bad} (jami {n} sahifa)")
    return [p - 1 for p in result]


def merge(out, *files):
    w = PdfWriter()
    for f in files:
        for p in PdfReader(f).pages:
            w.add_page(p)
    w.write(out); print(f"Birlashtirildi: {out}")


def split(src, folder):
    d = pathlib.Path(folder); d.mkdir(parents=True, exist_ok=True)
    r = PdfReader(src)
    for i, p in enumerate(r.pages, 1):
        w = PdfWriter(); w.add_page(p); w.write(d / f"page_{i:03d}.pdf")
    print(f"{len(r.pages)} ta faylga bo'lindi: {d}")


def extract(src, spec, out):
    r = PdfReader(src); w = PdfWriter()
    for i in pages_from_spec(spec, len(r.pages)):
        w.add_page(r.pages[i])
    w.write(out); print(f"Ajratildi: {out}")


def rotate(src, deg, out):
    r = PdfReader(src); w = PdfWriter()
    for p in r.pages:
        w.add_page(p.rotate(int(deg)))
    w.write(out); print(f"Aylantirildi: {out}")


def protect(src, password, out):
    r = PdfReader(src); w = PdfWriter()
    for p in r.pages:
        w.add_page(p)
    w.encrypt(password, algorithm="AES-256")
    w.write(out); print(f"Parol qo'yildi: {out}")


def info(src, password=""):
    r = PdfReader(src)
    if r.is_encrypted:
        if not password or not r.decrypt(password):
            print("Fayl parol bilan himoyalangan. Ko'rish uchun: python pdftool.py info fayl.pdf PAROL"); return
    print(f"Sahifalar: {len(r.pages)}; shifrlangan: {r.is_encrypted}; meta: {dict(r.metadata or {})}")


if __name__ == "__main__":
    cmds = {"merge": merge, "split": split, "extract": extract, "rotate": rotate, "protect": protect, "info": info}
    if len(sys.argv) < 3 or sys.argv[1] not in cmds:
        print(__doc__); sys.exit(1)
    cmds[sys.argv[1]](*sys.argv[2:])

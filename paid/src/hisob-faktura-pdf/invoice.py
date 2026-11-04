"""Generate a clean invoice PDF from a JSON file.
Usage: python invoice.py invoice.json invoice.pdf
"""
import json, sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle

from reportlab.lib.fonts import addMapping
FONT = "Helvetica"
for reg, bold in (("DejaVuSans.ttf", "DejaVuSans-Bold.ttf"),
                  ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
                  ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf")):
    try:
        pdfmetrics.registerFont(TTFont("Main", reg)); pdfmetrics.registerFont(TTFont("Main-Bold", bold))
        addMapping("Main", 0, 0, "Main"); addMapping("Main", 1, 0, "Main-Bold")
        FONT = "Main"; break
    except Exception:
        continue


def money(n, cur):
    return f"{n:,.0f}".replace(",", " ") + f" {cur}"


def build(data, out):
    cur = data.get("currency", "so'm")
    st = ParagraphStyle("n", fontName=FONT, fontSize=10, leading=14)
    big = ParagraphStyle("b", fontName=FONT, fontSize=20, leading=24, textColor=colors.HexColor("#1F4E78"))
    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm)
    s = data["seller"]; b = data["buyer"]
    els = [Paragraph(f"HISOB-FAKTURA № {data['number']}", big), Paragraph(f"Sana: {data['date']}", st), Spacer(1, 8 * mm)]
    parties = Table([[Paragraph(f"<b>Sotuvchi</b><br/>{s['name']}<br/>{s.get('address','')}<br/>{s.get('phone','')}<br/>STIR: {s.get('tin','')}", st),
                      Paragraph(f"<b>Xaridor</b><br/>{b['name']}<br/>{b.get('address','')}<br/>{b.get('phone','')}", st)]], colWidths=[87 * mm, 87 * mm])
    els += [parties, Spacer(1, 8 * mm)]
    rows = [["#", "Nomi", "Soni", "Narxi", "Summa"]]
    total = 0
    for i, it in enumerate(data["items"], 1):
        sm = it["qty"] * it["price"]; total += sm
        rows.append([i, Paragraph(it["name"], st), it["qty"], money(it["price"], cur), money(sm, cur)])
    vat = total * data.get("vat_percent", 0) / 100
    rows += [["", "", "", "Jami:", money(total, cur)]]
    if vat:
        rows += [["", "", "", f"QQS {data['vat_percent']}%:", money(vat, cur)], ["", "", "", "To'lovga:", money(total + vat, cur)]]
    t = Table(rows, colWidths=[10 * mm, 76 * mm, 18 * mm, 34 * mm, 36 * mm])
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), FONT, 10),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, len(data["items"])), 0.5, colors.HexColor("#BBBBBB")),
        ("ALIGN", (2, 1), (-1, -1), "RIGHT"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, len(data["items"])), [colors.white, colors.HexColor("#F2F6FA")]),
    ]))
    els += [t, Spacer(1, 10 * mm), Paragraph(data.get("note", ""), st), Spacer(1, 14 * mm),
            Paragraph("Imzo: ____________________          M.O'.", st)]
    doc.build(els)
    return total + vat


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "invoice.json"
    out = sys.argv[2] if len(sys.argv) > 2 else "invoice.pdf"
    print("Tayyor:", out, "| to'lovga:", build(json.load(open(src, encoding="utf-8")), out))

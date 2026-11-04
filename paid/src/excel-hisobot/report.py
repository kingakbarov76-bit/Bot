"""Turn a sales CSV into a formatted Excel report with summaries and a chart.
Usage: python report.py sales.csv report.xlsx
CSV columns: date (YYYY-MM-DD), product, quantity, price
"""
import csv, sys
from collections import defaultdict
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

HEAD = PatternFill("solid", fgColor="1F4E78")
WHITE = Font(bold=True, color="FFFFFF")


def style_header(ws, row=1):
    for c in ws[row]:
        c.fill, c.font, c.alignment = HEAD, WHITE, Alignment(horizontal="center")


def autosize(ws):
    for col in ws.columns:
        width = max(len(str(c.value or "")) for c in col) + 3
        ws.column_dimensions[get_column_letter(col[0].column)].width = min(width, 40)


def build(src, dst):
    rows = list(csv.DictReader(open(src, encoding="utf-8-sig")))
    wb = Workbook()
    ws = wb.active; ws.title = "Ma'lumot"
    ws.append(["Sana", "Mahsulot", "Soni", "Narxi", "Summa"])
    for i, r in enumerate(rows, start=2):
        ws.append([r["date"], r["product"], int(r["quantity"]), int(r["price"]), f"=C{i}*D{i}"])
    style_header(ws); autosize(ws)
    for row in ws.iter_rows(min_row=2, min_col=4, max_col=5):
        for c in row:
            c.number_format = "#,##0"

    by_product, by_month = defaultdict(int), defaultdict(int)
    for r in rows:
        s = int(r["quantity"]) * int(r["price"])
        by_product[r["product"]] += s
        by_month[r["date"][:7]] += s

    sp = wb.create_sheet("Mahsulotlar")
    sp.append(["Mahsulot", "Tushum"])
    for k, v in sorted(by_product.items(), key=lambda x: -x[1]):
        sp.append([k, v])
    sp.append(["JAMI", f"=SUM(B2:B{sp.max_row})"])
    sp.cell(sp.max_row, 1).font = Font(bold=True)
    style_header(sp); autosize(sp)
    for c in sp["B"][1:]:
        c.number_format = "#,##0"
    ch = BarChart(); ch.title = "Mahsulotlar bo'yicha tushum"; ch.height, ch.width = 8, 16
    ch.add_data(Reference(sp, min_col=2, min_row=1, max_row=sp.max_row - 1), titles_from_data=True)
    ch.set_categories(Reference(sp, min_col=1, min_row=2, max_row=sp.max_row - 1))
    sp.add_chart(ch, "D2")

    sm = wb.create_sheet("Oylar")
    sm.append(["Oy", "Tushum"])
    for k in sorted(by_month):
        sm.append([k, by_month[k]])
    style_header(sm); autosize(sm)
    wb.save(dst)
    return sum(by_product.values())


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "sales.csv"
    dst = sys.argv[2] if len(sys.argv) > 2 else "report.xlsx"
    total = build(src, dst)
    print(f"Tayyor: {dst} (jami tushum: {total:,})")

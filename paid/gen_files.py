# 10 ta fayl: 6 Excel, 3 Word, 1 PDF
import datetime as dt, os
from openpyxl import Workbook
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

OUT = "/home/claude/bot/paid/files"; os.makedirs(OUT, exist_ok=True)
H = PatternFill("solid", fgColor="1F4E78"); HW = Font(bold=True, color="FFFFFF")
IN = PatternFill("solid", fgColor="FFF2CC")  # kiritiladigan kataklar
TOT = PatternFill("solid", fgColor="DDEBF7")
thin = Side(style="thin", color="BFBFBF"); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
NUM = '#,##0'

def head(ws, row, cols, widths=None):
    for i, t in enumerate(cols, 1):
        c = ws.cell(row, i, t); c.fill, c.font = H, HW; c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True); c.border = BOX
    if widths:
        for i, wd in enumerate(widths, 1): ws.column_dimensions[get_column_letter(i)].width = wd

def title(ws, text, sub=""):
    ws["A1"] = text; ws["A1"].font = Font(bold=True, size=16, color="1F4E78")
    if sub: ws["A2"] = sub; ws["A2"].font = Font(italic=True, color="7F7F7F")

def box(ws, rng):
    for row in ws[rng]:
        for c in row: c.border = BOX

# ---------------------------------------------------------------- F1 Oylik byudjet
wb = Workbook(); ws = wb.active; ws.title = "Byudjet"
title(ws, "Oylik oilaviy byudjet", "Sariq kataklarni to'ldiring. Qolganlari avtomatik hisoblanadi.")
ws["A4"] = "Oy:"; ws["B4"] = "Noyabr 2026"; ws["B4"].fill = IN
head(ws, 6, ["Daromad manbai", "Reja", "Fakt"], [30, 16, 16, 16, 12])
inc = [("Asosiy ish haqi", 8000000, 8000000), ("Qo'shimcha daromad", 2000000, 1500000), ("Boshqa", 0, 300000)]
for i, (n, r, f) in enumerate(inc, 7):
    ws.cell(i, 1, n); ws.cell(i, 2, r).fill = IN; ws.cell(i, 3, f).fill = IN
ws["A10"] = "JAMI DAROMAD"; ws["B10"] = "=SUM(B7:B9)"; ws["C10"] = "=SUM(C7:C9)"
for c in ("A10", "B10", "C10"): ws[c].font = Font(bold=True); ws[c].fill = TOT
box(ws, "A6:C10")
head(ws, 12, ["Xarajat toifasi", "Reja", "Fakt", "Farq", "% fakt"])
exp = [("Uy-joy (ijara/kredit)", 3000000, 3000000), ("Kommunal to'lovlar", 600000, 720000), ("Oziq-ovqat", 2500000, 2800000),
       ("Transport", 500000, 450000), ("Aloqa va internet", 150000, 150000), ("Kiyim", 400000, 250000), ("Sog'liq", 300000, 120000),
       ("Ta'lim", 500000, 500000), ("Ko'ngilochar", 400000, 350000), ("Jamg'arma", 1400000, 1000000), ("Boshqa", 200000, 310000)]
r0 = 13
for i, (n, r, f) in enumerate(exp, r0):
    ws.cell(i, 1, n); ws.cell(i, 2, r).fill = IN; ws.cell(i, 3, f).fill = IN
    ws.cell(i, 4, f"=B{i}-C{i}"); ws.cell(i, 5, f"=IF($C${r0 + len(exp)}=0,0,C{i}/$C${r0 + len(exp)})")
    ws.cell(i, 5).number_format = "0.0%"
t = r0 + len(exp)
ws.cell(t, 1, "JAMI XARAJAT"); ws.cell(t, 2, f"=SUM(B{r0}:B{t - 1})"); ws.cell(t, 3, f"=SUM(C{r0}:C{t - 1})"); ws.cell(t, 4, f"=B{t}-C{t}")
for col in range(1, 6): ws.cell(t, col).font = Font(bold=True); ws.cell(t, col).fill = TOT
box(ws, f"A12:E{t}")
ws.cell(t + 2, 1, "QOLDIQ (daromad − xarajat)").font = Font(bold=True, size=12)
ws.cell(t + 2, 2, f"=B10-B{t}"); ws.cell(t + 2, 3, f"=C10-C{t}")
ws.cell(t + 3, 1, "Jamg'arma ulushi (fakt)"); ws.cell(t + 3, 3, f"=IF(C10=0,0,(C22+C{t + 2})/C10)"); ws.cell(t + 3, 3).number_format = "0.0%"
for row in ws.iter_rows(min_row=7, max_row=t + 2, min_col=2, max_col=4):
    for c in row:
        if c.number_format != "0.0%": c.number_format = NUM
ws.conditional_formatting.add(f"D{r0}:D{t}", CellIsRule(operator="lessThan", formula=["0"], font=Font(color="C00000", bold=True)))
ws.conditional_formatting.add(f"B{t + 2}:C{t + 2}", CellIsRule(operator="lessThan", formula=["0"], fill=PatternFill("solid", fgColor="F8CBAD")))
pie = PieChart(); pie.title = "Xarajatlar tarkibi (fakt)"; pie.height, pie.width = 9, 12
pie.add_data(Reference(ws, min_col=3, min_row=12, max_row=t - 1), titles_from_data=True)
pie.set_categories(Reference(ws, min_col=1, min_row=r0, max_row=t - 1)); ws.add_chart(pie, "G4")
ws.freeze_panes = "A7"
wb.save(f"{OUT}/Oylik_byudjet.xlsx")

# ---------------------------------------------------------------- F2 Mini CRM
wb = Workbook(); ws = wb.active; ws.title = "Mijozlar"
title(ws, "Mini CRM: mijozlar va sotuvlar", "Holat va manbani ro'yxatdan tanlang. «Keyingi qadam» sanasi o'tib ketsa, qator qizaradi.")
cols = ["№", "Ism / kompaniya", "Telefon", "Manba", "Holat", "Summa (so'm)", "Murojaat sanasi", "Keyingi qadam", "Keyingi qadam sanasi", "Izoh"]
head(ws, 4, cols, [5, 24, 17, 13, 18, 15, 15, 26, 16, 30])
src = ["Instagram", "Telegram", "Tavsiya", "Reklama", "Sayt", "Boshqa"]
st = ["Yangi", "Muloqotda", "Taklif yuborildi", "Sotildi", "Rad etdi"]
today = dt.date(2026, 11, 4)
sample = [("Dilnoza (Gul do'koni)", "+998 90 111 22 33", "Instagram", "Sotildi", 1500000, -10, "Qayta sotuv: aksiya taklifi", 20),
          ("Sardor Logistics", "+998 91 222 33 44", "Tavsiya", "Taklif yuborildi", 4500000, -5, "Qo'ng'iroq: qaror", -1),
          ("Aziza", "+998 93 333 44 55", "Telegram", "Muloqotda", 800000, -2, "Narx ro'yxatini yuborish", 1),
          ("Javohir (kafe)", "+998 94 444 55 66", "Reklama", "Yangi", 0, 0, "Tanishuv qo'ng'irog'i", 0),
          ("Madina", "+998 95 555 66 77", "Sayt", "Rad etdi", 0, -15, "-", 0)]
for i, (n, ph, s, h, sm, d1, nx, d2) in enumerate(sample, 5):
    ws.append([i - 4, n, ph, s, h, sm, today + dt.timedelta(days=d1), nx, (today + dt.timedelta(days=d2)) if nx != "-" else None, ""])
last = 300
for r in range(5, last + 1):
    if r > 9: ws.cell(r, 1, f'=IF(B{r}="","",ROW()-4)')
    ws.cell(r, 6).number_format = NUM; ws.cell(r, 7).number_format = "DD.MM.YYYY"; ws.cell(r, 9).number_format = "DD.MM.YYYY"
dv1 = DataValidation(type="list", formula1='"' + ",".join(src) + '"', allow_blank=True); dv2 = DataValidation(type="list", formula1='"' + ",".join(st) + '"', allow_blank=True)
ws.add_data_validation(dv1); ws.add_data_validation(dv2); dv1.add(f"D5:D{last}"); dv2.add(f"E5:E{last}")
ws.conditional_formatting.add(f"A5:J{last}", FormulaRule(formula=[f'AND($I5<>"",$I5<TODAY(),$E5<>"Sotildi",$E5<>"Rad etdi")'], fill=PatternFill("solid", fgColor="F8CBAD")))
ws.conditional_formatting.add(f"E5:E{last}", CellIsRule(operator="equal", formula=['"Sotildi"'], fill=PatternFill("solid", fgColor="C6EFCE")))
ws.conditional_formatting.add(f"E5:E{last}", CellIsRule(operator="equal", formula=['"Rad etdi"'], font=Font(color="7F7F7F")))
ws.freeze_panes = "C5"; ws.auto_filter.ref = f"A4:J{last}"
d = wb.create_sheet("Hisobot"); title(d, "Sotuv hisoboti (avtomatik)")
head(d, 3, ["Holat", "Mijozlar soni", "Summa"], [22, 16, 18])
for i, s in enumerate(st, 4):
    d.cell(i, 1, s); d.cell(i, 2, f'=COUNTIF(Mijozlar!$E$5:$E${last},A{i})'); d.cell(i, 3, f'=SUMIF(Mijozlar!$E$5:$E${last},A{i},Mijozlar!$F$5:$F${last})'); d.cell(i, 3).number_format = NUM
d.cell(9, 1, "JAMI").font = Font(bold=True); d.cell(9, 2, "=SUM(B4:B8)"); d.cell(9, 3, "=SUM(C4:C8)"); d.cell(9, 3).number_format = NUM
d.cell(11, 1, "Konversiya (sotildi / jami)"); d.cell(11, 2, '=IF(B9=0,0,B7/B9)'); d.cell(11, 2).number_format = "0%"
d.cell(12, 1, "O'rtacha chek"); d.cell(12, 2, '=IF(B7=0,0,C7/B7)'); d.cell(12, 2).number_format = NUM
d.cell(13, 1, "Muddati o'tgan vazifalar"); d.cell(13, 2, f'=COUNTIFS(Mijozlar!$I$5:$I${last},"<"&TODAY(),Mijozlar!$E$5:$E${last},"<>Sotildi",Mijozlar!$E$5:$E${last},"<>Rad etdi")')
head(d, 15, ["Manba", "Mijozlar", "Sotildi"])
for i, s in enumerate(src, 16):
    d.cell(i, 1, s); d.cell(i, 2, f'=COUNTIF(Mijozlar!$D$5:$D${last},A{i})'); d.cell(i, 3, f'=COUNTIFS(Mijozlar!$D$5:$D${last},A{i},Mijozlar!$E$5:$E${last},"Sotildi")')
box(d, "A3:C9"); box(d, "A15:C21")
ch = BarChart(); ch.title = "Mijozlar manbasi"; ch.height, ch.width = 8, 14
ch.add_data(Reference(d, min_col=2, min_row=15, max_row=21), titles_from_data=True); ch.set_categories(Reference(d, min_col=1, min_row=16, max_row=21)); d.add_chart(ch, "E3")
wb.save(f"{OUT}/Mini_CRM.xlsx")

# ---------------------------------------------------------------- F3 30 kunlik kontent reja
wb = Workbook(); ws = wb.active; ws.title = "Kontent reja"
title(ws, "30 kunlik kontent reja (Instagram / Telegram)", "B3 ga boshlanish sanasini yozing: sanalar va hafta kunlari avtomatik o'zgaradi.")
ws["A3"] = "Boshlanish:"; ws["B3"] = dt.date(2026, 11, 5); ws["B3"].number_format = "DD.MM.YYYY"; ws["B3"].fill = IN
head(ws, 5, ["Kun", "Sana", "Hafta kuni", "Platforma", "Format", "Mavzu / g'oya", "Maqsad", "Chaqiriq (CTA)", "Holat"], [6, 12, 12, 13, 12, 46, 14, 26, 14])
ideas = [("Reels", "O'zingiz va biznesingiz haqida 15 soniyada", "Tanishuv", "Obuna bo'ling"),
         ("Carousel", "Mijozlar ko'p beradigan 5 savol va javob", "Ishonch", "Savolingizni yozing"),
         ("Stories", "So'rovnoma: qaysi mahsulot qiziqroq?", "Faollik", "Ovoz bering"),
         ("Reels", "Jarayon ortidan: mahsulot qanday tayyorlanadi", "Ishonch", "Saqlab qo'ying"),
         ("Post", "Mijoz natijasi (ruxsat bilan, haqiqiy)", "Sotuv", "Direktga yozing"),
         ("Reels", "3 ta keng tarqalgan xato va ularning yechimi", "Foyda", "Do'stingizga yuboring"),
         ("Stories", "Savol-javob: «Menga savol bering»", "Faollik", "Savol qoldiring")]
dv_p = DataValidation(type="list", formula1='"Instagram,Telegram,TikTok,YouTube,Hammasi"'); dv_f = DataValidation(type="list", formula1='"Reels,Post,Carousel,Stories,Live,Video"')
dv_s = DataValidation(type="list", formula1='"Reja,Tayyorlanmoqda,Tayyor,Chiqdi"'); dv_g = DataValidation(type="list", formula1='"Tanishuv,Ishonch,Foyda,Faollik,Sotuv"')
for v in (dv_p, dv_f, dv_s, dv_g): ws.add_data_validation(v)
for k in range(30):
    r = 6 + k; f, t, g, c = ideas[k % len(ideas)]
    ws.append([k + 1, f"=$B$3+{k}", f'=CHOOSE(WEEKDAY(B{r},2),"Dushanba","Seshanba","Chorshanba","Payshanba","Juma","Shanba","Yakshanba")', "Instagram", f, t, g, c, "Reja"])
    ws.cell(r, 2).number_format = "DD.MM.YYYY"
dv_p.add("D6:D35"); dv_f.add("E6:E35"); dv_s.add("I6:I35"); dv_g.add("G6:G35")
for val, col in (("Chiqdi", "C6EFCE"), ("Tayyor", "DDEBF7"), ("Tayyorlanmoqda", "FFF2CC")):
    ws.conditional_formatting.add("I6:I35", CellIsRule(operator="equal", formula=[f'"{val}"'], fill=PatternFill("solid", fgColor=col)))
box(ws, "A5:I35"); ws.freeze_panes = "A6"
ws["K5"] = "Holat"; ws["L5"] = "Soni"; ws["K5"].font = ws["L5"].font = Font(bold=True)
for i, s in enumerate(["Reja", "Tayyorlanmoqda", "Tayyor", "Chiqdi"], 6):
    ws.cell(i, 11, s); ws.cell(i, 12, f'=COUNTIF($I$6:$I$35,K{i})')
ws.cell(10, 11, "Bajarildi %"); ws.cell(10, 12, "=L9/30"); ws.cell(10, 12).number_format = "0%"
wb.save(f"{OUT}/Kontent_reja_30_kun.xlsx")

# ---------------------------------------------------------------- F4 Ombor hisobi
wb = Workbook(); m = wb.active; m.title = "Mahsulotlar"
title(m, "Ombor hisobi: kirim, chiqim, qoldiq", "1) Mahsulotlarni kiriting  2) Kirim va Chiqim varaqlariga yozing  3) Qoldiq avtomatik hisoblanadi.")
head(m, 4, ["Kod", "Mahsulot", "Birlik", "Min. qoldiq", "Tannarx", "Sotuv narxi", "Kirim", "Chiqim", "Qoldiq", "Qoldiq qiymati", "Holat"], [9, 26, 8, 11, 12, 12, 9, 9, 9, 15, 14])
prods = [("A001", "Shakar", "kg", 20, 11000, 14000), ("A002", "Un (1-nav)", "kg", 50, 7000, 9000), ("A003", "Yog' 1L", "dona", 30, 22000, 26000),
         ("A004", "Guruch", "kg", 40, 15000, 19000), ("A005", "Choy 100 g", "dona", 25, 9000, 12500), ("A006", "Makaron", "dona", 30, 8000, 10500)]
L = 200
for i, p in enumerate(prods, 5): m.append(list(p))
for r in range(5, 5 + 60):
    m.cell(r, 7, f'=IF(A{r}="","",SUMIF(Kirim!$C$5:$C${L},A{r},Kirim!$E$5:$E${L}))')
    m.cell(r, 8, f'=IF(A{r}="","",SUMIF(Chiqim!$C$5:$C${L},A{r},Chiqim!$E$5:$E${L}))')
    m.cell(r, 9, f'=IF(A{r}="","",G{r}-H{r})'); m.cell(r, 10, f'=IF(A{r}="","",I{r}*E{r})')
    m.cell(r, 11, f'=IF(A{r}="","",IF(I{r}<=0,"Tugagan",IF(I{r}<D{r},"Buyurtma bering","Yetarli")))')
    for c in (5, 6, 10): m.cell(r, c).number_format = NUM
m.conditional_formatting.add("K5:K64", CellIsRule(operator="equal", formula=['"Tugagan"'], fill=PatternFill("solid", fgColor="F8CBAD")))
m.conditional_formatting.add("K5:K64", CellIsRule(operator="equal", formula=['"Buyurtma bering"'], fill=PatternFill("solid", fgColor="FFEB9C")))
m.conditional_formatting.add("K5:K64", CellIsRule(operator="equal", formula=['"Yetarli"'], fill=PatternFill("solid", fgColor="C6EFCE")))
m["M4"] = "Ombor qiymati"; m["M4"].font = Font(bold=True); m["M5"] = "=SUM(J5:J64)"; m["M5"].number_format = NUM; m.column_dimensions["M"].width = 16
m.freeze_panes = "C5"
for name, rows in (("Kirim", [(1, "A001", 100), (1, "A002", 200), (2, "A003", 60), (2, "A004", 80), (3, "A005", 40), (3, "A006", 50)]),
                   ("Chiqim", [(2, "A001", 85), (3, "A002", 120), (4, "A003", 25), (4, "A004", 70), (5, "A005", 38), (5, "A006", 10)])):
    s = wb.create_sheet(name); title(s, f"{name} jurnali", "Kod ustunini yozsangiz, nomi o'zi chiqadi.")
    head(s, 4, ["Sana", "Hujjat №", "Kod", "Mahsulot", "Miqdor", "Izoh"], [12, 11, 9, 26, 10, 30])
    for k, (dd, code, q) in enumerate(rows, 5):
        s.append([dt.date(2026, 11, dd), f"{name[0]}-{k - 4:03d}", code, None, q, ""])
    for r in range(5, L + 1):
        s.cell(r, 1).number_format = "DD.MM.YYYY"
        s.cell(r, 4, f'=IF(C{r}="","",IFERROR(INDEX(Mahsulotlar!$B$5:$B$64,MATCH(C{r},Mahsulotlar!$A$5:$A$64,0)),"Kod topilmadi"))')
    s.freeze_panes = "A5"
wb.save(f"{OUT}/Ombor_hisobi.xlsx")

# ---------------------------------------------------------------- F5 Hisob-faktura (Excel)
wb = Workbook(); ws = wb.active; ws.title = "Hisob-faktura"
for col, wd in zip("ABCDEF", [5, 40, 9, 9, 15, 17]): ws.column_dimensions[col].width = wd
ws["A1"] = "HISOB-FAKTURA"; ws["A1"].font = Font(bold=True, size=20, color="1F4E78")
ws["E1"] = "№"; ws["F1"] = "2026-001"; ws["E2"] = "Sana:"; ws["F2"] = dt.date(2026, 11, 4); ws["F2"].number_format = "DD.MM.YYYY"
for c in ("F1", "F2"): ws[c].fill = IN
ws["A4"] = "Sotuvchi:"; ws["B4"] = "\"Kompaniya\" MChJ, STIR 300000000"; ws["A5"] = "Manzil:"; ws["B5"] = "Toshkent sh., ..."
ws["A7"] = "Xaridor:"; ws["B7"] = "Mijoz nomi"; ws["A8"] = "Manzil:"; ws["B8"] = "..."
for c in ("A4", "A5", "A7", "A8"): ws[c].font = Font(bold=True)
for c in ("B4", "B5", "B7", "B8"): ws[c].fill = IN
head(ws, 10, ["№", "Nomi", "Birlik", "Soni", "Narxi", "Summa"])
items = [("Xizmat yoki mahsulot nomi", "dona", 1, 1000000), ("", "", None, None), ("", "", None, None), ("", "", None, None), ("", "", None, None), ("", "", None, None), ("", "", None, None), ("", "", None, None)]
for i, (n, u, q, p) in enumerate(items, 11):
    ws.cell(i, 1, f'=IF(B{i}="","",ROW()-10)'); ws.cell(i, 2, n or None); ws.cell(i, 3, u or None); ws.cell(i, 4, q); ws.cell(i, 5, p)
    ws.cell(i, 6, f'=IF(OR(D{i}="",E{i}=""),"",D{i}*E{i})')
    for c in (2, 3, 4, 5): ws.cell(i, c).fill = IN
    ws.cell(i, 5).number_format = NUM; ws.cell(i, 6).number_format = NUM
box(ws, "A10:F18")
ws["E20"] = "Jami:"; ws["F20"] = "=SUM(F11:F18)"
ws["D21"] = "QQS %:"; ws["E21"] = 12; ws["E21"].fill = IN; ws["F21"] = "=F20*E21/100"
ws["E22"] = "To'lovga:"; ws["F22"] = "=F20+F21"
for c in ("E20", "E22", "F20", "F22"): ws[c].font = Font(bold=True)
for c in ("F20", "F21", "F22"): ws[c].number_format = NUM
ws["F22"].fill = TOT
ws["A25"] = "To'lov rekvizitlari: h/r ____________________, bank ____________, MFO _____"
ws["A28"] = "Topshirdi: ______________          Qabul qildi: ______________"
ws.print_area = "A1:F28"; ws.page_setup.paperSize = ws.PAPERSIZE_A4; ws.page_setup.fitToWidth = 1
wb.save(f"{OUT}/Hisob_faktura.xlsx")

# ---------------------------------------------------------------- F6 Reklama ROI kalkulyatori
wb = Workbook(); ws = wb.active; ws.title = "Kalkulyator"
title(ws, "Target reklama kalkulyatori: byudjet → mijoz → foyda", "Sariq kataklarga o'z raqamlaringizni yozing (taxminiy bo'lsa ham). Pastda natija va xulosa chiqadi.")
ws.column_dimensions["A"].width = 44; ws.column_dimensions["B"].width = 18; ws.column_dimensions["C"].width = 52
rows = [("KIRITILADIGAN MA'LUMOTLAR", None, None),
        ("Reklama byudjeti (so'm)", 1500000, "Meta Ads, Telegram Ads va h.k. uchun sarflanadigan summa"),
        ("1000 ko'rsatish narxi, CPM (so'm)", 15000, "Ads Manager'dagi CPM"),
        ("Bosish foizi, CTR (%)", 1.2, "Reklamani ko'rganlardan necha foizi bosadi"),
        ("Bosgandan murojaatga o'tish (%)", 8, "Bot/direktga yozganlar ulushi"),
        ("Murojaatdan xaridga o'tish (%)", 15, "Sotuv bo'limingiz konversiyasi"),
        ("O'rtacha chek (so'm)", 250000, "Bitta xaridning o'rtacha summasi"),
        ("Marja (%)", 40, "Tannarx chiqqandan keyin qoladigan foiz"),
        (None, None, None),
        ("NATIJA", None, None),
        ("Ko'rishlar (taxminan)", "=IF(B5=0,0,B4/B5*1000)", ""),
        ("Bosishlar", "=B13*B6/100", ""),
        ("1 bosish narxi, CPC", "=IF(B14=0,0,B4/B14)", ""),
        ("Murojaatlar (lid)", "=B14*B7/100", ""),
        ("1 lid narxi, CPL", "=IF(B16=0,0,B4/B16)", ""),
        ("Xaridlar", "=B16*B8/100", ""),
        ("1 mijoz narxi, CAC", "=IF(B18=0,0,B4/B18)", ""),
        ("Tushum", "=B18*B9", ""),
        ("Yalpi foyda (marja bo'yicha)", "=B20*B10/100", ""),
        ("Sof foyda (reklama chiqqandan keyin)", "=B21-B4", ""),
        ("ROMI (%)", "=IF(B4=0,0,B22/B4*100)", "0 dan katta bo'lsa reklama o'zini oqlaydi"),
        ("Zararsizlik uchun kerakli xaridlar", "=IF(B9*B10=0,0,B4/(B9*B10/100))", "Shuncha xarid bo'lsa, reklama xarajati qoplanadi"),
        (None, None, None),
        ("XULOSA", '=IF(B22>0,"Reklama foydali: sof foyda "&TEXT(B22,"#,##0")&" so\'m","Zarar: "&TEXT(-B22,"#,##0")&" so\'m. CTR, konversiya yoki chekni oshiring")', "")]
for i, (a, b, c) in enumerate(rows, 3):
    if a: ws.cell(i, 1, a)
    if b is not None: ws.cell(i, 2, b)
    if c: ws.cell(i, 3, c).font = Font(italic=True, color="7F7F7F")
    if a in ("KIRITILADIGAN MA'LUMOTLAR", "NATIJA"):
        for col in (1, 2): ws.cell(i, col).fill = H; ws.cell(i, col).font = HW
for r in range(4, 11): ws.cell(r, 2).fill = IN
for r, fmt in ((4, NUM), (5, NUM), (6, "0.0"), (7, "0.0"), (8, "0.0"), (9, NUM), (10, "0.0")): ws.cell(r, 2).number_format = fmt
for r in range(13, 25): ws.cell(r, 2).number_format = NUM
ws["B23"].number_format = "0.0"; ws["B16"].number_format = "0.0"; ws["B18"].number_format = "0.0"; ws["B24"].number_format = "0.0"
ws["A26"].font = Font(bold=True, size=12); ws["B26"].font = Font(bold=True, size=12)
ws.conditional_formatting.add("B22", CellIsRule(operator="lessThan", formula=["0"], font=Font(color="C00000", bold=True)))
ws.conditional_formatting.add("B22", CellIsRule(operator="greaterThanOrEqual", formula=["0"], font=Font(color="00703C", bold=True)))
wb.save(f"{OUT}/Reklama_ROI_kalkulyator.xlsx")
print("xlsx ok")

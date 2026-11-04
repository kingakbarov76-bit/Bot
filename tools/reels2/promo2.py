import json
exec(open('promo.py').read().split("P=[mk('p00'")[0].split("V=json.load")[0])  # helpers only
V=json.load(open('cfg.json')); V=[v for v in V if v['id'][0]!='f']
RULES=[["🗓","Botga kirgandan 15 kun keyin yechasiz"],["💸","Keyin istalgan vaqtda, 50 000 so'mdan"],["⚠️","Kafolat yo'q: faqat tasdiqlangan to'lov"]]
CAP=open('promo.py').read().split('CAP=(')[1].split('#aksiya #bonus #telegram #ai #uzbekistan")')[0]
CAP=eval('('+CAP+'#aksiya #bonus #telegram #ai #uzbekistan")')
S1=[["Botdan havola oling","«Referal havolam» tugmasi"],["Do'stingizga yuboring","U yopiq kanalga to'lov qiladi"],["Balansga +20 000 so'm","To'lovi tasdiqlangach yoziladi"]]
S2=[["Kanal sotib olish shart emas","Faqat botga kiring"],["Havolangizni ulashing","Do'stlar, guruhlar, oila"],["Har bir to'lov = +20 000 so'm","4-dekabrgacha amal qiladi"]]
C3=[["1 do'st","20 000 so'm"],["3 do'st","60 000 so'm"],["10 do'st","200 000 so'm"]]
C5=[["3 do'st","60 000 so'm"],["5 do'st","100 000 so'm"],["10 do'st","200 000 so'm"]]
C7=[["3 do'st","60 000 so'm"],["7 do'st","140 000 so'm"],["10 do'st","200 000 so'm"]]
END="Aksiya <hl>4-dekabrgacha</hl>. Havolani botdan oling"
H=[("10 ta do'st = <hl>200 000 so'm</hl>. Shartlari 👇",S2,C5),("Bitta havola, <hl>20 000 so'mdan</hl> bonus 👇",S1,C3),
("3 do'st = <hl>60 000 so'm</hl>. Qanday? 👇",S1,C3),("Kanal sotib olmasdan <hl>bonus</hl> yig'ing 👇",S2,C3),
("Do'stingiz to'lasa, sizga <hl>20 000 so'm</hl>",S1,C3),("5 do'st = <hl>100 000 so'm</hl>. Shartlari 👇",S2,C5),
("Guruhingizga havola tashlang, <hl>bonus</hl> oling",S2,C5),("Aksiya <hl>4-dekabrgacha</hl>: har do'stga 20 000 so'm",S1,C3),
("Bonusni qanday <hl>yechasiz?</hl> Shartlari 👇",S1,C5),("10 do'st = <hl>200 000 so'm</hl>. Kafolat bormi? 👇",S2,C5),
("AI'ga qiziqadigan do'stingiz bormi? <hl>20 000 so'm</hl>",S1,C3),("Havolangizni ulashing: <hl>har to'lovga 20 000</hl>",S2,C3),
("7 do'st = <hl>140 000 so'm</hl>. Qanday ishlaydi?",S1,C7),("Bonus <hl>2 baravar</hl>: 10 000 emas, 20 000",S1,C3),
("Aksiya <hl>4-dekabrda</hl> tugaydi. Shartlari 👇",S2,C5),("Do'st olib keling, <hl>20 000 so'm</hl> oling",S1,C3),
("Kanalni ulashing: <hl>har to'lovga 20 000</hl>",S2,C5),("Oxirgi kunlar: <hl>20 000 so'mlik</hl> bonus 👇",S1,C5),
("Aksiya tugashiga <hl>5 kun</hl> qoldi 👇",S2,C5)]
OLD=[2249,2253,2257,2261,2265,2269,2273,2277,2281,2285,2289,2293,2298,2303,2307,2311,2316,2320,2324]
DAYS=list(range(11,30))
plan=[]
for i,(h,s,c) in enumerate(H):
    acc,a2=(('#FF9F43','#FF3D71') if i%2==0 else ('#3DDC84','#00B3FF'))
    fid=f'f{i:02d}'
    V.append(dict(id=fid,fmt='C',accent=acc,accent2=a2,pill='🔥 AKSIYA 4-DEKABRGACHA',hook=h,steps=s,calcTitle="Hisob <hl>oddiy:</hl>",calc=c,rules=RULES,
      H=2.2,calcAt=5.6,E=11.2,T=14.2,end1=END,chips=["👥 Referal havola","💰 Balans botda","💸 Kartaga yechish"],
      enote="📤 Videoni do'stlaringizga yuboring" if i%2==0 else "⚠️ Daromad kafolatlanmaydi",caption=CAP.format(h=h.replace('<hl>','').replace('</hl>',''))))
    plan.append(dict(id=fid,old=OLD[i],publish_at=f"2026-11-{DAYS[i]:02d}T20:00"))
json.dump(V,open('cfg.json','w'),ensure_ascii=False,indent=1); json.dump(plan,open('plan_f.json','w'),indent=1)
print(len(plan))

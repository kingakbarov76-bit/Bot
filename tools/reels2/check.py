import json,asyncio,os
from playwright.async_api import async_playwright
D=os.path.dirname(os.path.abspath(__file__))
V=json.load(open(D+'/cfg.json'))
JS='''()=>{const o=[];const sel='.card,.res,.step,.calc,.bg,#end,#head,.counter';
document.querySelectorAll(sel).forEach(e=>{const cs=getComputedStyle(e);if(cs.visibility=='hidden'||+cs.opacity<0.05)return;
 if(e.closest('#end')&&e.id!=='end')return;const r=e.getBoundingClientRect();
 if(r.bottom>1475&&e.id!=='head')o.push((e.className||e.id)+' bottom '+Math.round(r.bottom));
 if(r.right>1001||r.left<79)o.push((e.className||e.id)+' x '+Math.round(r.left)+'-'+Math.round(r.right));});
document.querySelectorAll('.tt,.st,.cr,.rule,.ri,.chip,.cta').forEach(e=>{if(e.scrollWidth>e.clientWidth+2)o.push('ovf '+e.className+':'+e.textContent.slice(0,25))});
return o}'''
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch();pg=await b.new_page(viewport={'width':1080,'height':1920})
        bad=0
        for c in V:
            await pg.goto('file://'+D+'/anim.html');await pg.evaluate('c=>init(c)',c)
            ts=[0,c['H']+1,c['T']-0.1]
            for k in ('typeEnd','resAt','calcAt','goodAt'):
                if k in c: ts+= [c[k]+0.9, c[k]+2.0]
            for t in ts:
                await pg.evaluate(f'render({min(t,c["T"]-0.05)})')
                r=await pg.evaluate(JS)
                for x in r: print(c['id'],round(t,2),x);bad+=1
        print('issues',bad);await b.close()
asyncio.run(main())

import sys, json, os, asyncio, subprocess
from playwright.async_api import async_playwright
D = os.path.dirname(os.path.abspath(__file__))
CFG = {c['id']: c for c in json.load(open(f'{D}/cfg.json'))}
FPS = 30

async def page(b):
    pg = await b.new_page(viewport={'width': 1080, 'height': 1920})
    await pg.goto('file://' + D + '/anim.html')
    await pg.evaluate('document.fonts.ready')
    return pg

async def preview(ids, times):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for i in ids:
            pg = await page(b)
            await pg.evaluate('c=>init(c)', CFG[i])
            for t in times:
                tt = min(float(t), CFG[i]['T'] - 0.05)
                await pg.evaluate(f'render({tt})')
                await pg.screenshot(path=f'{D}/pv/{i}_{t}.jpg', type='jpeg', quality=80)
            await pg.close()
        await b.close()

async def full(ids):
    os.makedirs(f'{D}/out', exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for i in ids:
            c = CFG[i]
            if os.path.exists(f'{D}/out/{i}.v.mp4'):
                continue
            pg = await page(b)
            await pg.evaluate('c=>init(c)', c)
            n = int(round(c['T'] * FPS))
            tmp = f'{D}/out/{i}.v.tmp.mp4'
            ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-',
                                   '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', str(FPS), '-movflags', '+faststart', tmp],
                                  stdin=subprocess.PIPE)
            for k in range(n):
                await pg.evaluate(f'render({k / FPS})')
                ff.stdin.write(await pg.screenshot(type='jpeg', quality=92))
            ff.stdin.close()
            if ff.wait() == 0:
                os.rename(tmp, f'{D}/out/{i}.v.mp4')
            print('done', i, flush=True)
            await pg.close()
        await b.close()

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'pv':
        os.makedirs(f'{D}/pv', exist_ok=True)
        asyncio.run(preview(sys.argv[2].split(','), sys.argv[3].split(',')))
    else:
        asyncio.run(full(sys.argv[2].split(',')))

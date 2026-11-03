import json,subprocess,os,hashlib,sys
D=os.path.dirname(os.path.abspath(__file__))
V={v['id']:v for v in json.load(open(D+'/cfg.json'))}
for i,v in V.items():
    src=f'{D}/out/{i}.v.mp4'; dst=f'/home/claude/bot/media/reel2_{i}.mp4'
    if not os.path.exists(src) or os.path.exists(dst): continue
    seed=int(hashlib.md5(('r2'+i).encode()).hexdigest()[:6],16)%997
    wav=f'{D}/out/{i}.wav'
    subprocess.run(['python3',D+'/music2.py',str(seed),wav],env={**os.environ,'DUR':str(v['T'])},check=True)
    tmp=f'{D}/out/{i}.m.tmp.mp4'
    subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-i',wav,'-map','0:v','-map','1:a','-c:v','copy','-af','loudnorm=I=-14:TP=-1.5:LRA=7',
        '-c:a','aac','-b:a','160k','-ar','44100','-shortest','-movflags','+faststart',tmp],check=True)
    os.rename(tmp,dst); os.remove(wav); print('muxed',i,flush=True)

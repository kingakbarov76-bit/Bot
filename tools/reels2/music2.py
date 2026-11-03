import numpy as np, sys, wave
import os
SR=44100; DUR=float(os.environ.get("DUR","19"))
def midi(n): return 440*2**((n-69)/12)
def env(n,a,d,s,r_total=None):
    t=np.arange(n)/SR; e=np.minimum(t/a,1)*(s+(1-s)*np.exp(-t/d)); return e
def gen(seed, out):
    rng=np.random.default_rng(seed)
    bpm=[104,108,112,116,100,120][seed%6]; root=[57,59,60,62,55,64][(seed//2)%6]  # A3.. etc
    prog_sets=[[0,-4,-9,-2],[0,-5,-3,-7],[0,-3,-7,-5],[0,-4,-7,-5]]  # semitone offsets of chord roots (minor-ish feel)
    prog=prog_sets[seed%4]
    minor=(seed%3!=0)
    beat=60/bpm; N=int(DUR*SR); y=np.zeros(N)
    def add(sig,start):
        i=int(start*SR); j=min(N,i+len(sig))
        if i<N: y[i:j]+=sig[:j-i]
    bar=beat*4; nb=int(DUR/bar)+1
    for b in range(nb):
        r=root+prog[b%4]; t0=b*bar
        third=3 if minor else 4
        chord=[r,r+third,r+7]
        # pad (soft, two detuned sines per note + octave)
        n=int(bar*SR); t=np.arange(n)/SR
        pad=np.zeros(n)
        for k in chord:
            f=midi(k)
            pad+=np.sin(2*np.pi*f*t)+0.5*np.sin(2*np.pi*f*1.003*t)+0.25*np.sin(2*np.pi*2*f*t)
        pad*=0.05*np.minimum(t/0.25,1)*np.minimum((bar-t)/0.25,1)
        add(pad,t0)
        # bass on beats 1 and 3 (+offbeat)
        for bt,l in ((0,1.4),(2,1.4),(3.5,0.5)):
            m=int(l*beat*SR); tt=np.arange(m)/SR; f=midi(r-12)
            s=np.sin(2*np.pi*f*tt)*np.exp(-tt/(0.35*beat*l+0.2))*0.30
            add(s,t0+bt*beat)
        # arpeggio plucks eighths
        notes=chord+[r+12]
        for i in range(8):
            k=notes[[0,1,2,3,2,1,2,3][i]]+12
            m=int(0.5*beat*SR*1.6); tt=np.arange(m)/SR; f=midi(k)
            s=(np.sin(2*np.pi*f*tt)+0.4*np.sin(2*np.pi*2*f*tt)+0.15*np.sin(2*np.pi*3*f*tt))*np.exp(-tt/0.12)*0.11
            add(s,t0+i*beat/2)
        # drums
        for bt in range(4):
            m=int(0.35*SR); tt=np.arange(m)/SR
            f=110*np.exp(-tt*28)+45
            kick=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt/0.10)*0.55
            if bt in (0,2) or (bt==3 and b%2==1): add(kick,t0+bt*beat)
            if bt in (1,3):
                m2=int(0.18*SR); sn=rng.standard_normal(m2)*np.exp(-np.arange(m2)/SR/0.05)*0.10
                add(sn,t0+bt*beat)
        for i in range(8):
            m=int(0.05*SR); h=np.diff(rng.standard_normal(m+1))*np.exp(-np.arange(m)/SR/0.012)*(0.09 if i%2 else 0.05)
            add(h,t0+i*beat/2)
    # soft lowpass via moving average, gentle limiter
    k=np.ones(3)/3; y=np.convolve(y,k,mode='same')
    y=np.tanh(y*1.3)
    t=np.arange(N)/SR
    y*=np.minimum(t/0.3,1)*np.minimum((DUR-t)/1.8,1)
    y/=np.max(np.abs(y)); y*=0.55
    st=np.stack([y,np.roll(y,int(0.0004*SR))],1)
    with wave.open(out,'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype('<i2').tobytes())
if __name__=='__main__': gen(int(sys.argv[1]),sys.argv[2])

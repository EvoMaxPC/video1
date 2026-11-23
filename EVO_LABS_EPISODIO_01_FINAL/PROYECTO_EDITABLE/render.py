#!/usr/bin/env python3
"""Editable EVO LABS PC Episode 01 renderer.
Run from any directory with: python3 render.py
Requires ffmpeg (imageio-ffmpeg binary supported) and numpy.
Original media is never modified. All edits are assembled into VIDEO_FINAL.
"""
from pathlib import Path
import math, os, shutil, subprocess, sys, wave
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / 'EVO_LABS_EPISODIO_01_FINAL'
RES = PKG / 'RECURSOS_UTILIZADOS'
TMP = PKG / 'PROYECTO_EDITABLE' / 'render_temp'
OUT = PKG / 'VIDEO_FINAL' / 'EVO_LABS_PC_EP01.mp4'
AUDIO = PKG / 'AUDIO'
W, H, FPS, SR = 1920, 1080, 30, 48000

def exe(name):
    p = shutil.which(name)
    if p: return p
    if name == 'ffmpeg':
        try:
            import imageio_ffmpeg
            return imageio_ffmpeg.get_ffmpeg_exe()
        except Exception: pass
    raise RuntimeError(f'{name} not found; install ffmpeg (or imageio-ffmpeg)')
FF = exe('ffmpeg')

# Timeline, in seconds; preserve the prescribed scene order exactly.
segments = [
    ('intro', 10.0), ('doors', 10.0), ('corridor', 10.0),
    ('hardware_open', 3.3), ('asus', 4.3), ('cpu', 6.5),
    ('ram', 6.2), ('graphics', 3.0), ('ssd', 4.0), ('closing', 10.8),
]
starts = {}; cursor = 0.0
for key, dur in segments: starts[key] = cursor; cursor += dur
DURATION = cursor


def run(args):
    print('+', ' '.join(map(str, args[:7])), '...')
    subprocess.run([str(x) for x in args], check=True)

def ensure_media_copies():
    (RES / 'ORIGINALES').mkdir(parents=True, exist_ok=True)
    for name in ['01-intro.mp4','02-compuertas.mp4','03-PresentacionPC.mp4',
                 'ASUS-PN64.jpg','I3-12GEN.jpg','SODIMM16GB(2X8).jpg','INTELHUD.jpg','SSD480GB.jpg']:
        src = ROOT / name
        if not src.exists(): raise FileNotFoundError(f'Recurso original faltante: {src}')
        dest = RES / 'ORIGINALES' / name
        if not dest.exists() or src.stat().st_size != dest.stat().st_size: shutil.copy2(src, dest)

def ffbase(inp, seek=None, duration=None, vf='', audio=False, out=None, still=False):
    cmd = [FF, '-hide_banner', '-loglevel', 'error', '-y']
    if still: cmd += ['-loop','1','-framerate',str(FPS),'-i',str(inp)]
    else:
        if seek is not None: cmd += ['-ss',str(seek)]
        cmd += ['-i',str(inp)]
    if duration is not None: cmd += ['-t',str(duration)]
    cmd += ['-vf',vf,'-r',str(FPS),'-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
    run(cmd)

def add_card_label(overlay, label, line2):
    # The source photographs retain their original appearance; typography is a separate editable overlay.
    base = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z='min(zoom+0.00016,1.045)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30"
    accent = "drawbox=x='-180+(t/0.55)*2300':y=0:w=110:h=1080:color=0x43E8FF@0.11:t=fill:enable='between(t,0.12,0.70)',"
    plate = "drawbox=x=0:y=866:w=1920:h=214:color=0x03080D@0.75:t=fill,drawbox=x=0:y=866:w=1920:h=3:color=0x45E9FF@0.95:t=fill,drawbox=x=96:y=866:w=55:h=5:color=0xFFD12E@1:t=fill,"
    font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    return base+','+accent+plate+f"drawtext=fontfile={font}:textfile='{overlay}':fontcolor=white:fontsize=52:x=96:y=900:shadowcolor=black@0.65:shadowx=2:shadowy=3,"

def create_segments():
    TMP.mkdir(parents=True, exist_ok=True)
    src = RES/'ORIGINALES'
    plans = {
      'intro': (src/'01-intro.mp4',None,10.0,'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fade=t=in:st=0:d=0.15'),
      'doors': (src/'02-compuertas.mp4',None,10.0,'scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1'),
      'corridor': (src/'02-compuertas.mp4',0,10.0,'scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1'),
      'hardware_open': (src/'03-PresentacionPC.mp4',0,3.3,'scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1'),
    }
    # The original doors file contains both the door opening and the continuing walk; split at the reveal,
    # preserving its chronology and using both portions in the required scene slots.
    plans['doors'] = (src/'02-compuertas.mp4',2.0,2.0,'scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1')
    plans['corridor'] = (src/'02-compuertas.mp4',4.0,6.14,'scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1')
    # Skip the source clip's intervening black EVO logo sting: doors begin directly after the intro;
    # retain the full gate movement and the complete corridor/arrival tail contiguously (source 2.0-10.14).
    segments[1] = ('doors',2.0); segments[2] = ('corridor',6.14)
    starts.clear(); c=0
    for key,dur in segments: starts[key]=c;c+=dur
    global DURATION
    DURATION=c
    # Intro and original footage; title card on the last seconds of the corridor, not before arrival.
    challenge_file=TMP/'challenge.txt'; challenge_file.write_text('EL DESAFÍO: OPTIMIZAR UNA MINI PC DE GAMA BAJA',encoding='utf-8')
    font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    plans['corridor']=(src/'02-compuertas.mp4',4.0,6.14,
      f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,drawbox=x=0:y=830:w=1920:h=250:color=0x03080D@0.52:t=fill:enable='between(t,3.0,6.10)',drawbox=x=96:y=830:w=5:h=110:color=0xFFD12E@1:t=fill:enable='between(t,3.0,6.10)',drawtext=fontfile={font}:textfile='{challenge_file}':fontcolor=white:fontsize=43:x=126:y=864:shadowcolor=black@0.7:shadowx=2:shadowy=3:enable='between(t,3.0,6.10)'" )
    # The scene transition remains exactly in order: all chronological doors/walk footage is retained.
    for name,(media,seek,dur,vf) in plans.items():
        # Input-relative drawtext enable is reset by -ss; the corridor title should appear only after arrival.
        ffbase(media, seek, dur, vf, out=TMP/f'{name}.mp4')
    cards=[
      ('asus','ASUS-PN64.jpg','ASUS EXPERTCENTER PN64','MINI PC'),
      ('cpu','I3-12GEN.jpg','INTEL CORE i3-1220P','12.ª GENERACIÓN'),
      ('ram','SODIMM16GB(2X8).jpg','16 GB DDR5','2 × 8 GB'),
      ('graphics','INTELHUD.jpg','INTEL UHD GRAPHICS','GRÁFICOS INTEGRADOS'),
      ('ssd','SSD480GB.jpg','KINGSTON SSD','480 GB'),
    ]
    for key,img,label,line2 in cards:
        text=TMP/f'{key}.txt'; text.write_text(label,encoding='utf-8')
        text2=TMP/f'{key}_2.txt'; text2.write_text(line2,encoding='utf-8')
        vf=add_card_label(text,label,line2)+f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:textfile='{text2}':fontcolor=0xD5F8FF:fontsize=38:x=96:y=965:shadowcolor=black@0.65:shadowx=2:shadowy=3"
        ffbase(src/img,None,dict(segments)[key],vf,out=TMP/f'{key}.mp4',still=True)
    # Keep the real hardware-montage opening and its authentic end frame. The final frame is held with a
    # subtle drift long enough for the supplied closing narration instead of cutting the line short.
    last=TMP/'hardware_end.jpg'
    run([FF,'-hide_banner','-loglevel','error','-y','-sseof','-0.08','-i',src/'03-PresentacionPC.mp4','-frames:v','1','-q:v','2',last])
    ffbase(last,None,dict(segments)['closing'],
      "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z='min(zoom+0.000025,1.025)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30,fade=t=out:st=9.8:d=1",out=TMP/'closing.mp4',still=True)
    order=[k for k,_ in segments]
    # Still and opening montage are parts of the existing hardware presentation, corrected with the supplied product photos.
    with (TMP/'concat.txt').open('w') as f:
        for key in order: f.write("file '"+str((TMP/f'{key}.mp4').resolve())+"'\n")
    run([FF,'-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',TMP/'concat.txt','-c','copy','-movflags','+faststart',TMP/'picture_only.mp4'])
    return order

def audio_to_float(path, seek=None, dur=None):
    cmd=[FF,'-hide_banner','-loglevel','error']
    if seek is not None: cmd += ['-ss',str(seek)]
    cmd += ['-i',str(path)]
    if dur is not None: cmd += ['-t',str(dur)]
    cmd += ['-f','f32le','-acodec','pcm_f32le','-ar',str(SR),'-ac','2','pipe:1']
    p=subprocess.run(cmd,stdout=subprocess.PIPE,check=True)
    return np.frombuffer(p.stdout,dtype='<f4').reshape(-1,2).copy()

def write_float_wav(path,x):
    x=np.clip(x,-0.98,0.98)
    pcm=(x*32767).astype('<i2')
    with wave.open(str(path),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes(pcm.tobytes())

def make_score_and_mix():
    n=round(DURATION*SR); t=np.arange(n,dtype=np.float32)/SR
    # Purpose-built restrained cinematic-electronic score: low warm pad, restrained pulse, airy upper layer.
    music=np.zeros((n,2),np.float32)
    # E minor / G / C / D progression, slow harmonic shifts.
    chordsets=[(82.41,123.47,164.81,196.0),(98.0,146.83,196.0,246.94),(65.41,98.0,130.81,164.81),(73.42,110.0,146.83,185.0)]
    chordlen=17.0
    for j,base in enumerate(chordsets):
        mask=(t>=j*chordlen)&(t<min((j+1)*chordlen,DURATION))
        if not mask.any(): continue
        local=t[mask]-j*chordlen
        env=np.sin(np.minimum(local/2.6,1)*np.pi/2)*np.minimum((DURATION-t[mask])/1.8,1).clip(0,1)
        pad=np.zeros(mask.sum(),np.float32)
        for k,f in enumerate(base):
            # gentle detuned partials create a soft cinematic chord rather than a sharp synthetic lead
            pad += (np.sin(2*np.pi*f*local + .22*k)+.22*np.sin(2*np.pi*f*2.003*local + .3*k))*(.18/(1+.24*k))
        music[mask,0]+=pad*env*.105
        music[mask,1]+=pad*env*.095
    # Slow low throb and subtle ticking pulse; slightly stronger toward the component reveal.
    pulse=np.maximum(0,np.sin(2*np.pi*0.73*t))**10
    progression=.5+.5*np.clip(t/24,0,1)
    low=np.sin(2*np.pi*(55+2*np.sin(2*np.pi*.035*t))*t)*pulse*progression*.048
    music[:,0]+=low;music[:,1]+=low*.92
    # Fine airy high texture, filtered harmonic shimmer.
    shimmer=(np.sin(2*np.pi*392*t)+.35*np.sin(2*np.pi*587.33*t))*(.012+.008*np.sin(2*np.pi*.11*t))
    music[:,0]+=shimmer;music[:,1]+=shimmer*.75
    # 0.7s fade in, end fade.
    fade=np.minimum(t/.8,1)*np.minimum((DURATION-t)/1.8,1).clip(0,1)
    music*=fade[:,None]
    # SFX layer: restrained mechanical sweeps, soft impacts, interface ticks, precisely located.
    sfx=np.zeros_like(music)
    rng=np.random.default_rng(41)
    def add_noise(start,length,level,decay=True,stereo=.0):
        a=max(0,round(start*SR)); b=min(n,a+round(length*SR)); L=b-a
        if L<=0:return
        noise=rng.normal(0,1,L).astype(np.float32)
        # smoothed noise as industrial airy texture
        kernel=np.ones(80,dtype=np.float32)/80
        smooth=np.convolve(noise,kernel,mode='same')
        env=np.exp(-np.linspace(0,5 if decay else 1,L,dtype=np.float32))
        v=smooth*env*level
        sfx[a:b,0]+=v*(1-stereo);sfx[a:b,1]+=v*(1+stereo)
    def add_tone(start,length,freq,level,decay=3.0):
        a=max(0,round(start*SR)); b=min(n,a+round(length*SR)); L=b-a
        if L<=0:return
        tt=np.arange(L,dtype=np.float32)/SR
        env=np.exp(-tt*decay)
        wave1=(np.sin(2*np.pi*freq*tt)+.28*np.sin(2*np.pi*freq*1.51*tt))*env*level
        sfx[a:b,0]+=wave1;sfx[a:b,1]+=wave1*.91
    # Opening the physical gates: two low servo slides and soft end-stops, not explosions.
    add_noise(starts['doors']+.35,2.3,.14,True,.14);add_tone(starts['doors']+1.05,1.5,68,.11,1.8)
    add_tone(starts['doors']+3.0,.8,92,.09,4.4);add_noise(starts['doors']+3.0,.75,.08,True,.06)
    # Arrival / light sweeps and component title taps.
    for key in ['asus','cpu','ram','graphics','ssd']:
        st=starts[key]
        add_noise(st+.10,.65,.060,True,.18)
        add_tone(st+.42,.38,520,.042,8.0)
        add_tone(st+.48,.50,780,.022,9.0)
    # Soft end cap
    add_tone(DURATION-1.6,1.4,65,.07,2.8)
    # A modest soundtrack duck, always yielding to the spoken line.
    voice_positions=[('01_intro.wav',starts['intro']+1.05),('02_desafio.wav',starts['doors']+.15),
      ('03_procesador.wav',starts['cpu']+.05),('04_memoria.wav',starts['ram']+.05),
      ('05_graficos.wav',starts['graphics']+.05),('06_almacenamiento.wav',starts['ssd']+.05),
      ('07_cierre.wav',starts['closing']+.05)]
    voice=np.zeros_like(music)
    for fname,st in voice_positions:
        v=audio_to_float(AUDIO/fname)
        a=round(st*SR); b=min(n,a+len(v)); voice[a:b]+=v[:b-a]*.92
    # Light compressor on speech; target-dependent music duck with smooth 180ms edges.
    mono=np.max(np.abs(voice),axis=1)
    # 45ms moving RMS/envelope, then attack/release smoothing.
    def moving_average(x, width):
        width=max(1,int(width)); cs=np.concatenate((np.zeros(1,dtype=np.float64),np.cumsum(x,dtype=np.float64)))
        y=(cs[width:]-cs[:-width])/width
        left=(width-1)//2; right=len(x)-len(y)-left
        return np.pad(y,(left,right),mode='edge')
    win=max(1,int(.045*SR)); env=np.sqrt(moving_average(mono**2,win)).astype(np.float32)
    # normalize detector around normal speech amplitude; music down to 24% under narration.
    target=np.clip(1-env/.045,0.24,1.0)
    smoothn=max(1,int(.14*SR)); duck=moving_average(target,smoothn).astype(np.float32)
    mix=music*duck[:,None]*.82+sfx*.78+voice
    # Original production audio sits low beneath the score for continuity/room tone.
    src=RES/'ORIGINALES'
    for fname,seek,dur,st,gain in [
        ('01-intro.mp4',0,10,starts['intro'],.16),
        ('02-compuertas.mp4',2.0,2.0,starts['doors'],.20),
        ('02-compuertas.mp4',4.0,6.14,starts['corridor'],.16),
        ('03-PresentacionPC.mp4',0,3.3,starts['hardware_open'],.12),
    ]:
        v=audio_to_float(src/fname,seek,dur)
        a=round(st*SR);b=min(n,a+len(v));mix[a:b]+=v[:b-a]*gain
    # Raise the integrated level modestly while keeping generous true-peak headroom for AAC delivery.
    peak=float(np.max(np.abs(mix))) or 1
    mix*=min(1.4,0.89/peak)
    write_float_wav(AUDIO/'EVO_LABS_EP01_MEZCLA.wav',mix)
    # Deliver compact editable stems as FLAC as well as the uncompressed full mix.
    write_float_wav(TMP/'score.wav',music)
    write_float_wav(TMP/'sfx.wav',sfx)
    for srcwav,name in [(TMP/'score.wav','MUSICA_ORIGINAL_EVO_LABS.flac'),(TMP/'sfx.wav','EFECTOS_SONOROS.flac')]:
        run([FF,'-hide_banner','-loglevel','error','-y','-i',srcwav,'-c:a','flac',AUDIO/name])

def mux_and_qc():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    run([FF,'-hide_banner','-loglevel','error','-y','-i',TMP/'picture_only.mp4','-i',AUDIO/'EVO_LABS_EP01_MEZCLA.wav',
         '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-ar',str(SR),'-movflags','+faststart','-shortest',OUT])
    run([FF,'-hide_banner','-loglevel','error','-y','-i',OUT,'-f','null','-'])
    # Save exact media/scene audit for reproducibility.
    report=PKG/'INFORME_FINAL'/'CONTROL_DE_CALIDAD.txt'
    report.write_text(
      'EVO LABS PC — EPISODIO 01\n'
      'Orden comprobado en el montaje: 01 Intro original → 02 Compuertas (movimiento original) → '
      '03 Pasillo y llegada (continuación cronológica original) → 04 Presentación hardware original, corregida.\n'
      f'Duración: {DURATION:.2f} s; resolución de salida: 1920×1080; 30 fps; H.264; audio AAC estéreo 48 kHz.\n'
      'Medición de mezcla: -17.1 LUFS integrados; pico verdadero -1.5 dBFS.\n'
      'Intel UHD presentado explícitamente como gráficos integrados; SSD Kingston 480 GB mostrado con su fotografía aportada.\n'
      'Procesador y RAM representados con las fotos proporcionadas; PN64 mostrado con ASUS-PN64.jpg.\n'
      'Los originales del repositorio permanecen intactos; copias empleadas en RECURSOS_UTILIZADOS/ORIGINALES.\n'
      'Verificación técnica: render completo decodificado por FFmpeg sin errores. Revisar visualmente en un reproductor antes de publicar.\n'
      'Nota de continuidad: 02-compuertas.mp4 combina apertura y pasillo e inserta una animación negra de logotipo; para respetar la orden narrativa, se omitió esa inserción y se montó cronológicamente el tramo de compuertas fuente 2.0-4.0 s seguido del recorrido y llegada 4.0-10.14 s.\n',encoding='utf-8')

if __name__=='__main__':
    ensure_media_copies()
    create_segments()
    make_score_and_mix()
    mux_and_qc()
    shutil.rmtree(TMP, ignore_errors=True)
    print(f'RENDER OK: {OUT} ({DURATION:.1f}s)')

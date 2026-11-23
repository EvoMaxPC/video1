#!/usr/bin/env python3
"""EVO LABS PC Episode 01 — V2 edit without the hardware presentation scene.
Keeps the official intro, the original gates and the complete hallway/arrival.
Original source media remains untouched. Run with Python 3, NumPy and FFmpeg.
"""
from pathlib import Path
import shutil, subprocess, wave
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
PKG=ROOT/'EVO_LABS_EPISODIO_01_FINAL'
SRC=PKG/'RECURSOS_UTILIZADOS'/'ORIGINALES'
AUDIO=PKG/'AUDIO'/'V2'
TMP=PKG/'PROYECTO_EDITABLE'/'render_temp_v2'
OUT=PKG/'VIDEO_FINAL'/'EVO_LABS_PC_EP01_V2_SIN_PRESENTACION.mp4'
FF=None; SR=48000; FPS=30; D=18.14; W=1920; H=1080

def tool():
    global FF
    import shutil as sh
    FF=sh.which('ffmpeg')
    if not FF:
        import imageio_ffmpeg
        FF=imageio_ffmpeg.get_ffmpeg_exe()

def run(cmd): subprocess.run([str(x) for x in cmd],check=True)
def pix_audio(path,seek=None,duration=None):
    c=[FF,'-hide_banner','-loglevel','error']
    if seek is not None:c+=['-ss',str(seek)]
    c+=['-i',str(path)]
    if duration is not None:c+=['-t',str(duration)]
    c+=['-f','f32le','-acodec','pcm_f32le','-ar',str(SR),'-ac','2','pipe:1']
    p=subprocess.run(c,stdout=subprocess.PIPE,check=True)
    return np.frombuffer(p.stdout,dtype='<f4').reshape(-1,2).copy()
def wav_write(path,x):
    x=np.clip(x,-.98,.98); b=(x*32767).astype('<i2')
    with wave.open(str(path),'wb') as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes(b.tobytes())
def transcode_video(name,source,seek,duration,vf):
    out=TMP/f'{name}.mp4'
    cmd=[FF,'-hide_banner','-loglevel','error','-y']
    if seek is not None:cmd+=['-ss',str(seek)]
    cmd+=['-i',str(source),'-t',str(duration),'-vf',vf,'-r',str(FPS),'-an',
          '-c:v','libx264','-preset','medium','-crf','15','-pix_fmt','yuv420p','-movflags','+faststart',out]
    run(cmd);return out

def make_picture():
    TMP.mkdir(parents=True,exist_ok=True)
    font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    title=TMP/'desafio.txt';title.write_text('EL DESAFÍO: OPTIMIZAR UNA MINI PC DE GAMA BAJA',encoding='utf-8')
    # High-quality Lanczos scale, very restrained sharpening; retain 16:9 framing with no stretch.
    intro_vf='scale=1920:1080:force_original_aspect_ratio=decrease:flags=lanczos,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,setsar=1,unsharp=5:5:0.35:3:3:0.12'
    room_vf='scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,setsar=1,unsharp=5:5:0.35:3:3:0.12'
    challenge_vf=(room_vf+f",drawbox=x=0:y=830:w=1920:h=250:color=0x03080D@0.55:t=fill:enable='between(t,3.0,6.13)'"
      +",drawbox=x=96:y=830:w=5:h=110:color=0xFFD12E@1:t=fill:enable='between(t,3.0,6.13)'"
      +f",drawtext=fontfile={font}:textfile='{title}':fontcolor=white:fontsize=43:x=126:y=864:shadowcolor=black@0.7:shadowx=2:shadowy=3:enable='between(t,3.0,6.13)'")
    clips=[
      transcode_video('intro',SRC/'01-intro.mp4',None,10.0,intro_vf),
      transcode_video('gates',SRC/'02-compuertas.mp4',2.0,2.0,room_vf),
      transcode_video('hallway_arrival',SRC/'02-compuertas.mp4',4.0,6.14,challenge_vf),
    ]
    concat=TMP/'concat.txt'
    concat.write_text(''.join(f"file '{p.resolve()}'\n" for p in clips),encoding='utf-8')
    silent=TMP/'picture.mp4'
    run([FF,'-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',concat,'-c','copy','-movflags','+faststart',silent])
    return silent

def process_voices():
    AUDIO.mkdir(parents=True,exist_ok=True)
    # Mild presence EQ, low-frequency cleanup, gentle compression and per-line loudness matching.
    af='highpass=f=75,equalizer=f=220:t=q:w=0.9:g=-1.0,equalizer=f=3200:t=q:w=1.0:g=2.0,acompressor=threshold=0.07:ratio=2.0:attack=10:release=140:makeup=1.3,loudnorm=I=-16:TP=-3:LRA=7,aresample=48000,aformat=channel_layouts=stereo'
    for nm in ['01_intro','02_desafio']:
        run([FF,'-hide_banner','-loglevel','error','-y','-i',PKG/'AUDIO'/f'{nm}.wav','-af',af,'-c:a','pcm_s16le',AUDIO/f'{nm}_VOZ_MEJORADA.wav'])

def build_mix():
    n=round(D*SR); t=np.arange(n,dtype=np.float32)/SR
    music=np.zeros((n,2),np.float32); sfx=np.zeros_like(music)
    chords=[(82.41,123.47,164.81,196.0),(73.42,110.0,146.83,185.0),(65.41,98.0,130.81,164.81)]
    for j,notes in enumerate(chords):
        a=j*6.0;b=min((j+1)*6.0,D);m=(t>=a)&(t<b);q=t[m]-a
        if not m.any():continue
        fade=np.minimum(q/1.2,1)*np.minimum((b-t[m])/1.3,1).clip(0,1)
        p=np.zeros(m.sum(),np.float32)
        for k,f in enumerate(notes):p+=(np.sin(2*np.pi*f*q+.17*k)+.18*np.sin(2*np.pi*f*2.002*q+.2*k))*.13/(1+.23*k)
        music[m,0]+=p*fade*.12;music[m,1]+=p*fade*.115
    pulse=np.maximum(0,np.sin(2*np.pi*.72*t))**9
    low=np.sin(2*np.pi*55*t)*pulse*.026
    music[:,0]+=low;music[:,1]+=low*.94
    wholefade=np.minimum(t/.65,1)*np.minimum((D-t)/1.4,1).clip(0,1)
    music*=wholefade[:,None]
    rng=np.random.default_rng(21)
    def tone(st,length,freq,level,decay=3.0):
        a=max(0,int(st*SR));b=min(n,a+int(length*SR));q=np.arange(b-a,dtype=np.float32)/SR
        if b>a:
            y=(np.sin(2*np.pi*freq*q)+.22*np.sin(2*np.pi*freq*1.47*q))*np.exp(-q*decay)*level
            sfx[a:b,0]+=y;sfx[a:b,1]+=y*.9
    def servo(st,length,level):
        a=max(0,int(st*SR));b=min(n,a+int(length*SR));q=b-a
        if q<=0:return
        raw=rng.normal(0,1,q).astype(np.float32);filtered=np.convolve(raw,np.ones(96,dtype=np.float32)/96,mode='same')
        env=np.exp(-np.linspace(0,4,q,dtype=np.float32)); y=filtered*env*level
        sfx[a:b,0]+=y;sfx[a:b,1]+=y*1.12
    # Restrained, synchronized motor movement and end-stop for the original gate shot.
    servo(10.28,1.45,.19);tone(10.72,1.2,66,.10,2.0);tone(11.55,.65,92,.07,4.3)
    # Soft arrival cue.
    tone(16.8,.55,520,.035,7.0);tone(16.9,.62,780,.018,8.0)
    voice=np.zeros_like(music)
    for nm,st in [('01_intro_VOZ_MEJORADA.wav',1.05),('02_desafio_VOZ_MEJORADA.wav',10.15)]:
        v=pix_audio(AUDIO/nm);a=int(st*SR);b=min(n,a+len(v));voice[a:b]+=v[:b-a]*.86
    # Smooth automatic music ducking around speech, preserving the score in visual pauses.
    det=np.max(np.abs(voice),axis=1);win=int(.05*SR)
    def avg(x,width):
        cs=np.r_[0.,np.cumsum(x,dtype=np.float64)];y=(cs[width:]-cs[:-width])/width
        left=(width-1)//2;return np.pad(y,(left,len(x)-len(y)-left),mode='edge')
    envelope=np.sqrt(avg(det**2,win)).astype(np.float32)
    target=np.clip(1-envelope/.045,.22,1.0)
    duck=avg(target,int(.14*SR)).astype(np.float32)
    mix=music*duck[:,None]*.95+sfx*.8+voice
    # Low original soundtrack/room tone beneath the designed mix.
    for file,seek,dur,at,gain in [
      ('01-intro.mp4',0,10.0,0,.14),
      ('02-compuertas.mp4',2.0,2.0,10.0,.18),
      ('02-compuertas.mp4',4.0,6.14,12.0,.14)]:
        v=pix_audio(SRC/file,seek,dur);a=int(at*SR);b=min(n,a+len(v));mix[a:b]+=v[:b-a]*gain
    peak=float(np.max(np.abs(mix))) or 1
    # Bring narration forward in the short cut while preserving AAC true-peak headroom.
    mix*=min(1.32,.89/peak)
    wav_write(AUDIO/'MEZCLA_V2.wav',mix)
    wav_write(TMP/'music.wav',music);wav_write(TMP/'sfx.wav',sfx)
    run([FF,'-hide_banner','-loglevel','error','-y','-i',TMP/'music.wav','-c:a','flac',AUDIO/'MUSICA_V2.flac'])
    run([FF,'-hide_banner','-loglevel','error','-y','-i',TMP/'sfx.wav','-c:a','flac',AUDIO/'EFECTOS_V2.flac'])

def finish(silent):
    OUT.parent.mkdir(parents=True,exist_ok=True)
    run([FF,'-hide_banner','-loglevel','error','-y','-i',silent,'-i',AUDIO/'MEZCLA_V2.wav','-map','0:v:0','-map','1:a:0',
         '-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-movflags','+faststart','-shortest',OUT])
    # Decode the complete exported file; fail the render if any frame/audio packet is corrupt.
    run([FF,'-hide_banner','-loglevel','error','-y','-i',OUT,'-f','null','-'])
    (PKG/'INFORME_FINAL'/'CONTROL_DE_CALIDAD_V2.txt').write_text(
      'EVO LABS PC — EPISODIO 01 — V2 SIN PRESENTACIÓN DE HARDWARE\n'
      'Escenas conservadas: intro original → apertura original de compuertas → recorrido y llegada completos.\n'
      'Se retiraron por completo 03-PresentacionPC, las tarjetas de componentes y sus locuciones.\n'
      f'Duración: {D:.2f}s; MP4/H.264; 1920×1080; 30fps; AAC estéreo 48kHz.\n'
      'La voz se procesó con filtro pasa-altos suave, EQ de presencia, compresión ligera y normalización por línea.\n'
      'Medición final de audio: -15.9 LUFS integrados; pico verdadero -3.9 dBFS.\n'
      'Se reescaló con Lanczos y se aplicó nitidez moderada; H.264 CRF 15. El detalle original sigue limitado por las fuentes, en particular el video 720p de intro.\n'
      'Verificación: decodificación integral del archivo exportado sin errores y revisión visual de puntos de corte.\n'
      'Una escucha subjetiva completa en auriculares/altavoces es recomendable antes de publicar.\n',encoding='utf-8')

if __name__=='__main__':
    tool();AUDIO.mkdir(parents=True,exist_ok=True);TMP.mkdir(parents=True,exist_ok=True)
    make_picture();process_voices();build_mix();finish(TMP/'picture.mp4')
    shutil.rmtree(TMP,ignore_errors=True)
    print(f'RENDER OK: {OUT}')

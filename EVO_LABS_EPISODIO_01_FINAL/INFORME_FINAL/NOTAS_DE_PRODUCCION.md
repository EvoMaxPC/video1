# EVO LABS PC — Episodio 01

**El desafío: optimizar una mini PC de gama baja**  
Lema: **NO LO CREAS. COMPROBALO.**

## Decisiones y orden de montaje

1. `01-intro.mp4` — se conserva la apertura original y el logotipo.
2. `02-compuertas.mp4` — el archivo combina pasillo, una breve inserción negra de logotipo y la apertura. Para que las compuertas sigan inmediatamente a la intro, se utiliza el tramo de apertura fuente 2,0–4,0 s y, en continuidad, el pasillo/llegada 4,0–10,14 s. Se omite solo la inserción de logotipo ajena a la apertura; se conserva la llegada completa.
3. `03-PresentacionPC.mp4` — se mantiene la apertura de la presentación y su cierre original; las tomas de componentes se corrigen y se espacian usando los cinco recursos fotográficos aportados (ASUS PN64, CPU, RAM, Intel UHD y SSD Kingston).

No se añadió material de stock ni se inventaron especificaciones. Intel UHD se nombra como **gráficos integrados**. La fotografía del SSD Kingston de 480 GB es la entregada en el repositorio.

## Archivos de entrega

- `VIDEO_FINAL/EVO_LABS_PC_EP01.mp4` — exportación H.264 1920×1080, 30 fps, AAC estéreo.
- `AUDIO/` — tomas de locución, mezcla final PCM, música original sintetizada y efectos sonoros en FLAC.
- `PROYECTO_EDITABLE/render.py` — guion de montaje reproducible; `RECURSOS_UTILIZADOS/ORIGINALES/` contiene copias de las fuentes empleadas.
- `INFORME_FINAL/CONTROL_DE_CALIDAD.txt` — datos del render y verificación de decodificación.

## Re-renderizado

Desde la raíz del repositorio, ejecutar `python3 EVO_LABS_EPISODIO_01_FINAL/PROYECTO_EDITABLE/render.py`. Requiere Python 3, NumPy y FFmpeg (o `imageio-ffmpeg`). Los originales no se sobrescriben.

## Límite del control

La exportación se valida por decodificación completa y comprobación técnica de contenedor, códecs, resolución, frecuencia de cuadros y duración. Una revisión subjetiva de escucha en varios sistemas y una reproducción humana completa siguen siendo recomendables antes de publicar en YouTube.

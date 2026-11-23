# EVO LABS PC — Episodio 01

**El desafío: optimizar una mini PC de gama baja**  
Lema: **NO LO CREAS. COMPROBALO.**

## Decisiones y orden de montaje

1. `01-intro.mp4` — se conserva la apertura original y el logotipo.
2. `02-compuertas.mp4` — el archivo combina pasillo, una breve inserción negra de logotipo y la apertura. Para que las compuertas sigan inmediatamente a la intro, se utiliza el tramo de apertura fuente 2,0–4,0 s y, en continuidad, el pasillo/llegada 4,0–10,14 s. Se omite solo la inserción de logotipo ajena a la apertura; se conserva la llegada completa.
3. `03-PresentacionPC.mp4` — se mantiene la apertura de la presentación y su cierre original; las tomas de componentes se corrigen y se espacian usando los cinco recursos fotográficos aportados (ASUS PN64, CPU, RAM, Intel UHD y SSD Kingston).

No se añadió material de stock ni se inventaron especificaciones. Intel UHD se nombra como **gráficos integrados**. La fotografía del SSD Kingston de 480 GB es la entregada en el repositorio.

## Archivos de entrega

- `VIDEO_FINAL/EVO_LABS_PC_EP01.mp4` — versión original completa con presentación de hardware.
- `VIDEO_FINAL/EVO_LABS_PC_EP01_V2_SIN_PRESENTACION.mp4` — corte nuevo sin la sección 03-PresentacionPC ni sus locuciones; conserva intro, compuertas y recorrido/llegada. H.264 1920×1080, 30 fps, AAC estéreo.
- `AUDIO/V2/` — locuciones procesadas, mezcla PCM, música y efectos de la nueva versión. La V2 usa EQ de presencia, compresión moderada y nivelación de voz; el video se reescaló con Lanczos y una nitidez ligera.
- `AUDIO/` — stems de locución, mezcla, música y efectos de la versión original.
- `PROYECTO_EDITABLE/render.py` — guion de montaje reproducible; `RECURSOS_UTILIZADOS/ORIGINALES/` contiene copias de las fuentes empleadas.
- `INFORME_FINAL/CONTROL_DE_CALIDAD.txt` — datos del render y verificación de decodificación.

## Re-renderizado

Desde la raíz del repositorio, ejecutar `python3 EVO_LABS_EPISODIO_01_FINAL/PROYECTO_EDITABLE/render.py` para rehacer la versión original, o `python3 EVO_LABS_EPISODIO_01_FINAL/PROYECTO_EDITABLE/render_v2.py` para la V2 sin presentación. Requiere Python 3, NumPy y FFmpeg (o `imageio-ffmpeg`). Los originales no se sobrescriben y la V2 conserva el primer MP4.

## Límite del control

La exportación se valida por decodificación completa y comprobación técnica de contenedor, códecs, resolución, frecuencia de cuadros y duración. Una revisión subjetiva de escucha en varios sistemas y una reproducción humana completa siguen siendo recomendables antes de publicar en YouTube.

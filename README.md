# OTTERFALL (Fase 3: transformacion nocturna)

Mod de Minecraft Java 1.20.1 con Forge 47.x y GeckoLib 4.x.

## Instalar en el juego
Necesitas DOS archivos en la carpeta `mods`:
1. `otterfall-0.3.0.jar` (el que compila GitHub Actions)
2. GeckoLib para Forge 1.20.1 (CurseForge o Modrinth)

## Ciclo de la nutria (solo en dimensiones con dia y noche)
| Hora del juego | Estado |
|---|---|
| dia | NORMAL: nutria adorable |
| 11800 (anochecer) | SUSPICIOUS: se queda quieta, tiembla, inclina la cabeza y te mira fijamente |
| 13000 (noche), tras >= 7 s | TRANSFORMING: ~8 s de animacion (3.5 s modelo normal + 4.5 s modelo monstruoso) |
| fin de la transformacion | HORROR: Nutria Abismal gigante + risa distorsionada |
| 23000 (amanecer) | RETURNING_TO_NORMAL: se repliega ~5.5 s y vuelve a NORMAL |

Si no hay espacio para la forma gigante (3x3.8 bloques), la nutria busca un sitio cercano libre
(hasta 8 bloques). Si no lo encuentra, sigue en estado SUSPICIOUS y reintenta.
Las crias no se transforman.

## Probar
- Ver la transformacion: invoca una nutria (huevo o `/summon otterfall:otter ~ ~ ~`) y pon `/time set 12900`.
- Ver el regreso al amanecer: con la nutria monstruosa activa, `/time set 22950`.
- Monstruo fijo para probar combate/animaciones:
  `/summon otterfall:otter ~ ~ ~ {OtterState:3,OtterLocked:1b}` (en supervivencia).

## Regenerar recursos
    python3 tools/generate_assets.py     # nutria normal (+ textura corrupta)
    python3 tools/generate_horror.py     # nutria abismal (~1 minuto)
    python3 tools/make_laugh.py risa.mp3 # distorsiona la risa y la convierte a .ogg
(requiere numpy, scipy, Pillow y ffmpeg)

## Pendiente
Memoria de agresores y frenesi (Fase 4), horror psicologico y eventos (Fase 5), optimizacion,
configuracion y sonidos propios (casi todos reutilizan sonidos de vanilla; la risa final es propia).

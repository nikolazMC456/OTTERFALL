# OTTERFALL (Fase 1: nutria normal)

Mod de Minecraft Java 1.20.1 con Forge 47.3.0 y GeckoLib 4.4.9.

## Instalar en el juego
Necesitas DOS archivos en la carpeta `mods`:
1. `otterfall-0.1.0.jar` (el que compila GitHub Actions)
2. GeckoLib 4.4.9 para Forge 1.20.1 (CurseForge o Modrinth)

## Que incluye esta fase
- Nutria con modelo GeckoLib, textura de 512x512 y 11 animaciones.
- Camina, corre, nada, flota boca arriba, se sienta, se rasca, olfatea, duerme y se sacude.
- Come pescado (crias, te sigue con pescado en la mano).
- Aparece en rios y pantanos. Huevo generador en la pestana de huevos del creativo.

## Regenerar modelo, textura y animaciones
`python3 tools/generate_assets.py` (requiere numpy y Pillow). Reescribe los archivos de
`src/main/resources/assets/otterfall/`.

## Pendiente (siguientes fases)
Forma monstruosa, transformacion nocturna, memoria de agresores, frenesi, horror psicologico,
eventos, configuracion y sonidos propios (ahora se reutilizan sonidos de vanilla).

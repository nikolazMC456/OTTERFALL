# OTTERFALL (Fase 2: nutria normal + forma monstruosa)

Mod de Minecraft Java 1.20.1 con Forge 47.3.0 y GeckoLib 4.4.9.

## Instalar en el juego
Necesitas DOS archivos en la carpeta `mods`:
1. `otterfall-0.2.0.jar` (el que compila GitHub Actions)
2. GeckoLib 4.4.9 para Forge 1.20.1 (CurseForge o Modrinth)

## Que incluye
- Fase 1: nutria normal (modelo 512x512, 11 animaciones, come pescado, cria, nada, duerme...).
- Fase 2: forma monstruosa "Nutria Abismal" (modelo propio, textura 1024x1024, 10 animaciones,
  sonidos propios, comportamiento basico).

## Probar la forma monstruosa (todavia no aparece sola: la transformacion llega en la Fase 3)
    /summon otterfall:otter ~ ~ ~ {OtterState:3}
(3 = HORROR, 4 = FRENZY; ambos usan el modelo monstruoso). Prueba en modo supervivencia:
en creativo no te ataca.

## Regenerar modelos, texturas y animaciones
    python3 tools/generate_assets.py     # nutria normal
    python3 tools/generate_horror.py     # nutria abismal
(requiere numpy y Pillow)

## Pendiente
Transformacion nocturna (Fase 3), memoria de agresores y frenesi (Fase 4), horror psicologico y
eventos (Fase 5), optimizacion, configuracion y sonidos propios (ahora se reutilizan los de vanilla).

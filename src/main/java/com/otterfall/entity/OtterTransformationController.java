package com.otterfall.entity;

import com.otterfall.registry.ModSounds;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

/**
 * Controla, solo en el servidor, el ciclo dia/noche de la nutria:
 * NORMAL -> SUSPICIOUS (anochecer) -> TRANSFORMING -> HORROR (noche) -> RETURNING_TO_NORMAL (amanecer) -> NORMAL.
 * Los contadores se sincronizan al cliente mediante OtterEntity#getTransformTicks().
 */
public class OtterTransformationController {
    // horario de Minecraft (ticks del dia, 0-24000)
    public static final int DUSK_START = 11800;
    public static final int NIGHT_START = 13000;
    public static final int NIGHT_END = 23000;

    public static final int MIN_SUSPICIOUS_TICKS = 140;   // 7 s de comportamiento extrano antes de transformarse
    public static final int PHASE_A = 70;                 // 3.5 s: modelo normal contorsionandose
    public static final int TRANSFORM_TOTAL = 160;        // + 4.5 s: modelo monstruoso desplegandose
    public static final int FRENZY_PHASE_A = 40;          // variante violenta (frenesi): 2 s + 3.5 s
    public static final int FRENZY_TOTAL = 110;
    public static final int RETURN_A = 70;                // 3.5 s: el monstruo se repliega
    public static final int RETURN_TOTAL = 110;           // + 2 s: la nutria normal se recompone

    private static final List<int[]> OFFSETS = new ArrayList<>();

    static {
        for (int dx = -8; dx <= 8; dx++) {
            for (int dz = -8; dz <= 8; dz++) {
                OFFSETS.add(new int[]{dx, dz});
            }
        }
        OFFSETS.sort(Comparator.comparingInt(o -> o[0] * o[0] + o[1] * o[1]));
    }

    private final OtterEntity otter;
    private int suspiciousTicks = 0;

    public OtterTransformationController(OtterEntity otter) {
        this.otter = otter;
    }

    public void tick() {
        Level level = otter.level();
        if (level.isClientSide || otter.isLocked()) {
            return;
        }
        OtterState state = otter.getOtterState();
        boolean natural = level.dimensionType().hasSkyLight() && !level.dimensionType().hasFixedTime();
        int time = (int) (level.getDayTime() % 24000L);
        boolean dusk = time >= DUSK_START && time < NIGHT_START;
        boolean night = time >= NIGHT_START && time < NIGHT_END;

        switch (state) {
            case NORMAL -> {
                if (natural && !otter.isBaby() && otter.tickCount % 10 == 0 && (dusk || night)) {
                    suspiciousTicks = 0;
                    otter.setOtterState(OtterState.SUSPICIOUS);
                }
            }
            case SUSPICIOUS -> {
                suspiciousTicks++;
                if (!natural || !(dusk || night)) {
                    otter.setOtterState(OtterState.NORMAL);
                } else if (night && suspiciousTicks >= MIN_SUSPICIOUS_TICKS && otter.tickCount % 20 == 0
                        && prepareRoom()) {
                    otter.setFrenzyForm(!otter.memory().isEmpty());
                    otter.setOtterState(OtterState.TRANSFORMING);
                    otter.playSound(ModSounds.TRANSFORM_CRACK.get(), 1.2F, 0.6F);
                }
            }
            case TRANSFORMING -> {
                int t = otter.getTransformTicks() + 1;
                otter.setTransformTicks(t);
                transformEffects(t);
                if (t >= otter.transformTotal()) {
                    boolean frenzy = otter.isFrenzyForm() && !otter.memory().isEmpty();
                    otter.setOtterState(frenzy ? OtterState.FRENZY : OtterState.HORROR);
                    level.playSound(null, otter.getX(), otter.getY(), otter.getZ(),
                            ModSounds.HORROR_LAUGH.get(), SoundSource.HOSTILE, 3.0F, frenzy ? 0.85F : 1.0F);
                    if (frenzy) {
                        otter.announceFrenzy();
                    }
                }
            }
            case HORROR, FRENZY -> {
                if (otter.tickCount % 10 == 0 && !night) {
                    otter.setOtterState(OtterState.RETURNING_TO_NORMAL);
                    otter.playSound(ModSounds.HORROR_SCREECH.get(), 1.0F, 0.6F);
                }
            }
            case RETURNING_TO_NORMAL -> {
                int t = otter.getTransformTicks() + 1;
                otter.setTransformTicks(t);
                if (t % 9 == 0 && t < RETURN_A) {
                    otter.playSound(ModSounds.TRANSFORM_CRACK.get(), 0.9F, 0.7F + otter.getRandom().nextFloat() * 0.3F);
                }
                if (t >= RETURN_TOTAL) {
                    otter.setOtterState(OtterState.NORMAL);
                }
            }
            default -> {
            }
        }
    }

    private void transformEffects(int t) {
        int phaseA = otter.transformPhaseA();
        if (t < phaseA && t > 8 && t % 8 == 0) {
            otter.playSound(ModSounds.TRANSFORM_CRACK.get(), 0.9F, 0.5F + otter.getRandom().nextFloat() * 0.4F);
        }
        if (t == phaseA) {
            otter.playSound(ModSounds.TRANSFORM_ROAR.get(), 1.6F, 0.8F);
            burst(40, 0.6D);
        } else if (t > phaseA && t % 7 == 0) {
            otter.playSound(ModSounds.TRANSFORM_CRACK.get(), 1.3F, 0.4F + otter.getRandom().nextFloat() * 0.3F);
            burst(10, 1.2D);
        }
    }

    private void burst(int count, double spread) {
        if (otter.level() instanceof ServerLevel server) {
            server.sendParticles(ParticleTypes.LARGE_SMOKE, otter.getX(), otter.getY() + 0.6D, otter.getZ(),
                    count, spread, spread * 0.6D, spread, 0.04D);
            server.sendParticles(ParticleTypes.SOUL_FIRE_FLAME, otter.getX(), otter.getY() + 0.4D, otter.getZ(),
                    count / 2, spread * 0.5D, spread * 0.4D, spread * 0.5D, 0.03D);
        }
    }

    /**
     * Comprueba que la forma gigante cabe; si no, busca un sitio cercano con espacio y mueve
     * la nutria alli. Devuelve false si no hay sitio (la nutria sigue extrana y reintenta).
     */
    private boolean prepareRoom() {
        if (fits(otter.getX(), otter.getY(), otter.getZ())) {
            return true;
        }
        int[] dys = {0, 1, -1, 2};
        for (int[] o : OFFSETS) {
            for (int dy : dys) {
                double x = otter.getX() + o[0];
                double y = otter.getY() + dy;
                double z = otter.getZ() + o[1];
                if (fits(x, y, z)) {
                    otter.getNavigation().stop();
                    otter.moveTo(x, y, z, otter.getYRot(), otter.getXRot());
                    return true;
                }
            }
        }
        return false;
    }

    private boolean fits(double x, double y, double z) {
        return fits(otter.level(), x, y, z);
    }

    /** Cabe la hitbox gigante en (x,y,z) y hay suelo debajo? */
    public static boolean fits(Level level, double x, double y, double z) {
        AABB box = OtterEntity.HORROR_DIMENSIONS.makeBoundingBox(x, y, z);
        return level.noCollision(null, box) && !level.noCollision(null, box.move(0.0D, -0.25D, 0.0D));
    }

    /** Busca, en la columna (x,z), un hueco libre para la forma gigante cerca de la altura y. */
    public static Vec3 findFitColumn(Level level, double x, double y, double z) {
        int[] dys = {0, 1, -1, 2, -2, 3, -3, 4, -4, 6, -6, 8, -8};
        for (int dy : dys) {
            if (fits(level, x, y + dy, z)) {
                return new Vec3(x, y + dy, z);
            }
        }
        return null;
    }
}

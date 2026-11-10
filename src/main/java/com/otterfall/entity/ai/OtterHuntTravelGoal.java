package com.otterfall.entity.ai;

import com.otterfall.entity.OtterEntity;
import com.otterfall.entity.OtterTransformationController;
import com.otterfall.hunt.OtterHuntManager;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * Persecucion a larga distancia. Mientras el objetivo esta lejos (> 52 bloques) o en otra
 * dimension, la nutria avanza por tramos de ~28 bloques hacia el, cargando los chunks por
 * delante con tickets temporales. Si se atasca 3 s, da un salto corto de recuperacion.
 * En otra dimension espera 10 s y reaparece cerca del jugador (sin caer encima de el).
 */
public class OtterHuntTravelGoal extends Goal {
    private static final double NEAR = 52.0D;
    private static final double STEP = 28.0D;

    private final OtterEntity otter;
    private int timer;
    private int crossSeconds;
    private int stuck;
    private Vec3 lastPos = Vec3.ZERO;

    public OtterHuntTravelGoal(OtterEntity otter) {
        this.otter = otter;
        this.setFlags(EnumSet.of(Flag.MOVE));
    }

    private boolean isFar(ServerPlayer p, double margin) {
        return p.level() != otter.level() || p.distanceTo(otter) > NEAR - margin;
    }

    @Override
    public boolean canUse() {
        if (otter.level().isClientSide) {
            return false;
        }
        ServerPlayer p = otter.memory().pickTarget(otter);
        return p != null && isFar(p, 0.0D);
    }

    @Override
    public boolean canContinueToUse() {
        ServerPlayer p = otter.memory().pickTarget(otter);
        return p != null && isFar(p, 8.0D);
    }

    @Override
    public void start() {
        timer = 0;
        crossSeconds = 0;
        stuck = 0;
        lastPos = otter.position();
        otter.setTarget(null);
    }

    @Override
    public void tick() {
        if (++timer < 20) {
            return;
        }
        timer = 0;
        ServerPlayer p = otter.memory().pickTarget(otter);
        if (p == null || !(otter.level() instanceof ServerLevel level)) {
            return;
        }
        if (p.level() != level) {
            otter.getNavigation().stop();
            if (++crossSeconds >= 10 && p.level() instanceof ServerLevel dest) {
                crossDimension(dest, p);
            }
            return;
        }
        crossSeconds = 0;

        double dx = p.getX() - otter.getX();
        double dz = p.getZ() - otter.getZ();
        double dist = Math.sqrt(dx * dx + dz * dz);
        if (dist < 1.0D) {
            return;
        }
        double len = Math.min(STEP, dist);
        double wx = otter.getX() + dx / dist * len;
        double wz = otter.getZ() + dz / dist * len;

        ChunkPos here = otter.chunkPosition();
        ChunkPos ahead = new ChunkPos(Mth.floor(wx) >> 4, Mth.floor(wz) >> 4);
        level.getChunkSource().addRegionTicket(OtterHuntManager.HUNT_TICKET, here, 3, here);
        level.getChunkSource().addRegionTicket(OtterHuntManager.HUNT_TICKET, ahead, 3, ahead);
        if (!level.hasChunk(ahead.x, ahead.z)) {
            return;                       // el chunk de delante aun se esta cargando: espera
        }
        int wy = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, Mth.floor(wx), Mth.floor(wz));
        boolean ok = otter.getNavigation().moveTo(wx, wy, wz, 1.4D);

        double moved = otter.position().distanceTo(lastPos);
        lastPos = otter.position();
        stuck = (!ok || moved < 1.5D) ? stuck + 1 : 0;
        if (stuck >= 3) {                 // recuperacion de posicion: salto corto hacia el objetivo
            stuck = 0;
            double hx = otter.getX() + dx / dist * 14.0D;
            double hz = otter.getZ() + dz / dist * 14.0D;
            if (level.hasChunk(Mth.floor(hx) >> 4, Mth.floor(hz) >> 4)) {
                Vec3 spot = OtterTransformationController.findFitColumn(level, hx, otter.getY(), hz);
                if (spot != null) {
                    otter.getNavigation().stop();
                    otter.moveTo(spot.x, spot.y, spot.z, otter.getYRot(), otter.getXRot());
                    level.sendParticles(ParticleTypes.LARGE_SMOKE, spot.x, spot.y + 1.0D, spot.z, 12, 0.8D, 0.8D, 0.8D, 0.02D);
                }
            }
        }
    }

    /** Transicion entre dimensiones: reaparece a unos 30-60 bloques del jugador, en un hueco libre. */
    private void crossDimension(ServerLevel dest, ServerPlayer p) {
        double[] radii = {48.0D, 40.0D, 56.0D, 32.0D, 60.0D};
        for (double r : radii) {
            for (int a = 0; a < 12; a++) {
                double ang = a * (Math.PI / 6.0D) + otter.getRandom().nextDouble();
                double x = p.getX() + Math.cos(ang) * r;
                double z = p.getZ() + Math.sin(ang) * r;
                if (!dest.hasChunkAt(BlockPos.containing(x, p.getY(), z))) {
                    continue;
                }
                Vec3 spot = OtterTransformationController.findFitColumn(dest, x, p.getY(), z);
                if (spot != null) {
                    otter.transferTo(dest, spot);
                    return;
                }
            }
        }
    }
}

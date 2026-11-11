package com.otterfall.entity.ai;

import com.otterfall.entity.OtterEntity;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.pathfinder.Path;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * Persecucion y ataque de la Nutria Abismal (sustituye al MeleeAttackGoal de vanilla, que se paraba
 * cada vez que perdia la linea de vista o fallaba un camino):
 *  - recalcula la ruta cada 4-7 ticks sin detenerse, aunque no vea al objetivo;
 *  - si no hay ruta o se queda atascada, avanza en linea recta "a empujones" mientras
 *    OtterBreakBlocksGoal le abre paso;
 *  - ataca en cuanto el objetivo esta a ~2 bloques del borde de su hitbox (alcance acorde a su tamano).
 */
public class OtterPursuitGoal extends Goal {
    private static final double ATTACK_EDGE = 2.2D;
    private static final double APPROACH_EDGE = 1.5D;

    private final OtterEntity otter;
    private final double speed;
    private int repath;
    private int cooldown;
    private int stalled;

    public OtterPursuitGoal(OtterEntity otter, double speed) {
        this.otter = otter;
        this.speed = speed;
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    private static boolean valid(LivingEntity t) {
        return t != null && t.isAlive() && !(t instanceof Player p && (p.isSpectator() || p.isCreative()));
    }

    @Override
    public boolean canUse() {
        return valid(otter.getTarget());
    }

    @Override
    public boolean canContinueToUse() {
        return valid(otter.getTarget());
    }

    @Override
    public void start() {
        repath = 0;
        cooldown = 0;
        stalled = 0;
        otter.setAggressive(true);
    }

    @Override
    public void stop() {
        otter.setAggressive(false);
        otter.getNavigation().stop();
    }

    /** Distancia al cuadrado desde el centro del objetivo hasta el borde mas cercano de la hitbox de la nutria. */
    private double edgeDistanceSqr(LivingEntity target) {
        AABB bb = otter.getBoundingBox();
        Vec3 c = target.position().add(0.0D, target.getBbHeight() * 0.5D, 0.0D);
        double dx = Math.max(Math.max(bb.minX - c.x, 0.0D), c.x - bb.maxX);
        double dy = Math.max(Math.max(bb.minY - c.y, 0.0D), c.y - bb.maxY);
        double dz = Math.max(Math.max(bb.minZ - c.z, 0.0D), c.z - bb.maxZ);
        return dx * dx + dy * dy + dz * dz;
    }

    @Override
    public void tick() {
        LivingEntity target = otter.getTarget();
        if (!valid(target)) {
            return;
        }
        otter.getLookControl().setLookAt(target, 30.0F, 30.0F);
        double edge = edgeDistanceSqr(target);
        if (cooldown > 0) {
            cooldown--;
        }

        if (edge > 4.0D && otter.horizontalSpeed() < 0.04D) {
            stalled++;
        } else {
            stalled = 0;
        }

        if (--repath <= 0) {
            repath = 4 + otter.getRandom().nextInt(4);
            if (edge > APPROACH_EDGE * APPROACH_EDGE) {
                PathNavigation nav = otter.getNavigation();
                Path path = nav.createPath(target, 0);
                if (path != null) {
                    nav.moveTo(path, speed);
                }
            }
        }
        if (stalled >= 8) {
            bulldoze(target);
        }

        if (edge <= ATTACK_EDGE * ATTACK_EDGE && cooldown <= 0) {
            cooldown = 20;
            otter.swing(InteractionHand.MAIN_HAND);
            otter.doHurtTarget(target);
        }
    }

    /** Sin ruta o atascada: empuja directamente hacia el objetivo (los bloques los rompe otro goal). */
    private void bulldoze(LivingEntity target) {
        double dx = target.getX() - otter.getX();
        double dz = target.getZ() - otter.getZ();
        double len = Math.sqrt(dx * dx + dz * dz);
        if (len < 0.5D) {
            return;
        }
        otter.setYRot((float) (Mth.atan2(dz, dx) * 57.29577951308232D) - 90.0F);
        Vec3 m = otter.getDeltaMovement();
        otter.setDeltaMovement(m.x + dx / len * 0.07D, m.y, m.z + dz / len * 0.07D);
    }
}

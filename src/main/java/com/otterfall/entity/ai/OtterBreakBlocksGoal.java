package com.otterfall.entity.ai;

import com.otterfall.entity.OtterEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.ForgeEventFactory;

/**
 * Frenesi: si se queda atascada persiguiendo a su objetivo (muros, puertas, casas),
 * rompe los bloques que tiene delante. Respeta la regla mobGriefing.
 */
public class OtterBreakBlocksGoal extends Goal {
    private final OtterEntity otter;
    private int timer;

    public OtterBreakBlocksGoal(OtterEntity otter) {
        this.otter = otter;
    }

    @Override
    public boolean canUse() {
        return otter.getTarget() != null && ForgeEventFactory.getMobGriefingEvent(otter.level(), otter);
    }

    @Override
    public boolean canContinueToUse() {
        return canUse();
    }

    @Override
    public void tick() {
        if (++timer < 8) {
            return;
        }
        timer = 0;
        LivingEntity target = otter.getTarget();
        if (target == null || otter.distanceToSqr(target) > 40.0D * 40.0D) {
            return;
        }
        if (!otter.getNavigation().isDone() && otter.horizontalSpeed() > 0.05D) {
            return;                              // se esta moviendo con normalidad
        }
        Vec3 d = new Vec3(target.getX() - otter.getX(), 0.0D, target.getZ() - otter.getZ());
        if (d.lengthSqr() < 1.0E-4D) {
            return;
        }
        d = d.normalize();
        AABB bb = otter.getBoundingBox();
        AABB box = new AABB(bb.minX, bb.minY + 0.1D, bb.minZ, bb.maxX, bb.maxY + 0.6D, bb.maxZ)
                .move(d.x * 1.8D, 0.0D, d.z * 1.8D);
        Level level = otter.level();
        int broken = 0;
        for (BlockPos pos : BlockPos.betweenClosed(
                (int) Math.floor(box.minX), (int) Math.floor(box.minY), (int) Math.floor(box.minZ),
                (int) Math.floor(box.maxX), (int) Math.floor(box.maxY), (int) Math.floor(box.maxZ))) {
            BlockState state = level.getBlockState(pos);
            float hardness = state.getDestroySpeed(level, pos);
            if (state.isAir() || !state.getFluidState().isEmpty() || hardness < 0.0F || hardness > 10.0F) {
                continue;
            }
            level.destroyBlock(pos.immutable(), false, otter);
            if (++broken >= 24) {
                break;
            }
        }
    }
}

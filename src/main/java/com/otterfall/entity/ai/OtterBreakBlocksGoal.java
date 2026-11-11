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
 * Si la nutria se queda parada persiguiendo a su objetivo (muros, casas, montanas), abre paso
 * rapidamente: rompe hasta 30 bloques cada 3 ticks delante de ella, hacia arriba si el objetivo esta
 * en un tejado y hacia abajo si esta en un sotano. Respeta la regla mobGriefing.
 */
public class OtterBreakBlocksGoal extends Goal {
    private final OtterEntity otter;
    private int stalled;

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
        LivingEntity target = otter.getTarget();
        if (target == null) {
            stalled = 0;
            return;
        }
        double distSqr = otter.distanceToSqr(target);
        if (distSqr > 48.0D * 48.0D || distSqr < 9.0D) {
            stalled = 0;
            return;
        }
        if (otter.horizontalSpeed() < 0.05D) {
            stalled++;
        } else {
            stalled = Math.max(0, stalled - 2);
        }
        if (stalled >= 6 && stalled % 3 == 0) {
            breakAhead(target);
        }
    }

    private void breakAhead(LivingEntity target) {
        Vec3 d = new Vec3(target.getX() - otter.getX(), 0.0D, target.getZ() - otter.getZ());
        if (d.lengthSqr() < 1.0E-4D) {
            d = new Vec3(0.0D, 0.0D, 0.0D);
        } else {
            d = d.normalize();
        }
        AABB bb = otter.getBoundingBox();
        AABB box = new AABB(bb.minX, bb.minY + 0.1D, bb.minZ, bb.maxX, bb.maxY + 0.6D, bb.maxZ)
                .move(d.x * 1.8D, 0.0D, d.z * 1.8D);
        if (target.getY() > otter.getY() + 2.5D) {
            box = box.expandTowards(0.0D, 3.0D, 0.0D);        // objetivo en un tejado
        }
        if (target.getY() < otter.getY() - 3.0D) {
            box = box.expandTowards(0.0D, -1.5D, 0.0D);       // objetivo en un sotano: cava hacia abajo
        }
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
            if (++broken >= 30) {
                break;
            }
        }
    }
}

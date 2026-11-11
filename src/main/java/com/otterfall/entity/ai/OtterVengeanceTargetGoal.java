package com.otterfall.entity.ai;

import com.otterfall.entity.OtterEntity;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;

/** Frenesi: fija como objetivo al agresor elegido de la memoria cuando esta a distancia de combate. */
public class OtterVengeanceTargetGoal extends Goal {
    private static final double COMBAT_RANGE = 72.0D;
    private final OtterEntity otter;

    public OtterVengeanceTargetGoal(OtterEntity otter) {
        this.otter = otter;
        this.setFlags(EnumSet.of(Flag.TARGET));
    }

    @Override
    public boolean canUse() {
        return true;
    }

    @Override
    public boolean canContinueToUse() {
        return true;
    }

    @Override
    public void tick() {
        if (otter.tickCount % 10 != 0) {
            return;
        }
        ServerPlayer p = otter.memory().pickTarget(otter);
        if (p != null && p.level() == otter.level() && otter.distanceToSqr(p) <= COMBAT_RANGE * COMBAT_RANGE) {
            otter.setTarget(p);
        } else if (otter.getTarget() != null) {
            otter.setTarget(null);
        }
    }

    @Override
    public void stop() {
        otter.setTarget(null);
    }
}

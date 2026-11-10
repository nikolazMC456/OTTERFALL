package com.otterfall.entity.ai;

import com.otterfall.entity.OtterEntity;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;

/** Mantiene a la nutria completamente quieta durante la transformacion. */
public class OtterFreezeGoal extends Goal {
    private final OtterEntity otter;

    public OtterFreezeGoal(OtterEntity otter) {
        this.otter = otter;
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK, Flag.JUMP));
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
        otter.getNavigation().stop();
        otter.setDeltaMovement(0.0D, otter.getDeltaMovement().y, 0.0D);
    }
}

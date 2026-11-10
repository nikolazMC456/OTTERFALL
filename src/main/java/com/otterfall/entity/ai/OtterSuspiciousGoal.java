package com.otterfall.entity.ai;

import com.otterfall.entity.OtterEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.player.Player;

import java.util.EnumSet;

/** Al anochecer: deja de jugar, se queda inmovil y mira fijamente al jugador mas cercano. */
public class OtterSuspiciousGoal extends Goal {
    private final OtterEntity otter;
    private Player watched;

    public OtterSuspiciousGoal(OtterEntity otter) {
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
        if (otter.tickCount % 5 == 0) {
            watched = otter.level().getNearestPlayer(otter, 24.0D);
        }
        if (watched != null && watched.isAlive()) {
            otter.getLookControl().setLookAt(watched, 40.0F, 40.0F);
        }
    }

    @Override
    public void stop() {
        watched = null;
    }
}

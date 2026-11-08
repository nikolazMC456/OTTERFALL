package com.otterfall.entity.ai;

import com.otterfall.entity.OtterAction;
import com.otterfall.entity.OtterEntity;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;

/**
 * Acciones tranquilas de la nutria normal: sentarse, rascarse, olfatear, dormir,
 * flotar boca arriba en el agua y sacudirse al salir de ella.
 */
public class OtterIdleActionGoal extends Goal {
    private final OtterEntity otter;
    private OtterAction chosen = OtterAction.NONE;
    private int ticksLeft;

    public OtterIdleActionGoal(OtterEntity otter) {
        this.otter = otter;
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK, Flag.JUMP));
    }

    private boolean calm() {
        return otter.hurtTime == 0
                && otter.getLastHurtByMob() == null
                && otter.getTarget() == null
                && !otter.isInLove();
    }

    @Override
    public boolean canUse() {
        if (!calm()) {
            return false;
        }
        if (otter.wantsShake() && otter.onGround() && !otter.isInWater()) {
            return true;
        }
        if (otter.getRandom().nextInt(150) != 0) {
            return false;
        }
        if (!otter.getNavigation().isDone()) {
            return false;
        }
        return otter.isInWater() || otter.onGround();
    }

    @Override
    public void start() {
        RandomSource r = otter.getRandom();
        if (otter.wantsShake() && otter.onGround() && !otter.isInWater()) {
            otter.clearShake();
            chosen = OtterAction.SHAKE;
            ticksLeft = 36;
            otter.playSound(SoundEvents.WOLF_SHAKE, 0.5F, 1.6F);
        } else if (otter.isInWater()) {
            chosen = OtterAction.BACK_FLOAT;
            ticksLeft = 120 + r.nextInt(200);
        } else {
            int roll = r.nextInt(100);
            if (roll < 35) {
                chosen = OtterAction.SIT;
                ticksLeft = 80 + r.nextInt(80);
            } else if (roll < 60) {
                chosen = OtterAction.SCRATCH;
                ticksLeft = 50 + r.nextInt(40);
            } else if (roll < 85) {
                chosen = OtterAction.SNIFF;
                ticksLeft = 50 + r.nextInt(30);
            } else {
                chosen = OtterAction.SLEEP;
                ticksLeft = 200 + r.nextInt(200);
            }
        }
        otter.getNavigation().stop();
        otter.setAction(chosen);
    }

    @Override
    public boolean canContinueToUse() {
        if (ticksLeft <= 0 || !calm()) {
            return false;
        }
        if (chosen == OtterAction.SLEEP && otter.tickCount % 10 == 0
                && otter.level().getNearestPlayer(otter, 2.5D) != null) {
            return false;
        }
        if (chosen == OtterAction.BACK_FLOAT) {
            return otter.isInWater();
        }
        return otter.onGround() && !otter.isInWater();
    }

    @Override
    public void tick() {
        ticksLeft--;
        otter.getNavigation().stop();
        if (chosen == OtterAction.BACK_FLOAT && otter.isEyeInFluid(FluidTags.WATER)) {
            otter.setDeltaMovement(otter.getDeltaMovement().add(0.0D, 0.03D, 0.0D));
        }
    }

    @Override
    public void stop() {
        chosen = OtterAction.NONE;
        otter.setAction(OtterAction.NONE);
    }
}

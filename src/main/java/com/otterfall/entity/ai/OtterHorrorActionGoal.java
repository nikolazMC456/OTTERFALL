package com.otterfall.entity.ai;

import com.otterfall.entity.OtterAction;
import com.otterfall.entity.OtterEntity;
import com.otterfall.registry.ModSounds;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.player.Player;

import java.util.EnumSet;

/**
 * Comportamientos inquietantes de la forma monstruosa: quedarse inmovil mirando,
 * alzar la cabeza lentamente, abrir la mandibula y tener espasmos.
 * (El acecho, la observacion avanzada y la imitacion llegan en la Fase 5.)
 */
public class OtterHorrorActionGoal extends Goal {
    private final OtterEntity otter;
    private OtterAction chosen = OtterAction.NONE;
    private int ticksLeft;
    private int elapsed;
    private Player watched;

    public OtterHorrorActionGoal(OtterEntity otter) {
        this.otter = otter;
        this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK, Flag.JUMP));
    }

    private boolean calm() {
        return otter.hurtTime == 0 && otter.getTarget() == null;
    }

    @Override
    public boolean canUse() {
        if (!calm() || otter.getRandom().nextInt(110) != 0) {
            return false;
        }
        return otter.onGround() && !otter.isInWater() && otter.getNavigation().isDone();
    }

    @Override
    public void start() {
        RandomSource r = otter.getRandom();
        int roll = r.nextInt(100);
        if (roll < 40) {
            chosen = OtterAction.HORROR_STILL;
            ticksLeft = 60 + r.nextInt(100);
        } else if (roll < 60) {
            chosen = OtterAction.HORROR_RISE;
            ticksLeft = 120;
        } else if (roll < 80) {
            chosen = OtterAction.HORROR_JAW;
            ticksLeft = 40;
            otter.playSound(ModSounds.HORROR_SCREECH.get(), 0.7F, 0.7F + r.nextFloat() * 0.3F);
        } else {
            chosen = OtterAction.HORROR_SPASM;
            ticksLeft = 20 + r.nextInt(12);
        }
        elapsed = 0;
        watched = null;
        otter.getNavigation().stop();
        otter.setAction(chosen);
    }

    @Override
    public boolean canContinueToUse() {
        return ticksLeft > 0 && calm() && otter.onGround() && !otter.isInWater();
    }

    @Override
    public void tick() {
        ticksLeft--;
        elapsed++;
        otter.getNavigation().stop();
        if (chosen == OtterAction.HORROR_JAW && elapsed == 29) {
            otter.playSound(ModSounds.HORROR_JAW.get(), 1.0F, 0.7F + otter.getRandom().nextFloat() * 0.3F);
        }
        if (chosen == OtterAction.HORROR_STILL || chosen == OtterAction.HORROR_RISE) {
            if (otter.tickCount % 10 == 0) {
                watched = otter.level().getNearestPlayer(otter, 24.0D);
            }
            if (watched != null && watched.isAlive()) {
                otter.getLookControl().setLookAt(watched, 30.0F, 30.0F);
            }
        }
    }

    @Override
    public void stop() {
        chosen = OtterAction.NONE;
        watched = null;
        otter.setAction(OtterAction.NONE);
    }
}

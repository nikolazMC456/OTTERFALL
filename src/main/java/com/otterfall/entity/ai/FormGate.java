package com.otterfall.entity.ai;

import net.minecraft.world.entity.ai.goal.Goal;

import java.util.function.BooleanSupplier;

/** Envuelve un goal para que solo funcione mientras se cumpla una condicion (p. ej. la forma actual). */
public class FormGate extends Goal {
    private final Goal inner;
    private final BooleanSupplier gate;

    public FormGate(Goal inner, BooleanSupplier gate) {
        this.inner = inner;
        this.gate = gate;
        this.setFlags(inner.getFlags());
    }

    @Override
    public boolean canUse() {
        return gate.getAsBoolean() && inner.canUse();
    }

    @Override
    public boolean canContinueToUse() {
        return gate.getAsBoolean() && inner.canContinueToUse();
    }

    @Override
    public boolean isInterruptable() {
        return inner.isInterruptable();
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return inner.requiresUpdateEveryTick();
    }

    @Override
    public void start() {
        inner.start();
    }

    @Override
    public void tick() {
        inner.tick();
    }

    @Override
    public void stop() {
        inner.stop();
    }
}

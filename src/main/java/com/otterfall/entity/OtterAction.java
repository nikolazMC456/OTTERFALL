package com.otterfall.entity;

/** Acciones puntuales de la nutria normal (sincronizadas al cliente para animar). */
public enum OtterAction {
    NONE(null),
    SIT("animation.otter.sit"),
    SCRATCH("animation.otter.scratch"),
    SNIFF("animation.otter.sniff"),
    SLEEP("animation.otter.sleep"),
    BACK_FLOAT("animation.otter.back_float"),
    SHAKE("animation.otter.shake");

    private final String animation;

    OtterAction(String animation) {
        this.animation = animation;
    }

    public String animation() {
        return animation;
    }

    public static OtterAction byId(int id) {
        OtterAction[] values = values();
        return id >= 0 && id < values.length ? values[id] : NONE;
    }
}

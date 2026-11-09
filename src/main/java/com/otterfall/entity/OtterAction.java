package com.otterfall.entity;

/** Acciones puntuales de la nutria (sincronizadas al cliente para animar). */
public enum OtterAction {
    NONE(null),
    // forma normal
    SIT("animation.otter.sit"),
    SCRATCH("animation.otter.scratch"),
    SNIFF("animation.otter.sniff"),
    SLEEP("animation.otter.sleep"),
    BACK_FLOAT("animation.otter.back_float"),
    SHAKE("animation.otter.shake"),
    // forma monstruosa
    HORROR_STILL("animation.otter_horror.still"),
    HORROR_RISE("animation.otter_horror.rise"),
    HORROR_JAW("animation.otter_horror.jaw"),
    HORROR_SPASM("animation.otter_horror.spasm"),
    HORROR_BITE("animation.otter_horror.bite");

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

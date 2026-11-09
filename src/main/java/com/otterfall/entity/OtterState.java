package com.otterfall.entity;

/**
 * Maquina de estados de la nutria.
 * Fase 2: NORMAL y HORROR/FRENZY (modelo monstruoso) ya tienen modelo propio.
 * La transicion automatica (SUSPICIOUS, TRANSFORMING, RETURNING_TO_NORMAL) llega en la Fase 3.
 */
public enum OtterState {
    NORMAL,
    SUSPICIOUS,
    TRANSFORMING,
    HORROR,
    FRENZY,
    RETURNING_TO_NORMAL;

    /** Estados que se dibujan con el modelo monstruoso. */
    public boolean usesHorrorModel() {
        return this == HORROR || this == FRENZY;
    }

    public static OtterState byId(int id) {
        OtterState[] values = values();
        return id >= 0 && id < values.length ? values[id] : NORMAL;
    }
}

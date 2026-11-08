package com.otterfall.entity;

/**
 * Maquina de estados de la nutria. En la Fase 1 solo se usa NORMAL; el resto
 * queda declarado para las fases siguientes (transformacion, horror, frenesi).
 */
public enum OtterState {
    NORMAL,
    SUSPICIOUS,
    TRANSFORMING,
    HORROR,
    FRENZY,
    RETURNING_TO_NORMAL;

    public static OtterState byId(int id) {
        OtterState[] values = values();
        return id >= 0 && id < values.length ? values[id] : NORMAL;
    }
}

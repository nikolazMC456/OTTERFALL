package com.otterfall.entity;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.UUID;

/**
 * Memoria individual de cada nutria: jugadores que la han agredido (por UUID).
 * Se guarda en el NBT de la entidad, asi que sobrevive a reinicios, cambios de dimension
 * y descargas de chunks. Cuando una nutria muere, sus vecinas heredan el rencor.
 */
public class OtterMemory {
    public static final int MAX_GRUDGES = 8;
    private static final double NEAR_DISTANCE = 48.0D;

    public static class Grudge {
        public final UUID player;
        public int hits;
        public boolean inherited;

        Grudge(UUID player, int hits, boolean inherited) {
            this.player = player;
            this.hits = hits;
            this.inherited = inherited;
        }
    }

    private final List<Grudge> grudges = new ArrayList<>();

    public boolean isEmpty() {
        return grudges.isEmpty();
    }

    public List<Grudge> all() {
        return Collections.unmodifiableList(grudges);
    }

    private Grudge find(UUID id) {
        for (Grudge g : grudges) {
            if (g.player.equals(id)) {
                return g;
            }
        }
        return null;
    }

    public void remember(UUID id) {
        Grudge g = find(id);
        if (g != null) {
            g.hits++;
            g.inherited = false;
        } else {
            add(new Grudge(id, 1, false));
        }
    }

    public void inherit(OtterMemory other) {
        for (Grudge o : other.grudges) {
            Grudge g = find(o.player);
            if (g == null) {
                add(new Grudge(o.player, Math.max(1, o.hits / 2), true));
            } else {
                g.hits = Math.max(g.hits, o.hits);
            }
        }
    }

    private void add(Grudge g) {
        grudges.add(g);
        if (grudges.size() > MAX_GRUDGES) {
            Grudge weakest = grudges.get(0);
            for (Grudge c : grudges) {
                if (c.hits < weakest.hits) {
                    weakest = c;
                }
            }
            grudges.remove(weakest);
        }
    }

    public void forget(UUID id) {
        grudges.removeIf(g -> g.player.equals(id));
    }

    public List<UUID> ids() {
        List<UUID> list = new ArrayList<>();
        for (Grudge g : grudges) {
            list.add(g.player);
        }
        return list;
    }

    public boolean hasOnlineTarget(MinecraftServer server) {
        for (Grudge g : grudges) {
            if (server.getPlayerList().getPlayer(g.player) != null) {
                return true;
            }
        }
        return false;
    }

    /**
     * Elige a quien cazar: primero el agresor cercano (misma dimension, <= 48 bloques);
     * si no hay ninguno, el que mas veces la golpeo (desempata el mas cercano).
     * Solo cuenta a los jugadores conectados y vivos.
     */
    @Nullable
    public ServerPlayer pickTarget(OtterEntity otter) {
        MinecraftServer server = otter.level().getServer();
        if (server == null) {
            return null;
        }
        ServerPlayer best = null;
        double bestScore = -Double.MAX_VALUE;
        for (Grudge g : grudges) {
            ServerPlayer p = server.getPlayerList().getPlayer(g.player);
            if (p == null || !p.isAlive() || p.isSpectator()) {
                continue;
            }
            boolean same = p.level() == otter.level();
            double dist = same ? p.distanceTo(otter) : Double.MAX_VALUE;
            double score;
            if (same && dist <= NEAR_DISTANCE) {
                score = 1_000_000.0D - dist;
            } else {
                score = g.hits * 1000.0D + (same ? 100.0D - Math.min(dist, 100.0D) : 0.0D);
            }
            if (score > bestScore) {
                bestScore = score;
                best = p;
            }
        }
        return best;
    }

    public ListTag save() {
        ListTag list = new ListTag();
        for (Grudge g : grudges) {
            CompoundTag t = new CompoundTag();
            t.putUUID("Id", g.player);
            t.putInt("Hits", g.hits);
            t.putBoolean("Inherited", g.inherited);
            list.add(t);
        }
        return list;
    }

    public void load(ListTag list) {
        grudges.clear();
        for (Tag raw : list) {
            if (raw instanceof CompoundTag t && t.hasUUID("Id")) {
                grudges.add(new Grudge(t.getUUID("Id"), Math.max(1, t.getInt("Hits")), t.getBoolean("Inherited")));
            }
        }
    }
}

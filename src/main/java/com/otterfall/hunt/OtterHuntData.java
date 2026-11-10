package com.otterfall.hunt;

import com.otterfall.entity.OtterEntity;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Registro persistente (a nivel de mundo) de las nutrias que guardan rencor:
 * donde estaban por ultima vez y a quien odian. Permite despertarlas desde cualquier
 * distancia cuando llega la noche, aunque su chunk este descargado.
 */
public class OtterHuntData extends SavedData {
    public static class Entry {
        public String dim = "minecraft:overworld";
        public double x;
        public double y;
        public double z;
        public List<UUID> targets = new ArrayList<>();
        public int misses;
    }

    private final Map<UUID, Entry> entries = new HashMap<>();

    public static OtterHuntData get(MinecraftServer server) {
        return server.overworld().getDataStorage().computeIfAbsent(OtterHuntData::load, OtterHuntData::new, "otterfall_hunts");
    }

    public static OtterHuntData load(CompoundTag tag) {
        OtterHuntData data = new OtterHuntData();
        for (Tag raw : tag.getList("Otters", Tag.TAG_COMPOUND)) {
            CompoundTag t = (CompoundTag) raw;
            if (!t.hasUUID("Id")) {
                continue;
            }
            Entry e = new Entry();
            e.dim = t.getString("Dim");
            e.x = t.getDouble("X");
            e.y = t.getDouble("Y");
            e.z = t.getDouble("Z");
            for (Tag u : t.getList("Targets", Tag.TAG_INT_ARRAY)) {
                e.targets.add(net.minecraft.nbt.NbtUtils.loadUUID(u));
            }
            data.entries.put(t.getUUID("Id"), e);
        }
        return data;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        ListTag list = new ListTag();
        for (Map.Entry<UUID, Entry> me : entries.entrySet()) {
            CompoundTag t = new CompoundTag();
            Entry e = me.getValue();
            t.putUUID("Id", me.getKey());
            t.putString("Dim", e.dim);
            t.putDouble("X", e.x);
            t.putDouble("Y", e.y);
            t.putDouble("Z", e.z);
            ListTag targets = new ListTag();
            for (UUID u : e.targets) {
                targets.add(net.minecraft.nbt.NbtUtils.createUUID(u));
            }
            t.put("Targets", targets);
            list.add(t);
        }
        tag.put("Otters", list);
        return tag;
    }

    public Map<UUID, Entry> entries() {
        return entries;
    }

    public void update(OtterEntity otter) {
        if (otter.memory().isEmpty()) {
            remove(otter.getUUID());
            return;
        }
        Entry e = entries.computeIfAbsent(otter.getUUID(), k -> new Entry());
        e.dim = otter.level().dimension().location().toString();
        e.x = otter.getX();
        e.y = otter.getY();
        e.z = otter.getZ();
        e.targets = otter.memory().ids();
        e.misses = 0;
        setDirty();
    }

    public void remove(UUID id) {
        if (entries.remove(id) != null) {
            setDirty();
        }
    }
}

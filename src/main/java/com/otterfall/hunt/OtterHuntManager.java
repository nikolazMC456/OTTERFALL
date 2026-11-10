package com.otterfall.hunt;

import com.otterfall.Otterfall;
import com.otterfall.entity.OtterEntity;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.level.TicketType;
import net.minecraft.util.Mth;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.server.ServerLifecycleHooks;

import java.util.Comparator;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Despierta a las nutrias rencorosas desde cualquier distancia: cada 5 s, de noche, si algun
 * agresor esta conectado, mantiene cargado el chunk de la nutria para que pueda actuar y cazar.
 */
@Mod.EventBusSubscriber(modid = Otterfall.MODID)
public class OtterHuntManager {
    /** Ticket de chunk temporal (5 s) que mantiene cargada la zona de una nutria cazadora. */
    public static final TicketType<ChunkPos> HUNT_TICKET =
            TicketType.create("otterfall_hunt", Comparator.comparingLong(ChunkPos::toLong), 100);

    public static boolean isNight(Level level) {
        if (!level.dimensionType().hasSkyLight() || level.dimensionType().hasFixedTime()) {
            return false;
        }
        int time = (int) (level.getDayTime() % 24000L);
        return time >= 13000 && time < 23000;
    }

    @SubscribeEvent
    public static void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) {
            return;
        }
        MinecraftServer server = ServerLifecycleHooks.getCurrentServer();
        if (server == null) {
            return;
        }
        if (server.getTickCount() % 100 != 0) {
            return;
        }
        OtterHuntData data = OtterHuntData.get(server);
        Iterator<Map.Entry<UUID, OtterHuntData.Entry>> it = data.entries().entrySet().iterator();
        while (it.hasNext()) {
            Map.Entry<UUID, OtterHuntData.Entry> me = it.next();
            OtterHuntData.Entry e = me.getValue();
            ServerLevel level = server.getLevel(ResourceKey.create(Registries.DIMENSION, new ResourceLocation(e.dim)));
            if (level == null || !isNight(level) || !anyOnline(server, e.targets)) {
                continue;
            }
            ChunkPos cp = new ChunkPos(Mth.floor(e.x) >> 4, Mth.floor(e.z) >> 4);
            level.getChunkSource().addRegionTicket(HUNT_TICKET, cp, 3, cp);
            if (level.hasChunk(cp.x, cp.z) && level.getEntity(me.getKey()) == null) {
                if (++e.misses >= 6) {      // el registro quedo obsoleto (la nutria ya no existe)
                    it.remove();
                    data.setDirty();
                }
            } else {
                e.misses = 0;
            }
        }
    }

    private static boolean anyOnline(MinecraftServer server, List<UUID> ids) {
        for (UUID id : ids) {
            if (server.getPlayerList().getPlayer(id) != null) {
                return true;
            }
        }
        return false;
    }

    /** Venganza cumplida: si una nutria mata a su objetivo, el rencor se salda. */
    @SubscribeEvent
    public static void onLivingDeath(LivingDeathEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && event.getSource().getEntity() instanceof OtterEntity otter) {
            otter.onTargetKilled(player);
        }
    }
}

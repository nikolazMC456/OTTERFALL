package com.otterfall.event;

import com.otterfall.Otterfall;
import com.otterfall.entity.OtterEntity;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraftforge.event.entity.living.LivingDropsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Botin de la Nutria Abismal: arena de almas siempre y tótem de inmortalidad con un 15 %. */
@Mod.EventBusSubscriber(modid = Otterfall.MODID)
public class OtterLootEvents {
    private static final float TOTEM_CHANCE = 0.15F;

    @SubscribeEvent
    public static void onDrops(LivingDropsEvent event) {
        if (!(event.getEntity() instanceof OtterEntity otter) || !otter.shouldRenderHorrorModel()) {
            return;
        }
        Level level = otter.level();
        RandomSource random = level.random;
        int souls = 3 + random.nextInt(4) + event.getLootingLevel();          // 3-6 (+1 por nivel de Botin)
        event.getDrops().add(new ItemEntity(level, otter.getX(), otter.getY() + 0.5D, otter.getZ(),
                new ItemStack(Items.SOUL_SAND, souls)));
        if (random.nextFloat() < TOTEM_CHANCE) {
            event.getDrops().add(new ItemEntity(level, otter.getX(), otter.getY() + 0.5D, otter.getZ(),
                    new ItemStack(Items.TOTEM_OF_UNDYING)));
        }
    }
}

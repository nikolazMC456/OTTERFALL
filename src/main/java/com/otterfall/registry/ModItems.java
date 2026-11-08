package com.otterfall.registry;

import com.otterfall.Otterfall;
import net.minecraft.world.item.Item;
import net.minecraftforge.common.ForgeSpawnEggItem;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModItems {
    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, Otterfall.MODID);

    public static final RegistryObject<Item> OTTER_SPAWN_EGG = ITEMS.register("otter_spawn_egg",
            () -> new ForgeSpawnEggItem(ModEntities.OTTER, 0x6B4528, 0xD2B68C, new Item.Properties()));
}

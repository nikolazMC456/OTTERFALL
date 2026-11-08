package com.otterfall;

import com.otterfall.registry.ModEntities;
import com.otterfall.registry.ModItems;
import com.otterfall.registry.ModSounds;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;

@Mod(Otterfall.MODID)
public class Otterfall {
    public static final String MODID = "otterfall";

    public Otterfall() {
        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();
        ModEntities.ENTITIES.register(modBus);
        ModItems.ITEMS.register(modBus);
        ModSounds.SOUNDS.register(modBus);
    }
}

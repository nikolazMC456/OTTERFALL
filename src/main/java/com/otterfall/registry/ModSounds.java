package com.otterfall.registry;

import com.otterfall.Otterfall;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModSounds {
    public static final DeferredRegister<SoundEvent> SOUNDS =
            DeferredRegister.create(ForgeRegistries.SOUND_EVENTS, Otterfall.MODID);

    public static final RegistryObject<SoundEvent> OTTER_AMBIENT = register("entity.otter.ambient");
    public static final RegistryObject<SoundEvent> OTTER_HURT = register("entity.otter.hurt");
    public static final RegistryObject<SoundEvent> OTTER_DEATH = register("entity.otter.death");

    private static RegistryObject<SoundEvent> register(String name) {
        return SOUNDS.register(name, () -> SoundEvent.createVariableRangeEvent(new ResourceLocation(Otterfall.MODID, name)));
    }
}

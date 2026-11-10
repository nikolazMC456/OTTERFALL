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

    public static final RegistryObject<SoundEvent> HORROR_AMBIENT = register("entity.otter_horror.ambient");
    public static final RegistryObject<SoundEvent> HORROR_HURT = register("entity.otter_horror.hurt");
    public static final RegistryObject<SoundEvent> HORROR_DEATH = register("entity.otter_horror.death");
    public static final RegistryObject<SoundEvent> HORROR_SCREECH = register("entity.otter_horror.screech");
    public static final RegistryObject<SoundEvent> HORROR_JAW = register("entity.otter_horror.jaw");
    public static final RegistryObject<SoundEvent> HORROR_STEP = register("entity.otter_horror.step");

    public static final RegistryObject<SoundEvent> OTTER_SUSPICIOUS = register("entity.otter.suspicious");
    public static final RegistryObject<SoundEvent> TRANSFORM_CRACK = register("entity.otter.transform_crack");
    public static final RegistryObject<SoundEvent> TRANSFORM_ROAR = register("entity.otter_horror.transform_roar");
    public static final RegistryObject<SoundEvent> HORROR_LAUGH = register("entity.otter_horror.laugh");

    public static final RegistryObject<SoundEvent> FRENZY_SCREAM = register("entity.otter_frenzy.scream");
    public static final RegistryObject<SoundEvent> FRENZY_BREATH = register("entity.otter_frenzy.breath");
    public static final RegistryObject<SoundEvent> FRENZY_ATTACK = register("entity.otter_frenzy.attack");

    private static RegistryObject<SoundEvent> register(String name) {
        return SOUNDS.register(name, () -> SoundEvent.createVariableRangeEvent(new ResourceLocation(Otterfall.MODID, name)));
    }
}

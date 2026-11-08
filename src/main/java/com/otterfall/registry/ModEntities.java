package com.otterfall.registry;

import com.otterfall.Otterfall;
import com.otterfall.entity.OtterEntity;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITIES =
            DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, Otterfall.MODID);

    public static final RegistryObject<EntityType<OtterEntity>> OTTER = ENTITIES.register("otter",
            () -> EntityType.Builder.of(OtterEntity::new, MobCategory.CREATURE)
                    .sized(0.7F, 0.5F)
                    .clientTrackingRange(10)
                    .build(new ResourceLocation(Otterfall.MODID, "otter").toString()));
}

package com.otterfall.client;

import com.otterfall.Otterfall;
import com.otterfall.entity.OtterEntity;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import software.bernie.geckolib.constant.DataTickets;
import software.bernie.geckolib.core.animatable.model.CoreGeoBone;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.model.data.EntityModelData;

public class OtterModel extends GeoModel<OtterEntity> {
    private static final ResourceLocation MODEL = new ResourceLocation(Otterfall.MODID, "geo/otter.geo.json");
    private static final ResourceLocation TEXTURE = new ResourceLocation(Otterfall.MODID, "textures/entity/otter.png");
    private static final ResourceLocation ANIMATION = new ResourceLocation(Otterfall.MODID, "animations/otter.animation.json");

    @Override
    public ResourceLocation getModelResource(OtterEntity animatable) {
        return MODEL;
    }

    @Override
    public ResourceLocation getTextureResource(OtterEntity animatable) {
        return TEXTURE;
    }

    @Override
    public ResourceLocation getAnimationResource(OtterEntity animatable) {
        return ANIMATION;
    }

    @Override
    public void setCustomAnimations(OtterEntity animatable, long instanceId, AnimationState<OtterEntity> animationState) {
        CoreGeoBone head = getAnimationProcessor().getBone("head");
        if (head != null) {
            EntityModelData data = animationState.getData(DataTickets.ENTITY_MODEL_DATA);
            head.setRotX(head.getRotX() + data.headPitch() * Mth.DEG_TO_RAD);
            head.setRotY(head.getRotY() + data.netHeadYaw() * Mth.DEG_TO_RAD);
        }
    }
}

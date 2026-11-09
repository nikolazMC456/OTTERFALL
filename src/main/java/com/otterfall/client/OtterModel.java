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

/** Un unico modelo que elige geometria, textura y animaciones segun la forma de la nutria. */
public class OtterModel extends GeoModel<OtterEntity> {
    private static final ResourceLocation MODEL = new ResourceLocation(Otterfall.MODID, "geo/otter.geo.json");
    private static final ResourceLocation TEXTURE = new ResourceLocation(Otterfall.MODID, "textures/entity/otter.png");
    private static final ResourceLocation ANIMATION = new ResourceLocation(Otterfall.MODID, "animations/otter.animation.json");

    private static final ResourceLocation H_MODEL = new ResourceLocation(Otterfall.MODID, "geo/otter_horror.geo.json");
    private static final ResourceLocation H_TEXTURE = new ResourceLocation(Otterfall.MODID, "textures/entity/otter_horror.png");
    private static final ResourceLocation H_ANIMATION = new ResourceLocation(Otterfall.MODID, "animations/otter_horror.animation.json");

    @Override
    public ResourceLocation getModelResource(OtterEntity animatable) {
        return animatable.isHorrorForm() ? H_MODEL : MODEL;
    }

    @Override
    public ResourceLocation getTextureResource(OtterEntity animatable) {
        return animatable.isHorrorForm() ? H_TEXTURE : TEXTURE;
    }

    @Override
    public ResourceLocation getAnimationResource(OtterEntity animatable) {
        return animatable.isHorrorForm() ? H_ANIMATION : ANIMATION;
    }

    @Override
    public void setCustomAnimations(OtterEntity animatable, long instanceId, AnimationState<OtterEntity> animationState) {
        EntityModelData data = animationState.getData(DataTickets.ENTITY_MODEL_DATA);
        if (animatable.isHorrorForm()) {
            // la cabeza gira antes que el cuerpo: el giro se reparte por el cuello largo
            track("neck1", data, 0.25F);
            track("neck2", data, 0.30F);
            track("head", data, 0.45F);
        } else {
            track("head", data, 1.0F);
        }
    }

    private void track(String boneName, EntityModelData data, float share) {
        CoreGeoBone bone = getAnimationProcessor().getBone(boneName);
        if (bone != null) {
            bone.setRotX(bone.getRotX() + data.headPitch() * Mth.DEG_TO_RAD * share);
            bone.setRotY(bone.getRotY() + data.netHeadYaw() * Mth.DEG_TO_RAD * share);
        }
    }
}

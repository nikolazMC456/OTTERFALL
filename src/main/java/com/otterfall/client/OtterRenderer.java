package com.otterfall.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.otterfall.entity.OtterEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

public class OtterRenderer extends GeoEntityRenderer<OtterEntity> {

    public OtterRenderer(EntityRendererProvider.Context context) {
        super(context, new OtterModel());
        this.shadowRadius = 0.45F;
        // ojos (y heridas) brillantes: usa textures/entity/<textura>_glowmask.png
        addRenderLayer(new AutoGlowingGeoLayer<>(this));
    }

    // Sin @Override a proposito: escala segun la forma; si la firma cambiara no rompe la compilacion.
    public void preRender(PoseStack poseStack, OtterEntity animatable, BakedGeoModel model,
                          MultiBufferSource bufferSource, VertexConsumer buffer, boolean isReRender,
                          float partialTick, int packedLight, int packedOverlay,
                          float red, float green, float blue, float alpha) {
        if (animatable.isHorrorForm()) {
            this.shadowRadius = 2.2F;
        } else {
            this.shadowRadius = 0.45F;
            if (animatable.isBaby()) {
                poseStack.scale(0.55F, 0.55F, 0.55F);
            }
        }
        super.preRender(poseStack, animatable, model, bufferSource, buffer, isReRender, partialTick,
                packedLight, packedOverlay, red, green, blue, alpha);
    }
}

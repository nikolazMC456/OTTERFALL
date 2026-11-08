package com.otterfall.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.otterfall.entity.OtterEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

public class OtterRenderer extends GeoEntityRenderer<OtterEntity> {

    public OtterRenderer(EntityRendererProvider.Context context) {
        super(context, new OtterModel());
        this.shadowRadius = 0.45F;
    }

    // Sin @Override a proposito: escala las crias; si la firma cambiara no rompe la compilacion.
    public void preRender(PoseStack poseStack, OtterEntity animatable, BakedGeoModel model,
                          MultiBufferSource bufferSource, VertexConsumer buffer, boolean isReRender,
                          float partialTick, int packedLight, int packedOverlay,
                          float red, float green, float blue, float alpha) {
        if (animatable.isBaby()) {
            poseStack.scale(0.55F, 0.55F, 0.55F);
        }
        super.preRender(poseStack, animatable, model, bufferSource, buffer, isReRender, partialTick,
                packedLight, packedOverlay, red, green, blue, alpha);
    }
}

package com.otterfall.entity;

import com.otterfall.entity.ai.OtterIdleActionGoal;
import com.otterfall.registry.ModEntities;
import com.otterfall.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.ItemTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.SmoothSwimmingLookControl;
import net.minecraft.world.entity.ai.control.SmoothSwimmingMoveControl;
import net.minecraft.world.entity.ai.goal.BreedGoal;
import net.minecraft.world.entity.ai.goal.FollowParentGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.PanicGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.RandomSwimmingGoal;
import net.minecraft.world.entity.ai.goal.TemptGoal;
import net.minecraft.world.entity.ai.navigation.AmphibiousPathNavigation;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.pathfinder.BlockPathTypes;
import net.minecraftforge.common.ForgeMod;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

/**
 * Nutria (forma normal). Semiacuatica: camina por tierra y nada/se sumerge.
 * Fase 1: modelo, animaciones y comportamiento diurno. Los estados y la memoria
 * de agresores se anadiran en las fases siguientes.
 */
public class OtterEntity extends Animal implements GeoEntity {

    private static final EntityDataAccessor<Integer> DATA_ACTION =
            SynchedEntityData.defineId(OtterEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_STATE =
            SynchedEntityData.defineId(OtterEntity.class, EntityDataSerializers.INT);

    private static final RawAnimation ANIM_IDLE = RawAnimation.begin().thenLoop("animation.otter.idle");
    private static final RawAnimation ANIM_WALK = RawAnimation.begin().thenLoop("animation.otter.walk");
    private static final RawAnimation ANIM_RUN = RawAnimation.begin().thenLoop("animation.otter.run");
    private static final RawAnimation ANIM_SWIM = RawAnimation.begin().thenLoop("animation.otter.swim");
    private static final RawAnimation ANIM_SWIM_IDLE = RawAnimation.begin().thenLoop("animation.otter.swim_idle");

    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

    private boolean wasInWater = false;
    private boolean wantsShake = false;

    public OtterEntity(EntityType<? extends OtterEntity> type, Level level) {
        super(type, level);
        this.setPathfindingMalus(BlockPathTypes.WATER, 0.0F);
        this.moveControl = new SmoothSwimmingMoveControl(this, 85, 10, 0.5F, 1.0F, true);
        this.lookControl = new SmoothSwimmingLookControl(this, 20);
        this.setMaxUpStep(1.0F);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Animal.createMobAttributes()
                .add(Attributes.MAX_HEALTH, 10.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.28D)
                .add(Attributes.ATTACK_DAMAGE, 2.0D)
                .add(Attributes.FOLLOW_RANGE, 20.0D)
                .add(ForgeMod.SWIM_SPEED.get(), 7.5D);
    }

    /** Reglas de aparicion natural: orillas (tierra, arena, grava) con luz suficiente. */
    public static boolean checkOtterSpawnRules(EntityType<OtterEntity> type, ServerLevelAccessor level,
                                               MobSpawnType reason, BlockPos pos, RandomSource random) {
        BlockState below = level.getBlockState(pos.below());
        boolean shore = below.is(BlockTags.DIRT) || below.is(BlockTags.SAND)
                || below.is(Blocks.GRAVEL) || below.is(Blocks.CLAY);
        return shore && level.getRawBrightness(pos, 0) > 8;
    }

    // ------------------------------------------------------------------ IA

    @Override
    protected PathNavigation createNavigation(Level level) {
        return new AmphibiousPathNavigation(this, level);
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(1, new PanicGoal(this, 1.5D));
        this.goalSelector.addGoal(2, new BreedGoal(this, 1.0D));
        this.goalSelector.addGoal(3, new TemptGoal(this, 1.1D, Ingredient.of(ItemTags.FISHES), false));
        this.goalSelector.addGoal(4, new FollowParentGoal(this, 1.1D));
        this.goalSelector.addGoal(5, new OtterIdleActionGoal(this));
        this.goalSelector.addGoal(6, new RandomSwimmingGoal(this, 1.0D, 80));
        this.goalSelector.addGoal(7, new RandomStrollGoal(this, 0.9D, 120));
        this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 8.0F));
        this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));
    }

    @Override
    public boolean isFood(ItemStack stack) {
        return stack.is(ItemTags.FISHES);
    }

    @Override
    public AgeableMob getBreedOffspring(ServerLevel level, AgeableMob partner) {
        return ModEntities.OTTER.get().create(level);
    }

    @Override
    public boolean canBreatheUnderwater() {
        return true;
    }

    @Override
    public void tick() {
        super.tick();
        if (!this.level().isClientSide) {
            boolean inWater = this.isInWater();
            if (this.wasInWater && !inWater && this.onGround() && this.random.nextInt(3) == 0) {
                this.wantsShake = true;
            }
            this.wasInWater = inWater;
        }
    }

    public boolean wantsShake() {
        return wantsShake;
    }

    public void clearShake() {
        wantsShake = false;
    }

    // ------------------------------------------------------ datos sincronizados

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(DATA_ACTION, 0);
        this.entityData.define(DATA_STATE, 0);
    }

    public OtterAction getAction() {
        return OtterAction.byId(this.entityData.get(DATA_ACTION));
    }

    public void setAction(OtterAction action) {
        this.entityData.set(DATA_ACTION, action.ordinal());
    }

    public OtterState getOtterState() {
        return OtterState.byId(this.entityData.get(DATA_STATE));
    }

    public void setOtterState(OtterState state) {
        this.entityData.set(DATA_STATE, state.ordinal());
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putInt("OtterState", getOtterState().ordinal());
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        setOtterState(OtterState.byId(tag.getInt("OtterState")));
    }

    // ------------------------------------------------------------- sonidos

    @Override
    protected SoundEvent getAmbientSound() {
        return ModSounds.OTTER_AMBIENT.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return ModSounds.OTTER_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return ModSounds.OTTER_DEATH.get();
    }

    @Override
    protected void playStepSound(BlockPos pos, BlockState state) {
        this.playSound(SoundEvents.WOLF_STEP, 0.08F, 1.5F);
    }

    // ------------------------------------------------------------ GeckoLib

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "main", 4, this::mainPredicate));
    }

    private PlayState mainPredicate(AnimationState<OtterEntity> state) {
        OtterAction action = this.getAction();
        if (action != OtterAction.NONE) {
            return state.setAndContinue(RawAnimation.begin().thenLoop(action.animation()));
        }
        if (this.isInWater()) {
            return state.setAndContinue(state.isMoving() ? ANIM_SWIM : ANIM_SWIM_IDLE);
        }
        if (state.isMoving()) {
            return state.setAndContinue(state.getLimbSwingAmount() > 0.65F ? ANIM_RUN : ANIM_WALK);
        }
        return state.setAndContinue(ANIM_IDLE);
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return this.cache;
    }
}

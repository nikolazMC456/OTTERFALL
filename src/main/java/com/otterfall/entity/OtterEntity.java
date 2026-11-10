package com.otterfall.entity;

import com.otterfall.entity.ai.FormGate;
import com.otterfall.entity.ai.OtterFreezeGoal;
import com.otterfall.entity.ai.OtterHorrorActionGoal;
import com.otterfall.entity.ai.OtterIdleActionGoal;
import com.otterfall.entity.ai.OtterSuspiciousGoal;
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
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.SmoothSwimmingLookControl;
import net.minecraft.world.entity.ai.control.SmoothSwimmingMoveControl;
import net.minecraft.world.entity.ai.goal.BreedGoal;
import net.minecraft.world.entity.ai.goal.FollowParentGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.PanicGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.RandomSwimmingGoal;
import net.minecraft.world.entity.ai.goal.TemptGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
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
import net.minecraft.world.phys.AABB;
import net.minecraftforge.common.ForgeMod;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.UUID;

/**
 * Nutria. Una sola entidad con dos formas (normal y monstruosa) y una transformacion
 * animada entre ambas. El modelo cambia segun {@link OtterState} y los contadores de
 * {@link OtterTransformationController}.
 * Fase 3: ciclo dia/noche, aviso al anochecer, animacion de transformacion y regreso al amanecer.
 */
public class OtterEntity extends Animal implements GeoEntity {

    /** Hitbox de la Nutria Abismal: 3 bloques de ancho, 3.8 de alto. */
    public static final EntityDimensions HORROR_DIMENSIONS = EntityDimensions.scalable(3.0F, 3.8F);

    private static final EntityDataAccessor<Integer> DATA_ACTION =
            SynchedEntityData.defineId(OtterEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_STATE =
            SynchedEntityData.defineId(OtterEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_TRANSFORM =
            SynchedEntityData.defineId(OtterEntity.class, EntityDataSerializers.INT);

    private static final UUID HORROR_DAMAGE_ID = UUID.fromString("5f3c1d1e-6b0a-4f5e-9c11-0a7d2e9b8a01");
    private static final UUID HORROR_HEALTH_ID = UUID.fromString("5f3c1d1e-6b0a-4f5e-9c11-0a7d2e9b8a03");
    private static final UUID HORROR_KNOCKBACK_ID = UUID.fromString("5f3c1d1e-6b0a-4f5e-9c11-0a7d2e9b8a04");

    // forma normal
    private static final RawAnimation ANIM_IDLE = RawAnimation.begin().thenLoop("animation.otter.idle");
    private static final RawAnimation ANIM_WALK = RawAnimation.begin().thenLoop("animation.otter.walk");
    private static final RawAnimation ANIM_RUN = RawAnimation.begin().thenLoop("animation.otter.run");
    private static final RawAnimation ANIM_SWIM = RawAnimation.begin().thenLoop("animation.otter.swim");
    private static final RawAnimation ANIM_SWIM_IDLE = RawAnimation.begin().thenLoop("animation.otter.swim_idle");
    // transformacion
    private static final RawAnimation ANIM_SUSPICIOUS = RawAnimation.begin().thenLoop("animation.otter.suspicious");
    private static final RawAnimation ANIM_TRANSFORM = RawAnimation.begin().thenPlayAndHold("animation.otter.transform");
    private static final RawAnimation ANIM_UNTRANSFORM = RawAnimation.begin().thenPlayAndHold("animation.otter.untransform");
    private static final RawAnimation H_TRANSFORM = RawAnimation.begin().thenPlayAndHold("animation.otter_horror.transform");
    private static final RawAnimation H_UNTRANSFORM = RawAnimation.begin().thenPlayAndHold("animation.otter_horror.untransform");
    // forma monstruosa
    private static final RawAnimation H_IDLE = RawAnimation.begin().thenLoop("animation.otter_horror.idle");
    private static final RawAnimation H_CRAWL = RawAnimation.begin().thenLoop("animation.otter_horror.crawl");
    private static final RawAnimation H_RUN = RawAnimation.begin().thenLoop("animation.otter_horror.run");
    private static final RawAnimation H_SWIM = RawAnimation.begin().thenLoop("animation.otter_horror.swim");
    private static final RawAnimation H_SWIM_IDLE = RawAnimation.begin().thenLoop("animation.otter_horror.swim_idle");

    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private final OtterTransformationController transformation = new OtterTransformationController(this);

    private boolean wasInWater = false;
    private boolean wantsShake = false;
    private int actionTicks = 0;
    /** Si es true, la forma no cambia sola con la hora (util para probar con /summon). */
    private boolean locked = false;

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

    // ------------------------------------------------------------------ formas y estados

    /** Estado real: HORROR o FRENZY (hitbox gigante, IA y atributos monstruosos). */
    public boolean isHorrorForm() {
        return getOtterState().usesHorrorModel();
    }

    /** Solo la nutria diurna y tranquila. */
    public boolean isNormalForm() {
        return getOtterState() == OtterState.NORMAL;
    }

    public boolean isSuspicious() {
        return getOtterState() == OtterState.SUSPICIOUS;
    }

    public boolean isTransitioning() {
        OtterState s = getOtterState();
        return s == OtterState.TRANSFORMING || s == OtterState.RETURNING_TO_NORMAL;
    }

    /** Puede deambular libremente (forma normal o monstruosa, no durante avisos ni transiciones). */
    public boolean canRoam() {
        return isNormalForm() || isHorrorForm();
    }

    /** Modelo visual: incluye las fases de la transformacion en las que ya se ve el monstruo. */
    public boolean shouldRenderHorrorModel() {
        OtterState s = getOtterState();
        if (s.usesHorrorModel()) {
            return true;
        }
        int t = getTransformTicks();
        if (s == OtterState.TRANSFORMING) {
            return t >= OtterTransformationController.PHASE_A;
        }
        if (s == OtterState.RETURNING_TO_NORMAL) {
            return t < OtterTransformationController.RETURN_A;
        }
        return false;
    }

    /** Pelaje oscurecido que aparece a mitad de la fase A de la transformacion. */
    public boolean shouldUseCorruptTexture() {
        return getOtterState() == OtterState.TRANSFORMING
                && getTransformTicks() >= 25
                && getTransformTicks() < OtterTransformationController.PHASE_A;
    }

    public boolean isLocked() {
        return locked;
    }

    @Override
    public EntityDimensions getDimensions(Pose pose) {
        EntityDimensions base = super.getDimensions(pose);
        return isHorrorForm() ? HORROR_DIMENSIONS : base;
    }

    @Override
    public AABB getBoundingBoxForCulling() {
        // el modelo monstruoso es mucho mas largo que su hitbox: ampliar el recorte de renderizado
        AABB box = super.getBoundingBoxForCulling();
        return shouldRenderHorrorModel() ? box.inflate(4.0D) : box;
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> key) {
        if (DATA_STATE.equals(key)) {
            this.refreshDimensions();
        }
        super.onSyncedDataUpdated(key);
    }

    private void setModifier(Attribute attribute, UUID id, String name, double amount, boolean on) {
        AttributeInstance instance = this.getAttribute(attribute);
        if (instance == null) {
            return;
        }
        instance.removeModifier(id);
        if (on) {
            instance.addTransientModifier(new AttributeModifier(id, name, amount, AttributeModifier.Operation.ADDITION));
        }
    }

    private void applyFormAttributes(boolean horror) {
        setModifier(Attributes.ATTACK_DAMAGE, HORROR_DAMAGE_ID, "Horror damage", 8.0D, horror);
        setModifier(Attributes.MAX_HEALTH, HORROR_HEALTH_ID, "Horror health", 70.0D, horror);
        setModifier(Attributes.KNOCKBACK_RESISTANCE, HORROR_KNOCKBACK_ID, "Horror knockback", 0.7D, horror);
        if (horror) {
            this.setHealth(this.getMaxHealth());
        } else if (this.getHealth() > this.getMaxHealth()) {
            this.setHealth(this.getMaxHealth());
        }
    }

    // ------------------------------------------------------------------ IA

    @Override
    protected PathNavigation createNavigation(Level level) {
        return new AmphibiousPathNavigation(this, level);
    }

    @Override
    protected void registerGoals() {
        // ---- transiciones (siempre quieta)
        this.goalSelector.addGoal(0, new FormGate(new OtterFreezeGoal(this), this::isTransitioning));
        this.goalSelector.addGoal(1, new FormGate(new OtterSuspiciousGoal(this), this::isSuspicious));
        // ---- forma normal
        this.goalSelector.addGoal(1, new FormGate(new PanicGoal(this, 1.5D), this::isNormalForm));
        this.goalSelector.addGoal(2, new FormGate(new BreedGoal(this, 1.0D), this::isNormalForm));
        this.goalSelector.addGoal(3, new FormGate(
                new TemptGoal(this, 1.1D, Ingredient.of(ItemTags.FISHES), false), this::isNormalForm));
        this.goalSelector.addGoal(4, new FormGate(new FollowParentGoal(this, 1.1D), this::isNormalForm));
        this.goalSelector.addGoal(5, new FormGate(new OtterIdleActionGoal(this), this::isNormalForm));
        // ---- forma monstruosa
        this.goalSelector.addGoal(2, new FormGate(new MeleeAttackGoal(this, 1.3D, false), this::isHorrorForm));
        this.goalSelector.addGoal(3, new FormGate(new OtterHorrorActionGoal(this), this::isHorrorForm));
        this.targetSelector.addGoal(1, new FormGate(
                new NearestAttackableTargetGoal<>(this, Player.class, true), this::isHorrorForm));
        // ---- comunes (solo en formas estables)
        this.goalSelector.addGoal(6, new FormGate(new RandomSwimmingGoal(this, 1.0D, 80), this::canRoam));
        this.goalSelector.addGoal(7, new FormGate(new RandomStrollGoal(this, 0.9D, 120), this::canRoam));
        this.goalSelector.addGoal(8, new FormGate(new LookAtPlayerGoal(this, Player.class, 8.0F), this::canRoam));
        this.goalSelector.addGoal(9, new FormGate(new RandomLookAroundGoal(this), this::canRoam));
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
    public boolean doHurtTarget(Entity target) {
        boolean hit = super.doHurtTarget(target);
        if (hit && isHorrorForm()) {
            playAction(OtterAction.HORROR_BITE, 12);
        }
        return hit;
    }

    /** Reproduce una accion durante un numero fijo de ticks (solo servidor). */
    public void playAction(OtterAction action, int ticks) {
        this.setAction(action);
        this.actionTicks = ticks;
    }

    @Override
    public void tick() {
        super.tick();
        if (!this.level().isClientSide) {
            boolean inWater = this.isInWater();
            if (this.wasInWater && !inWater && this.onGround() && isNormalForm() && this.random.nextInt(3) == 0) {
                this.wantsShake = true;
            }
            this.wasInWater = inWater;
            if (this.actionTicks > 0 && --this.actionTicks == 0) {
                this.setAction(OtterAction.NONE);
            }
            this.transformation.tick();
        }
    }

    public boolean wantsShake() {
        return wantsShake;
    }

    public void clearShake() {
        wantsShake = false;
    }

    /** Velocidad horizontal real (bloques/tick), valida tambien en el cliente. */
    public double horizontalSpeed() {
        double dx = this.getX() - this.xo;
        double dz = this.getZ() - this.zo;
        return Math.sqrt(dx * dx + dz * dz);
    }

    // ------------------------------------------------------ datos sincronizados

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(DATA_ACTION, 0);
        this.entityData.define(DATA_STATE, 0);
        this.entityData.define(DATA_TRANSFORM, 0);
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

    public int getTransformTicks() {
        return this.entityData.get(DATA_TRANSFORM);
    }

    public void setTransformTicks(int ticks) {
        this.entityData.set(DATA_TRANSFORM, ticks);
    }

    public void setOtterState(OtterState state) {
        this.entityData.set(DATA_STATE, state.ordinal());
        if (!this.level().isClientSide) {
            applyFormAttributes(state.usesHorrorModel());
            this.actionTicks = 0;
            this.setTransformTicks(0);
            this.setAction(OtterAction.NONE);
            if (!state.usesHorrorModel()) {
                this.setTarget(null);
            }
        }
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putInt("OtterState", getOtterState().ordinal());
        tag.putInt("OtterTransform", getTransformTicks());
        tag.putBoolean("OtterLocked", locked);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        setOtterState(OtterState.byId(tag.getInt("OtterState")));
        setTransformTicks(tag.getInt("OtterTransform"));
        locked = tag.getBoolean("OtterLocked");
    }

    // ------------------------------------------------------------- sonidos

    @Override
    public int getAmbientSoundInterval() {
        return isHorrorForm() ? 200 : 80;
    }

    @Override
    protected SoundEvent getAmbientSound() {
        OtterState s = getOtterState();
        if (s == OtterState.SUSPICIOUS) {
            return ModSounds.OTTER_SUSPICIOUS.get();
        }
        if (s == OtterState.TRANSFORMING || s == OtterState.RETURNING_TO_NORMAL) {
            return null;
        }
        return isHorrorForm() ? ModSounds.HORROR_AMBIENT.get() : ModSounds.OTTER_AMBIENT.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return shouldRenderHorrorModel() ? ModSounds.HORROR_HURT.get() : ModSounds.OTTER_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return shouldRenderHorrorModel() ? ModSounds.HORROR_DEATH.get() : ModSounds.OTTER_DEATH.get();
    }

    @Override
    protected void playStepSound(BlockPos pos, BlockState state) {
        if (isHorrorForm()) {
            this.playSound(ModSounds.HORROR_STEP.get(), 0.25F, 0.9F + this.random.nextFloat() * 0.2F);
        } else {
            this.playSound(SoundEvents.WOLF_STEP, 0.08F, 1.5F);
        }
    }

    // ------------------------------------------------------------ GeckoLib

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "main", 4, this::mainPredicate));
    }

    private PlayState mainPredicate(AnimationState<OtterEntity> state) {
        OtterState os = getOtterState();
        if (os == OtterState.TRANSFORMING) {
            return state.setAndContinue(shouldRenderHorrorModel() ? H_TRANSFORM : ANIM_TRANSFORM);
        }
        if (os == OtterState.RETURNING_TO_NORMAL) {
            return state.setAndContinue(shouldRenderHorrorModel() ? H_UNTRANSFORM : ANIM_UNTRANSFORM);
        }
        if (os == OtterState.SUSPICIOUS) {
            return state.setAndContinue(ANIM_SUSPICIOUS);
        }
        OtterAction action = this.getAction();
        if (action != OtterAction.NONE) {
            return state.setAndContinue(RawAnimation.begin().thenLoop(action.animation()));
        }
        boolean moving = horizontalSpeed() > 0.02D;
        if (isHorrorForm()) {
            if (this.isInWater()) {
                return state.setAndContinue(moving ? H_SWIM : H_SWIM_IDLE);
            }
            if (moving) {
                return state.setAndContinue(horizontalSpeed() > 0.28D ? H_RUN : H_CRAWL);
            }
            return state.setAndContinue(H_IDLE);
        }
        if (this.isInWater()) {
            return state.setAndContinue(moving ? ANIM_SWIM : ANIM_SWIM_IDLE);
        }
        if (moving) {
            return state.setAndContinue(horizontalSpeed() > 0.30D ? ANIM_RUN : ANIM_WALK);
        }
        return state.setAndContinue(ANIM_IDLE);
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return this.cache;
    }
}

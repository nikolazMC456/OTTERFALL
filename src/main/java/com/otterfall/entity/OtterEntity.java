package com.otterfall.entity;

import com.otterfall.entity.ai.FormGate;
import com.otterfall.entity.ai.OtterFreezeGoal;
import com.otterfall.entity.ai.OtterHorrorActionGoal;
import com.otterfall.entity.ai.GiantPathNavigation;
import com.otterfall.entity.ai.OtterBreakBlocksGoal;
import com.otterfall.entity.ai.OtterHuntTravelGoal;
import com.otterfall.entity.ai.OtterIdleActionGoal;
import com.otterfall.entity.ai.OtterPursuitGoal;
import com.otterfall.entity.ai.OtterVengeanceTargetGoal;
import com.otterfall.hunt.OtterHuntData;
import com.otterfall.hunt.OtterHuntManager;
import com.otterfall.entity.ai.OtterSuspiciousGoal;
import com.otterfall.registry.ModEntities;
import com.otterfall.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundSetSubtitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitlesAnimationPacket;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
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
import net.minecraft.world.entity.ai.goal.PanicGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.RandomSwimmingGoal;
import net.minecraft.world.entity.ai.goal.TemptGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.pathfinder.BlockPathTypes;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
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

    private static final EntityDataAccessor<Boolean> DATA_FRENZY_FORM =
            SynchedEntityData.defineId(OtterEntity.class, EntityDataSerializers.BOOLEAN);

    private static final UUID FRENZY_DAMAGE_ID = UUID.fromString("5f3c1d1e-6b0a-4f5e-9c11-0a7d2e9b8a05");
    private static final UUID FRENZY_SPEED_ID = UUID.fromString("5f3c1d1e-6b0a-4f5e-9c11-0a7d2e9b8a06");
    private static final UUID HORROR_FOLLOW_ID = UUID.fromString("5f3c1d1e-6b0a-4f5e-9c11-0a7d2e9b8a09");
    private static final UUID FRENZY_FOLLOW_ID = UUID.fromString("5f3c1d1e-6b0a-4f5e-9c11-0a7d2e9b8a07");
    private static final UUID HORROR_SPEED_ID = UUID.fromString("5f3c1d1e-6b0a-4f5e-9c11-0a7d2e9b8a08");
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
    private static final RawAnimation ANIM_TRANSFORM_F = RawAnimation.begin().thenPlayAndHold("animation.otter.transform_frenzy");
    private static final RawAnimation H_TRANSFORM_F = RawAnimation.begin().thenPlayAndHold("animation.otter_horror.transform_frenzy");
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
    private final OtterMemory memory = new OtterMemory();

    private boolean wasInWater = false;
    private boolean wantsShake = false;
    private int actionTicks = 0;
    private int stepCount = 0;
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

    public boolean isFrenzy() {
        return getOtterState() == OtterState.FRENZY;
    }

    /** Monstruo "normal": sin rencor activo (el frenesi tiene su propia IA). */
    public boolean isPlainHorror() {
        return getOtterState() == OtterState.HORROR;
    }

    public OtterMemory memory() {
        return memory;
    }

    public boolean isFrenzyForm() {
        return this.entityData.get(DATA_FRENZY_FORM);
    }

    public void setFrenzyForm(boolean frenzy) {
        this.entityData.set(DATA_FRENZY_FORM, frenzy);
    }

    /** Fin de la fase A (modelo normal) segun la variante de transformacion. */
    public int transformPhaseA() {
        return isFrenzyForm() ? OtterTransformationController.FRENZY_PHASE_A : OtterTransformationController.PHASE_A;
    }

    public int transformTotal() {
        return isFrenzyForm() ? OtterTransformationController.FRENZY_TOTAL : OtterTransformationController.TRANSFORM_TOTAL;
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
            return t >= transformPhaseA();
        }
        if (s == OtterState.RETURNING_TO_NORMAL) {
            return t < OtterTransformationController.RETURN_A;
        }
        return false;
    }

    /** Pelaje oscurecido que aparece a mitad de la fase A de la transformacion. */
    public boolean shouldUseCorruptTexture() {
        return getOtterState() == OtterState.TRANSFORMING
                && getTransformTicks() >= (int) (transformPhaseA() * 0.36F)
                && getTransformTicks() < transformPhaseA();
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

    private void applyFormAttributes(OtterState state, boolean wasHorror) {
        boolean horror = state.usesHorrorModel();
        boolean frenzy = state == OtterState.FRENZY;
        setModifier(Attributes.ATTACK_DAMAGE, HORROR_DAMAGE_ID, "Horror damage", 8.0D, horror);
        setModifier(Attributes.MAX_HEALTH, HORROR_HEALTH_ID, "Horror health", 70.0D, horror);
        setModifier(Attributes.MOVEMENT_SPEED, HORROR_SPEED_ID, "Horror speed", 0.04D, horror);
        setModifier(Attributes.KNOCKBACK_RESISTANCE, HORROR_KNOCKBACK_ID, "Horror knockback", 0.7D, horror);
        // frenesi: mas dano, mas velocidad y un radio de rastreo enorme
        setModifier(Attributes.ATTACK_DAMAGE, FRENZY_DAMAGE_ID, "Frenzy damage", 5.0D, frenzy);
        setModifier(Attributes.MOVEMENT_SPEED, FRENZY_SPEED_ID, "Frenzy speed", 0.05D, frenzy);
        setModifier(Attributes.FOLLOW_RANGE, HORROR_FOLLOW_ID, "Horror follow range", 32.0D, horror);       // 20 -> 52
        setModifier(Attributes.FOLLOW_RANGE, FRENZY_FOLLOW_ID, "Frenzy follow range", 28.0D, frenzy);       // 52 -> 80
        this.setMaxUpStep(horror ? 2.1F : 1.0F);                                                              // sube escalones de 2 bloques
        if (horror && !wasHorror) {
            this.setHealth(this.getMaxHealth());
        } else if (this.getHealth() > this.getMaxHealth()) {
            this.setHealth(this.getMaxHealth());
        }
    }

    // ------------------------------------------------------------------ IA

    @Override
    protected PathNavigation createNavigation(Level level) {
        return new GiantPathNavigation(this, level);
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
        this.goalSelector.addGoal(2, new FormGate(new OtterPursuitGoal(this, 1.3D), this::isHorrorForm));
        this.goalSelector.addGoal(3, new FormGate(new OtterHorrorActionGoal(this), this::isPlainHorror));
        this.targetSelector.addGoal(1, new FormGate(
                new NearestAttackableTargetGoal<>(this, Player.class, 10, false, false, null), this::isPlainHorror));
        // ---- frenesi: venganza persistente
        this.targetSelector.addGoal(0, new FormGate(new OtterVengeanceTargetGoal(this), this::isFrenzy));
        this.goalSelector.addGoal(1, new FormGate(new OtterHuntTravelGoal(this), this::isFrenzy));
        this.goalSelector.addGoal(4, new FormGate(new OtterBreakBlocksGoal(this), this::isFrenzy));
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
            if (isFrenzy()) {
                this.playSound(ModSounds.FRENZY_ATTACK.get(), 1.0F, 0.8F + this.random.nextFloat() * 0.2F);
            }
        }
        return hit;
    }

    /** Memoria de agravios: cualquier jugador que la hiera queda grabado (UUID) de forma permanente. */
    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (!this.level().isClientSide && source.getEntity() instanceof ServerPlayer player
                && amount > 0.0F && !this.isInvulnerableTo(source)) {
            this.memory.remember(player.getUUID());
            refreshRegistry();
            if (isPlainHorror()) {          // golpeada de noche: salta directamente al frenesi
                this.setOtterState(OtterState.FRENZY);
                this.playSound(ModSounds.FRENZY_SCREAM.get(), 2.0F, 1.0F);
                announceFrenzy();
            }
        }
        return super.hurt(source, amount);
    }

    /** Al morir, las nutrias cercanas heredan sus agravios (la colonia recuerda). */
    @Override
    public void die(DamageSource source) {
        if (!this.level().isClientSide) {
            if (!this.memory.isEmpty()) {
                for (OtterEntity other : this.level().getEntitiesOfClass(OtterEntity.class,
                        this.getBoundingBox().inflate(48.0D), o -> o != this && o.isAlive())) {
                    other.memory.inherit(this.memory);
                    if (other.isPlainHorror()) {
                        other.setOtterState(OtterState.FRENZY);
                        other.playSound(ModSounds.FRENZY_SCREAM.get(), 2.0F, 1.0F);
                        other.announceFrenzy();
                    }
                    other.refreshRegistry();
                }
            }
            MinecraftServer server = this.level().getServer();
            if (server != null) {
                OtterHuntData.get(server).remove(this.getUUID());
            }
        }
        super.die(source);
    }

    private void refreshRegistry() {
        MinecraftServer server = this.level().getServer();
        if (server != null && !this.level().isClientSide) {
            OtterHuntData.get(server).update(this);
        }
    }

    /** Muestra "OTTER FRENZY" a los jugadores que esta nutria quiere matar. */
    public void announceFrenzy() {
        MinecraftServer server = this.level().getServer();
        if (server == null) {
            return;
        }
        for (UUID id : this.memory.ids()) {
            ServerPlayer p = server.getPlayerList().getPlayer(id);
            if (p != null) {
                p.connection.send(new ClientboundSetTitlesAnimationPacket(10, 70, 25));
                p.connection.send(new ClientboundSetSubtitleTextPacket(
                        Component.literal("FRANKLY UNFORGIVING").withStyle(ChatFormatting.DARK_RED)));
                p.connection.send(new ClientboundSetTitleTextPacket(
                        Component.literal("OTTER FRENZY").withStyle(ChatFormatting.RED, ChatFormatting.BOLD)));
            }
        }
    }

    /** Venganza cumplida: el rencor contra ese jugador se salda. */
    public void onTargetKilled(ServerPlayer player) {
        this.memory.forget(player.getUUID());
        this.setTarget(null);
        this.playSound(ModSounds.HORROR_LAUGH.get(), 2.0F, 0.9F);
        if (this.memory.isEmpty() && isFrenzy()) {
            this.setOtterState(OtterState.HORROR);
        }
        refreshRegistry();
    }

    /** Persecucion entre dimensiones: reaparece en la dimension del objetivo conservando todo su estado. */
    public void transferTo(ServerLevel dest, Vec3 pos) {
        CompoundTag tag = new CompoundTag();
        this.saveWithoutId(tag);
        this.discard();
        OtterEntity copy = ModEntities.OTTER.get().create(dest);
        if (copy != null) {
            copy.load(tag);
            copy.moveTo(pos.x, pos.y, pos.z, this.getYRot(), 0.0F);
            dest.addFreshEntity(copy);
            copy.refreshRegistry();
        }
    }

    /** Mantiene cargada su zona mientras alguno de sus enemigos este conectado y ella este activa. */
    private void huntSupport() {
        if (this.tickCount % 20 != 0 || this.memory.isEmpty()) {
            return;
        }
        MinecraftServer server = this.level().getServer();
        if (server == null) {
            return;
        }
        if (this.tickCount % 100 == 0) {
            OtterHuntData.get(server).update(this);
        }
        OtterState s = getOtterState();
        if ((s == OtterState.SUSPICIOUS || s == OtterState.TRANSFORMING || s == OtterState.FRENZY)
                && this.memory.hasOnlineTarget(server) && this.level() instanceof ServerLevel sl) {
            ChunkPos cp = this.chunkPosition();
            sl.getChunkSource().addRegionTicket(OtterHuntManager.HUNT_TICKET, cp, 3, cp);
        }
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
            this.huntSupport();
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
        this.entityData.define(DATA_FRENZY_FORM, false);
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
        boolean wasHorror = getOtterState().usesHorrorModel();
        this.entityData.set(DATA_STATE, state.ordinal());
        if (!this.level().isClientSide) {
            applyFormAttributes(state, wasHorror);
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
        tag.putBoolean("OtterFrenzyForm", isFrenzyForm());
        tag.put("OtterMemory", memory.save());
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        float health = this.getHealth();
        setOtterState(OtterState.byId(tag.getInt("OtterState")));
        this.setHealth(Math.min(health, this.getMaxHealth()));
        setTransformTicks(tag.getInt("OtterTransform"));
        locked = tag.getBoolean("OtterLocked");
        setFrenzyForm(tag.getBoolean("OtterFrenzyForm"));
        memory.load(tag.getList("OtterMemory", net.minecraft.nbt.Tag.TAG_COMPOUND));
    }

    // ------------------------------------------------------------- sonidos

    @Override
    public int getAmbientSoundInterval() {
        return isFrenzy() ? 60 : (isHorrorForm() ? 200 : 80);
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
        if (s == OtterState.FRENZY) {
            return ModSounds.FRENZY_BREATH.get();
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
            // paso pesado (audio propio, 4 variantes); suena uno de cada dos para no saturar al correr
            if ((this.stepCount++ & 1) == 0) {
                this.playSound(ModSounds.HORROR_STEP.get(), 1.0F, 0.95F + this.random.nextFloat() * 0.1F);
            }
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
            boolean f = isFrenzyForm();
            if (shouldRenderHorrorModel()) {
                return state.setAndContinue(f ? H_TRANSFORM_F : H_TRANSFORM);
            }
            return state.setAndContinue(f ? ANIM_TRANSFORM_F : ANIM_TRANSFORM);
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

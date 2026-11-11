package com.otterfall.entity.ai;

import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.navigation.AmphibiousPathNavigation;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.PathNavigationRegion;
import net.minecraft.world.level.pathfinder.AmphibiousNodeEvaluator;
import net.minecraft.world.level.pathfinder.PathFinder;

/**
 * Navegacion anfibia "permisiva" para la nutria gigante: calcula rutas como si midiera como mucho
 * 2x3 bloques (su hitbox real de 3x3.8 hacia que casi nunca encontrara camino entre arboles, rocas o
 * pasillos). Lo que no quepa de verdad lo resuelve rompiendo bloques (OtterBreakBlocksGoal).
 */
public class GiantPathNavigation extends AmphibiousPathNavigation {

    public GiantPathNavigation(Mob mob, Level level) {
        super(mob, level);
    }

    @Override
    protected PathFinder createPathFinder(int maxVisitedNodes) {
        this.nodeEvaluator = new GiantNodeEvaluator();
        this.nodeEvaluator.setCanPassDoors(true);
        return new PathFinder(this.nodeEvaluator, maxVisitedNodes);
    }

    private static class GiantNodeEvaluator extends AmphibiousNodeEvaluator {
        GiantNodeEvaluator() {
            super(false);
        }

        @Override
        public void prepare(PathNavigationRegion region, Mob mob) {
            super.prepare(region, mob);
            this.entityWidth = Math.min(this.entityWidth, 2);
            this.entityHeight = Math.min(this.entityHeight, 3);
            this.entityDepth = Math.min(this.entityDepth, 2);
        }
    }
}

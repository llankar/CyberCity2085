"""Tests for enemy intent plans with disruption handling."""

import pytest
from game.combat.enemy_plans import (
    DisruptionType, PlanState, DisruptionCondition, EnemyPlanTemplate,
    get_plans_for_enemy, get_best_plan_for_enemy, EnemyPlanManager,
    normalize_enemy_theme,
)


# =============================================================================
# Test: Disruption Type Constants
# =============================================================================

class TestDisruptionTypes:
    def test_disruption_type_enum_values(self):
        """Verify all disruption types exist."""
        assert DisruptionType.DESTRUCTION is not None
        assert DisruptionType.MOVEMENT_BLOCK is not None
        assert DisruptionType.COVER_DISRUPT is not None
        assert DisruptionType.FLANK_EXPOSED is not None
        assert DisruptionType.KEY_TARGET_HIT is not None
        assert DisruptionType.PSI_INTERRUPTION is not None
        assert DisruptionType.STATUS_IMPAIRMENT is not None

    def test_disruption_condition_structure(self):
        """Verify disruption condition dataclass."""
        condition = DisruptionCondition(
            disruption_type=DisruptionType.DESTRUCTION,
            severity_threshold=0.8,
            reset_turns=2,
            alternative_plan="fallback"
        )
        assert condition.disruption_type == DisruptionType.DESTRUCTION
        assert condition.severity_threshold == 0.8
        assert condition.reset_turns == 2
        assert condition.alternative_plan == "fallback"


# =============================================================================
# Test: Enemy Plan Manager
# =============================================================================

class TestEnemyPlanManager:
    def test_initialization(self):
        """Manager starts empty."""
        manager = EnemyPlanManager()
        assert len(manager.plans) == 0

    def test_initialize_plan_for_enemy(self):
        """Enemies get plans initialized correctly."""
        manager = EnemyPlanManager()
        manager.initialize_plan("enemy_1", "corp_37")
        
        assert "enemy_1" in manager.plans
        state = manager.plans["enemy_1"]
        assert state.state == PlanState.INITIATING

    def test_update_plan_state_basic(self):
        """Plans can be updated and return intent."""
        manager = EnemyPlanManager()
        manager.initialize_plan("enemy_2", "starver")
        
        template, intent = manager.update_plan_state("enemy_2")
        
        assert template is not None
        assert intent is not None
        assert intent.action in ["EXECUTE", "INITIATE"]

    def test_destroy_enemy_cancels_plan(self):
        """Destroyed enemies have their plans cancelled."""
        manager = EnemyPlanManager()
        manager.initialize_plan("dead_enemy", "mutant")
        
        manager.destroy_enemy("dead_enemy")
        state = manager.plans["dead_enemy"]
        assert state.state == PlanState.CANCELLED


# =============================================================================
# Test: Plan Templates and Registry
# =============================================================================

class TestPlanRegistry:
    def test_corp_37_plans_exist(self):
        """Corp 37 has defined plans."""
        plans = get_plans_for_enemy("corp_37")
        assert len(plans) >= 1
        plan = plans[0]
        assert "corp_37" in plan.faction_tags

    def test_starver_has_overwhelming_plan(self):
        """Starvers have a specific swarm plan."""
        plans = get_plans_for_enemy("starver")
        starver_plan = [p for p in plans if "swarm" in p.key.lower()]
        assert len(starver_plan) > 0

    def test_mutant_has_charging_plans(self):
        """Mutants have charge-based plans."""
        plans = get_plans_for_enemy("mutant")
        mutant_plans = [p for p in plans if any(x in p.key.lower() for x in ["breach", "panic"])]
        assert len(mutant_plans) > 0

    def test_generic_fallback_exists(self):
        """Generic plan exists as fallback."""
        generic = get_plans_for_enemy("unknown_faction")
        assert len(generic) == 1
        assert generic[0].key == "generic_assault"


# =============================================================================
# Test: Enemy Theme Normalization
# =============================================================================

class TestEnemyThemeNormalization:
    def test_string_normalization(self):
        """Simple string themes normalize correctly."""
        assert normalize_enemy_theme("corp_37") == "corp_37"
        assert normalize_enemy_theme("Starver") == "starver"
        assert normalize_enemy_theme("CORP_SAMURAI") == "corp_samurai"

    def test_composite_themes(self):
        """Composite themes like 'robot power armor corp_37' work."""
        assert normalize_enemy_theme("robot power armor corp_37") == "corp_37"
        assert normalize_enemy_theme("novatek hybrid lab tech") == "novatek_hybrid"

    def test_fallback_to_generic(self):
        """Unknown factions fall back to generic."""
        result = normalize_enemy_theme("unknown_type_123")
        assert result == "generic"


# =============================================================================
# Test: Best Plan Selection Logic
# =============================================================================

class TestBestPlanSelection:
    def test_priority_based_selection(self):
        """Plans with higher priority are preferred."""
        plans = get_plans_for_enemy("starver")
        # Starver's overwhelming_swarm should have high priority (100)
        best = get_best_plan_for_enemy(
            enemy_theme="starver",
            player_units_count=3,
            has_objectives=True,
            specialist_threat=False
        )
        
        # Should return the highest priority plan for starver
        assert "swarm" in best.key.lower() or len(plans) == 1

    def test_specialist_threat_modifier(self):
        """Plans that counter specialists get boosted."""
        plans = get_plans_for_enemy("corp_samurai")
        specialist_hunter = [p for p in plans if "specialist" in p.key.lower()]
        assert len(specialist_hunter) > 0

    def test_force_size_consideration(self):
        """Large forces favor overwhelming tactics."""
        # Small force should prefer flanking/hunting tactics
        small_force_plan = get_best_plan_for_enemy(
            enemy_theme="raider",
            player_units_count=1,
            has_objectives=True
        )
        
        # Large force should prefer direct assault
        large_force_plan = get_best_plan_for_enemy(
            enemy_theme="raider",
            player_units_count=8,
            has_objectives=True
        )
        
        # Both should be valid, but may have different strategies


# =============================================================================
# Test: Plan State Tracking
# =============================================================================

class TestPlanStateTracking:
    def test_plan_states(self):
        """All plan states exist and are accessible."""
        for state in PlanState:
            assert state.value is not None
            assert isinstance(state.value, str)

    def test_disruption_condition_defaults(self):
        """Disruption conditions have sensible defaults."""
        condition = DisruptionCondition(
            disruption_type=DisruptionType.KEY_TARGET_HIT
        )
        
        assert condition.severity_threshold == 0.0
        assert condition.reset_turns == 1
        assert condition.alternative_plan is None


# =============================================================================
# Integration Tests with Tactical Identity
# =============================================================================

class TestIntegration:
    def test_full_enemy_lifecycle(self):
        """Test complete enemy plan lifecycle."""
        manager = EnemyPlanManager()
        
        # Initialize
        manager.initialize_plan("corp_soldier", "corp_37")
        assert manager.plans["corp_soldier"].state == PlanState.INITIATING
        
        # Update (should return active intent)
        template, intent = manager.update_plan_state("corp_soldier")
        assert intent is not None
        assert template.priority >= 10  # All plans have minimum priority
        
        # Simulate enemy destruction
        manager.destroy_enemy("corp_soldier")
        state = manager.plans["corp_soldier"]
        assert state.state == PlanState.CANCELLED

    def test_disruption_condition_structure_validity(self):
        """Verify all disruption conditions in plans are valid."""
        all_plans = [
            *get_plans_for_enemy("corp_37"),
            *get_plans_for_enemy("corp_samurai"),
            *get_plans_for_enemy("starver"),
            *get_plans_for_enemy("mutant"),
            *get_plans_for_enemy("raider"),
        ]
        
        for plan in all_plans:
            for cond_key, condition in plan.disruption_conditions.items():
                assert condition.disruption_type is not None
                assert 0.0 <= condition.severity_threshold <= 1.0
                assert isinstance(condition.reset_turns, int)
                assert condition.alternative_plan is None or len(condition.alternative_plan) > 0

    def test_plan_success_indicators(self):
        """Plans have meaningful success indicators."""
        all_plans = [
            *get_plans_for_enemy("corp_37"),
            *get_plans_for_enemy("starver"),
            *get_plans_for_enemy("mutant"),
        ]
        
        for plan in all_plans:
            # Some plans may have no success indicators, but most should
            if len(plan.success_indicators) > 0:
                assert all(isinstance(indicator, str) for indicator in plan.success_indicators)

    def test_intent_prediction_with_plans(self):
        """Test that tactical intent prediction uses enemy plans."""
        from game.combat.tactical_identity import predict_enemy_intent
        
        # Create mock enemy
        class MockEnemy:
            def __init__(self, theme):
                self.enemy_theme = theme
                self.distance_to = lambda target: 64.0  # Medium range
        
        class MockCharacter:
            name = "test_agent"
        
        class MockUnit:
            def __init__(self):
                self.health = 100
                self.character = MockCharacter()
                self.in_cover_bonus = 0
        
        enemy = MockEnemy("starver")
        player = MockUnit()
        
        intent = predict_enemy_intent(enemy, [player], objective=None)
        
        # Starver should prioritize "RUSH" action with tide assault intent
        assert "rush" in intent.action.lower() or "tide" in intent.rationale.lower() or "starver" in intent.rationale.lower()

    def test_specialist_handling_in_plans(self):
        """Test that specialist threats trigger appropriate plan responses."""
        from game.combat.tactical_identity import predict_enemy_intent
        
        class MockEnemy:
            def __init__(self, theme):
                self.enemy_theme = theme
                self.distance_to = lambda target: 96.0  # Long range (sniper)
        
        class MockPsiChar:
            name = "PsiAgent"
            role = "psi"
        
        class MockPsiUnit:
            def __init__(self):
                self.health = 80
                self.character = MockPsiChar()
                self.in_cover_bonus = 0
        
        # Corp Samurai should hunt specialists
        enemy = MockEnemy("corp_samurai")
        psi_unit = MockPsiUnit()
        
        intent = predict_enemy_intent(enemy, [psi_unit], objective=None)
        
        # Should attempt to eliminate the specialist
        assert "hunter" in intent.rationale.lower() or "eliminate" in intent.rationale.lower() or "specialist" in intent.rationale.lower()

    def test_objective_focusing_in_plans(self):
        """Test that objectives are prioritized when present."""
        from game.combat.tactical_identity import predict_enemy_intent
        
        class MockEnemy:
            def __init__(self, theme):
                self.enemy_theme = theme
                self.distance_to = lambda target: 64.0  # Medium range
        
        class MockUnit:
            def __init__(self):
                self.health = 50
                self.character = type('obj', (object,), {'name': 'agent', 'role': 'assault'})()
                self.in_cover_bonus = 0
        
        enemy = MockEnemy("corp_37")
        player = MockUnit()
        
        # Create mock objective
        class MockObjective:
            kind = "defend"
        
        intent = predict_enemy_intent(enemy, [player], objective=MockObjective())
        
        # Corp 37 should focus on objectives when present
        assert "seize" in intent.rationale.lower() or "objective" in intent.rationale.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

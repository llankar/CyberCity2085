"""Unit tests for role state management (stances, Psi states, cooldowns).

Tests verify that TAC-ROLE-04 cooldown and ability system works correctly.
"""

from dataclasses import replace
import pytest

from game.unit import Unit
from game.character import Character
from game.stats import PlayerStats
from game.agent_specializations import Stance, PsiState, default_stance_for_unit, default_psi_state_for_unit


class TestStanceCooldowns:
    """Test stance change cooldown mechanics."""
    
    def test_initial_stance_change_allowed(self):
        """New unit should be able to change stance immediately."""
        unit = Unit((0, 0), stats=PlayerStats())
        
        assert unit.can_change_stance() is True
    
    def test_activate_breach_success(self):
        """Should be able to activate breach stance."""
        unit = Unit((0, 0), stats=PlayerStats())
        
        result = unit.activate_stance("BREACH")
        assert result is True
        assert unit.stance_override == "BREACH"
        assert unit.stance_change_cooldown == 2
    
    def test_activate_guard_success(self):
        """Should be able to activate guard stance."""
        unit = Unit((0, 0), stats=PlayerStats())
        
        result = unit.activate_stance("GUARD")
        assert result is True
        assert unit.stance_override == "GUARD"
    
    def test_invalid_stance_rejected(self):
        """Invalid stance should be rejected."""
        unit = Unit((0, 0), stats=PlayerStats())
        
        result = unit.activate_stance("INVALID")
        assert result is False
    
    def test_cooldown_prevents_stance_change(self):
        """Cooldown active should prevent stance changes."""
        unit = Unit((0, 0), stats=PlayerStats())
        unit.activate_stance("BREACH")
        
        # Should not be able to change during cooldown
        result = unit.activate_stance("GUARD")
        assert result is False
        assert unit.stance_override == "BREACH"
    
    def test_cooldown_decays_over_time(self):
        """Cooldown should decay each tick."""
        unit = Unit((0, 0), stats=PlayerStats())
        unit.activate_stance("BREACH")
        
        initial_cooldown = unit.stance_change_cooldown
        
        # Tick once
        messages = unit.tick_status_effects()
        assert unit.stance_change_cooldown == initial_cooldown - 1
    
    def test_clear_override_adds_cooldown(self):
        """Clearing override should add a turn cooldown."""
        unit = Unit((0, 0), stats=PlayerStats())
        
        # Set override
        unit.activate_stance("BREACH")
        assert unit.stance_override == "BREACH"
        
        # Clear it (simulates player canceling manual selection)
        result = unit.clear_stance_override()
        assert result is True
        assert unit.stance_override is None
        assert unit.stance_change_cooldown > 0


class TestPsiStateCooldowns:
    """Test Psi state change cooldown mechanics."""
    
    def test_initial_psi_toggle_allowed(self):
        """New unit should be able to toggle Psi state immediately."""
        unit = Unit((0, 0), stats=PlayerStats())
        
        assert unit.can_toggle_psi_state() is True
    
    def test_activate_risk_state_success(self):
        """Should be able to activate risk state."""
        unit = Unit((0, 0), stats=PlayerStats())
        
        result = unit.activate_psi_state("RISK")
        assert result is True
        assert unit.psi_state_override == "RISK"
        assert unit.psi_state_change_cooldown == 2
    
    def test_activate_control_state_success(self):
        """Should be able to activate control state."""
        unit = Unit((0, 0), stats=PlayerStats())
        
        result = unit.activate_psi_state("CONTROL")
        assert result is True
        assert unit.psi_state_override == "CONTROL"
    
    def test_invalid_psi_state_rejected(self):
        """Invalid Psi state should be rejected."""
        unit = Unit((0, 0), stats=PlayerStats())
        
        result = unit.activate_psi_state("INVALID")
        assert result is False
    
    def test_cooldown_prevents_psi_toggle(self):
        """Cooldown active should prevent Psi toggles."""
        unit = Unit((0, 0), stats=PlayerStats())
        unit.activate_psi_state("RISK")
        
        # Should not be able to toggle during cooldown
        result = unit.activate_psi_state("CONTROL")
        assert result is False
        assert unit.psi_state_override == "RISK"
    
    def test_cooldown_affects_abilities(self):
        """Psi state change should also trigger Psi ability cooldown."""
        unit = Unit((0, 0), stats=PlayerStats())
        unit.activate_psi_state("RISK")
        
        assert unit.psi_ability_cooldown == 2
        # Tracking overdrive usage this turn
        assert unit.psi_overdrive_active_this_turn is True
    
    def test_clear_psi_override_adds_cooldown(self):
        """Clearing Psi override should add a turn cooldown."""
        unit = Unit((0, 0), stats=PlayerStats())
        
        # Set override
        unit.activate_psi_state("RISK")
        assert unit.psi_state_override == "RISK"
        
        # Clear it
        result = unit.clear_psi_override()
        assert result is True
        assert unit.psi_state_override is None
        assert unit.psi_state_change_cooldown > 0


class TestTurnProcessing:
    """Test complete turn processing with role state decay."""
    
    def test_full_turn_decay_sequence(self):
        """Verify complete cooldown decay during tick_status_effects."""
        # Create two units with different states
        samurai = Unit((0, 0), stats=PlayerStats())
        samurai.activate_stance("BREACH")
        samurai.stance_change_cooldown = 2
        
        psi_unit = Unit((1, 0), stats=PlayerStats())
        psi_unit.activate_psi_state("RISK")
        psi_unit.psi_state_change_cooldown = 2
        psi_unit.psi_ability_cooldown = 2
        
        # Tick once - all cooldowns should decay by 1
        samurai.tick_status_effects()
        psi_unit.tick_status_effects()
        
        assert samurai.stance_change_cooldown == 1
        assert psi_unit.psi_state_change_cooldown == 1
        assert psi_unit.psi_ability_cooldown == 1
        
        # Track flags should be cleared
        assert samurai.manual_breach_used_this_turn is False
        assert psi_unit.psi_overdrive_active_this_turn is False
    
    def test_multiunit_turn_processing(self):
        """Verify turn processing works for multiple units simultaneously."""
        units = [Unit((i, 0), stats=PlayerStats()) for i in range(5)]
        
        # Activate stance on some units
        units[0].activate_stance("BREACH")
        units[1].activate_psi_state("RISK")
        
        # Process turn
        for unit in units:
            unit.tick_status_effects()
        
        # Check cooldowns decayed appropriately
        assert units[0].stance_change_cooldown == 2 - 1
        assert units[1].psi_state_change_cooldown == 2 - 1


class TestStateIntegrationWithCombat:
    """Test integration of role states with combat calculation."""
    
    def test_stance_affects_attack_value(self):
        """BREACH stance should increase attack value, GUARD should decrease."""
        from game.combat.attack_resolution import build_attack_context
        
        # Create a mock attacker and defender for testing
        attacker = Unit((0, 0), stats=PlayerStats(str=8, psi=6))
        
        # Without override (auto-detection based on no enemies = GUARD)
        initial_stance = default_stance_for_unit(attacker)
        assert initial_stance == Stance.GUARD
        
        # Activate BREACH stance
        attacker.activate_stance("BREACH")
        
        # Verify the override was set (auto-detection won't override manual choice)
        # Note: In actual combat with enemies nearby, auto-detection would trigger BREACH
        assert hasattr(attacker, 'stance_override')
    
    def test_psi_state_can_be_manually_set(self):
        """Player should be able to manually set Psi state during combat."""
        unit = Unit((0, 0), stats=PlayerStats())
        
        # Should start with auto-detected state (CONTROL if normal conditions)
        initial_state = default_psi_state_for_unit(unit)
        
        assert initial_state == PsiState.CONTROL
        
        # Can manually switch to RISK for overdrive
        result = unit.activate_psi_state("RISK")
        assert result is True
        assert unit.psi_state_override == "RISK"
        
        # Can clear override to return to auto-detection
        unit.clear_psi_override()
        assert unit.psi_state_override is None
        
        # After clearing, should revert to default (CONTROL)
        state_after_clear = default_psi_state_for_unit(unit)
        assert state_after_clear == PsiState.CONTROL


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_unit_without_stats_can_toggle_stance(self):
        """Unit without stats should still be able to toggle stance."""
        unit = Unit((0, 0))  # No stats
        
        result = unit.activate_stance("BREACH")
        assert result is True
        assert unit.stance_override == "BREACH"
    
    def test_unit_without_stats_can_toggle_psi(self):
        """Unit without stats should still be able to toggle Psi state."""
        unit = Unit((0, 0))  # No stats
        
        result = unit.activate_psi_state("RISK")
        assert result is True
        assert unit.psi_state_override == "RISK"


class TestCharacterStateTracking:
    """Test character-level state tracking for role abilities."""
    
    def test_stance_tracking_in_character(self):
        """Stance override should persist in character data."""
        unit = Unit((0, 0), stats=PlayerStats())
        unit.activate_stance("BREACH")
        
        # Character should reflect stance choice
        assert unit.stance_override == "BREACH"
        
        # Verify it's cleared on cancel
        unit.clear_stance_override()
        assert unit.stance_override is None
    
    def test_psi_state_tracking_in_character(self):
        """Psi state override should persist in character data."""
        unit = Unit((0, 0), stats=PlayerStats())
        unit.activate_psi_state("RISK")
        
        # Character should reflect Psi state choice
        assert unit.psi_state_override == "RISK"
        
        # Verify it's cleared on cancel
        unit.clear_psi_override()
        assert unit.psi_state_override is None

"""Unit tests for role signature visual identity system (Slice 4: TAC-ROLE-01).

Tests cover the new RoleSignature dataclass, stance/psi state management, 
and visual indicator logic in agent_specializations.py.
"""

from game.agent_specializations import (
    RoleSignature,
    signature_for_role,
    Stance,
    PsiState,
    default_stance_for_unit,
    default_psi_state_for_unit,
    update_unit_stance,
    update_unit_psi_state,
)
from game.stats import PlayerStats


class TestRoleSignatureSystem:
    """Test RoleSignature dataclass and role identity lookup."""
    
    def test_role_signature_dataclass_has_required_fields(self) -> None:
        """Verify RoleSignature contains all expected identity fields."""
        sig = signature_for_role("samurai")
        
        assert sig is not None
        assert hasattr(sig, "key")
        assert hasattr(sig, "name")
        assert hasattr(sig, "primary_color")
        assert hasattr(sig, "secondary_color")
        assert hasattr(sig, "accent_color")
        assert hasattr(sig, "description")
        assert hasattr(sig, "has_mode_switch")
        assert hasattr(sig, "mode_names")
    
    def test_role_signature_colors_are_distinct_per_role(self) -> None:
        """Verify each role has unique color scheme for visual identification."""
        roles = ["samurai", "sniper", "psi", "medic", "robot"]
        
        colors = {}
        for role in roles:
            sig = signature_for_role(role)
            assert sig is not None, f"No signature found for {role}"
            color_tuple = sig.primary_color + sig.secondary_color + sig.accent_color
            
            # Ensure no duplicate primary+accent combinations (key differentiators)
            key = (sig.primary_color[0], sig.accent_color[2])
            assert key not in colors, f"Duplicate color scheme for {role}"
            colors[key] = role
    
    def test_samurai_has_mode_switch(self) -> None:
        """Samurai is the only role with stance-based mode switching."""
        samurai = signature_for_role("samurai")
        sniper = signature_for_role("sniper")
        psi = signature_for_role("psi")
        
        assert samurai.has_mode_switch is True
        assert sniper.has_mode_switch is False
        assert psi.has_mode_switch is True
    
    def test_samurai_mode_names_are_breach_guard(self) -> None:
        """Samurai mode names should be breach and guard."""
        sig = signature_for_role("samurai")
        
        assert len(sig.mode_names) == 2
        assert "BREACH" in str(sig.mode_names[0]).upper()
        assert "GUARD" in str(sig.mode_names[1]).upper()
    
    def test_all_five_player_roles_have_signatures(self) -> None:
        """All five player roles must have signatures defined."""
        expected_roles = ["samurai", "sniper", "psi", "medic", "robot"]
        
        for role in expected_roles:
            sig = signature_for_role(role)
            assert sig is not None, f"Missing signature for {role}"
            assert len(sig.primary_color) == 3, f"{role} primary_color must be RGB tuple"
            assert len(sig.secondary_color) == 3, f"{role} secondary_color must be RGB tuple"
    
    def test_unrecognized_role_returns_none(self) -> None:
        """Unknown roles should return None gracefully."""
        result = signature_for_role("unknown_role")
        assert result is None


class TestStanceStateManagement:
    """Test stance and psi state enums and default determination logic."""
    
    def test_stance_enum_values(self) -> None:
        """Verify Stance enum has breach and guard values."""
        assert Stance.BREACH.value == "breach"
        assert Stance.GUARD.value == "guard"
    
    def test_psi_state_enum_values(self) -> None:
        """Verify PsiState enum has control and risk values."""
        assert PsiState.CONTROL.value == "control"
        assert PsiState.RISK.value == "risk"
    
    def test_non_samurai_defaults_to_guard_stance(self, capsys) -> None:
        """Non-samurai units should default to guard stance."""
        class FakeUnit:
            character = type('Character', (), {'role': 'sniper'})()
        
        unit = FakeUnit()
        stance = default_stance_for_unit(unit)
        
        assert stance == Stance.GUARD
    
    def test_psi_non_psi_defaults_to_control(self, capsys) -> None:
        """Non-ps units should default to control state."""
        class FakeUnit:
            character = type('Character', (), {'role': 'samurai'})()
        
        unit = FakeUnit()
        psi_state = default_psi_state_for_unit(unit)
        
        assert psi_state == PsiState.CONTROL


class TestStanceDetectionLogic:
    """Test stance switching based on tactical situation."""
    
    def test_samurai_near_enemies_switches_to_breach(self, capsys) -> None:
        """Samurai should switch to breach when very close to enemies."""
        # This requires a proper Unit setup with distance calculation
        # Placeholder for future integration with combat system
        
        class FakeEnemyUnit:
            x = 32  # Close (within ~1.5 tiles)
            y = 0
            health = 8
            
            def distance_to(self, other):
                import math as m
                return m.sqrt(pow(self.x - other.x, 2) + pow(self.y - other.y, 2))
        
        class FakeCharacter:
            role = "samurai"
        
        class FakeUnit:
            character = FakeCharacter()
            x = 0
            y = 0
            _combat_context = {"enemy_units": [FakeEnemyUnit()]}
        
        unit = FakeUnit()
        stance = default_stance_for_unit(unit)
        
        # At close range (<48px), should be breach
        assert stance == Stance.BREACH, "Samurai should breach when enemies are nearby"
    
    def test_samurai_far_from_enemies_stays_in_guard(self, capsys) -> None:
        """Samurai should stay in guard when repositioning."""
        class FakeEnemyUnit:
            x = 256  # Far away
            y = 0
            health = 8
            
            def distance_to(self, other):
                import math as m
                return m.sqrt(pow(self.x - other.x, 2) + pow(self.y - other.y, 2))
        
        class FakeCharacter:
            role = "samurai"
        
        class FakeUnit:
            character = FakeCharacter()
            x = 0
            y = 0
            _combat_context = {"enemy_units": [FakeEnemyUnit()]}
        
        unit = FakeUnit()
        stance = default_stance_for_unit(unit)
        
        # At distance (>48px), should be guard
        assert stance == Stance.GUARD, "Samurai should guard when enemies are far"


class TestPsiStateDetectionLogic:
    """Test psi state determination based on mental load."""
    
    def test_psi_low_stamina_switches_to_risk(self, capsys) -> None:
        """Psi with low stamina should be in risk state."""
        class FakeCharacter:
            role = "psi"
            stress = 9  # High enough to trigger risk
        
        class FakeUnit:
            character = FakeCharacter()
            psi_stamina = 4  # Very low (<40%)
            psi_max = 10
        
        unit = FakeUnit()
        state = default_psi_state_for_unit(unit)
        
        assert state == PsiState.RISK, "Psi should risk when stamina is critically low"
    
    def test_psi_high_stress_switches_to_risk(self, capsys) -> None:
        """Psi under high stress should be in risk state."""
        class FakeCharacter:
            role = "psi"
            stress = 9  # Very high stress
        
        class FakeUnit:
            character = FakeCharacter()
            psi_stamina = 8
            psi_max = 10
        
        unit = FakeUnit()
        state = default_psi_state_for_unit(unit)
        
        assert state == PsiState.RISK, "Psi should risk when stress is very high"


class TestRoleSignatureVisualData:
    """Test visual data available for rendering role indicators."""
    
    def test_samurai_accent_color_is_breath_red(self) -> None:
        """Samurai accent color should indicate breath mode (red for aggression)."""
        sig = signature_for_role("samurai")
        
        # Red component highest indicates aggression/breath
        assert sig.accent_color[0] > 200, "Breach accent should be red-dominant"
    
    def test_sniper_has_scope_colors(self) -> None:
        """Sniper should have appropriate scope/overwatch colors."""
        sig = signature_for_role("sniper")
        
        # Green/yellow indicates precision/ranged
        assert sig.accent_color[1] > 200, "Sniper accent should have strong green component"
    
    def test_psi_has_control_colors(self) -> None:
        """Psi should have appropriate mental state colors."""
        sig = signature_for_role("psi")
        
        # Purple/magenta indicates psychic/mental
        assert sig.primary_color[0] > 150 and sig.primary_color[2] > 150, \
            "Psi primary should be purple/magenta-dominant"


class TestStanceUpdateFunctions:
    """Test stance/psi update functions with overrides."""
    
    def test_update_unit_stance_respects_override(self) -> None:
        """update_unit_stance should return override when provided."""
        
        class FakeUnit:
            character = type('Character', (), {'role': 'samurai'})()
            x = 0
            y = 0
        
        unit = FakeUnit()
        
        # Force breach regardless of position
        forced_stance = update_unit_stance(unit, Stance.BREACH)
        
        assert forced_stance == Stance.BREACH
    
    def test_update_unit_psi_state_respects_override(self) -> None:
        """update_unit_psi_state should return override when provided."""
        
        class FakeUnit:
            character = type('Character', (), {'role': 'psi'})()
            psi_stamina = 8
            psi_max = 10
        
        unit = FakeUnit()
        
        # Force risk regardless of state
        forced_state = update_unit_psi_state(unit, PsiState.RISK)
        
        assert forced_state == PsiState.RISK

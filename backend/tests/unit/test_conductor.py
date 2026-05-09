"""Unit tests for the narrative conductor (phase state machine)."""

from app.engine.narrative.conductor import PHASES, Conductor


class TestConductorPhases:
    def test_phases_order(self):
        assert PHASES == ["RAPPORT", "EXPLORATION", "CONFRONTATION", "SYNTHESIS", "ENDED"]

    def test_initial_phase(self):
        c = Conductor()
        assert c.current_phase == "RAPPORT"
        assert c.turn_count == 0
        assert c.effective_words == 0

    def test_custom_initial_phase(self):
        c = Conductor(current_phase="EXPLORATION", turn_count=5, effective_words=300)
        assert c.current_phase == "EXPLORATION"


class TestPhaseTransition:
    LOW_CONF = {"E_I": 0.3, "S_N": 0.3, "T_F": 0.3, "J_P": 0.3}
    HIGH_CONF = {"E_I": 0.9, "S_N": 0.9, "T_F": 0.9, "J_P": 0.9}

    def test_stays_in_rapport_with_too_few_turns(self):
        c = Conductor(turn_count=1, effective_words=50)
        result = c.evaluate_transition(self.LOW_CONF)
        assert result == "RAPPORT"

    def test_rapport_to_exploration_with_enough_words(self):
        c = Conductor(turn_count=3, effective_words=250)
        result = c.evaluate_transition(self.LOW_CONF)
        assert result == "EXPLORATION"

    def test_exploration_to_confrontation(self):
        c = Conductor(current_phase="EXPLORATION", turn_count=5, effective_words=600)
        result = c.evaluate_transition(self.LOW_CONF)
        assert result == "CONFRONTATION"

    def test_confrontation_to_synthesis_when_confident(self):
        c = Conductor(current_phase="CONFRONTATION", turn_count=4, effective_words=900)
        result = c.evaluate_transition(self.HIGH_CONF)
        assert result == "SYNTHESIS"

    def test_confrontation_stays_with_low_confidence(self):
        c = Conductor(current_phase="CONFRONTATION", turn_count=4, effective_words=900)
        result = c.evaluate_transition(self.LOW_CONF)
        assert result == "CONFRONTATION"

    def test_synthesis_to_ended(self):
        c = Conductor(current_phase="SYNTHESIS", turn_count=10, effective_words=1000)
        result = c.evaluate_transition(self.HIGH_CONF)
        assert result == "ENDED"

    def test_ended_stays_ended(self):
        c = Conductor(current_phase="ENDED")
        result = c.evaluate_transition(self.HIGH_CONF)
        assert result == "ENDED"

    def test_early_convergence_skip_to_synthesis(self):
        c = Conductor(current_phase="EXPLORATION", turn_count=5, effective_words=700)
        result = c.evaluate_transition(self.HIGH_CONF)
        assert result == "SYNTHESIS"


class TestSafetyAnchor:
    CONF = {"E_I": 0.5, "S_N": 0.5, "T_F": 0.5, "J_P": 0.5}

    def test_high_risk_retreats_from_exploration(self):
        c = Conductor(current_phase="EXPLORATION", turn_count=5, effective_words=500)
        result = c.evaluate_transition(self.CONF, risk_level="HIGH")
        assert result == "RAPPORT"

    def test_high_risk_stays_at_rapport(self):
        c = Conductor(current_phase="RAPPORT", turn_count=3, effective_words=200)
        result = c.evaluate_transition(self.CONF, risk_level="HIGH")
        assert result == "RAPPORT"


class TestAdvance:
    def test_advance_increments_turns(self):
        c = Conductor()
        c.advance(50)
        assert c.turn_count == 1
        assert c.effective_words == 50

    def test_advance_accumulates(self):
        c = Conductor()
        c.advance(30)
        c.advance(40)
        assert c.turn_count == 2
        assert c.effective_words == 70


class TestSerialization:
    def test_to_dict_and_from_dict(self):
        c = Conductor(current_phase="EXPLORATION", turn_count=5, effective_words=300)
        d = c.to_dict()
        c2 = Conductor.from_dict(d)
        assert c2.current_phase == "EXPLORATION"
        assert c2.turn_count == 5
        assert c2.effective_words == 300

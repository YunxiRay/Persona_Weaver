"""Unit tests for Bayesian inference engine."""

from app.engine.inference.bayesian import DIMENSIONS, BayesianEngine, DimensionTracker


class TestDimensionTracker:
    def test_initial_prior(self):
        t = DimensionTracker("E_I")
        assert 0.4 < t.mean < 0.6  # E_I prior ~0.49
        assert t.std > 0.1  # initial uncertainty is high

    def test_update_shifts_mean(self):
        t = DimensionTracker("E_I")
        initial_mean = t.mean
        # Strong E signal
        for _ in range(5):
            t.update(0.8, 0.9, "RAPPORT")
        assert t.mean > initial_mean  # shifted toward E

    def test_update_tracks_samples(self):
        t = DimensionTracker("E_I")
        t.update(0.5, 0.8, "RAPPORT")
        t.update(-0.3, 0.7, "EXPLORATION")
        assert t.sample_count == 2
        assert t.cross_phase_count == 2

    def test_std_decreases_with_more_data(self):
        t = DimensionTracker("E_I")
        initial_std = t.std
        for _ in range(10):
            t.update(0.2, 0.8, "EXPLORATION")
        assert t.std < initial_std

    def test_convergence_with_enough_consistent_data(self):
        t = DimensionTracker("E_I")
        for _ in range(20):
            t.update(0.7, 0.9, "CONFRONTATION")
        assert t.is_converged

    def test_dimension_score_mapping(self):
        t = DimensionTracker("E_I")
        t.update(0.8, 0.9, "RAPPORT")
        score = t.dimension_score()
        assert -1.0 <= score <= 1.0

    def test_extreme_values_are_clamped(self):
        t = DimensionTracker("E_I")
        t.update(5.0, 1.0, "RAPPORT")  # should be clamped to 0.99
        assert 0.0 < t.mean < 1.0


class TestBayesianEngine:
    def test_initial_state(self):
        engine = BayesianEngine()
        assert len(engine.trackers) == 4
        assert not engine.is_converged()

    def test_update_all_dimensions(self):
        engine = BayesianEngine()
        dims = {"E_I": 0.6, "S_N": -0.3, "T_F": 0.7, "J_P": 0.2}
        confs = {"E_I": 0.8, "S_N": 0.6, "T_F": 0.9, "J_P": 0.5}
        engine.update(dims, confs, "EXPLORATION")
        for d in DIMENSIONS:
            assert engine.trackers[d].sample_count == 1

    def test_determine_mbti_enfj(self):
        engine = BayesianEngine()
        # Strong E, N, F, J signals
        for _ in range(10):
            engine.update(
                {"E_I": 0.6, "S_N": -0.5, "T_F": 0.7, "J_P": 0.4},
                {"E_I": 0.9, "S_N": 0.9, "T_F": 0.9, "J_P": 0.9},
                "CONFRONTATION",
            )
        mbti = engine.determine_mbti()
        assert mbti[0] == "E"
        assert mbti[1] == "N"
        assert mbti[2] == "F"
        assert mbti[3] == "J"

    def test_determine_mbti_istp(self):
        engine = BayesianEngine()
        for _ in range(10):
            engine.update(
                {"E_I": -0.6, "S_N": 0.5, "T_F": -0.7, "J_P": -0.4},
                {"E_I": 0.9, "S_N": 0.9, "T_F": 0.9, "J_P": 0.9},
                "CONFRONTATION",
            )
        mbti = engine.determine_mbti()
        assert mbti == "ISTP"

    def test_convergence_after_many_updates(self):
        engine = BayesianEngine()
        for _ in range(30):
            engine.update(
                {"E_I": 0.5, "S_N": 0.3, "T_F": 0.6, "J_P": -0.2},
                {"E_I": 0.9, "S_N": 0.9, "T_F": 0.9, "J_P": 0.9},
                "CONFRONTATION",
            )
        assert engine.is_converged()

    def test_summary_contains_mbti(self):
        engine = BayesianEngine()
        s = engine.summary()
        assert "mbti" in s
        assert len(s["mbti"]) == 4
        assert "dimensions" in s
        assert "converged" in s

    def test_confidence_values_in_range(self):
        engine = BayesianEngine()
        conf = engine.confidence_values()
        for d in DIMENSIONS:
            assert 0.0 <= conf[d] <= 1.0

# ...existing code...
from tasks.learning import get_adjusted_weights
# ...existing code...

# inside compute_scores or wherever you pick weights:
# strategy is the current strategy name, WEIGHT_PRESETS is your preset dict
weights = get_adjusted_weights(strategy, WEIGHT_PRESETS.get(strategy, {}))
# then use `weights` in scoring computations
# ...existing code...from django.test import TestCase
from .scoring import compute_scores, detect_cycles

class ScoringTests(TestCase):
    def test_overdue_boost(self):
        tasks = [
            {"id":"a","title":"Old task","due_date":"2000-01-01","estimated_hours":2,"importance":5,"dependencies":[]},
            {"id":"b","title":"Future task","due_date":"2999-01-01","estimated_hours":2,"importance":5,"dependencies":[]}
        ]
        res = compute_scores(tasks, strategy='smart_balance')
        self.assertEqual(res['tasks'][0]['id'], 'a')

    def test_fastest_wins(self):
        tasks = [
            {"id":"t1","title":"Big job","estimated_hours":40,"importance":8,"dependencies":[]},
            {"id":"t2","title":"Small job","estimated_hours":1,"importance":5,"dependencies":[]}
        ]
        res = compute_scores(tasks, strategy='fastest_wins')
        self.assertEqual(res['tasks'][0]['id'], 't2')

    def test_cycle_detection(self):
        t = [
            {"id":"x","dependencies":["y"]},
            {"id":"y","dependencies":["z"]},
            {"id":"z","dependencies":["x"]}
        ]
        cycles = detect_cycles(t)
        self.assertTrue(len(cycles) > 0)

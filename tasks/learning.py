import json
import os
from typing import Dict

STATS_FILE = os.path.join(os.path.dirname(__file__), 'weight_stats.json')
WARMUP = 5

def _ensure_file():
    if not os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'w') as f:
                json.dump({}, f)
        except OSError:
            pass

def load_stats() -> Dict[str, Dict[str, int]]:
    _ensure_file()
    try:
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_stats(s: Dict[str, Dict[str, int]]):
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(s, f, indent=2)
    except Exception:
        pass

def register_feedback(strategy: str, was_helpful: bool):
    s = load_stats()
    st = s.setdefault(strategy, {"positive": 0, "total": 0})
    st['total'] = st.get('total', 0) + 1
    if was_helpful:
        st['positive'] = st.get('positive', 0) + 1
    save_stats(s)

def _normalize(weights: Dict[str, float]) -> Dict[str, float]:
    total = sum(weights.values()) or 1.0
    return {k: float(v) / total for k, v in weights.items()}

def get_adjusted_weights(strategy: str, base_weights: Dict[str, float]) -> Dict[str, float]:
    """
    Return slightly adjusted weights based on simple online feedback stats.
    Keeps changes tiny and requires a small warmup count.
    """
    s = load_stats().get(strategy, {"positive": 0, "total": 0})
    if s.get('total', 0) < WARMUP:
        return _normalize(dict(base_weights))

    rate = float(s.get('positive', 0)) / max(1, s.get('total', 0))
    adj = dict(base_weights)

    # Example: nudge the 'importance' factor according to success rate around 0.5
    if 'importance' in adj:
        # scale factor: 1 + small_delta where delta in [-0.05, +0.05] when rate in [0,1]
        delta = (rate - 0.5) * 0.1
        adj['importance'] = min(0.9, max(0.01, adj['importance'] * (1 + delta)))

    # other factors can be left unchanged or similarly adjusted

    return _normalize(adj)

from tasks.learning import get_adjusted_weights

# inside compute_scores or wherever you pick weights:
# strategy is the current strategy name, WEIGHT_PRESETS is your preset dict
weights = get_adjusted_weights(strategy, WEIGHT_PRESETS.get(strategy, {}))
# then use `weights` in scoring computations
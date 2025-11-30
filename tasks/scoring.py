from datetime import date, datetime
import math
from collections import defaultdict
import holidays
from datetime import timedelta

HOLIDAY_COUNTRY = 'IN'

DEFAULTS = {"importance": 5, "estimated_hours": 4}
URGENCY_WINDOW_DAYS = 30.0
WEIGHT_PRESETS = {
    "fastest_wins": {"effort": 0.6, "importance": 0.2, "urgency": 0.1, "dependency": 0.1},
    "high_impact": {"importance": 0.7, "dependency": 0.15, "urgency": 0.1, "effort": 0.05},
    "deadline_driven": {"urgency": 0.7, "dependency": 0.15, "importance": 0.1, "effort": 0.05},
    "smart_balance": {"urgency": 0.35, "importance": 0.35, "dependency": 0.15, "effort": 0.15},
}

def parse_date(d):
    if d is None:
        return None
    if isinstance(d, date):
        return d
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except Exception:
        return None

def normalize_importance(importance):
    i = max(1, min(10, importance))
    return (i - 1) / 9.0

def normalize_effort(hours):
    h = max(0.0, float(hours))
    return 1.0 / (1.0 + math.log1p(h))

def business_days_between(start_date, end_date, country=HOLIDAY_COUNTRY):
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    day = start_date
    count = 0
    hols = holidays.CountryHoliday(country)
    while day < end_date:
        if day.weekday() < 5 and day not in hols:
            count += 1
        day += timedelta(days=1)
    return count

def normalize_urgency(due_date):
    if due_date is None:
        return 0.1
    days = (due_date - date.today()).days
    # compute business days instead
    try:
        bdays = business_days_between(date.today(), due_date)
    except Exception:
        bdays = max(0, days)
    if days < 0:
        # overdue measured in business days
        overdue_days = business_days_between(due_date, date.today())
        return min(1.0 + min(1.0, overdue_days / 30.0), 2.0)
    return max(0.0, 1.0 - (bdays / URGENCY_WINDOW_DAYS))

def build_adj_map(tasks):
    adj = defaultdict(list)
    ids = set(t['id'] for t in tasks)
    for t in tasks:
        for dep in t.get('dependencies', []):
            if dep in ids:
                adj[dep].append(t['id'])
    return adj

def detect_cycles(tasks):
    ids = [t['id'] for t in tasks]
    dep_map = {t['id']: list(t.get('dependencies', [])) for t in tasks}
    visited = set()
    recstack = set()
    cycles = []
    path = []

    def dfs(u):
        visited.add(u)
        recstack.add(u)
        path.append(u)
        for v in dep_map.get(u, []):
            if v not in dep_map:
                continue
            if v not in visited:
                dfs(v)
            elif v in recstack:
                try:
                    idx = path.index(v)
                    cycles.append(path[idx:] + [v])
                except ValueError:
                    cycles.append([v, u, v])
        recstack.remove(u)
        path.pop()

    for node in ids:
        if node not in visited:
            dfs(node)
    return cycles

def reachable_counts(tasks):
    adj = build_adj_map(tasks)
    counts = {t['id']: 0 for t in tasks}
    for node in list(counts.keys()):
        seen = set()
        stack = list(adj.get(node, []))
        while stack:
            v = stack.pop()
            if v in seen:
                continue
            seen.add(v)
            counts[node] += 1
            for nxt in adj.get(v, []):
                if nxt not in seen:
                    stack.append(nxt)
    return counts

def compute_scores(tasks, strategy="smart_balance"):
    warnings = []
    task_map = {}
    for t in tasks:
        tid = str(t['id'])
        title = t.get('title', '')
        raw_due = t.get('due_date')
        due = parse_date(raw_due) if raw_due else None
        if raw_due and due is None:
            warnings.append({"id": tid, "warning": "invalid due_date format, expected YYYY-MM-DD"})
        importance = t.get('importance', DEFAULTS['importance'])
        estimated_hours = t.get('estimated_hours', DEFAULTS['estimated_hours'])
        deps = t.get('dependencies', []) or []
        task_map[tid] = {
            "id": tid,
            "title": title,
            "due_date": due,
            "importance": importance,
            "estimated_hours": estimated_hours,
            "dependencies": deps
        }

    task_list = list(task_map.values())
    cycles = detect_cycles(task_list)
    reach_counts = reachable_counts(task_list)
    max_reach = max(reach_counts.values()) if reach_counts else 1
    weights = WEIGHT_PRESETS.get(strategy, WEIGHT_PRESETS['smart_balance'])

    results = []
    for t in task_list:
        tid = t['id']
        imp_norm = normalize_importance(t['importance'])
        eff_norm = normalize_effort(t['estimated_hours'])
        urg_norm = normalize_urgency(t['due_date'])
        dep_norm = (reach_counts.get(tid, 0) / max_reach) if max_reach > 0 else 0.0

        in_cycle = any(tid in cycle for cycle in cycles)
        if in_cycle:
            results.append({
                "id": tid,
                "title": t['title'],
                "score": None,
                "subscores": {
                    "urgency": round(urg_norm,4),
                    "importance": round(imp_norm,4),
                    "effort": round(eff_norm,4),
                    "dependency": round(dep_norm,4)
                },
                "explanation": "Task is in a circular dependency. Resolve cycle to compute score."
            })
            continue

        score_raw = (weights['urgency'] * urg_norm +
                     weights['importance'] * imp_norm +
                     weights['effort'] * eff_norm +
                     weights['dependency'] * dep_norm)
        score = max(0.0, min(100.0, score_raw * 100.0))
        explanation = []
        if urg_norm >= 1.0:
            explanation.append("High urgency (due soon or overdue)")
        elif urg_norm > 0.5:
            explanation.append("Medium-high urgency")
        else:
            explanation.append("Low/No urgency")
        explanation.append(f"importance={t['importance']}")
        explanation.append(f"estimated_hours={t['estimated_hours']}")
        if reach_counts.get(tid, 0) > 0:
            explanation.append(f"unblocks {reach_counts[tid]} task(s)")

        results.append({
            "id": tid,
            "title": t['title'],
            "score": round(score, 2),
            "subscores": {
                "urgency": round(urg_norm, 4),
                "importance": round(imp_norm, 4),
                "effort": round(eff_norm, 4),
                "dependency": round(dep_norm, 4)
            },
            "explanation": " | ".join(explanation)
        })

    results_sorted = sorted(results, key=lambda x: (x['score'] is not None, x['score']), reverse=True)
    return {"strategy": strategy, "warnings": warnings, "cycles": cycles, "tasks": results_sorted}

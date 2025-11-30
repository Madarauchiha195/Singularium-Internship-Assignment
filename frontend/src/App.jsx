import React, { useState, useEffect } from "react";
import axios from "axios";
import Graph from "./Graph";
import Eisenhower from "./Eisenhower";

const API_BASE = "http://127.0.0.1:8001";

const SAMPLE_TASKS = [
  {
    id: "T1",
    title: "Fix critical login bug",
    due_date: "2025-12-01",
    estimated_hours: 3,
    importance: 9,
    dependencies: []
  },
  {
    id: "T2",
    title: "Database schema improvement",
    due_date: "2025-12-15",
    estimated_hours: 12,
    importance: 7,
    dependencies: ["T1"]
  },
  {
    id: "T3",
    title: "Frontend UI polishing",
    due_date: "2025-12-20",
    estimated_hours: 5,
    importance: 6,
    dependencies: ["T2"]
  },
  {
    id: "T4",
    title: "Write unit tests",
    due_date: "2025-11-20",
    estimated_hours: 2,
    importance: 8,
    dependencies: []
  },
  {
    id: "T5",
    title: "Prepare deployment pipeline",
    due_date: "2025-12-05",
    estimated_hours: 6,
    importance: 7,
    dependencies: []
  }
];

export default function App() {
  const [tasksJson, setTasksJson] = useState(JSON.stringify(SAMPLE_TASKS, null, 2));
  const [strategy, setStrategy] = useState("smart_balance");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastPayload, setLastPayload] = useState(null);

  useEffect(() => {
    // optional: auto-analyze sample on load
    // analyze();
  }, []);

  const analyze = async () => {
    setError("");
    setLoading(true);
    setResult(null);
    let tasks;
    try {
      tasks = JSON.parse(tasksJson);
      if (!Array.isArray(tasks)) throw new Error("JSON must be an array of tasks");
    } catch (e) {
      setLoading(false);
      setError("Invalid JSON: " + e.message);
      return;
    }

    const payload = { tasks, strategy };
    setLastPayload(payload);
    try {
      const res = await axios.post(`${API_BASE}/api/tasks/analyze/`, payload, { timeout: 20000 });
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Network error");
    } finally {
      setLoading(false);
    }
  };

  const autoFillCycle = () => {
    const cycle = [
      { id: "A", title: "Task A", dependencies: ["B"], importance: 5 },
      { id: "B", title: "Task B", dependencies: ["C"], importance: 6 },
      { id: "C", title: "Task C", dependencies: ["A"], importance: 7 }
    ];
    setTasksJson(JSON.stringify(cycle, null, 2));
  };

  const copyResults = () => {
    if (!result) return;
    navigator.clipboard.writeText(JSON.stringify(result, null, 2));
    alert("Results copied to clipboard");
  };

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">Smart Task Analyzer</div>
        <div className="controls">
          <select value={strategy} onChange={(e) => setStrategy(e.target.value)}>
            <option value="smart_balance">Smart Balance</option>
            <option value="fastest_wins">Fastest Wins</option>
            <option value="high_impact">High Impact</option>
            <option value="deadline_driven">Deadline Driven</option>
          </select>
          <button className="btn" onClick={analyze} disabled={loading}>
            {loading ? "Analyzing..." : "Analyze"}
          </button>
        </div>
      </header>

      <main className="layout">
        <section className="leftpane">
          <h3>Tasks JSON</h3>
          <textarea value={tasksJson} onChange={(e) => setTasksJson(e.target.value)} />
          <div className="left-actions">
            <button className="btn ghost" onClick={() => setTasksJson(JSON.stringify(SAMPLE_TASKS, null, 2))}>
              Load Sample
            </button>
            <button className="btn ghost" onClick={autoFillCycle}>
              Load Cycle Example
            </button>
            <button
              className="btn ghost"
              onClick={() => {
                setTasksJson("[]");
              }}
            >
              Clear
            </button>
          </div>

          <div className="legend">
            <strong>Legend</strong>
            <div className="legend-row">
              <span className="badge high" /> High urgency
            </div>
            <div className="legend-row">
              <span className="badge med" /> Medium urgency
            </div>
            <div className="legend-row">
              <span className="badge low" /> Low urgency
            </div>
          </div>

          <div className="help">
            <strong>Quick tips</strong>
            <ul>
              <li>Provide tasks as an array of JSON objects (id required).</li>
              <li>Dependencies are arrays of other task IDs.</li>
              <li>Try different strategies from the dropdown.</li>
            </ul>
          </div>
        </section>

        <section className="rightpane">
          {error && <div className="error">{error}</div>}
          {!result && <div className="placeholder">Run analysis to see results here.</div>}

          {result && (
            <>
              <div className="resultsTop">
                <h2>Results — {result.strategy}</h2>
                <div className="result-actions">
                  <button className="btn small" onClick={copyResults}>
                    Copy JSON
                  </button>
                  <button
                    className="btn small"
                    onClick={() => {
                      if (!lastPayload) return;
                      setTasksJson(JSON.stringify(lastPayload.tasks, null, 2));
                    }}
                  >
                    Reuse Input
                  </button>
                </div>
              </div>

              <div className="panels">
                <div className="panel panel-list">
                  <h3>Priority List</h3>
                  {result.tasks.map((t) => (
                    <TaskCard key={t.id} task={t} />
                  ))}
                </div>

                <div className="panel panel-graph">
                  <h3>Dependency Graph</h3>
                  <Graph tasks={result.tasks} cycles={result.cycles} />
                </div>

                <div className="panel panel-eisen">
                  <h3>Eisenhower Matrix</h3>
                  <Eisenhower tasks={result.tasks} />
                </div>
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  );
}

/* small helper component inside file */
function TaskCard({ task }) {
  const score = task.score;
  const urgency = task.subscores?.urgency ?? 0;
  // urgency thresholds: >0.9 overdue/high, >0.6 med-high, >0.3 med, else low
  const urgencyLevel = urgency >= 1.0 ? "high" : urgency >= 0.7 ? "med" : "low";
  return (
    <div className="taskcard">
      <div className="task-left">
        <div className="task-title">{task.title || task.id}</div>
        <div className="task-meta">
          <span className={`badge ${urgencyLevel}`}>{Math.round((urgency > 1 ? 1 : urgency) * 100)}%</span>
          <span className="pill">Imp: {Math.round((task.subscores?.importance ?? 0) * 100)}</span>
          <span className="pill">Eff: {Math.round((task.subscores?.effort ?? 0) * 100)}</span>
          <span className="pill">Dep: {Math.round((task.subscores?.dependency ?? 0) * 100)}</span>
        </div>
        <div className="explanation">{task.explanation}</div>
      </div>
      <div className="task-right">
        <div className="score">{score === null ? "—" : score.toFixed(0)}</div>
      </div>
    </div>
  );
}

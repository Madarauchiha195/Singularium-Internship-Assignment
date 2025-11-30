import React from "react";

export default function Eisenhower({ tasks = [] }) {
  if (!tasks || tasks.length === 0) return <div className="placeholder">No tasks</div>;

  const urgentThr = 0.6; // adjust as needed
  const importantThr = 0.6;

  const buckets = { do: [], schedule: [], delegate: [], eliminate: [] };
  tasks.forEach((t) => {
    const urg = t.subscores?.urgency ?? 0;
    const imp = t.subscores?.importance ?? 0;
    const urgent = urg >= urgentThr;
    const important = imp >= importantThr;
    if (urgent && important) buckets.do.push(t);
    else if (!urgent && important) buckets.schedule.push(t);
    else if (urgent && !important) buckets.delegate.push(t);
    else buckets.eliminate.push(t);
  });

  const panel = (title, items) => (
    <div className="eisen-panel">
      <h4>{title} <small>({items.length})</small></h4>
      {items.map((i) => (
        <div key={i.id} className="eisen-item">
          <div className="eisen-title">{i.title || i.id}</div>
          <div className="eisen-meta">Score: {i.score === null ? '—' : Math.round(i.score)}</div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="eisenhower">
      <div className="eisen-row">
        {panel("Do Now (Urgent & Important)", buckets.do)}
        {panel("Schedule (Important, not Urgent)", buckets.schedule)}
      </div>
      <div className="eisen-row">
        {panel("Delegate (Urgent, not Important)", buckets.delegate)}
        {panel("Eliminate (Not Urgent, not Important)", buckets.eliminate)}
      </div>
    </div>
  );
}

import { useState } from 'react';
import axios from 'axios';

function App() {
  const [jsonText, setJsonText] = useState('');
  const [strategy, setStrategy] = useState('smart_balance');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const analyze = async () => {
    setError('');
    setResult(null);
    try {
      const payload = { tasks: JSON.parse(jsonText || '[]'), strategy };
      const res = await axios.post('http://127.0.0.1:8001/api/tasks/analyze/', payload);
      setResult(res.data);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    }
  };

  return (
    <div style={{maxWidth:900, margin:'24px auto', fontFamily:'Arial, sans-serif'}}>
      <h1>Smart Task Analyzer</h1>
      <div>
        <label>Strategy: </label>
        <select value={strategy} onChange={e=>setStrategy(e.target.value)}>
          <option value="smart_balance">Smart Balance</option>
          <option value="fastest_wins">Fastest Wins</option>
          <option value="high_impact">High Impact</option>
          <option value="deadline_driven">Deadline Driven</option>
        </select>
      </div>
      <textarea rows={12} style={{width:'100%', fontFamily:'monospace', marginTop:12}} value={jsonText} onChange={e=>setJsonText(e.target.value)} placeholder='[{"id":"t1","title":"Fix bug","due_date":"2025-11-30","estimated_hours":3,"importance":9,"dependencies":[]}]' />
      <div style={{marginTop:12}}>
        <button onClick={analyze}>Analyze</button>
      </div>

      {error && <div style={{color:'red', marginTop:12}}>{error}</div>}

      {result && (
        <div style={{marginTop:20}}>
          <h2>Results (strategy: {result.strategy})</h2>
          {result.warnings && result.warnings.length > 0 && <div style={{color:'#b45309'}}>Warnings: {JSON.stringify(result.warnings)}</div>}
          {result.cycles && result.cycles.length > 0 && <div style={{color:'red'}}>Cycles: {JSON.stringify(result.cycles)}</div>}
          <div>
            {result.tasks.map(t => (
              <div key={t.id} style={{border:'1px solid #eee', padding:12, marginTop:8, display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                <div>
                  <div><strong>{t.title || t.id}</strong> — {t.explanation}</div>
                  <div style={{fontSize:12, color:'#666'}}>{JSON.stringify(t.subscores)}</div>
                </div>
                <div style={{fontWeight:700, fontSize:18}}>{t.score === null ? '—' : t.score.toFixed(2)}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

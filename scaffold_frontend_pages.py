import os

frontend_dir = os.path.join(os.getcwd(), "frontend")

alerts_tsx = """
import { useEffect, useState } from 'react';
import axios from 'axios';

export default function AlertsCenter() {
  const [alerts, setAlerts] = useState<any[]>([]);

  const fetchAlerts = () => {
    axios.get('http://localhost:8000/api/alerts').then(res => setAlerts(res.data)).catch(console.error);
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const updateAlert = async (id: number, status: string) => {
    await axios.patch(`http://localhost:8000/api/alerts/${id}`, { status });
    fetchAlerts();
  };

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white">Fraud Alerts Center</h2>
      <div className="space-y-4">
        {alerts.length === 0 ? <p className="text-slate-400">No alerts found.</p> : alerts.map(alert => (
          <div key={alert.id} className="bg-surface p-6 rounded-xl border border-slate-700">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-white">Alert #{alert.id}</h3>
              <select 
                value={alert.status} 
                onChange={(e) => updateAlert(alert.id, e.target.value)}
                className="bg-slate-800 text-white p-2 rounded"
              >
                <option value="Open">Open</option>
                <option value="Investigating">Investigating</option>
                <option value="Resolved">Resolved</option>
                <option value="False Positive">False Positive</option>
              </select>
            </div>
            {alert.transaction && (
              <div className="text-slate-300">
                <p>Transaction Amount: ${alert.transaction.amount}</p>
                <p>Risk Score: {(alert.transaction.risk_score * 100).toFixed(1)}%</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
"""
with open(os.path.join(frontend_dir, "src", "pages", "AlertsCenter.tsx"), "w") as f:
    f.write(alerts_tsx)

model_perf_tsx = """
import { useEffect, useState } from 'react';
import axios from 'axios';

export default function ModelPerformance() {
  const [info, setInfo] = useState<any>(null);

  const fetchInfo = () => {
    axios.get('http://localhost:8000/api/model/info').then(res => setInfo(res.data)).catch(console.error);
  };

  useEffect(() => {
    fetchInfo();
  }, []);

  const trainModel = async () => {
    setInfo(null);
    await axios.post('http://localhost:8000/api/model/train');
    fetchInfo();
  };

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white">Model Performance</h2>
      <button onClick={trainModel} className="bg-primary px-4 py-2 rounded text-white font-bold hover:bg-cyan-600">Train Model</button>
      {info ? (
        <div className="bg-surface p-6 rounded-xl border border-slate-700 text-white">
          {info.error ? (
            <p className="text-red-400">{info.error}</p>
          ) : (
            <div className="space-y-4">
              <p>Accuracy: {(info.accuracy * 100).toFixed(2)}%</p>
              <p>Training Samples: {info.n_samples}</p>
              <p>Dataset: {info.is_demo ? "Demo Synthetic Data" : "Real Dataset"}</p>
              <div>
                <p className="font-bold">Confusion Matrix:</p>
                <pre className="bg-slate-800 p-4 rounded mt-2">{JSON.stringify(info.confusion_matrix, null, 2)}</pre>
              </div>
            </div>
          )}
        </div>
      ) : (
        <p className="text-slate-400">Loading model information...</p>
      )}
    </div>
  );
}
"""
with open(os.path.join(frontend_dir, "src", "pages", "ModelPerformance.tsx"), "w") as f:
    f.write(model_perf_tsx)

app_tsx = """
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Activity, ShieldAlert, BarChart3, Settings, AlertTriangle, Cpu } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Analyzer from './pages/Analyzer';
import AlertsCenter from './pages/AlertsCenter';
import ModelPerformance from './pages/ModelPerformance';

function App() {
  return (
    <Router>
      <div className="flex h-screen overflow-hidden text-slate-200 bg-background">
        <aside className="w-64 bg-surface border-r border-slate-700 flex flex-col">
          <div className="p-6">
            <h1 className="text-2xl font-bold text-primary flex items-center gap-2">
              <ShieldAlert className="h-8 w-8" />
              Sentinel AI
            </h1>
          </div>
          <nav className="flex-1 px-4 space-y-2">
            <Link to="/" className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-700 transition-colors">
              <Activity className="h-5 w-5" /> Dashboard
            </Link>
            <Link to="/analyze" className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-700 transition-colors">
              <BarChart3 className="h-5 w-5" /> Analyzer
            </Link>
            <Link to="/alerts" className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-700 transition-colors">
              <AlertTriangle className="h-5 w-5" /> Alerts Center
            </Link>
            <Link to="/model" className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-700 transition-colors">
              <Cpu className="h-5 w-5" /> Model Performance
            </Link>
          </nav>
        </aside>
        <main className="flex-1 overflow-auto p-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analyze" element={<Analyzer />} />
            <Route path="/alerts" element={<AlertsCenter />} />
            <Route path="/model" element={<ModelPerformance />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
export default App;
"""
with open(os.path.join(frontend_dir, "src", "App.tsx"), "w") as f:
    f.write(app_tsx)

print("Frontend pages added.")

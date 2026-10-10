
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

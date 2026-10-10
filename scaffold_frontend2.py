import os

frontend_dir = os.path.join(os.getcwd(), "frontend")

postcss_config = """
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
"""
with open(os.path.join(frontend_dir, "postcss.config.js"), "w") as f:
    f.write(postcss_config)

tailwind_config = """
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0f172a",
        surface: "#1e293b",
        primary: "#06b6d4",
        secondary: "#14b8a6",
      }
    },
  },
  plugins: [],
}
"""
with open(os.path.join(frontend_dir, "tailwind.config.js"), "w") as f:
    f.write(tailwind_config)

index_css = """
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  @apply bg-background text-slate-200 font-sans;
}
"""
with open(os.path.join(frontend_dir, "src", "index.css"), "w") as f:
    f.write(index_css)

app_tsx = """
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Activity, ShieldAlert, BarChart3, Settings } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Analyzer from './pages/Analyzer';

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
          </nav>
        </aside>
        <main className="flex-1 overflow-auto p-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analyze" element={<Analyzer />} />
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

os.makedirs(os.path.join(frontend_dir, "src", "pages"), exist_ok=True)

dashboard_tsx = """
import { useEffect, useState } from 'react';
import axios from 'axios';
import { ShieldAlert, CheckCircle, AlertTriangle } from 'lucide-react';

export default function Dashboard() {
  const [summary, setSummary] = useState({ total_transactions: 0, high_risk: 0, review: 0, flagged_percentage: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('http://localhost:8000/api/dashboard/summary')
      .then(res => {
        setSummary(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-8 text-slate-400">Loading dashboard...</div>;

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white">Overview Dashboard</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-surface p-6 rounded-xl border border-slate-700 flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm font-medium">Total Analyzed</p>
            <p className="text-3xl font-bold mt-2 text-white">{summary.total_transactions}</p>
          </div>
          <div className="h-12 w-12 rounded-full bg-slate-800 flex items-center justify-center text-blue-400">
            <CheckCircle className="h-6 w-6" />
          </div>
        </div>
        <div className="bg-surface p-6 rounded-xl border border-slate-700 flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm font-medium">High Risk Alerts</p>
            <p className="text-3xl font-bold mt-2 text-red-400">{summary.high_risk}</p>
          </div>
          <div className="h-12 w-12 rounded-full bg-red-900/30 flex items-center justify-center text-red-400">
            <ShieldAlert className="h-6 w-6" />
          </div>
        </div>
        <div className="bg-surface p-6 rounded-xl border border-slate-700 flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm font-medium">Requires Review</p>
            <p className="text-3xl font-bold mt-2 text-yellow-400">{summary.review}</p>
          </div>
          <div className="h-12 w-12 rounded-full bg-yellow-900/30 flex items-center justify-center text-yellow-400">
            <AlertTriangle className="h-6 w-6" />
          </div>
        </div>
      </div>
    </div>
  );
}
"""
with open(os.path.join(frontend_dir, "src", "pages", "Dashboard.tsx"), "w") as f:
    f.write(dashboard_tsx)

analyzer_tsx = """
import { useState } from 'react';
import axios from 'axios';

export default function Analyzer() {
  const [amount, setAmount] = useState('');
  const [merchant, setMerchant] = useState('retail');
  const [result, setResult] = useState<any>(null);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await axios.post('http://localhost:8000/api/transactions/analyze', {
        amount: parseFloat(amount),
        merchant_category: merchant,
        transaction_type: 'online',
        distance_from_home: 0,
        recent_transactions: 1,
        new_device: false,
        is_demo: true
      });
      setResult(res.data);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h2 className="text-3xl font-bold text-white">Transaction Analyzer</h2>
      <form onSubmit={handleAnalyze} className="bg-surface p-6 rounded-xl border border-slate-700 space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-400 mb-1">Transaction Amount ($)</label>
          <input 
            type="number" 
            value={amount} 
            onChange={(e) => setAmount(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-primary"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-400 mb-1">Merchant Category</label>
          <select 
            value={merchant}
            onChange={(e) => setMerchant(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-primary"
          >
            <option value="retail">Retail</option>
            <option value="travel">Travel</option>
            <option value="digital">Digital Goods</option>
          </select>
        </div>
        <button type="submit" className="w-full bg-primary hover:bg-cyan-600 text-white font-bold py-3 px-4 rounded-lg transition-colors">
          Analyze Transaction
        </button>
      </form>

      {result && (
        <div className={`p-6 rounded-xl border ${result.risk_category === 'High Risk' ? 'bg-red-900/20 border-red-500/50 text-red-400' : 'bg-surface border-slate-700 text-slate-200'}`}>
          <h3 className="text-xl font-bold mb-4 text-white">Analysis Result</h3>
          <p>Risk Score: {(result.risk_score * 100).toFixed(1)}%</p>
          <p>Category: <span className="font-bold text-white">{result.risk_category}</span></p>
        </div>
      )}
    </div>
  );
}
"""
with open(os.path.join(frontend_dir, "src", "pages", "Analyzer.tsx"), "w") as f:
    f.write(analyzer_tsx)

print("Frontend setup continuation complete!")

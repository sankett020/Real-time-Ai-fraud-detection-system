
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

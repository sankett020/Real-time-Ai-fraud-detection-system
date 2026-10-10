
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

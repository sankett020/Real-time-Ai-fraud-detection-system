
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

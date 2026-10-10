
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

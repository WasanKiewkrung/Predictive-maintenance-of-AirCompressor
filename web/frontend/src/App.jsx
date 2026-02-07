import React, { useState, useEffect, useRef } from 'react';

const App = () => {
  const [logs, setLogs] = useState([]);
  const [current, setCurrent] = useState(null);
  const [status, setStatus] = useState("OPTIMAL");
  const ws = useRef(null);

  // ค่า Threshold (เกณฑ์อันตราย)
  const THRESHOLDS = { vibration: 1.2, temp: 60.0, amp: 5.0 };

  useEffect(() => {
    ws.current = new WebSocket("ws://localhost:8000/ws/frontend");
    ws.current.onopen = () => console.log("✅ Connected");

    ws.current.onmessage = (event) => {
      const json = JSON.parse(event.data);

      // Logic ตรวจจับความผิดปกติ (รวมแกน Z แล้ว)
      let issue = null;
      if (Math.abs(json.ax) > THRESHOLDS.vibration || Math.abs(json.ay) > THRESHOLDS.vibration || Math.abs(json.az) > THRESHOLDS.vibration) issue = "High Vibration Detected";
      else if (json.temp > THRESHOLDS.temp) issue = "Temp Elevated > 60°C";
      else if (json.amp > THRESHOLDS.amp) issue = "Motor Overcurrent";

      setStatus(issue ? "WARNING" : "OPTIMAL");
      setCurrent(json);

      // อัปเดต Log (สุ่มเก็บ หรือเก็บเมื่อมีปัญหา)
      if (issue || Math.random() > 0.95) {
        setLogs((prev) => {
          const newLog = {
            time: new Date().toLocaleTimeString('en-US', { hour12: false }),
            status: issue ? "WARNING" : "NORMAL",
            message: issue ? issue : "Routine check. All parameters within optimal range.",
            rul: json.rul_predict
          };
          return [newLog, ...prev].slice(0, 10);
        });
      }
    };
    return () => ws.current.close();
  }, []);

  if (!current) return <div className="min-h-screen flex items-center justify-center bg-slate-50 text-primary font-bold animate-pulse">Initializing Dashboard...</div>;

  // คำนวณวงกลม RUL
  const maxRul = 500;
  const circleDashArray = 283;
  const circleOffset = circleDashArray - ((current.rul_predict / maxRul) * circleDashArray);

  // เช็คว่ามีการสั่นผิดปกติหรือไม่ (รวม 3 แกน)
  const isVibrationHigh = Math.abs(current.ax) > THRESHOLDS.vibration ||
    Math.abs(current.ay) > THRESHOLDS.vibration ||
    Math.abs(current.az) > THRESHOLDS.vibration;

  // หาค่าสั่นสูงสุด (Peak) จาก 3 แกน
  const peakVibration = Math.max(Math.abs(current.ax), Math.abs(current.ay), Math.abs(current.az)).toFixed(2);

  return (
    <div className="bg-background-light text-text-main min-h-screen flex flex-col font-display selection:bg-primary selection:text-white">

      {/* HEADER */}
      <header className="w-full bg-surface-light/80 backdrop-blur-md border-b border-border-light sticky top-0 z-50 shadow-sm">
        <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <div className="flex items-center gap-3">
              <div className="bg-primary/10 p-2 rounded-lg text-primary border border-primary/20">
                <span className="material-symbols-outlined text-2xl">precision_manufacturing</span>
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-tight text-slate-900 leading-none">Air Compressor Monitoring Dashboard</h1>
                <span className="text-xs text-slate-500 font-medium tracking-wide uppercase mt-1 block">Model Output & Decision Support System</span>
              </div>
            </div>

            <div className="flex items-center gap-6">
              <div className="hidden md:flex flex-col items-end mr-2">
                <span className="text-xs text-slate-500 font-medium">Last Updated</span>
                <span className="text-sm font-mono text-slate-700 font-semibold">{new Date().toLocaleTimeString()}</span>
              </div>
              <div className={`flex items-center gap-2 px-4 py-2 rounded-lg shadow-sm border ${status === "OPTIMAL" ? "bg-success-bg border-success/30" : "bg-warning-bg border-warning/30"}`}>
                <span className="relative flex h-3 w-3">
                  <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${status === "OPTIMAL" ? "bg-success" : "bg-warning"}`}></span>
                  <span className={`relative inline-flex rounded-full h-3 w-3 ${status === "OPTIMAL" ? "bg-success" : "bg-warning"}`}></span>
                </span>
                <span className={`font-bold text-sm tracking-wide ${status === "OPTIMAL" ? "text-green-700" : "text-amber-700"}`}>
                  SYSTEM {status}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* MAIN CONTENT */}
      <main className="flex-grow max-w-[1400px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

          {/* LEFT: RUL CARD */}
          <div className="lg:col-span-5 flex flex-col">
            <div className="bg-surface-light border border-slate-200 rounded-xl p-8 flex flex-col h-full relative overflow-hidden group hover:border-primary/40 transition-all duration-300 shadow-soft hover:shadow-lg">
              <div className="absolute top-0 right-0 p-32 bg-blue-50/50 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none"></div>

              <div className="flex items-center justify-between mb-8 z-10">
                <div className="flex items-center gap-2 text-slate-600">
                  <span className="material-symbols-outlined text-primary">psychology</span>
                  <h3 className="font-semibold text-lg text-slate-800">Remaining Useful Life (RUL)</h3>
                </div>
                <button className="text-xs font-semibold text-primary hover:text-primary-dark flex items-center gap-1 transition-colors bg-primary-light/30 px-3 py-1.5 rounded-full">
                  View Model Details <span className="material-symbols-outlined text-sm">arrow_forward</span>
                </button>
              </div>

              {/* RUL CIRCLE */}
              <div className="flex-grow flex flex-col items-center justify-center py-6 z-10">
                <div className="relative w-64 h-64 flex items-center justify-center">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" fill="none" r="45" stroke="#f1f5f9" strokeWidth="8"></circle>
                    <circle
                      className="drop-shadow-lg transition-all duration-1000 ease-out"
                      cx="50" cy="50" fill="none" r="45"
                      stroke={current.rul_predict < 100 ? "#ef4444" : "#135bec"}
                      strokeDasharray="283"
                      strokeDashoffset={circleOffset}
                      strokeLinecap="round" strokeWidth="8"
                    ></circle>
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                    <span className="text-5xl font-extrabold text-slate-800 font-mono tracking-tighter">{current.rul_predict}</span>
                    <span className="text-sm text-slate-500 font-bold uppercase tracking-widest mt-1">Hours</span>
                  </div>
                </div>
              </div>

              <div className="mt-8 bg-slate-50 rounded-lg p-4 border border-slate-200 z-10">
                <div className="flex items-start gap-3">
                  <span className={`material-symbols-outlined mt-0.5 ${current.rul_predict < 100 ? "text-danger" : "text-success"}`}>
                    {current.rul_predict < 100 ? "warning" : "check_circle"}
                  </span>
                  <div>
                    <p className="text-sm font-bold text-slate-800 mb-1">AI Recommendation</p>
                    <p className="text-sm text-slate-600 leading-relaxed">
                      {current.rul_predict > 100
                        ? <><span className="text-green-600 font-semibold">Healthy Condition:</span> No immediate maintenance required.</>
                        : <><span className="text-red-600 font-semibold">Maintenance Required:</span> Schedule inspection immediately.</>
                      }
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT: SENSORS GRID */}
          <div className="lg:col-span-7 grid grid-cols-1 md:grid-cols-3 gap-6">

            {/* Temperature */}
            <div className={`bg-surface-light border rounded-xl p-6 flex flex-col relative overflow-hidden shadow-soft hover:shadow-md transition-all ${current.temp > THRESHOLDS.temp ? 'border-danger/50 bg-red-50/30' : 'border-slate-200'}`}>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2 text-slate-500">
                  <span className="material-symbols-outlined text-xl">thermostat</span>
                  <span className="text-sm font-bold uppercase tracking-wide">Temp</span>
                </div>
              </div>
              <div className="flex flex-row items-end gap-6 h-full">
                <div className="h-40 w-12 bg-slate-100 rounded-full relative overflow-hidden border border-slate-200 flex flex-col justify-end shadow-inner">
                  <div className="absolute bottom-[60%] w-full h-[2px] bg-danger z-20 opacity-80"></div>
                  <div
                    className={`w-full opacity-90 transition-all duration-1000 ease-out shadow-lg ${current.temp > THRESHOLDS.temp ? "bg-danger" : "bg-gradient-to-t from-blue-500 to-cyan-400"}`}
                    style={{ height: `${Math.min(current.temp, 100)}%` }}
                  ></div>
                </div>
                <div className="flex flex-col pb-2">
                  <span className="text-4xl font-bold text-slate-800 font-mono mb-1">{current.temp}</span>
                  <span className="text-sm text-slate-500 font-medium">Celsius (°C)</span>
                  <div className="mt-1 text-xs text-slate-400">Threshold: 60°C</div>
                </div>
              </div>
            </div>

            {/* Current */}
            <div className={`bg-surface-light border rounded-xl p-6 flex flex-col relative overflow-hidden shadow-soft hover:shadow-md transition-all ${current.amp > THRESHOLDS.amp ? 'border-danger/50 bg-red-50/30' : 'border-slate-200'}`}>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2 text-slate-500">
                  <span className="material-symbols-outlined text-xl">electric_bolt</span>
                  <span className="text-sm font-bold uppercase tracking-wide">Current</span>
                </div>
              </div>
              <div className="flex flex-row items-end gap-6 h-full">
                <div className="h-40 w-12 bg-slate-100 rounded-full relative overflow-hidden border border-slate-200 flex flex-col justify-end shadow-inner">
                  <div className="absolute bottom-[50%] w-full h-[2px] bg-danger z-20 opacity-80"></div>
                  <div
                    className={`w-full opacity-90 transition-all duration-1000 ease-out shadow-lg ${current.amp > THRESHOLDS.amp ? "bg-danger" : "bg-gradient-to-t from-primary to-indigo-400"}`}
                    style={{ height: `${Math.min((current.amp / 10) * 100, 100)}%` }}
                  ></div>
                </div>
                <div className="flex flex-col pb-2">
                  <span className="text-4xl font-bold text-slate-800 font-mono mb-1">{current.amp}</span>
                  <span className="text-sm text-slate-500 font-medium">Amperes (A)</span>
                  <div className="mt-1 text-xs text-slate-400">Threshold: 5.0A</div>
                </div>
              </div>
            </div>

            {/* Vibration (Updated with Z-Axis) */}
            <div className={`bg-surface-light border rounded-xl p-6 flex flex-col justify-between relative overflow-hidden md:col-span-1 shadow-soft hover:shadow-md transition-all ${isVibrationHigh ? 'border-danger/50' : 'border-slate-200'}`}>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2 text-slate-500">
                  <span className="material-symbols-outlined text-xl">vibration</span>
                  <span className="text-sm font-bold uppercase tracking-wide">Vibration</span>
                </div>
              </div>

              <div className="flex flex-col items-center justify-center h-full gap-4 py-2">
                {/* Simulation Equalizer */}
                <div className="flex items-center justify-center gap-1 h-12 w-full">
                  {[...Array(6)].map((_, i) => (
                    <div key={i} className={`w-1.5 rounded-full ${isVibrationHigh ? 'bg-danger animate-pulse' : 'bg-success'}`}
                      style={{ height: `${Math.random() * 40 + 10}px`, transition: 'height 0.2s' }}></div>
                  ))}
                </div>
                <div className="text-center">
                  <span className={`text-lg font-bold block mb-1 ${isVibrationHigh ? 'text-danger' : 'text-green-700'}`}>
                    {isVibrationHigh ? "High Vibration" : "Stable Operation"}
                  </span>
                  <span className="text-xs text-slate-500 font-medium">Peak: {peakVibration} g</span>
                </div>
              </div>

              {/* Axis List (เพิ่ม Z-Axis ตรงนี้) */}
              <div className="mt-auto pt-4 border-t border-slate-100 space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-500 font-medium">X-Axis</span>
                  <span className="text-slate-700 font-mono font-semibold">{current.ax} g</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-slate-500 font-medium">Y-Axis</span>
                  <span className="text-slate-700 font-mono font-semibold">{current.ay} g</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-slate-500 font-medium">Z-Axis</span>
                  <span className="text-slate-700 font-mono font-semibold">{current.az} g</span>
                </div>
              </div>
            </div>

          </div>
        </div>

        {/* LOGS TABLE */}
        <div className="bg-surface-light border border-slate-200 rounded-xl overflow-hidden shadow-soft">
          <div className="px-6 py-5 border-b border-slate-200 flex items-center justify-between bg-slate-50/50">
            <div className="flex items-center gap-3">
              <div className="bg-primary/10 p-1.5 rounded text-primary border border-primary/20">
                <span className="material-symbols-outlined text-lg">history</span>
              </div>
              <h3 className="font-bold text-slate-800 text-lg">Model Prediction & Alert History</h3>
            </div>
            <button className="px-3 py-1.5 text-xs font-semibold text-slate-600 bg-white hover:bg-slate-50 rounded border border-slate-200 shadow-sm transition-colors">Export CSV</button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-slate-500 text-xs uppercase tracking-wider">
                  <th className="px-6 py-4 font-semibold w-48">Time Logged</th>
                  <th className="px-6 py-4 font-semibold w-40">System Status</th>
                  <th className="px-6 py-4 font-semibold">AI Diagnosis / Message</th>
                  <th className="px-6 py-4 font-semibold w-40 text-right">RUL Estimate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm bg-white">
                {logs.map((log, index) => (
                  <tr key={index} className="group hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4 text-slate-600 font-mono font-medium">{log.time}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold border ${log.status === "NORMAL" ? "bg-success-bg text-green-700 border-success/20" : "bg-warning-bg text-amber-700 border-warning/30"}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${log.status === "NORMAL" ? "bg-success" : "bg-warning"}`}></span>
                        {log.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-700">
                      <div className="flex items-center gap-2">
                        <span className={`material-symbols-outlined text-lg ${log.status === "NORMAL" ? "text-success" : "text-warning"}`}>
                          {log.status === "NORMAL" ? "check_circle" : "warning"}
                        </span>
                        {log.message}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right text-slate-900 font-mono font-semibold">{log.rul} hrs</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {logs.length === 0 && <div className="p-8 text-center text-slate-500">Waiting for data...</div>}
          </div>
        </div>

      </main>
    </div>
  );
};

export default App;
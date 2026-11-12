import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Area, AreaChart, BarChart, Bar, Cell, Legend
} from 'recharts';
import {
  Brain, TrendingUp, TrendingDown, Minus, AlertTriangle,
  ShieldCheck, Activity, BarChart2, Lock, Eye, EyeOff
} from 'lucide-react';
import { API_BASE_URL } from '../api/client';

const API = API_BASE_URL;
const SESSION_ID = 'demo_user_001';
const CLINICIAN_PIN = '1234'; // In production, this would be a real auth token

const SEVERITY_COLORS = {
  Normal: '#10b981',
  Mild: '#f59e0b',
  Moderate: '#f97316',
  Severe: '#ef4444',
};

const SEVERITY_NUM = { Normal: 0, Mild: 1, Moderate: 2, Severe: 3 };

function PinGate({ onUnlock }) {
  const [pin, setPin] = useState('');
  const [error, setError] = useState(false);

  const handleSubmit = () => {
    if (pin === CLINICIAN_PIN) {
      onUnlock();
    } else {
      setError(true);
      setPin('');
      setTimeout(() => setError(false), 2000);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card max-w-sm w-full text-center space-y-6"
      >
        <div className="w-16 h-16 mx-auto rounded-2xl bg-teal/10 flex items-center justify-center">
          <Lock size={32} className="text-teal-600" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100">Clinician Dashboard</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Enter your PIN to access the XAI panel</p>
        </div>
        <input
          type="password"
          value={pin}
          onChange={e => setPin(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSubmit()}
          placeholder="Enter PIN"
          maxLength={6}
          className={`w-full text-center text-2xl tracking-widest border-2 rounded-xl py-3 bg-white/50 dark:bg-slate-800/50 text-slate-800 dark:text-white outline-none transition-all ${
            error ? 'border-red-400 shake' : 'border-teal/30 focus:border-teal'
          }`}
        />
        {error && <p className="text-red-500 text-sm animate-pulse">Incorrect PIN. Try again.</p>}
        <button
          onClick={handleSubmit}
          className="btn-primary w-full"
        >
          Unlock Dashboard
        </button>
        <p className="text-xs text-slate-400 dark:text-slate-500">Demo PIN: 1234</p>
      </motion.div>
    </div>
  );
}

function SeverityBadge({ label }) {
  const colors = {
    Normal: 'bg-emerald-100 text-emerald-700 border-emerald-200',
    Mild: 'bg-amber-100 text-amber-700 border-amber-200',
    Moderate: 'bg-orange-100 text-orange-700 border-orange-200',
    Severe: 'bg-red-100 text-red-700 border-red-200',
  };
  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${colors[label] || 'bg-slate-100 text-slate-600'}`}>
      {label}
    </span>
  );
}

function StatCard({ icon: Icon, label, value, sub, color = 'teal' }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel flex items-center gap-4"
    >
      <div className={`w-12 h-12 rounded-xl bg-${color}-100 dark:bg-${color}-900/30 flex items-center justify-center shrink-0`}>
        <Icon size={22} className={`text-${color}-600`} />
      </div>
      <div>
        <p className="text-2xl font-bold text-slate-800 dark:text-slate-100">{value}</p>
        <p className="text-sm font-medium text-slate-600 dark:text-slate-400">{label}</p>
        {sub && <p className="text-xs text-slate-400 dark:text-slate-500">{sub}</p>}
      </div>
    </motion.div>
  );
}

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-3 shadow-xl text-sm">
        <p className="font-semibold text-slate-700 dark:text-slate-300 mb-1">{label}</p>
        {payload.map((p, i) => (
          <p key={i} style={{ color: p.color }}>
            {p.name}: <strong>{p.value}</strong>
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default function ClinicalDashboard() {
  const [unlocked, setUnlocked] = useState(false);
  const [trajectory, setTrajectory] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showRaw, setShowRaw] = useState(false);

  useEffect(() => {
    if (unlocked) {
      loadData();
    }
  }, [unlocked]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [trajRes, sumRes] = await Promise.all([
        fetch(`${API}/trajectory/${SESSION_ID}?limit=30`),
        fetch(`${API}/trajectory/${SESSION_ID}/summary`),
      ]);
      const traj = await trajRes.json();
      const sum = await sumRes.json();
      setTrajectory(traj);
      setSummary(sum);
    } catch (e) {
      console.error('Failed to load trajectory:', e);
    } finally {
      setLoading(false);
    }
  };

  if (!unlocked) {
    return <PinGate onUnlock={() => setUnlocked(true)} />;
  }

  const chartData = trajectory?.trajectory?.map((r, i) => ({
    idx: i + 1,
    time: r.timestamp ? new Date(r.timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : `#${i + 1}`,
    severity: r.severity_score,
    severityLabel: r.severity_label,
    csi: Math.round((r.csi || 0) * 100),
    confidence: Math.round((r.confidence || 0) * 100),
  })) || [];

  const distData = summary?.severity_distribution
    ? Object.entries(summary.severity_distribution).map(([label, count]) => ({ label, count }))
    : [];

  const csiTrendIcon = {
    increasing: <TrendingUp size={16} className="text-orange-500" />,
    decreasing: <TrendingDown size={16} className="text-emerald-500" />,
    stable: <Minus size={16} className="text-slate-400" />,
  }[trajectory?.csi_trend || 'stable'];

  return (
    <div className="max-w-6xl mx-auto space-y-6 pb-12">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-teal/10 flex items-center justify-center">
            <Brain size={20} className="text-teal-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100">XAI Clinical Dashboard</h1>
            <p className="text-sm text-slate-500 dark:text-slate-400">Session: <code className="bg-slate-100 dark:bg-slate-800 px-1.5 rounded">{SESSION_ID}</code></p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {trajectory?.acute_drop_detected && (
            <motion.div
              animate={{ scale: [1, 1.05, 1] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
              className="flex items-center gap-2 bg-red-50 border border-red-200 text-red-700 rounded-xl px-3 py-2 text-sm font-semibold"
            >
              <AlertTriangle size={16} />
              Acute Drop Detected
            </motion.div>
          )}
          <button
            onClick={() => setShowRaw(!showRaw)}
            className="flex items-center gap-1.5 text-sm text-slate-500 dark:text-slate-400 hover:text-teal-600 dark:hover:text-teal-400 transition-colors"
          >
            {showRaw ? <EyeOff size={16} /> : <Eye size={16} />}
            {showRaw ? 'Hide' : 'Show'} Raw
          </button>
          <button onClick={loadData} className="btn-primary text-sm py-1.5 px-4">
            Refresh
          </button>
        </div>
      </motion.div>

      {loading ? (
        <div className="glass-card flex items-center justify-center h-40">
          <div className="animate-spin w-8 h-8 border-4 border-teal/30 border-t-teal rounded-full" />
        </div>
      ) : (
        <>
          {/* Stats Row */}
          {summary && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard icon={Activity} label="Total Messages" value={summary.total_messages} />
              <StatCard icon={ShieldCheck} label="Dominant Severity" value={summary.dominant_severity}
                color={summary.dominant_severity === 'Normal' ? 'emerald' : summary.dominant_severity === 'Severe' ? 'red' : 'amber'} />
              <StatCard icon={BarChart2} label="Crisis Events" value={summary.severe_events}
                sub={`+ ${summary.moderate_events} moderate`} color="orange" />
              <StatCard icon={TrendingUp} label="Avg CSI" value={`${Math.round((summary.avg_csi || 0) * 100)}%`}
                sub="Code-Switching Index" color="purple" />
            </div>
          )}

          {/* CSI Info Banner */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="glass-panel flex items-start gap-3 border-l-4 border-teal"
          >
            <Brain size={18} className="text-teal-600 mt-0.5 shrink-0" />
            <div>
              <p className="font-semibold text-slate-700 dark:text-slate-200 text-sm">
                Code-Switching Index (CSI) Trend: <span className="inline-flex items-center gap-1">{csiTrendIcon} {trajectory?.csi_trend}</span>
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                A rising CSI (more Tanglish over time) is a novel biomarker indicating increasing emotional distress. 
                Sociolinguistic research shows people revert to their native language under stress.
              </p>
            </div>
          </motion.div>

          {/* Risk Trajectory Chart */}
          {chartData.length > 0 ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card">
              <h3 className="font-bold text-slate-700 dark:text-slate-200 mb-4 flex items-center gap-2">
                <TrendingUp size={18} className="text-teal-600" />
                Longitudinal Risk Trajectory
              </h3>
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="sevGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#14b8a6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#14b8a6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" strokeOpacity={0.5} />
                  <XAxis dataKey="time" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                  <YAxis domain={[0, 3]} ticks={[0, 1, 2, 3]}
                    tickFormatter={v => ['Normal', 'Mild', 'Mod.', 'Severe'][v]}
                    tick={{ fontSize: 10, fill: '#94a3b8' }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="severity" name="Severity" stroke="#14b8a6"
                    strokeWidth={2.5} fill="url(#sevGrad)" dot={{ fill: '#14b8a6', r: 4 }}
                    activeDot={{ r: 6, strokeWidth: 2 }} />
                </AreaChart>
              </ResponsiveContainer>
            </motion.div>
          ) : (
            <div className="glass-card text-center py-12 text-slate-400 dark:text-slate-500">
              <Activity size={40} className="mx-auto mb-3 opacity-30" />
              <p className="font-medium">No trajectory data yet.</p>
              <p className="text-sm mt-1">Send a few messages in the Chat tab to populate this chart.</p>
            </div>
          )}

          {/* CSI Trend + Distribution Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* CSI Over Time */}
            {chartData.length > 0 && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card">
                <h3 className="font-bold text-slate-700 dark:text-slate-200 mb-4 text-sm flex items-center gap-2">
                  <Activity size={16} className="text-purple-500" />
                  Code-Switching Index (CSI) Over Time
                </h3>
                <ResponsiveContainer width="100%" height={160}>
                  <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" strokeOpacity={0.4} />
                    <XAxis dataKey="time" tick={{ fontSize: 10, fill: '#94a3b8' }} />
                    <YAxis domain={[0, 100]} tickFormatter={v => `${v}%`} tick={{ fontSize: 10, fill: '#94a3b8' }} />
                    <Tooltip content={<CustomTooltip />} />
                    <Line type="monotone" dataKey="csi" name="CSI (%)" stroke="#a855f7"
                      strokeWidth={2} dot={{ fill: '#a855f7', r: 3 }} />
                  </LineChart>
                </ResponsiveContainer>
              </motion.div>
            )}

            {/* Severity Distribution */}
            {distData.length > 0 && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card">
                <h3 className="font-bold text-slate-700 dark:text-slate-200 mb-4 text-sm flex items-center gap-2">
                  <BarChart2 size={16} className="text-teal-600" />
                  Severity Distribution
                </h3>
                <ResponsiveContainer width="100%" height={160}>
                  <BarChart data={distData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" strokeOpacity={0.4} />
                    <XAxis dataKey="label" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                    <YAxis allowDecimals={false} tick={{ fontSize: 10, fill: '#94a3b8' }} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="count" name="Messages" radius={[6, 6, 0, 0]}>
                      {distData.map((entry, index) => (
                        <Cell key={index} fill={SEVERITY_COLORS[entry.label] || '#94a3b8'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </motion.div>
            )}
          </div>

          {/* Raw Log */}
          <AnimatePresence>
            {showRaw && trajectory?.trajectory?.length > 0 && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="glass-card overflow-hidden"
              >
                <h3 className="font-bold text-slate-700 dark:text-slate-200 mb-3 text-sm">Raw Event Log</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="text-left text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-700">
                        <th className="pb-2 pr-4">#</th>
                        <th className="pb-2 pr-4">Severity</th>
                        <th className="pb-2 pr-4">Confidence</th>
                        <th className="pb-2 pr-4">CSI</th>
                        <th className="pb-2 pr-4">Language</th>
                        <th className="pb-2">Time</th>
                      </tr>
                    </thead>
                    <tbody>
                      {trajectory.trajectory.slice().reverse().map((r, i) => (
                        <tr key={i} className="border-b border-slate-100 dark:border-slate-800">
                          <td className="py-1.5 pr-4 text-slate-400 dark:text-slate-500">{trajectory.trajectory.length - i}</td>
                          <td className="py-1.5 pr-4"><SeverityBadge label={r.severity_label} /></td>
                          <td className="py-1.5 pr-4 text-slate-600 dark:text-slate-400">{Math.round((r.confidence || 0) * 100)}%</td>
                          <td className="py-1.5 pr-4 text-purple-600 dark:text-purple-400">{Math.round((r.csi || 0) * 100)}%</td>
                          <td className="py-1.5 pr-4 text-slate-500 dark:text-slate-400">{r.language || 'English'}</td>
                          <td className="py-1.5 text-slate-400 dark:text-slate-500">
                            {r.timestamp ? new Date(r.timestamp).toLocaleString('en-IN') : '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <p className="text-center text-xs text-slate-400 dark:text-slate-500 mt-2">
            MindGuard XAI Dashboard — For clinical review only. Not a diagnostic tool.
          </p>
        </>
      )}
    </div>
  );
}

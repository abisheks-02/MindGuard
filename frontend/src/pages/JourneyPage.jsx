import React, { useState, useEffect } from 'react';
import { XAxis, YAxis, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { Flame, Calendar, Activity, Zap, CheckCircle2, ChevronRight, Sparkles, Award } from 'lucide-react';
import { motion } from 'framer-motion';
import { API_BASE_URL } from '../api/client';

export default function JourneyPage() {
  const [history, setHistory] = useState(null);
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);

  const [emoji, setEmoji] = useState('😐');
  const [savedToday, setSavedToday] = useState(false);
  const [xp, setXp] = useState(1250);

  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE_URL}/mood/history?range_days=7`).then(res => res.json()),
      fetch(`${API_BASE_URL}/mood/plan`).then(res => res.json())
    ]).then(([hist, planData]) => {
      // Mock data if backend fails
      if (!hist || hist.error) {
        hist = { streak_days: 12, trend: 'improving', aggregates: [
          {date: 'Mon', avg_severity: 0}, {date: 'Tue', avg_severity: 1}, 
          {date: 'Wed', avg_severity: 0}, {date: 'Thu', avg_severity: 2},
          {date: 'Fri', avg_severity: 1}, {date: 'Sat', avg_severity: 0}, {date: 'Sun', avg_severity: 0}
        ]};
      }
      if (!planData || planData.error) {
        planData = { days: [
          {day: 'Day 1', activity: 'Morning Walk', cbt: 'Identify negative thought', reflection: 'What went well?', completed: true},
          {day: 'Day 2', activity: 'Box Breathing', cbt: 'Challenge the thought', reflection: 'Rate anxiety 1-10', completed: false},
          {day: 'Day 3', activity: 'Call a friend', cbt: 'Reframe', reflection: 'How do you feel now?', completed: false},
        ]};
      }
      setHistory(hist);
      setPlan(planData);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const handleLogToday = () => {
    setSavedToday(true);
    setXp(prev => prev + 50); // Give XP for logging
  };

  const isImproving = history?.trend === 'improving';

  if (loading) return (
    <div className="h-full flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto pb-20 overflow-x-hidden">
      
      {/* Hero Section */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        className="relative bg-teal-700 rounded-2xl p-8 text-white shadow-sm mb-8 overflow-hidden"
      >
        <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div>
            <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
              Good Evening, Alex <Sparkles size={24} className="text-teal-200" />
            </h1>
            <p className="text-teal-50 text-lg opacity-90 max-w-md">
              Your emotional resilience is growing. You've checked in for {history?.streak_days} days straight!
            </p>
          </div>
          <div className="bg-teal-800 border border-teal-600 rounded-xl p-4 flex items-center gap-4">
            <div className="bg-amber-400 p-3 rounded-xl shadow-inner">
              <Award className="text-amber-700" size={24} />
            </div>
            <div>
              <p className="text-xs uppercase tracking-wider font-bold text-teal-50 mb-1">Total XP</p>
              <p className="text-2xl font-black">{xp}</p>
            </div>
          </div>
        </div>
      </motion.div>

      <div className="grid md:grid-cols-3 gap-6 mb-8">
        {/* Quick Log Card */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="md:col-span-2 bg-white dark:bg-slate-800 rounded-3xl p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-none border border-slate-100 dark:border-slate-700"
        >
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100">How are you feeling today?</h2>
            {savedToday && <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-3 py-1 rounded-full flex items-center gap-1"><CheckCircle2 size={14}/> +50 XP</span>}
          </div>
          <div className="flex items-center gap-2 justify-between bg-slate-50 dark:bg-slate-900 p-3 rounded-2xl mb-6">
            {['😭', '😔', '😐', '🙂', '🤩'].map(e => (
              <button 
                key={e} 
                onClick={() => !savedToday && setEmoji(e)} 
                className={`text-4xl transition-all duration-300 hover:scale-110 ${emoji === e ? 'scale-125 drop-shadow-xl -translate-y-2' : 'opacity-40 grayscale'}`}
              >
                {e}
              </button>
            ))}
          </div>
          <button 
            onClick={handleLogToday}
            disabled={savedToday}
            className={`w-full py-3 rounded-xl font-bold transition-colors ${savedToday ? 'bg-slate-100 text-slate-500' : 'bg-slate-900 text-white hover:bg-slate-800 shadow-sm'}`}
          >
            {savedToday ? 'Logged for Today' : 'Save Check-in'}
          </button>
        </motion.div>

        {/* Mini Stats */}
        <div className="space-y-6">
          <motion.div 
            initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}
            className="bg-white dark:bg-slate-800 rounded-3xl p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-none border border-slate-100 dark:border-slate-700 flex items-center gap-4"
          >
            <div className="bg-orange-50 dark:bg-orange-500/10 p-4 rounded-2xl">
              <Flame className="text-orange-500" size={28} />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Streak</p>
              <p className="text-3xl font-black text-slate-800 dark:text-slate-100">{history?.streak_days}</p>
            </div>
          </motion.div>
          
          <motion.div 
            initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}
            className={`rounded-3xl p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-none border flex items-center gap-4 ${isImproving ? 'bg-emerald-50 dark:bg-emerald-900/20 border-emerald-100 dark:border-emerald-800' : 'bg-white dark:bg-slate-800 border-slate-100 dark:border-slate-700'}`}
          >
            <div className={`${isImproving ? 'bg-emerald-200 dark:bg-emerald-800/50' : 'bg-slate-100 dark:bg-slate-700'} p-4 rounded-2xl`}>
              <Activity className={isImproving ? 'text-emerald-700 dark:text-emerald-400' : 'text-slate-600 dark:text-slate-300'} size={28} />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Trend</p>
              <p className={`text-2xl font-black capitalize ${isImproving ? 'text-emerald-800 dark:text-emerald-400' : 'text-slate-800 dark:text-slate-100'}`}>
                {history?.trend}
              </p>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Chart Section */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
        className="bg-white dark:bg-slate-800 rounded-3xl p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-none border border-slate-100 dark:border-slate-700 mb-8"
      >
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100">Mood Trajectory (7 Days)</h2>
          <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-700 px-3 py-1 rounded-full">Lower is better</span>
        </div>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={history?.aggregates || []} margin={{ top: 10, right: 10, bottom: 0, left: -20 }}>
              <defs>
                <linearGradient id="colorSeverity" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} dy={10} />
              <YAxis domain={[0, 3]} axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} tickFormatter={(val) => ['Great', 'Mild', 'Mod', 'Severe'][val]} />
              <Tooltip 
                contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1)' }}
                formatter={(value) => [['Great', 'Mild Risk', 'Moderate Risk', 'Severe Risk'][value], 'State']}
              />
              <Area type="monotone" dataKey="avg_severity" stroke="#0ea5e9" strokeWidth={4} fillOpacity={1} fill="url(#colorSeverity)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* Wellness Plan */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
        <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100 mb-6 flex items-center gap-2">
          <Calendar className="text-teal-600 dark:text-teal-400" /> My Wellness Plan
        </h2>
        
        <div className="space-y-4">
          {plan?.days?.map((day, i) => (
            <div key={i} className={`rounded-2xl p-5 border transition-all hover:shadow-lg flex items-center gap-4 ${day.completed ? 'bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700' : 'bg-white dark:bg-slate-800 border-teal-100 dark:border-teal-900 shadow-sm'}`}>
              <div className={`w-12 h-12 rounded-full flex items-center justify-center shrink-0 ${day.completed ? 'bg-slate-200 dark:bg-slate-700 text-slate-400 dark:text-slate-500' : 'bg-teal-100 dark:bg-teal-900 text-teal-600 dark:text-teal-400'}`}>
                {day.completed ? <CheckCircle2 size={24}/> : <Zap size={24}/>}
              </div>
              <div className="flex-1">
                <div className="flex justify-between items-start mb-1">
                  <h3 className={`font-bold ${day.completed ? 'text-slate-500 dark:text-slate-500 line-through' : 'text-slate-800 dark:text-slate-100'}`}>{day.activity}</h3>
                  <span className="text-xs font-semibold text-slate-400 bg-slate-100 dark:bg-slate-700 px-2 py-0.5 rounded">{day.day}</span>
                </div>
                <p className="text-sm text-slate-500 dark:text-slate-400">{day.cbt}</p>
              </div>
              <button className="w-10 h-10 rounded-full bg-slate-50 dark:bg-slate-700 flex items-center justify-center hover:bg-slate-100 dark:hover:bg-slate-600 text-slate-400 transition-colors">
                <ChevronRight size={20} />
              </button>
            </div>
          ))}
        </div>
      </motion.div>

    </div>
  );
}

import React, { useState, useRef, useEffect } from 'react';
import { Mic, Send, Bot, User, AlertTriangle, ShieldCheck, Zap, Activity } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useStore } from '../store/useStore';
import { API_BASE_URL } from '../api/client';

// ── Severity config ──────────────────────────────────────────────────────────
const SEVERITY_CONFIG = {
  Normal:   { color: '#10b981', bg: 'rgba(16,185,129,0.12)', label: 'Normal',   icon: '✓', ring: '#10b981' },
  Mild:     { color: '#f59e0b', bg: 'rgba(245,158,11,0.12)', label: 'Mild',     icon: '!', ring: '#f59e0b' },
  Moderate: { color: '#f97316', bg: 'rgba(249,115,22,0.12)', label: 'Moderate', icon: '!!', ring: '#f97316' },
  Severe:   { color: '#ef4444', bg: 'rgba(239,68,68,0.15)',  label: 'Severe',   icon: '!!!', ring: '#ef4444' },
};

// ── Risk Pulse Indicator ─────────────────────────────────────────────────────
function RiskPulse({ label }) {
  const cfg = SEVERITY_CONFIG[label] || SEVERITY_CONFIG.Normal;
  if (label === 'Normal') return null;
  return (
    <motion.div
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold"
      style={{ backgroundColor: cfg.bg, color: cfg.color, border: `1px solid ${cfg.color}40` }}
    >
      <span className="relative flex h-2 w-2">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" style={{ backgroundColor: cfg.color }} />
        <span className="relative inline-flex rounded-full h-2 w-2" style={{ backgroundColor: cfg.color }} />
      </span>
      {cfg.label} Risk Detected
    </motion.div>
  );
}

// ── Confidence Bar ───────────────────────────────────────────────────────────
function ConfidenceBar({ confidence, label }) {
  const cfg = SEVERITY_CONFIG[label] || SEVERITY_CONFIG.Normal;
  return (
    <div className="mt-2">
      <div className="flex justify-between items-center mb-1">
        <span className="text-xs text-slate-400">AI Confidence</span>
        <span className="text-xs font-bold" style={{ color: cfg.color }}>{confidence}%</span>
      </div>
      <div className="h-1.5 bg-slate-200 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${confidence}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className="h-full rounded-full"
          style={{ backgroundColor: cfg.color }}
        />
      </div>
    </div>
  );
}

// ── Detector Vote Pills ──────────────────────────────────────────────────────
function DetectorVotes({ perDetector }) {
  if (!perDetector) return null;
  const detectors = [
    { key: 'lexicon', name: 'Lexicon' },
    { key: 'sentiment', name: 'Sentiment' },
    { key: 'knn', name: 'kNN Vector' },
  ];
  return (
    <div className="mt-2 flex flex-wrap gap-1.5">
      {detectors.map(d => {
        const result = perDetector[d.key];
        if (!result) return null;
        const cfg = SEVERITY_CONFIG[result.label] || SEVERITY_CONFIG.Normal;
        return (
          <span
            key={d.key}
            className="text-xs px-2 py-0.5 rounded-md font-medium"
            style={{ backgroundColor: cfg.bg, color: cfg.color, border: `1px solid ${cfg.color}30` }}
          >
            {d.name}: {result.label}
          </span>
        );
      })}
    </div>
  );
}

// ── Message Bubble ───────────────────────────────────────────────────────────
function MessageBubble({ m }) {
  const [showDetails, setShowDetails] = useState(false);
  const [completedTasks, setCompletedTasks] = useState({});
  const cfg = m.analysis ? (SEVERITY_CONFIG[m.analysis.predicted_class] || SEVERITY_CONFIG.Normal) : null;
  
  const handleTaskClick = (idx) => {
    setCompletedTasks(prev => ({ ...prev, [idx]: true }));
  };

  if (m.role === 'bot') {
    return (
      <motion.div
        initial={{ opacity: 0, y: 12, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ type: 'spring', stiffness: 300, damping: 25 }}
        className="flex gap-3 justify-start"
      >
        <div className="w-9 h-9 rounded-xl bg-slate-900 flex items-center justify-center shrink-0 mt-1">
          <Bot size={16} className="text-white" />
        </div>
        <div
          className="max-w-[78%] rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm"
          style={{
            background: '#ffffff',
            border: '1px solid #e2e8f0',
            color: '#1e293b'
          }}
        >
          <p className="text-sm leading-relaxed">{m.text}</p>
          {m.streaming && (
            <span className="inline-flex gap-0.5 ml-1 items-center">
              {[0, 1, 2].map(i => (
                <span key={i} className="w-1.5 h-1.5 bg-teal-400 rounded-full animate-bounce"
                  style={{ animationDelay: `${i * 100}ms` }} />
              ))}
            </span>
          )}

          {/* Render interactive tasks if provided */}
          {m.tasks && m.tasks.length > 0 && (
            <div className="mt-4 space-y-2">
              <p className="text-xs font-bold text-teal-700 uppercase tracking-wider mb-2">Suggested Actions</p>
              {m.tasks.map((task, idx) => (
                <div key={idx} className={`bg-white rounded-xl p-3 border shadow-sm flex items-center justify-between gap-3 transition-all ${completedTasks[idx] ? 'border-emerald-200 bg-emerald-50/30' : 'border-teal-100 hover:shadow-md cursor-pointer'}`} onClick={() => !completedTasks[idx] && handleTaskClick(idx)}>
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${completedTasks[idx] ? 'bg-emerald-100 text-emerald-600' : 'bg-teal-50 text-teal-600'}`}>
                      {completedTasks[idx] ? <ShieldCheck size={14}/> : (task.type === 'game' ? <Activity size={14}/> : <Zap size={14}/>)}
                    </div>
                    <div>
                      <h4 className={`text-sm font-bold leading-none mb-1 ${completedTasks[idx] ? 'text-emerald-700 line-through' : 'text-slate-700'}`}>{task.title}</h4>
                      <p className="text-xs text-slate-400">{task.time} • +{task.points} XP</p>
                    </div>
                  </div>
                  <button 
                    disabled={completedTasks[idx]}
                    className={`text-xs font-semibold px-3 py-1.5 rounded-lg transition-colors ${completedTasks[idx] ? 'text-emerald-600 bg-emerald-50' : 'text-teal-600 bg-teal-50 hover:bg-teal-100'}`}
                  >
                    {completedTasks[idx] ? 'Completed ✓' : 'Start'}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </motion.div>
    );
  }

  // User bubble
  return (
    <motion.div
      initial={{ opacity: 0, y: 12, x: 20 }}
      animate={{ opacity: 1, y: 0, x: 0 }}
      transition={{ type: 'spring', stiffness: 300, damping: 25 }}
      className="flex gap-3 justify-end"
    >
      <div className="max-w-[78%] flex flex-col items-end gap-2">
        {/* Main bubble */}
        <div
          className="rounded-2xl rounded-br-sm px-4 py-3 shadow-sm"
          style={{
            background: cfg && cfg.label !== 'Normal'
              ? '#0f766e'
              : '#0f766e',
            boxShadow: 'none',
          }}
        >
          {/* Token highlights */}
          {m.analysis?.shap_tokens?.length > 0 ? (
            <p className="text-sm leading-relaxed text-white">
              {m.analysis.shap_tokens.map((t, idx) => (
                <span
                  key={idx}
                  className="transition-all"
                  style={{
                    backgroundColor: t.weight > 0.3 ? 'rgba(255,255,255,0.25)' : 'transparent',
                    borderRadius: t.weight > 0.3 ? '4px' : '0',
                    padding: t.weight > 0.3 ? '0 3px' : '0',
                    fontWeight: t.weight > 0.3 ? '700' : '400',
                    textDecoration: t.weight > 0.5 ? 'underline' : 'none',
                    textDecorationStyle: 'dotted',
                  }}
                >
                  {t.text}
                </span>
              ))}
            </p>
          ) : (
            <p className="text-sm leading-relaxed text-white">{m.text}</p>
          )}
        </div>

        {/* Analysis card (non-Normal only) */}
        {m.analysis && m.analysis.predicted_class !== 'Normal' && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="w-full rounded-xl p-3 text-xs"
            style={{
              backgroundColor: cfg?.bg,
              border: `1px solid ${cfg?.color}30`,
            }}
          >
            <div className="flex items-center justify-between mb-2">
              <RiskPulse label={m.analysis.predicted_class} />
              <button
                onClick={() => setShowDetails(!showDetails)}
                className="text-xs underline opacity-60 hover:opacity-100"
                style={{ color: cfg?.color }}
              >
                {showDetails ? 'Less' : 'Why?'}
              </button>
            </div>

            <ConfidenceBar confidence={m.analysis.confidence} label={m.analysis.predicted_class} />

            {showDetails && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-3 space-y-2"
              >
                <DetectorVotes perDetector={m.analysis.per_detector_results} />
                {m.analysis.evidence?.length > 0 && (
                  <div className="mt-2 space-y-1">
                    {m.analysis.evidence.slice(0, 3).map((ev, i) => (
                      <p key={i} className="opacity-70 text-xs" style={{ color: cfg?.color }}>• {ev}</p>
                    ))}
                  </div>
                )}
                {m.analysis.tone_context?.negated && (
                  <p className="text-xs text-emerald-600 font-medium">✓ Negation detected — severity capped</p>
                )}
                <p className="text-xs opacity-40 italic">*Possible indicator only. Not a clinical diagnosis.</p>
              </motion.div>
            )}
          </motion.div>
        )}

        {/* Normal badge */}
        {m.analysis && m.analysis.predicted_class === 'Normal' && (
          <div className="flex items-center gap-1 text-xs text-emerald-500 px-2">
            <ShieldCheck size={12} />
            <span>No risk indicators detected</span>
          </div>
        )}
      </div>

      <div className="w-9 h-9 rounded-2xl bg-gradient-to-br from-slate-300 to-slate-400 dark:from-slate-600 dark:to-slate-700 flex items-center justify-center shrink-0 mt-1">
        <User size={16} className="text-slate-600 dark:text-slate-200" />
      </div>
    </motion.div>
  );
}

// ── Live Risk Header Bar ─────────────────────────────────────────────────────
function LiveRiskBar({ currentRisk }) {
  const cfg = SEVERITY_CONFIG[currentRisk] || SEVERITY_CONFIG.Normal;
  const levels = ['Normal', 'Mild', 'Moderate', 'Severe'];
  const idx = levels.indexOf(currentRisk);
  return (
    <div className="px-5 py-3 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 flex items-center gap-3">
      <Activity size={14} className="text-slate-400 shrink-0" />
      <div className="flex-1 flex items-center gap-1">
        {levels.map((l, i) => (
          <div
            key={l}
            className="flex-1 h-1.5 rounded-full transition-all duration-700"
            style={{
              backgroundColor: i <= idx
                ? (SEVERITY_CONFIG[l]?.color || '#94a3b8')
                : 'rgba(0,0,0,0.08)',
              opacity: i <= idx ? 1 : 0.3,
            }}
          />
        ))}
      </div>
      <span className="text-xs font-semibold shrink-0" style={{ color: cfg.color }}>
        {currentRisk}
      </span>
    </div>
  );
}

// ── Main Page ────────────────────────────────────────────────────────────────
export default function AnalyzePage() {
  const { setCrisisMode } = useStore();
  const [messages, setMessages] = useState([{
    role: 'bot',
    text: 'வணக்கம் 🙏 I am MindGuard. I understand both English and Tanglish. How are you feeling today?'
  }]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentRisk, setCurrentRisk] = useState('Normal');
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSend = async (textOverride) => {
    const textToSend = textOverride || input;
    if (!textToSend.trim() || isTyping) return;

    setMessages(prev => [...prev, { role: 'user', text: textToSend }]);
    setInput('');
    setIsTyping(true);

    try {
      // 1. Analyze severity
      const analyzeRes = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: 'demo_user_001', text: textToSend })
      });
      const analysis = await analyzeRes.json();

      setCurrentRisk(analysis.predicted_class || 'Normal');

      // Attach analysis to the last user message
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1].analysis = analysis;
        return updated;
      });

      // Crisis gate
      if (analysis.predicted_class === 'Severe' && analysis.confidence >= 40) {
        setIsTyping(false);
        setCrisisMode(true);
        return;
      }

      // Out-of-scope
      if (analysis.status && analysis.status !== 'ok' && analysis.message) {
        setMessages(prev => [...prev, { role: 'bot', text: analysis.message }]);
        setIsTyping(false);
        return;
      }

      // 2. Stream chat response
      setMessages(prev => [...prev, { role: 'bot', text: '', streaming: true }]);
      const chatReq = await fetch(`${API_BASE_URL}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: 'demo_user_001', text: textToSend, severity: analysis.predicted_class })
      });

      if (!chatReq.ok || !chatReq.body) {
        throw new Error(`Chat service unavailable (${chatReq.status})`);
      }

      const reader = chatReq.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let botResponse = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        for (const line of chunk.split('\n')) {
          if (line.startsWith('data: ')) {
            const dataStr = line.replace('data: ', '');
            if (dataStr.trim() === '[DONE]') break;
            try {
              const data = JSON.parse(dataStr);
              if (data.chunk) {
                botResponse += data.chunk;
                setMessages(prev => {
                  const updated = [...prev];
                  updated[updated.length - 1].text = botResponse;
                  return updated;
                });
              }
            } catch (e) {}
          }
        }
      }

      setMessages(prev => {
        const updated = [...prev];
        const lastMsg = updated[updated.length - 1];
        lastMsg.streaming = false;
        
        // Inject dynamic tasks based on severity
        if (analysis.predicted_class === 'Mild') {
          lastMsg.tasks = [
            { type: 'routine', title: '5-Minute Box Breathing', points: 20, time: '5 mins' },
            { type: 'game', title: 'Cognitive Bubble Pop', points: 50, time: '3 mins' }
          ];
        } else if (analysis.predicted_class === 'Moderate') {
          lastMsg.tasks = [
            { type: 'routine', title: 'Write 1 thing you liked today', points: 80, time: '2 mins' },
            { type: 'quest', title: 'Drink a Glass of Water', points: 20, time: '1 min' }
          ];
        }
        
        return updated;
      });
    } catch (e) {
      console.error(e);
      setMessages(prev => [...prev, { role: 'bot', text: 'Sorry, I could not connect to the server. Please make sure the backend is running.' }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <section className="grid gap-5 rounded-2xl bg-[#e0eee9] px-6 py-7 sm:px-8 md:grid-cols-[1fr_auto] md:items-end">
        <div><p className="text-xs font-bold uppercase tracking-[0.16em] text-[#0f625b]">Daily check-in</p><h1 className="mt-3 font-serif text-3xl font-semibold tracking-[-0.04em] text-[#142136] sm:text-4xl">Make room for how you feel.</h1><p className="mt-3 max-w-xl text-[15px] leading-6 text-[#405266]">Share a thought in English or Tanglish. MindGuard helps you pause, understand it, and choose a small next step.</p></div>
        <div className="flex items-center gap-2 rounded-xl border border-[#b9d8cf] bg-white px-3 py-2 text-xs font-bold text-[#285b55]"><ShieldCheck size={15} /> Private & judgment-free</div>
      </section>
      <div className="flex h-[min(650px,calc(100vh-15rem))] min-h-[500px] flex-col overflow-hidden rounded-2xl border border-[#dbe3e8] bg-white shadow-[0_2px_12px_rgba(15,34,52,0.05)]">
      <div className="flex items-center justify-between border-b border-[#e6ebef] px-5 py-4 sm:px-6"><div><h2 className="font-bold text-[#152033]">Your check-in</h2><p className="mt-0.5 text-xs text-[#526273]">Take your time. There is no right way to start.</p></div><span className="hidden rounded-full bg-[#edf7f4] px-3 py-1.5 text-xs font-bold text-[#0f625b] sm:block">English + Tanglish</span></div>
      {/* Live Risk Bar */}
      <LiveRiskBar currentRisk={currentRisk} />

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-5 scroll-smooth">
        <AnimatePresence initial={false}>
          {messages.map((m, i) => (
            <MessageBubble key={i} m={m} />
          ))}
        </AnimatePresence>

        {/* Typing indicator */}
        <AnimatePresence>
          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 8 }}
              className="flex gap-3 justify-start"
            >
              <div className="w-9 h-9 rounded-2xl bg-gradient-to-br from-teal-400 to-teal-600 flex items-center justify-center shadow-lg shadow-teal-500/30 shrink-0">
                <Bot size={16} className="text-white" />
              </div>
              <div className="rounded-xl border border-slate-200 bg-white px-5 py-4 flex gap-1.5 items-center shadow-sm">
                {[0, 1, 2].map(i => (
                  <span key={i} className="w-2 h-2 bg-teal-400 rounded-full animate-bounce"
                    style={{ animationDelay: `${i * 120}ms` }} />
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div ref={endRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-[#e6ebef] bg-[#f6f8f9] px-4 pb-4 pt-3">
        {/* Input bar */}
        <div
          className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white p-2 shadow-sm"
          style={{
            background: '#ffffff',
          }}
        >
          <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-700 flex items-center justify-center shrink-0">
            <Zap size={14} />
          </div>
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend()}
            placeholder="Type in English or Tanglish..."
            className="flex-1 bg-transparent border-0 focus:ring-0 text-sm font-medium outline-none text-slate-800 placeholder:text-slate-400"
            disabled={isTyping}
          />
          <motion.button
            onClick={() => handleSend()}
            disabled={!input.trim() || isTyping}
            whileTap={{ scale: 0.9 }}
            whileHover={{ scale: 1.05 }}
            className="w-9 h-9 rounded-xl flex items-center justify-center transition-all disabled:opacity-40"
            style={{ background: input.trim() ? '#0f766e' : '#e2e8f0', boxShadow: 'none' }}
          >
            <Send size={15} className={input.trim() ? 'text-white ml-0.5' : 'text-slate-400 ml-0.5'} />
          </motion.button>
        </div>

        <p className="text-center text-xs text-[#627386] mt-2">
          Your note is analysed privately • MindGuard is not a substitute for professional care
        </p>
      </div>
      </div>
    </div>
  );
}

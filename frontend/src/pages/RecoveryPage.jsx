import { motion, AnimatePresence } from 'framer-motion';
import { Target, CheckCircle, RefreshCcw, Sparkles, Wind } from 'lucide-react';

import { useQuests } from '../hooks/useQuests';
import { useBreathing } from '../hooks/useBreathing';
import { SESSION_ID } from '../store/sessionStore';

export default function RecoveryPage() {
  const { pendingQuests, completedQuests, isGenerating, handleGenerate, handleComplete } = useQuests(SESSION_ID);
  const breathPhase = useBreathing();

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="grid grid-cols-1 lg:grid-cols-2 gap-8 pb-10"
    >
      {/* Left Column: Gamified Quests */}
      <div className="flex flex-col gap-6">
        <section className="glass-card">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-navy flex items-center gap-2">
              <Target className="text-coral" /> Active Quests
            </h2>
            <button 
              onClick={handleGenerate} 
              disabled={isGenerating}
              className="btn-primary flex items-center gap-2 px-4 py-2 text-sm bg-gradient-to-r from-teal to-cyan"
            >
              {isGenerating ? <RefreshCcw size={16} className="animate-spin" /> : <Sparkles size={16} />}
              {isGenerating ? 'Generating...' : 'New Quest'}
            </button>
          </div>
          
          <AnimatePresence>
            {pendingQuests.length === 0 ? (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-slate-600 text-center py-8 bg-slate-50 rounded-xl border border-dashed border-slate-200">
                You have no active quests! Click 'New Quest' to get an AI-generated recovery activity.
              </motion.div>
            ) : (
              <div className="flex flex-col gap-4">
                {pendingQuests.map((quest) => (
                  <motion.div 
                    key={quest.id}
                    initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, scale: 0.95 }}
                    className="p-5 rounded-xl border border-coral/30 bg-gradient-to-br from-white to-coral/5 shadow-md flex justify-between items-center gap-4 group hover:border-coral/60 transition-colors"
                  >
                    <p className="text-slate-800 font-medium leading-relaxed">{quest.quest_text}</p>
                    <button 
                      onClick={() => handleComplete(quest.id)}
                      className="flex-shrink-0 w-10 h-10 rounded-full bg-white border-2 border-coral text-coral flex items-center justify-center hover:bg-coral hover:text-white transition-all shadow-sm"
                    >
                      <CheckCircle size={20} />
                    </button>
                  </motion.div>
                ))}
              </div>
            )}
          </AnimatePresence>
        </section>

        {completedQuests.length > 0 && (
          <section className="glass-card opacity-80">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4">Completed Quests ({completedQuests.length})</h3>
            <div className="flex flex-col gap-3">
              {completedQuests.map(quest => (
                <div key={quest.id} className="p-4 rounded-lg bg-emerald-50/50 border border-emerald-100 flex items-center gap-3 text-emerald-800">
                  <CheckCircle size={18} className="text-emerald-500" />
                  <span className="text-sm line-through opacity-70">{quest.quest_text}</span>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>

      {/* Right Column: Breathing */}
      <div className="flex flex-col gap-6">
        <section className="glass-card flex flex-col items-center justify-center text-center p-10 min-h-[400px]">
          <h2 className="text-2xl font-bold text-navy mb-2 flex items-center gap-2">
            <Wind className="text-cyan" /> 4-7-8 Breathing
          </h2>
          <p className="text-slate-500 mb-12">Sync your breath with the circle to rapidly reduce anxiety.</p>
          
          <div className="relative w-64 h-64 flex items-center justify-center">
            <motion.div 
              animate={{
                scale: breathPhase === 'Inhale' ? 1.5 : breathPhase === 'Hold' ? 1.5 : 1,
                opacity: breathPhase === 'Inhale' ? 0.8 : breathPhase === 'Hold' ? 0.6 : 0.3,
                backgroundColor: breathPhase === 'Inhale' ? '#00BCD4' : breathPhase === 'Hold' ? '#33A095' : '#00897B'
              }}
              transition={{
                duration: breathPhase === 'Inhale' ? 4 : breathPhase === 'Hold' ? 7 : 8,
                ease: "easeInOut"
              }}
              className="absolute w-40 h-40 rounded-full blur-xl"
            />
            <div className="relative z-10 w-40 h-40 bg-white rounded-full shadow-lg border border-slate-200 flex flex-col items-center justify-center">
              <span className="text-3xl font-extrabold text-navy tracking-tight">{breathPhase}</span>
              <span className="text-xs font-bold text-slate-400 uppercase mt-1">
                {breathPhase === 'Inhale' ? '4 Seconds' : breathPhase === 'Hold' ? '7 Seconds' : '8 Seconds'}
              </span>
            </div>
          </div>
        </section>
      </div>
    </motion.div>
  );
}

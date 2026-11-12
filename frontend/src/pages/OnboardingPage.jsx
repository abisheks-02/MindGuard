import React, { useState } from 'react';
import { useStore } from '../store/useStore';
import { useNavigate } from 'react-router-dom';
import { Shield, Lock, Bell, Globe } from 'lucide-react';
import { API_BASE_URL } from '../api/client';

export default function OnboardingPage() {
  const { setLanguage, updateConsents, completeOnboarding } = useStore();
  const navigate = useNavigate();
  
  const [step, setStep] = useState(1);
  const [lang, setLang] = useState('en');
  const [consents, setConsents] = useState({
    support_messages: false,
    notify_trusted: false,
    research_data: false
  });

  const handleFinish = async () => {
    setLanguage(lang);
    updateConsents(consents);
    
    // In production, we'd POST this to the backend /api/v1/onboarding/consent
    try {
      await fetch(`${API_BASE_URL}/onboarding/consent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'demo_user_001',
          ...consents
        })
      });
    } catch (e) {
      console.warn("Backend not reachable, saving locally", e);
    }
    
    completeOnboarding();
    navigate('/');
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="glass-card max-w-lg w-full">
        <div className="p-6 bg-white dark:bg-slate-900 rounded-xl">
          
          {step === 1 && (
            <div className="space-y-6 animate-in fade-in zoom-in duration-500">
              <div className="text-center">
                <Globe className="w-12 h-12 text-teal mx-auto mb-4" />
                <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100">Welcome to MindGuard</h1>
                <p className="text-slate-600 dark:text-slate-300 mt-2">Choose your preferred language</p>
              </div>
              
              <div className="grid gap-3">
                {['en', 'ta', 'tanglish'].map((l) => (
                  <button
                    key={l}
                    onClick={() => setLang(l)}
                    className={`p-4 rounded-xl border-2 transition-colors ${lang === l ? 'border-teal bg-teal/10' : 'border-slate-200 bg-white hover:bg-slate-50'}`}
                  >
                    <span className="font-semibold capitalize text-slate-800 dark:text-slate-100">{l === 'en' ? 'English' : l === 'ta' ? 'தமிழ் (Tamil)' : 'Tanglish'}</span>
                  </button>
                ))}
              </div>
              
              <button onClick={() => setStep(2)} className="btn-primary w-full mt-8">Continue</button>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right duration-500">
              <div className="text-center">
                <Shield className="w-12 h-12 text-teal mx-auto mb-4" />
                <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100">Your Privacy, Your Rules</h1>
                <p className="text-slate-600 dark:text-slate-300 mt-2">MindGuard analyzes your text locally or privately. Please review the following permissions.</p>
              </div>

              <div className="space-y-4">
                <label className="flex items-start space-x-4 p-4 glass-panel cursor-pointer hover:bg-slate-50 transition-colors">
                  <input type="checkbox" checked={consents.support_messages} onChange={(e) => setConsents({...consents, support_messages: e.target.checked})} className="mt-1 w-5 h-5 text-teal rounded focus:ring-teal" />
                  <div>
                    <p className="font-semibold text-slate-800 dark:text-slate-100 flex items-center gap-2"><Bell size={16}/> Send me support messages</p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">Receive SMS helplines if we detect severe distress.</p>
                  </div>
                </label>

                <label className="flex items-start space-x-4 p-4 glass-panel cursor-pointer hover:bg-slate-50 transition-colors">
                  <input type="checkbox" checked={consents.notify_trusted} onChange={(e) => setConsents({...consents, notify_trusted: e.target.checked})} className="mt-1 w-5 h-5 text-teal rounded focus:ring-teal" />
                  <div>
                    <p className="font-semibold text-slate-800 dark:text-slate-100 flex items-center gap-2"><Lock size={16}/> Notify Trusted Contact</p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">Alert your designated contact if you are in a crisis. (You can add one later in Settings).</p>
                  </div>
                </label>

                <label className="flex items-start space-x-4 p-4 glass-panel cursor-pointer hover:bg-slate-50 transition-colors">
                  <input type="checkbox" checked={consents.research_data} onChange={(e) => setConsents({...consents, research_data: e.target.checked})} className="mt-1 w-5 h-5 text-teal rounded focus:ring-teal" />
                  <div>
                    <p className="font-semibold text-slate-800 dark:text-slate-100 flex items-center gap-2"><Globe size={16}/> Allow Anonymous Research</p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">Help improve mental health AI by sharing anonymized linguistic patterns.</p>
                  </div>
                </label>
              </div>

              <div className="flex gap-4 mt-8">
                <button onClick={() => setStep(1)} className="px-6 py-2.5 rounded-xl font-semibold text-slate-600 bg-slate-200 dark:bg-slate-700 dark:text-slate-300 hover:bg-slate-300 dark:hover:bg-slate-600 transition-colors">Back</button>
                <button onClick={handleFinish} className="btn-primary flex-1">Complete Setup</button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

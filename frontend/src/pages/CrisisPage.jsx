import React, { useEffect, useState } from 'react';
import { PhoneCall, Heart, Wind, ShieldCheck } from 'lucide-react';
import { motion } from 'framer-motion';
import { useStore } from '../store/useStore';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../api/client';

export default function CrisisPage() {
  const { setCrisisMode } = useStore();
  const navigate = useNavigate();
  const [timeLeft, setTimeLeft] = useState(60);
  
  const helplines = [
    { name: "Tele-MANAS", number: "14416", color: "bg-teal-500" },
    { name: "iCall", number: "9152987821", color: "bg-sky-500" },
    { name: "Vandrevala", number: "9999666555", color: "bg-indigo-500" },
    { name: "Emergency", number: "112", color: "bg-red-500" }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft(t => Math.max(0, t - 1));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const handleSafe = async () => {
    try {
      await fetch(`${API_BASE_URL}/escalation/cancel?user_id=demo_user_001`, { method: 'POST' });
    } catch (e) {}
    setCrisisMode(false);
    navigate('/');
  };

  return (
    <div className="fixed inset-0 z-50 bg-[#F0FDF4] dark:bg-[#022C22] flex flex-col items-center justify-center p-6 overflow-y-auto">
      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }} 
        animate={{ opacity: 1, scale: 1 }} 
        className="max-w-2xl w-full text-center space-y-8"
      >
        <div className="flex justify-center mb-8">
          <motion.div 
            animate={{ scale: [1, 1.2, 1] }} 
            transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
            className="w-32 h-32 bg-emerald-100 dark:bg-emerald-800/40 rounded-full flex items-center justify-center"
          >
            <Heart className="w-16 h-16 text-emerald-600 dark:text-emerald-400" />
          </motion.div>
        </div>

        <h1 className="text-4xl font-extrabold text-emerald-900 dark:text-emerald-100">You are not alone.</h1>
        <p className="text-xl text-emerald-700 dark:text-emerald-300 font-medium max-w-lg mx-auto">
          We noticed you might be going through a very difficult time right now. Professional help is available 24/7.
        </p>

        <div className="grid md:grid-cols-2 gap-4 mt-8 w-full max-w-lg mx-auto">
          {helplines.map((h, i) => (
            <a 
              href={`tel:${h.number}`} 
              key={i}
              className={`${h.color} text-white p-4 rounded-2xl flex items-center justify-center gap-3 font-bold text-lg hover:brightness-110 transition-all shadow-lg hover:shadow-xl hover:-translate-y-1`}
            >
              <PhoneCall size={24} /> {h.name}
            </a>
          ))}
        </div>

        <div className="mt-12 bg-white border border-slate-200 p-6 rounded-2xl max-w-lg mx-auto shadow-sm">
          <p className="text-emerald-800 dark:text-emerald-200 mb-4 font-semibold">
            {timeLeft > 0 ? `We will notify your trusted contact in ${timeLeft}s unless you cancel.` : "Trusted contact notified."}
          </p>
          <button 
            onClick={handleSafe}
            className="w-full bg-emerald-100 hover:bg-emerald-200 dark:bg-emerald-900 dark:hover:bg-emerald-800 text-emerald-800 dark:text-emerald-100 py-4 rounded-xl font-bold flex items-center justify-center gap-2 transition-colors"
          >
            <ShieldCheck size={20} /> I am safe right now (Cancel Alert)
          </button>
        </div>
      </motion.div>
    </div>
  );
}

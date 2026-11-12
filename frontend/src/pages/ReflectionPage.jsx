import { useEffect, useState } from 'react';
import { Check, Moon, Sparkles, Sun } from 'lucide-react';

const storageKey = 'mindguard-weekly-reflection';

function Scale({ label, value, onChange, low, high }) {
  return <div><div className="mb-3 flex items-center justify-between"><label className="text-sm font-bold text-[#334155]">{label}</label><span className="rounded-full bg-[#edf7f4] px-2.5 py-1 text-xs font-bold text-[#0f625b]">{value}/5</span></div><input type="range" min="1" max="5" value={value} onChange={e => onChange(Number(e.target.value))} className="w-full accent-[#0f625b]" /><div className="mt-1 flex justify-between text-xs text-[#68798a]"><span>{low}</span><span>{high}</span></div></div>;
}

export default function ReflectionPage() {
  const [form, setForm] = useState({ mood: 3, energy: 3, sleep: 3, highlight: '', intention: '' });
  const [saved, setSaved] = useState(false);
  useEffect(() => { try { const value = localStorage.getItem(storageKey); if (value) setForm(JSON.parse(value)); } catch {} }, []);
  const update = (key, value) => { setForm(current => ({ ...current, [key]: value })); setSaved(false); };
  const save = () => { localStorage.setItem(storageKey, JSON.stringify({ ...form, savedAt: new Date().toISOString() })); setSaved(true); };

  return <div className="mx-auto max-w-4xl"><section className="rounded-2xl bg-[#f7ebdf] px-6 py-8 sm:px-8"><p className="tool-kicker text-[#9a5625]">Weekly reflection</p><h1 className="mt-2 text-4xl font-bold tracking-[-.045em] text-[#142136]">Notice what your week held.</h1><p className="mt-3 max-w-2xl text-[15px] leading-7 text-[#5f5148]">A few quiet prompts to help you spot what supported you and choose a gentle direction for next week.</p></section><section className="mt-7 rounded-2xl border border-[#dbe3e8] bg-white p-6 sm:p-8"><div className="grid gap-7 md:grid-cols-3"><Scale label="Overall mood" value={form.mood} onChange={value => update('mood', value)} low="Very low" high="Steady" /><Scale label="Energy" value={form.energy} onChange={value => update('energy', value)} low="Drained" high="Restored" /><Scale label="Sleep quality" value={form.sleep} onChange={value => update('sleep', value)} low="Restless" high="Restful" /></div><div className="mt-9 grid gap-6 md:grid-cols-2"><label className="tool-label"><span className="flex items-center gap-2"><Sparkles size={16} className="text-[#9a5625]" /> One thing that helped</span><textarea value={form.highlight} onChange={e => update('highlight', e.target.value)} className="tool-textarea" placeholder="A person, habit, moment, or place…" /></label><label className="tool-label"><span className="flex items-center gap-2"><Sun size={16} className="text-[#9a5625]" /> A gentle intention for next week</span><textarea value={form.intention} onChange={e => update('intention', e.target.value)} className="tool-textarea" placeholder="For example: take a short break after work." /></label></div><div className="mt-7 flex flex-wrap items-center justify-between gap-3 border-t border-[#e6ebef] pt-6"><p className="inline-flex items-center gap-2 text-sm text-[#526273]"><Moon size={16} /> Saved only in this browser.</p><button className="btn-primary" onClick={save}>{saved ? <><Check size={17} /> Reflection saved</> : 'Save reflection'}</button></div></section></div>;
}

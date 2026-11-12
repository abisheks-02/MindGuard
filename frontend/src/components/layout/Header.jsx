import { Link, useLocation } from 'react-router-dom';
import { Activity, BarChart3, Compass, HeartPulse, Settings, ShieldCheck, Sparkles, LayoutGrid, NotebookPen } from 'lucide-react';

const navItems = [
  { to: '/discover', label: 'Explore', icon: LayoutGrid },
  { to: '/', label: 'Check in', icon: HeartPulse },
  { to: '/journey', label: 'Journey', icon: Compass },
  { to: '/tools', label: 'Tools', icon: Sparkles },
  { to: '/reflection', label: 'Reflection', icon: NotebookPen },
  { to: '/intervention', label: 'Support plan', icon: Activity },
];

function Brand() {
  return <div className="flex items-center gap-3"><div className="grid h-10 w-10 place-items-center rounded-xl bg-[#c8f1e7] text-[#0d4f4a]"><ShieldCheck size={21} strokeWidth={2.4} /></div><div><p className="font-serif text-xl font-bold tracking-[-0.04em] text-white">MindGuard</p><p className="text-[11px] font-medium text-slate-400">A space for your wellbeing</p></div></div>;
}

export default function Header() {
  const { pathname } = useLocation();
  const active = (to) => pathname === to;
  const navClass = (to) => `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-semibold transition-colors ${active(to) ? 'bg-white text-[#142136] shadow-sm' : 'text-slate-300 hover:bg-[#223249] hover:text-white'}`;

  return <>
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-72 flex-col bg-[#142136] px-4 py-6 lg:flex">
      <Link to="/" className="px-2"><Brand /></Link>
      <p className="mt-12 px-3 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-500">Your space</p>
      <nav className="mt-3 space-y-1">{navItems.map(({ to, label, icon: Icon }) => <Link key={to} to={to} className={navClass(to)}><Icon size={18} strokeWidth={2} />{label}</Link>)}</nav>
      <div className="mt-auto border-t border-white/10 pt-4">
        <p className="mb-2 px-3 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-500">Account</p>
        <Link to="/dashboard" className={navClass('/dashboard')}><BarChart3 size={18} />Clinical view</Link>
        <Link to="/settings" className={navClass('/settings')}><Settings size={18} />Settings</Link>
      </div>
      <div className="mx-2 mt-5 rounded-xl border border-[#31425a] bg-[#1c2b40] p-3"><p className="text-xs font-semibold text-white">A calmer pace</p><p className="mt-1 text-xs leading-5 text-slate-300">Choose a tool when you need a brief pause.</p></div>
    </aside>
    <header className="sticky top-0 z-30 border-b border-[#223249] bg-[#142136] lg:hidden">
      <div className="flex h-16 items-center justify-between px-5"><Link to="/"><Brand /></Link><div className="rounded-full border border-[#315b55] bg-[#1b3a38] px-3 py-1.5 text-xs font-bold text-emerald-200">Private</div></div>
      <nav className="flex gap-1 overflow-x-auto px-3 pb-3">{navItems.map(({ to, label, icon: Icon }) => <Link key={to} to={to} className={`flex shrink-0 items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-bold ${active(to) ? 'bg-white text-[#142136]' : 'text-slate-300'}`}><Icon size={15} />{label}</Link>)}<Link to="/settings" className={`flex shrink-0 items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-bold ${active('/settings') ? 'bg-white text-[#142136]' : 'text-slate-300'}`}><Settings size={15} />More</Link></nav>
    </header>
  </>;
}

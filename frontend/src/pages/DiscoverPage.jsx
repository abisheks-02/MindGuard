import { Link } from 'react-router-dom';
import { Compass, HeartHandshake, HeartPulse, LockKeyhole, Settings, Sparkles, NotebookPen } from 'lucide-react';

const features = [
  { to: '/', icon: HeartPulse, title: 'Daily check-in', detail: 'Write what is on your mind in English or Tanglish and receive a supportive response.', color: 'bg-[#e0eee9] text-[#0f625b]', action: 'Start a check-in' },
  { to: '/tools', icon: Sparkles, title: 'Wellbeing tools & games', detail: 'Try breathing, grounding, reflection, gratitude, and short mindful games.', color: 'bg-[#e7eef8] text-[#315c99]', action: 'Explore tools' },
  { to: '/journey', icon: Compass, title: 'My journey', detail: 'Review check-ins, notice patterns, and build a gentle weekly rhythm.', color: 'bg-[#f7ebdf] text-[#9a5625]', action: 'View journey' },
  { to: '/intervention', icon: HeartHandshake, title: 'Personal support plan', detail: 'Save your own reminders, next steps, and people you may want to reach.', color: 'bg-[#f3e7f2] text-[#824477]', action: 'Create a plan' },
  { to: '/reflection', icon: NotebookPen, title: 'Weekly reflection', detail: 'Record your mood, energy, sleep, a helpful moment, and a gentle intention.', color: 'bg-[#f7ebdf] text-[#9a5625]', action: 'Reflect on your week' },
  { to: '/settings', icon: Settings, title: 'Preferences', detail: 'Manage your language, consent choices, data options, and trusted contacts.', color: 'bg-[#eceef1] text-[#46576a]', action: 'Open settings' },
  { to: '/settings', icon: LockKeyhole, title: 'Privacy controls', detail: 'Review how MindGuard uses your data and export your information.', color: 'bg-[#edf7f4] text-[#0f625b]', action: 'Review privacy' },
];

export default function DiscoverPage() {
  return <div className="mx-auto max-w-5xl"><section className="rounded-2xl bg-[#e0eee9] px-6 py-9 sm:px-8"><p className="tool-kicker">Explore MindGuard</p><h1 className="mt-2 text-4xl font-bold tracking-[-.045em] text-[#142136]">Support, one feature at a time.</h1><p className="mt-3 max-w-2xl text-[15px] leading-7 text-[#405266]">Everything in MindGuard is optional. Choose the tool that feels useful today and leave the rest for another time.</p></section><div className="mt-7 grid gap-4 sm:grid-cols-2">{features.map(({ to, icon: Icon, title, detail, color, action }) => <Link key={title} to={to} className="group rounded-2xl border border-[#dbe3e8] bg-white p-5 transition-all hover:-translate-y-0.5 hover:border-[#9ccfc3] hover:shadow-[0_5px_18px_rgba(15,34,52,.08)]"><span className={`grid h-11 w-11 place-items-center rounded-xl ${color}`}><Icon size={21} /></span><h2 className="mt-5 text-lg font-bold text-[#152033]">{title}</h2><p className="mt-1 text-sm leading-6 text-[#526273]">{detail}</p><span className="mt-5 inline-block text-sm font-bold text-[#0f625b]">{action} →</span></Link>)}</div></div>;
}

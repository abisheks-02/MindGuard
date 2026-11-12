import { useMemo, useState } from 'react';
import { ArrowLeft, Brain, Check, ChevronRight, CircleDot, Heart, PenLine, Sparkles, Timer, Wind } from 'lucide-react';

const TOOL_LIST = [
  { id: 'breathe', name: 'Steady breathing', time: '2 min', icon: Wind, color: 'bg-[#e0eee9] text-[#0f625b]', description: 'Follow a slow, simple rhythm.' },
  { id: 'ground', name: 'Grounding guide', time: '3 min', icon: Brain, color: 'bg-[#e7eef8] text-[#315c99]', description: 'Notice what is around you, one sense at a time.' },
  { id: 'reset', name: 'Thought reset', time: '4 min', icon: Sparkles, color: 'bg-[#f7ebdf] text-[#9a5625]', description: 'Create a kinder, more balanced response.' },
  { id: 'gratitude', name: 'Good things', time: '2 min', icon: Heart, color: 'bg-[#f3e7f2] text-[#824477]', description: 'Capture a few moments worth keeping.' },
];

const GAME_LIST = [
  { id: 'focus', name: 'Focus match', time: '1 min', icon: CircleDot, color: 'bg-[#e7eef8] text-[#315c99]', description: 'Find the one tile that is different. Reset your attention, one round at a time.' },
  { id: 'count', name: 'Quiet count', time: '1 min', icon: Sparkles, color: 'bg-[#f7ebdf] text-[#9a5625]', description: 'Count slowly and tap when your attention wanders back.' },
];

function BreathingTool() {
  const [active, setActive] = useState(false);
  const [rounds, setRounds] = useState(0);
  const [phase, setPhase] = useState('Ready');
  const start = () => {
    setActive(true); setPhase('Breathe in');
    window.setTimeout(() => setPhase('Hold gently'), 4000);
    window.setTimeout(() => setPhase('Breathe out'), 7000);
    window.setTimeout(() => { setPhase('Ready'); setRounds(value => value + 1); setActive(false); }, 12000);
  };
  return <div className="grid gap-8 md:grid-cols-[.9fr_1.1fr] md:items-center"><div><p className="tool-kicker">Two-minute practice</p><h2 className="tool-title">Find a slower rhythm.</h2><p className="tool-copy">Let your shoulders soften. Breathe in slowly, pause, then make the exhale longer and gentler.</p><button className="btn-primary mt-6" disabled={active} onClick={start}>{active ? 'Breathing with you…' : 'Start one round'}</button><p className="mt-4 text-sm text-[#526273]">Completed rounds: <strong className="text-[#152033]">{rounds}</strong></p></div><div className="grid min-h-64 place-items-center rounded-2xl bg-[#edf7f4] p-8"><div className={`grid h-44 w-44 place-items-center rounded-full border-[14px] border-white bg-[#bfe8da] text-center shadow-sm transition-all duration-[4000ms] ${phase === 'Breathe in' ? 'scale-110' : phase === 'Breathe out' ? 'scale-90' : 'scale-100'}`}><div><p className="text-lg font-bold text-[#0d4f4a]">{phase}</p><p className="mt-1 text-xs font-semibold text-[#3c746b]">{active ? 'Stay with the pace' : 'Tap to begin'}</p></div></div></div></div>;
}

function GroundingTool() {
  const steps = ['5 things you can see', '4 things you can feel', '3 things you can hear', '2 things you can smell', '1 thing you can taste'];
  const [index, setIndex] = useState(0);
  const complete = index === steps.length;
  return <div className="mx-auto max-w-2xl text-center"><p className="tool-kicker">5–4–3–2–1 grounding</p><h2 className="tool-title">Come back to this moment.</h2><p className="mx-auto mt-3 max-w-lg text-[15px] leading-7 text-[#526273]">There is nothing to solve right now. Slowly name what you notice around you.</p><div className="my-8 rounded-2xl border border-[#dbe3e8] bg-[#f8fafb] p-7"><p className="text-xs font-bold uppercase tracking-[.14em] text-[#68798a]">Step {Math.min(index + 1, 5)} of 5</p><p className="mt-3 text-2xl font-bold tracking-[-.03em] text-[#152033]">{complete ? 'You are here.' : steps[index]}</p><p className="mt-3 text-sm text-[#526273]">{complete ? 'Notice if anything feels even slightly different.' : 'Take one slow breath before continuing.'}</p></div><button className="btn-primary" onClick={() => setIndex(value => complete ? 0 : value + 1)}>{complete ? 'Start again' : <><span>Next step</span><ChevronRight size={17} /></>}</button></div>;
}

function ThoughtTool() {
  const [thought, setThought] = useState(''); const [reply, setReply] = useState(''); const [saved, setSaved] = useState(false);
  return <div className="mx-auto max-w-2xl"><p className="tool-kicker">A small thought reset</p><h2 className="tool-title">Make space for another view.</h2><p className="tool-copy">Write the thought exactly as it arrives, then answer it as you would answer someone you care about.</p><label className="tool-label">The thought I am having<textarea value={thought} onChange={e => setThought(e.target.value)} placeholder="For example: I am not handling this well." className="tool-textarea" /></label><label className="tool-label">A more balanced response<textarea value={reply} onChange={e => setReply(e.target.value)} placeholder="For example: This is hard, but I have handled difficult days before." className="tool-textarea" /></label><button className="btn-primary mt-2" disabled={!thought.trim() || !reply.trim()} onClick={() => setSaved(true)}>{saved ? <><Check size={17} /> Saved for today</> : <><PenLine size={17} /> Save reflection</>}</button></div>;
}

function GratitudeTool() {
  const [items, setItems] = useState(['', '', '']); const [done, setDone] = useState(false);
  const complete = items.every(item => item.trim());
  return <div className="mx-auto max-w-2xl"><p className="tool-kicker">Two-minute reflection</p><h2 className="tool-title">Three good things.</h2><p className="tool-copy">They can be ordinary: warm tea, a kind message, a moment of quiet.</p><div className="space-y-3">{items.map((item, index) => <label key={index} className="flex items-center gap-4 rounded-xl border border-[#dbe3e8] bg-white px-4 py-3"><span className="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-[#f3e7f2] text-sm font-bold text-[#824477]">{index + 1}</span><input value={item} onChange={e => setItems(values => values.map((value, i) => i === index ? e.target.value : value))} placeholder="A small good thing…" className="w-full border-0 bg-transparent text-[15px] text-[#152033] outline-none placeholder:text-[#8392a1]" /></label>)}</div><button className="btn-primary mt-6" disabled={!complete} onClick={() => setDone(true)}>{done ? <><Check size={17} /> Noted for today</> : 'Save three things'}</button></div>;
}

function FocusGame() {
  const [round, setRound] = useState(1); const [score, setScore] = useState(0); const [notice, setNotice] = useState('Find the single different tile.');
  const odd = (round * 5 + 2) % 9;
  const play = (index) => {
    if (index === odd) { setScore(value => value + 1); setRound(value => value + 1); setNotice('Nice noticing. Try the next one.'); }
    else setNotice('Not that one. Slow down and look again.');
  };
  return <div className="mx-auto max-w-xl text-center"><p className="tool-kicker">One-minute attention game</p><h2 className="tool-title">Focus match.</h2><p className="mx-auto mt-3 max-w-md text-[15px] leading-7 text-[#526273]">There is no timer and no penalty. Look for the tile with a different center.</p><div className="mt-7 grid grid-cols-3 gap-3 rounded-2xl bg-[#edf3f8] p-5">{Array.from({ length: 9 }, (_, index) => <button key={`${round}-${index}`} onClick={() => play(index)} aria-label={`Focus tile ${index + 1}`} className={`grid aspect-square place-items-center rounded-xl border-2 transition-transform hover:scale-105 ${index === odd ? 'border-[#8eb4e8] bg-[#cbdcf4]' : 'border-[#b9d0ea] bg-[#dce8f7]'}`}><span className={`block rounded-full ${index === odd ? 'h-4 w-4 bg-[#315c99]' : 'h-5 w-5 border-2 border-[#315c99]'}`} /></button>)}</div><p className="mt-5 text-sm font-semibold text-[#315c99]">{notice}</p><p className="mt-2 text-xs text-[#68798a]">Rounds completed: {score}</p></div>;
}

function QuietCountGame() {
  const [count, setCount] = useState(0); const [complete, setComplete] = useState(false);
  const tap = () => { if (count >= 9) { setComplete(true); return; } setCount(value => value + 1); };
  const reset = () => { setCount(0); setComplete(false); };
  return <div className="mx-auto max-w-xl text-center"><p className="tool-kicker">A small pause</p><h2 className="tool-title">Quiet count.</h2><p className="mx-auto mt-3 max-w-md text-[15px] leading-7 text-[#526273]">Take one comfortable breath for each number. If your mind drifts, simply tap and return—nothing has gone wrong.</p><button onClick={complete ? reset : tap} className="mx-auto mt-8 grid h-44 w-44 place-items-center rounded-full border-8 border-[#f5dfc8] bg-[#fdf3e9] transition-transform hover:scale-105"><div><p className="text-5xl font-bold tracking-[-.06em] text-[#9a5625]">{complete ? '✓' : count + 1}</p><p className="mt-2 text-xs font-bold uppercase tracking-[.12em] text-[#9a5625]">{complete ? 'Complete' : 'Tap after a breath'}</p></div></button><p className="mt-6 text-sm font-semibold text-[#9a5625]">{complete ? 'You gave yourself a minute of attention.' : `${count} of 10 gentle breaths`}</p></div>;
}

const TOOL_COMPONENTS = { breathe: BreathingTool, ground: GroundingTool, reset: ThoughtTool, gratitude: GratitudeTool, focus: FocusGame, count: QuietCountGame };

function ToolCard({ tool, onOpen }) {
  const { id, name, time, icon: Icon, color, description } = tool;
  return <button onClick={() => onOpen(id)} className="group rounded-2xl border border-[#dbe3e8] bg-white p-5 text-left transition-all hover:-translate-y-0.5 hover:border-[#9ccfc3] hover:shadow-[0_5px_18px_rgba(15,34,52,.08)]"><div className="flex items-start justify-between"><span className={`grid h-11 w-11 place-items-center rounded-xl ${color}`}><Icon size={21} /></span><span className="inline-flex items-center gap-1 text-xs font-bold text-[#68798a]"><Timer size={14} /> {time}</span></div><h3 className="mt-5 text-lg font-bold text-[#152033]">{name}</h3><p className="mt-1 text-sm leading-6 text-[#526273]">{description}</p><span className="mt-5 inline-flex items-center gap-1 text-sm font-bold text-[#0f625b]">Open <ChevronRight size={16} /></span></button>;
}

export default function ToolsPage() {
  const [activeTool, setActiveTool] = useState(null);
  const ActiveTool = useMemo(() => activeTool ? TOOL_COMPONENTS[activeTool] : null, [activeTool]);
  if (ActiveTool) return <div className="mx-auto max-w-5xl"><button onClick={() => setActiveTool(null)} className="mb-6 inline-flex items-center gap-2 text-sm font-bold text-[#315c99] hover:text-[#142136]"><ArrowLeft size={17} /> All wellbeing tools</button><section className="rounded-2xl border border-[#dbe3e8] bg-white p-6 shadow-[0_2px_12px_rgba(15,34,52,.05)] sm:p-9"><ActiveTool /></section></div>;
  return <div className="mx-auto max-w-5xl"><section className="rounded-2xl bg-[#e0eee9] px-6 py-8 sm:px-8"><p className="tool-kicker">Wellbeing tools</p><h1 className="mt-2 font-serif text-4xl font-semibold tracking-[-.045em] text-[#142136]">Choose one small reset.</h1><p className="mt-3 max-w-xl text-[15px] leading-7 text-[#405266]">Short, private practices for when you want to feel more settled. Pick what fits your moment—there is no score to chase.</p></section><section className="mt-7"><div className="mb-4 flex items-center justify-between"><h2 className="text-lg font-bold text-[#152033]">Guided practices</h2><span className="text-sm text-[#526273]">2–4 minutes each</span></div><div className="grid gap-4 sm:grid-cols-2">{TOOL_LIST.map(tool => <ToolCard key={tool.id} tool={tool} onOpen={setActiveTool} />)}</div></section><section className="mt-9 border-t border-[#dbe3e8] pt-7"><div className="mb-4"><p className="tool-kicker">Mindful play</p><h2 className="mt-1 text-xl font-bold tracking-[-.025em] text-[#152033]">A gentle change of focus.</h2><p className="mt-1 text-sm text-[#526273]">Short games for a pause—not a score or a competition.</p></div><div className="grid gap-4 sm:grid-cols-2">{GAME_LIST.map(tool => <ToolCard key={tool.id} tool={tool} onOpen={setActiveTool} />)}</div></section></div>;
}

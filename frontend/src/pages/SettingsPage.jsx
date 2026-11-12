import React, { useState } from 'react';
import { useStore } from '../store/useStore';
import { Monitor, UserPlus, Download, Trash2 } from 'lucide-react';
import { API_BASE_URL } from '../api/client';

export default function SettingsPage() {
  const { consents, updateConsents } = useStore();
  const [contactName, setContactName] = useState('');
  const [contactPhone, setContactPhone] = useState('');

  const handleExport = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/mood/export`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'MindGuard_Report.pdf';
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (e) {
      alert("Failed to export.");
    }
  };

  const handleAddContact = async () => {
    if(!contactName || !contactPhone) return;
    try {
      await fetch(`${API_BASE_URL}/onboarding/trusted-contact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 'demo_user_001', name: contactName, phone: contactPhone, relation: 'Friend' })
      });
      alert('Mock OTP sent. Please verify (simulated success).');
      setContactName('');
      setContactPhone('');
    } catch (e) {
      alert("Failed to add contact.");
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div><p className="tool-kicker">Preferences</p><h1 className="mt-1 text-3xl font-bold tracking-[-.035em] text-[#152033]">Your settings</h1><p className="mt-2 text-sm text-[#526273]">Manage your display, contacts, and data choices.</p></div>
      
      <div className="glass-card space-y-6">
        <h2 className="text-xl font-bold text-[#152033]">Display</h2>
        <div className="flex items-center justify-between p-4 glass-panel">
          <div className="flex items-center gap-3">
            <Monitor className="text-[#0f625b]" />
            <div><p className="font-semibold text-[#152033]">High-contrast light theme</p><p className="mt-0.5 text-sm text-[#526273]">Clear text and solid surfaces are enabled.</p></div>
          </div>
          <span className="rounded-full bg-[#edf7f4] px-3 py-1.5 text-xs font-bold text-[#0f625b]">Active</span>
        </div>
      </div>

      <div className="glass-card space-y-6">
        <h2 className="text-xl font-bold text-[#152033]">Trusted Contact</h2>
        <p className="text-[#526273] text-sm">Add a friend or family member you may want to reach. Notifications require a verified delivery service.</p>
        
        <div className="flex gap-4">
          <input type="text" placeholder="Name" value={contactName} onChange={e=>setContactName(e.target.value)} className="flex-1 rounded-xl border border-slate-300 bg-white p-3 text-slate-900 placeholder:text-slate-500 focus:ring-teal focus:border-teal outline-none" />
          <input type="tel" placeholder="Phone Number" value={contactPhone} onChange={e=>setContactPhone(e.target.value)} className="flex-1 rounded-xl border border-slate-300 bg-white p-3 text-slate-900 placeholder:text-slate-500 focus:ring-teal focus:border-teal outline-none" />
          <button onClick={handleAddContact} className="btn-primary flex items-center gap-2"><UserPlus size={18}/> Add</button>
        </div>
      </div>

      <div className="glass-card space-y-6">
        <h2 className="text-xl font-bold text-[#152033]">Data & Privacy</h2>
        <div className="flex items-center justify-between p-4 glass-panel">
          <div className="flex items-center gap-3">
            <Download className="text-teal" />
            <span className="font-medium text-[#152033]">Export PDF Report</span>
          </div>
          <button onClick={handleExport} className="bg-teal/10 text-teal px-4 py-2 rounded-lg font-medium hover:bg-teal/20 transition-colors">Download</button>
        </div>
        <div className="flex items-center justify-between p-4 glass-panel border-red-500/20 bg-red-500/5">
          <div className="flex items-center gap-3">
            <Trash2 className="text-red-500" />
            <span className="font-medium text-red-600">Delete My Data</span>
          </div>
          <button className="bg-red-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-red-600 transition-colors">Delete Account</button>
        </div>
      </div>
    </div>
  );
}

import React, { useEffect, useState } from 'react';
import { Bot, RefreshCw, Mail, Settings, Database, PlayCircle, Sparkles, Cpu } from 'lucide-react';
import { api } from '../api/client';

interface NavbarProps {
  currentView: 'dashboard' | 'knowledge';
  onNavigate: (view: 'dashboard' | 'knowledge') => void;
  onOpenSimulate: () => void;
  onOpenEmails: () => void;
  onOpenPolicy: () => void;
  onLoadDemoData: () => void;
  onSyncJira: () => void;
  loading: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentView,
  onNavigate,
  onOpenSimulate,
  onOpenEmails,
  onOpenPolicy,
  onLoadDemoData,
  onSyncJira,
  loading,
}) => {
  const [aiStatus, setAiStatus] = useState<any>(null);

  useEffect(() => {
    api.getNvidiaStatus().then(setAiStatus).catch(() => {});
  }, []);
  return (
    <header className="sticky top-0 z-40 bg-slate-900/90 backdrop-blur border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand & Logo */}
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onNavigate('dashboard')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-600 to-teal-400 flex items-center justify-center shadow-lg shadow-teal-500/20">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg tracking-tight text-white">JiraPilot AI</span>
                <span className="px-2 py-0.5 text-xs font-semibold bg-teal-500/10 text-teal-400 border border-teal-500/30 rounded-full">
                  v1.0 Enterprise
                </span>
              </div>
              <p className="text-xs text-slate-400">Autonomous Jira Triage & RCA Agent</p>
            </div>
          </div>

          <nav className="hidden md:flex items-center space-x-1 border-l border-slate-800 pl-6">
            <button
              onClick={() => onNavigate('dashboard')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
                currentView === 'dashboard'
                  ? 'bg-slate-800 text-teal-400 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              Operations Dashboard
            </button>
            <button
              onClick={() => onNavigate('knowledge')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition flex items-center space-x-1.5 ${
                currentView === 'knowledge'
                  ? 'bg-slate-800 text-teal-400 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Database className="w-3.5 h-3.5" />
              <span>Incident Memory</span>
            </button>
          </nav>
        </div>

        {/* Global Action Controls */}
        <div className="flex items-center space-x-2.5">
          {/* AI Engine Status Pill */}
          <div
            className={`hidden lg:flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border ${
              aiStatus?.configured
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                : 'bg-slate-800 text-slate-300 border-slate-700'
            }`}
            title={aiStatus?.configured ? `NVIDIA NIM Active: ${aiStatus?.model}` : 'Deterministic Fallback Engine active (offline safe)'}
          >
            <Cpu className={`w-3.5 h-3.5 ${aiStatus?.configured ? 'text-emerald-400' : 'text-slate-400'}`} />
            <span>{aiStatus?.configured ? 'NVIDIA NIM Active' : 'Deterministic AI Fallback'}</span>
          </div>

          <button
            onClick={onSyncJira}
            disabled={loading}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-sm shadow-indigo-600/30 transition active:scale-95 disabled:opacity-50"
            title="Fetch and synchronize live tickets from Atlassian Jira Cloud project"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Sync Jira (KAN)</span>
          </button>

          <button
            onClick={onLoadDemoData}
            disabled={loading}
            className="hidden sm:inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition active:scale-95 disabled:opacity-50"
            title="Load synthetic hackathon scenario tickets (HACK-1001 to HACK-1004)"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>Load Demo Data</span>
          </button>

          <button
            onClick={onOpenSimulate}
            className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-teal-600 hover:bg-teal-500 text-white shadow-sm shadow-teal-600/30 transition active:scale-95"
          >
            <PlayCircle className="w-4 h-4" />
            <span>Simulate Jira Issue</span>
          </button>

          <button
            onClick={onOpenEmails}
            className="relative p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-800 transition"
            title="Open Mock Email Notification Inbox"
          >
            <Mail className="w-4 h-4" />
          </button>

          <button
            onClick={onOpenPolicy}
            className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-800 transition"
            title="Triage & Investigation Policy Rules"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};

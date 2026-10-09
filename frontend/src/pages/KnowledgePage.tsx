import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { Database, Search, Plus, ShieldCheck, CheckCircle2 } from 'lucide-react';

export const KnowledgePage: React.FC = () => {
  const [records, setRecords] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchKnowledge();
  }, []);

  const fetchKnowledge = async () => {
    setLoading(true);
    try {
      const data = await api.getKnowledgeBase();
      setRecords(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const filtered = records.filter(
    (r) =>
      r.jiraKey?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.summary?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.affectedService?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.rootCause?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6 pb-12 animate-in fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-3 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <Database className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-base font-bold text-white">Engineering Incident Knowledge Memory</h1>
              <p className="text-xs text-slate-400">
                Persistent incident patterns, diagnosed root causes, and verified remediations for similarity correlation
              </p>
            </div>
          </div>

          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search historical incidents, services, root causes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 pr-4 py-2 rounded-lg bg-slate-950 border border-slate-700/80 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-teal-500 w-80"
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map((item, idx) => (
          <div key={idx} className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="font-mono text-xs font-bold text-teal-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                  {item.jiraKey}
                </span>
                <span className="text-[11px] font-mono font-semibold text-purple-300 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
                  {item.affectedService}
                </span>
              </div>
              <span className="text-[10px] text-emerald-400 flex items-center">
                <ShieldCheck className="w-3.5 h-3.5 mr-1" />
                Resolved & Verified
              </span>
            </div>

            <h3 className="text-xs font-bold text-white mb-2">{item.summary}</h3>

            <div className="space-y-2 text-xs">
              <div className="p-3 bg-slate-950 rounded-lg border border-slate-850">
                <span className="text-slate-500 font-medium block text-[10px] uppercase tracking-wider mb-0.5">Diagnosed Root Cause</span>
                <span className="text-slate-300">{item.rootCause}</span>
              </div>

              <div className="p-3 bg-emerald-950/20 rounded-lg border border-emerald-500/20">
                <span className="text-emerald-500 font-medium block text-[10px] uppercase tracking-wider mb-0.5">Applied Resolution</span>
                <span className="text-emerald-200">{item.resolution}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

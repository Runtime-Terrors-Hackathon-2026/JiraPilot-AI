import React, { useState, useEffect } from 'react';
import { PolicySettings } from '../types';
import { api } from '../api/client';
import { X, Settings, Sliders, Save, Check } from 'lucide-react';

interface PolicyModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PolicyModal: React.FC<PolicyModalProps> = ({ isOpen, onClose }) => {
  const [policy, setPolicy] = useState<PolicySettings | null>(null);
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (isOpen) {
      api.getPolicy().then(setPolicy).catch(console.error);
    }
  }, [isOpen]);

  if (!isOpen || !policy) return null;

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const updated = await api.updatePolicy(policy);
      setPolicy(updated);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-850">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-teal-500/10 text-teal-400 border border-teal-500/20">
              <Sliders className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Triage & Investigation Policy Rules</h2>
              <p className="text-xs text-slate-400">Configure weighted readiness scoring algorithms and automation thresholds</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSave} className="p-6 overflow-y-auto max-h-[65vh] space-y-6">
          {/* Automated Workflow Switches */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Workflow Automation Controls</h3>
            <div className="space-y-3 bg-slate-950 p-4 rounded-xl border border-slate-800">
              <label className="flex items-center justify-between cursor-pointer">
                <div>
                  <div className="text-xs font-semibold text-white">Automatic Investigation on Ready</div>
                  <div className="text-[11px] text-slate-400">Auto-triggers RCA and test suite when readiness score passes threshold</div>
                </div>
                <input
                  type="checkbox"
                  checked={policy.autoInvestigateEnabled}
                  onChange={(e) => setPolicy({ ...policy, autoInvestigateEnabled: e.target.checked })}
                  className="w-4 h-4 accent-teal-500 rounded cursor-pointer"
                />
              </label>

              <label className="flex items-center justify-between cursor-pointer pt-2 border-t border-slate-800/80">
                <div>
                  <div className="text-xs font-semibold text-white">Automated Jira Comments</div>
                  <div className="text-[11px] text-slate-400">Posts missing requirement lists and final RCA reports back to Jira Cloud</div>
                </div>
                <input
                  type="checkbox"
                  checked={policy.autoCommentEnabled}
                  onChange={(e) => setPolicy({ ...policy, autoCommentEnabled: e.target.checked })}
                  className="w-4 h-4 accent-teal-500 rounded cursor-pointer"
                />
              </label>

              <label className="flex items-center justify-between cursor-pointer pt-2 border-t border-slate-800/80">
                <div>
                  <div className="text-xs font-semibold text-white">Automated Reporter Emails</div>
                  <div className="text-[11px] text-slate-400">Notifies issue reporter when diagnostics are missing</div>
                </div>
                <input
                  type="checkbox"
                  checked={policy.autoEmailEnabled}
                  onChange={(e) => setPolicy({ ...policy, autoEmailEnabled: e.target.checked })}
                  className="w-4 h-4 accent-teal-500 rounded cursor-pointer"
                />
              </label>
            </div>
          </div>

          {/* Readiness Scoring Weights */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Diagnostic Readiness Scoring Weights (Total = 100)</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 bg-slate-950 p-4 rounded-xl border border-slate-800">
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Logs</label>
                <input
                  type="number"
                  value={policy.weightLogs}
                  onChange={(e) => setPolicy({ ...policy, weightLogs: parseInt(e.target.value) || 0 })}
                  className="w-full px-2.5 py-1.5 rounded bg-slate-900 border border-slate-800 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">API Details</label>
                <input
                  type="number"
                  value={policy.weightApiDetails}
                  onChange={(e) => setPolicy({ ...policy, weightApiDetails: parseInt(e.target.value) || 0 })}
                  className="w-full px-2.5 py-1.5 rounded bg-slate-900 border border-slate-800 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Request Payload</label>
                <input
                  type="number"
                  value={policy.weightRequestPayload}
                  onChange={(e) => setPolicy({ ...policy, weightRequestPayload: parseInt(e.target.value) || 0 })}
                  className="w-full px-2.5 py-1.5 rounded bg-slate-900 border border-slate-800 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Description</label>
                <input
                  type="number"
                  value={policy.weightDescription}
                  onChange={(e) => setPolicy({ ...policy, weightDescription: parseInt(e.target.value) || 0 })}
                  className="w-full px-2.5 py-1.5 rounded bg-slate-900 border border-slate-800 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Environment</label>
                <input
                  type="number"
                  value={policy.weightEnvironment}
                  onChange={(e) => setPolicy({ ...policy, weightEnvironment: parseInt(e.target.value) || 0 })}
                  className="w-full px-2.5 py-1.5 rounded bg-slate-900 border border-slate-800 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Error / Actual</label>
                <input
                  type="number"
                  value={policy.weightErrorMessage}
                  onChange={(e) => setPolicy({ ...policy, weightErrorMessage: parseInt(e.target.value) || 0 })}
                  className="w-full px-2.5 py-1.5 rounded bg-slate-900 border border-slate-800 text-xs text-white"
                />
              </div>
            </div>
          </div>

          {/* Thresholds */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Confidence & Acceptance Thresholds (%)</h3>
            <div className="grid grid-cols-3 gap-3 bg-slate-950 p-4 rounded-xl border border-slate-800">
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Readiness Threshold</label>
                <input
                  type="number"
                  value={policy.readinessThreshold}
                  onChange={(e) => setPolicy({ ...policy, readinessThreshold: parseInt(e.target.value) || 0 })}
                  className="w-full px-2.5 py-1.5 rounded bg-slate-900 border border-slate-800 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">AI Confidence Min</label>
                <input
                  type="number"
                  value={policy.confidenceThreshold}
                  onChange={(e) => setPolicy({ ...policy, confidenceThreshold: parseInt(e.target.value) || 0 })}
                  className="w-full px-2.5 py-1.5 rounded bg-slate-900 border border-slate-800 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Similarity Threshold</label>
                <input
                  type="number"
                  value={policy.similarityThreshold}
                  onChange={(e) => setPolicy({ ...policy, similarityThreshold: parseInt(e.target.value) || 0 })}
                  className="w-full px-2.5 py-1.5 rounded bg-slate-900 border border-slate-800 text-xs text-white"
                />
              </div>
            </div>
          </div>

          {/* Footer Save */}
          <div className="pt-4 border-t border-slate-800 flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 rounded-lg text-xs font-semibold bg-teal-600 hover:bg-teal-500 text-white shadow-lg shadow-teal-600/30 transition flex items-center space-x-2"
            >
              {saved ? <Check className="w-4 h-4 text-white" /> : <Save className="w-4 h-4" />}
              <span>{saved ? 'Policy Saved!' : loading ? 'Saving...' : 'Save Policy'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

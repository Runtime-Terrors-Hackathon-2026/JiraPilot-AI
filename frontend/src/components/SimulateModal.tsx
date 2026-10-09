import React, { useState } from 'react';
import { JiraIssue } from '../types';
import { api } from '../api/client';
import { X, PlayCircle, Sparkles, CheckCircle2 } from 'lucide-react';

interface SimulateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (issue: JiraIssue) => void;
}

export const SimulateModal: React.FC<SimulateModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [key, setKey] = useState('HACK-1001');
  const [summary, setSummary] = useState('Circuit creation API failing');
  const [description, setDescription] = useState('Circuit creation fails intermittently during provisioning in SANDBOX environment.');
  const [reporter, setReporter] = useState('developer@example.com');
  const [environment, setEnvironment] = useState('SANDBOX');
  const [apiDetails, setApiDetails] = useState('POST /api/circuit/provision');
  const [logs, setLogs] = useState('2026-10-08 10:31:42 ERROR [PEDS] Duplicate NFID detected: TEST-NFID-1001 correlationId=CORR-1001\n2026-10-08 10:31:43 ERROR [WFM] Downstream request failed status=500 endpoint=/api/circuit/provision correlationId=CORR-1001');
  const [requestPayload, setRequestPayload] = useState('{\n  "circuitId": "TEST-CKT-1001",\n  "customerId": "TEST-CUST-8821",\n  "nfid": "TEST-NFID-1001"\n}');
  const [errorMessage, setErrorMessage] = useState('HTTP 500 Internal Server Error: Duplicate NFID detected');
  const [expectedBehavior, setExpectedBehavior] = useState('HTTP 201 Created and active circuit record created');
  const [actualBehavior, setActualBehavior] = useState('HTTP 500 with SQL unique constraint error');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const loadPreset = (presetType: 'complete' | 'incomplete' | 'timeout') => {
    if (presetType === 'complete') {
      setKey('HACK-1001');
      setSummary('Circuit creation API failing');
      setDescription('Circuit creation fails intermittently during provisioning in SANDBOX environment.');
      setReporter('alice.engineer@example.com');
      setEnvironment('SANDBOX');
      setApiDetails('POST /api/circuit/provision');
      setLogs('2026-10-08 10:31:42 ERROR [PEDS] Duplicate NFID detected: TEST-NFID-1001 correlationId=CORR-1001\n2026-10-08 10:31:43 ERROR [WFM] Downstream request failed status=500 endpoint=/api/circuit/provision correlationId=CORR-1001');
      setRequestPayload('{\n  "circuitId": "TEST-CKT-1001",\n  "customerId": "TEST-CUST-8821",\n  "nfid": "TEST-NFID-1001"\n}');
      setErrorMessage('HTTP 500 Duplicate NFID');
      setExpectedBehavior('HTTP 201 Created');
      setActualBehavior('HTTP 500 Server Error');
    } else if (presetType === 'incomplete') {
      setKey('HACK-1002');
      setSummary('API is failing. Please check.');
      setDescription('API is failing. Please check why circuits are not being created.');
      setReporter('bob.developer@example.com');
      setEnvironment('DEV');
      setApiDetails('');
      setLogs('');
      setRequestPayload('');
      setErrorMessage('');
      setExpectedBehavior('');
      setActualBehavior('');
    } else if (presetType === 'timeout') {
      setKey('HACK-1003');
      setSummary('Work Order dispatch timeout when calling Inventory Service');
      setDescription('High latency and 504 Gateway Timeout during peak dispatch requests.');
      setReporter('carol.lead@example.com');
      setEnvironment('PROD-US-EAST');
      setApiDetails('POST /api/work-order/dispatch');
      setLogs('2026-10-08 11:15:25 ERROR [WFM] DownstreamTimeoutException: Read timed out connecting to Inventory Service correlationId=CORR-5542');
      setRequestPayload('{\n  "workOrderId": "WO-9942",\n  "serviceType": "FIBER"\n}');
      setErrorMessage('HTTP 504 Gateway Timeout');
      setExpectedBehavior('HTTP 200 OK within 500ms SLA');
      setActualBehavior('HTTP 504 Timeout');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const issue = await api.simulateIssue({
        key,
        summary,
        description,
        reporter,
        environment,
        apiDetails,
        logs,
        requestPayload,
        errorMessage,
        expectedBehavior,
        actualBehavior,
      });
      onSuccess(issue);
      onClose();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-3xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-850">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-teal-500/10 text-teal-400 border border-teal-500/20">
              <PlayCircle className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Simulate Jira Issue Ingestion</h2>
              <p className="text-xs text-slate-400">Trigger real-time validation, triage readiness scoring, and automated RCA pipeline</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Preset Selector */}
        <div className="px-6 py-3 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
          <span className="text-xs font-medium text-slate-400">Demo Scenario Presets:</span>
          <div className="flex space-x-2">
            <button
              type="button"
              onClick={() => loadPreset('complete')}
              className="px-2.5 py-1 rounded bg-teal-500/10 hover:bg-teal-500/20 text-teal-300 border border-teal-500/30 text-xs font-semibold"
            >
              1. Complete (Duplicate NFID)
            </button>
            <button
              type="button"
              onClick={() => loadPreset('incomplete')}
              className="px-2.5 py-1 rounded bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-semibold"
            >
              2. Incomplete (Needs Info)
            </button>
            <button
              type="button"
              onClick={() => loadPreset('timeout')}
              className="px-2.5 py-1 rounded bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/30 text-xs font-semibold"
            >
              3. Downstream Timeout
            </button>
          </div>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto max-h-[60vh] space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Jira Key</label>
              <input
                type="text"
                value={key}
                onChange={(e) => setKey(e.target.value)}
                required
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-teal-500 font-mono"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-slate-300 mb-1">Summary</label>
              <input
                type="text"
                value={summary}
                onChange={(e) => setSummary(e.target.value)}
                required
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-teal-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Issue Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
              required
              className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-teal-500 font-sans"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Reporter Email</label>
              <input
                type="email"
                value={reporter}
                onChange={(e) => setReporter(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-teal-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Environment</label>
              <input
                type="text"
                value={environment}
                onChange={(e) => setEnvironment(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-teal-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">API Endpoint</label>
              <input
                type="text"
                value={apiDetails}
                onChange={(e) => setApiDetails(e.target.value)}
                placeholder="POST /api/circuit/provision"
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-teal-500 font-mono"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Application / Server Logs</label>
            <textarea
              value={logs}
              onChange={(e) => setLogs(e.target.value)}
              rows={3}
              placeholder="Paste log traces here..."
              className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-teal-500 font-mono"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Request Payload (JSON)</label>
              <textarea
                value={requestPayload}
                onChange={(e) => setRequestPayload(e.target.value)}
                rows={3}
                placeholder="Paste JSON body..."
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-teal-500 font-mono"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Expected vs Actual Behavior</label>
              <input
                type="text"
                value={expectedBehavior}
                onChange={(e) => setExpectedBehavior(e.target.value)}
                placeholder="Expected Behavior"
                className="w-full mb-2 px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-teal-500"
              />
              <input
                type="text"
                value={actualBehavior}
                onChange={(e) => setActualBehavior(e.target.value)}
                placeholder="Actual Behavior"
                className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-teal-500"
              />
            </div>
          </div>

          {/* Footer Actions */}
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
              <Sparkles className="w-4 h-4" />
              <span>{loading ? 'Ingesting...' : 'Ingest & Trigger AI Triage'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

import React, { useState } from 'react';
import { Terminal, Copy, Check, ShieldCheck } from 'lucide-react';

interface CurlViewerProps {
  curlCommand?: string;
  postmanJson?: string;
}

export const CurlViewer: React.FC<CurlViewerProps> = ({ curlCommand, postmanJson }) => {
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState<'curl' | 'postman'>('curl');

  const defaultCurl = curlCommand || `curl -X POST "http://localhost:8080/mock-api/circuit/create" \\
  -H "Content-Type: application/json" \\
  -H "X-Correlation-ID: CORR-TEST-1001" \\
  -d '{
    "circuitId": "TEST-001",
    "customerId": "TEST-CUSTOMER-001",
    "nfid": "TEST-NFID-1001"
  }'`;

  const handleCopy = () => {
    const textToCopy = activeTab === 'curl' ? defaultCurl : (postmanJson || '{}');
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
        <div className="flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-teal-400" />
          <h3 className="text-sm font-semibold text-white">Safe Reproduction & Terminal Clone</h3>
        </div>

        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1 text-[11px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 mr-2">
            <ShieldCheck className="w-3.5 h-3.5 mr-1" />
            <span>Safe Synthetic Data Only</span>
          </div>

          <div className="flex bg-slate-800 rounded-lg p-0.5 border border-slate-700">
            <button
              onClick={() => setActiveTab('curl')}
              className={`px-2.5 py-1 text-xs font-medium rounded-md transition ${
                activeTab === 'curl' ? 'bg-slate-700 text-teal-400' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              cURL
            </button>
            <button
              onClick={() => setActiveTab('postman')}
              className={`px-2.5 py-1 text-xs font-medium rounded-md transition ${
                activeTab === 'postman' ? 'bg-slate-700 text-teal-400' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Postman
            </button>
          </div>
        </div>
      </div>

      <div className="relative">
        <pre className="p-4 bg-slate-950 rounded-xl text-xs font-mono text-teal-300 overflow-x-auto border border-slate-800">
          {activeTab === 'curl' ? defaultCurl : (postmanJson || '{\n  "info": { "name": "Incident Reproduction" }\n}')}
        </pre>

        <button
          onClick={handleCopy}
          className="absolute top-3 right-3 flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 border border-slate-700 transition"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-teal-400" />
              <span className="text-teal-400">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span>Copy {activeTab === 'curl' ? 'curl' : 'Postman JSON'}</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};

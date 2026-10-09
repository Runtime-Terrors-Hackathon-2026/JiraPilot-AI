import React, { useState } from 'react';
import { TestCase } from '../types';
import { CheckCircle, Code, Copy, Check } from 'lucide-react';

interface TestCaseListProps {
  testCases?: TestCase[];
}

export const TestCaseList: React.FC<TestCaseListProps> = ({ testCases }) => {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const defaultCases: TestCase[] = testCases && testCases.length > 0 ? testCases : [
    { id: 'TC-001', title: 'Valid circuit request baseline', type: 'INTEGRATION', description: 'Post valid payload to endpoint', expectedResult: 'HTTP 201 Created' },
    { id: 'TC-002', title: 'Duplicate NFID idempotency guard', type: 'UNIT', description: 'Duplicate NFID should reject gracefully', expectedResult: 'HTTP 409 Conflict / Handled exception' },
    { id: 'TC-003', title: 'Downstream timeout recovery', type: 'INTEGRATION', description: 'Simulate > 3000ms delay', expectedResult: 'Circuit breaker fallback triggered' },
    { id: 'TC-004', title: 'HTTP 500 error envelope standard', type: 'API', description: 'Verify standardized error JSON', expectedResult: 'Clean error response returned' },
    { id: 'TC-005', title: 'Missing required payload field validation', type: 'API', description: 'Empty or partial body', expectedResult: 'HTTP 400 Bad Request' },
  ];

  const handleCopy = (code: string, id: string) => {
    navigator.clipboard.writeText(code);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-white">Automated Regression & Reproduction Test Suite</h3>
          <p className="text-xs text-slate-400">Generated Unit, Integration, and API test cases tailored to diagnosed root cause</p>
        </div>
        <span className="text-xs font-mono text-teal-400 bg-teal-500/10 px-2.5 py-1 rounded-md border border-teal-500/30">
          {defaultCases.length} Test Cases Generated
        </span>
      </div>

      <div className="space-y-3">
        {defaultCases.map((tc) => (
          <div key={tc.id} className="p-4 rounded-lg bg-slate-850 border border-slate-800 hover:border-slate-700 transition">
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-2.5">
                <span className="font-mono text-xs font-bold text-teal-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                  {tc.id}
                </span>
                <span className="text-xs font-semibold text-slate-200">{tc.title}</span>
                <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded ${
                  tc.type === 'UNIT' ? 'bg-blue-500/20 text-blue-300' :
                  tc.type === 'INTEGRATION' ? 'bg-purple-500/20 text-purple-300' :
                  'bg-amber-500/20 text-amber-300'
                }`}>
                  {tc.type}
                </span>
              </div>
            </div>

            <p className="text-xs text-slate-400 mt-2">{tc.description}</p>
            <div className="mt-2 text-xs flex items-center text-emerald-400 font-medium">
              <span className="text-slate-500 mr-1.5">Expected Result:</span> {tc.expectedResult}
            </div>

            {tc.testCodeSnippet && (
              <div className="mt-3 relative">
                <pre className="p-3 bg-slate-950 rounded-lg text-[11px] font-mono text-slate-300 overflow-x-auto border border-slate-800">
                  {tc.testCodeSnippet}
                </pre>
                <button
                  onClick={() => handleCopy(tc.testCodeSnippet || '', tc.id)}
                  className="absolute top-2 right-2 p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
                  title="Copy Java JUnit code"
                >
                  {copiedId === tc.id ? <Check className="w-3.5 h-3.5 text-teal-400" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

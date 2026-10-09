import React from 'react';
import { TimelineEvent } from '../types';
import { Clock, CheckCircle2 } from 'lucide-react';

interface TimelineViewerProps {
  events?: TimelineEvent[];
}

export const TimelineViewer: React.FC<TimelineViewerProps> = ({ events }) => {
  const defaultEvents: TimelineEvent[] = events && events.length > 0 ? events : [
    { time: '10:31:02', title: 'Jira Ticket Ingestion', description: 'Issue payload captured and queued for validation pipeline.', stage: 'INGESTION', status: 'COMPLETED' },
    { time: '10:31:03', title: 'AI Readiness Validation', description: 'Diagnostic completeness check scored 100/100.', stage: 'VALIDATION', status: 'COMPLETED' },
    { time: '10:31:05', title: 'Investigation Pipeline Triggered', description: 'Log correlation and error parsing initiated.', stage: 'INVESTIGATION', status: 'COMPLETED' },
    { time: '10:31:10', title: 'API & Service Point Identified', description: 'Isolated to POST /api/circuit/provision via WFM -> PEDS.', stage: 'API_IDENTIFICATION', status: 'COMPLETED' },
    { time: '10:31:14', title: 'Root Cause Isolated', description: 'Duplicate NFID detected from upstream NTLS integration (94% confidence).', stage: 'ROOT_CAUSE', status: 'COMPLETED' },
    { time: '10:31:16', title: 'RCA & Reproduction Suite Generated', description: 'Curl clone, Postman schema, and JUnit tests synthesized.', stage: 'RCA_GENERATION', status: 'COMPLETED' },
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <div className="flex items-center space-x-2 mb-4">
        <Clock className="w-4 h-4 text-teal-400" />
        <h3 className="text-sm font-semibold text-white">AI Agent Execution Timeline</h3>
      </div>

      <div className="relative pl-6 space-y-4 border-l border-slate-800 ml-2">
        {defaultEvents.map((evt, idx) => (
          <div key={idx} className="relative group">
            {/* Timeline Dot */}
            <div className="absolute -left-[31px] top-1 w-4 h-4 rounded-full bg-slate-950 border-2 border-teal-500 flex items-center justify-center">
              <div className="w-1.5 h-1.5 rounded-full bg-teal-400"></div>
            </div>

            <div className="flex flex-col sm:flex-row sm:items-baseline justify-between">
              <span className="text-xs font-bold text-slate-200 group-hover:text-teal-400 transition">{evt.title}</span>
              <span className="text-[11px] font-mono text-slate-500">{evt.time}</span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">{evt.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

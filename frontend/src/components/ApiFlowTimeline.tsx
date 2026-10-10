import React from 'react';
import { ApiFlowTimelineStep } from '../types';
import { cn } from '../lib/cn';

interface ApiFlowTimelineProps {
  steps: ApiFlowTimelineStep[];
  selectedNodeId: string | null;
  onSelectStep: (nodeId: string) => void;
}

export const ApiFlowTimeline: React.FC<ApiFlowTimelineProps> = ({
  steps,
  selectedNodeId,
  onSelectStep,
}) => {
  return (
    <div className="rounded-2xl border border-indigo-500/20 bg-[#060a17]/90 p-4 shadow-xl backdrop-blur-md">
      <div className="mb-3 flex items-center justify-between">
        <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-300">
          Request Flow Timeline
        </h4>
        <span className="text-[11px] text-indigo-400/80">
          Click any step to highlight the corresponding API call
        </span>
      </div>

      <div className="flex items-center gap-1 overflow-x-auto pb-2 scrollbar-thin">
        {steps.map((step, idx) => {
          const isSelected = selectedNodeId === step.nodeId;
          const isError = step.isFailurePoint || step.status === 'FAILED';

          return (
            <React.Fragment key={step.nodeId}>
              {/* Timeline Step Item */}
              <button
                type="button"
                onClick={() => onSelectStep(step.nodeId)}
                className={cn(
                  'group flex shrink-0 flex-col items-center rounded-xl border p-2.5 transition-all text-center min-w-[92px]',
                  isSelected
                    ? isError
                      ? 'border-red-500 bg-red-950/60 shadow-[0_0_15px_rgba(239,68,68,0.5)] scale-105'
                      : 'border-cyan-400 bg-cyan-950/60 shadow-[0_0_15px_rgba(6,182,212,0.5)] scale-105'
                    : isError
                    ? 'border-red-500/40 bg-red-950/20 hover:border-red-400'
                    : 'border-indigo-500/20 bg-[#0b1222] hover:border-indigo-400/50'
                )}
              >
                {/* Step Number Circle */}
                <div
                  className={cn(
                    'flex h-6 w-6 items-center justify-center rounded-full text-[11px] font-bold font-mono transition-colors',
                    isError
                      ? 'bg-red-500 text-white'
                      : isSelected
                      ? 'bg-cyan-400 text-black'
                      : 'bg-indigo-500/20 text-indigo-300 group-hover:bg-indigo-500/40'
                  )}
                >
                  {step.stepNumber}
                </div>

                {/* Step Label */}
                <span
                  className={cn(
                    'mt-1.5 text-xs font-bold tracking-wide truncate max-w-[85px]',
                    isError ? 'text-red-300' : 'text-white'
                  )}
                >
                  {step.label}
                </span>

                {/* Latency / Duration */}
                <span
                  className={cn(
                    'mt-0.5 text-[10px] font-mono',
                    isError ? 'text-red-400 font-bold' : 'text-indigo-400'
                  )}
                >
                  {step.duration || (step.label === 'Response' ? 'Egress' : 'Sync')}
                </span>
              </button>

              {/* Connecting arrow line */}
              {idx < steps.length - 1 && (
                <div className="h-0.5 w-4 shrink-0 bg-indigo-500/30" />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};

import React from 'react';
import { ServiceNode, ServiceEdge } from '../types';
import { Server, Database, ShieldAlert, CheckCircle2, ArrowRight } from 'lucide-react';

interface ServiceGraphProps {
  nodes?: ServiceNode[];
  edges?: ServiceEdge[];
}

export const ServiceGraph: React.FC<ServiceGraphProps> = ({ nodes, edges }) => {
  const defaultNodes: ServiceNode[] = nodes && nodes.length > 0 ? nodes : [
    { id: 'gateway', name: 'API Gateway', type: 'gateway', status: 'HEALTHY', isFailurePoint: false, details: 'Route OK' },
    { id: 'circuit', name: 'Circuit Service', type: 'service', status: 'HEALTHY', isFailurePoint: false, details: 'Orchestration OK' },
    { id: 'wfm', name: 'WFM Service', type: 'service', status: 'DEGRADED', isFailurePoint: false, details: 'Received 500 error' },
    { id: 'peds', name: 'PEDS Downstream', type: 'downstream', status: 'FAILED', isFailurePoint: true, details: 'Duplicate NFID Violation' },
    { id: 'db', name: 'PostgreSQL DB', type: 'database', status: 'HEALTHY', isFailurePoint: false, details: 'Connections Active' },
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-white">Service Dependency & Failure Point Topology</h3>
          <p className="text-xs text-slate-400">Automated tracing of request execution path across microservice boundaries</p>
        </div>
        <div className="flex items-center space-x-3 text-xs">
          <span className="flex items-center text-emerald-400"><span className="w-2 h-2 rounded-full bg-emerald-500 mr-1.5 animate-pulse"></span> Healthy</span>
          <span className="flex items-center text-amber-400"><span className="w-2 h-2 rounded-full bg-amber-500 mr-1.5"></span> Degraded</span>
          <span className="flex items-center text-rose-400"><span className="w-2 h-2 rounded-full bg-rose-500 mr-1.5 animate-ping"></span> Failure Point</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-3 relative py-4 items-center">
        {defaultNodes.map((node, index) => {
          const isFailed = node.status === 'FAILED' || node.isFailurePoint;
          const isDegraded = node.status === 'DEGRADED';

          return (
            <div key={node.id} className="flex items-center space-x-2">
              <div
                className={`flex-1 p-4 rounded-xl border transition-all duration-300 ${
                  isFailed
                    ? 'bg-rose-950/40 border-rose-500/80 shadow-lg shadow-rose-950/50 ring-2 ring-rose-500/40'
                    : isDegraded
                    ? 'bg-amber-950/30 border-amber-500/60 ring-1 ring-amber-500/30'
                    : 'bg-slate-850 border-slate-700/70 hover:border-slate-600'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    {node.type === 'database' ? (
                      <Database className="w-4 h-4 text-slate-400" />
                    ) : (
                      <Server className="w-4 h-4 text-slate-400" />
                    )}
                    <span className="text-xs font-bold text-white truncate">{node.name}</span>
                  </div>
                  {isFailed ? (
                    <ShieldAlert className="w-4 h-4 text-rose-400 animate-bounce" />
                  ) : (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  )}
                </div>

                <div className="text-[11px] text-slate-400 truncate">
                  {node.details || (isFailed ? 'Failure Point Isolated' : 'Operational')}
                </div>

                {isFailed && (
                  <div className="mt-2 text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/40 inline-block">
                    Root Cause Node
                  </div>
                )}
              </div>

              {index < defaultNodes.length - 1 && (
                <div className="hidden md:flex text-slate-600">
                  <ArrowRight className="w-4 h-4" />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

import React, { useState } from 'react';
import { JiraIssue, DashboardSummary, DashboardMetrics } from '../types';
import { StatCard } from '../components/StatCard';
import {
  Inbox,
  CheckCircle2,
  AlertTriangle,
  Zap,
  FileCheck,
  Gauge,
  Clock,
  Search,
  ArrowUpRight,
  Filter,
  Layers,
  ChevronRight,
  TrendingUp
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  CartesianGrid,
  Legend
} from 'recharts';

interface DashboardPageProps {
  issues: JiraIssue[];
  summary: DashboardSummary | null;
  metrics: DashboardMetrics | null;
  onSelectIssue: (key: string) => void;
  onRefresh: () => void;
  loading: boolean;
}

const COLORS = ['#14b8a6', '#f59e0b', '#8b5cf6', '#3b82f6', '#ef4444', '#10b981'];

export const DashboardPage: React.FC<DashboardPageProps> = ({
  issues,
  summary,
  metrics,
  onSelectIssue,
  onRefresh,
  loading,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'READY' | 'WAITING' | 'INVESTIGATED'>('ALL');

  const filteredIssues = issues.filter((issue) => {
    const matchesSearch =
      issue.jiraKey.toLowerCase().includes(searchTerm.toLowerCase()) ||
      issue.summary.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (issue.affectedService && issue.affectedService.toLowerCase().includes(searchTerm.toLowerCase()));

    if (!matchesSearch) return false;
    if (statusFilter === 'READY') return issue.status === 'READY';
    if (statusFilter === 'WAITING') return issue.status === 'WAITING_FOR_INFORMATION';
    if (statusFilter === 'INVESTIGATED') return issue.status === 'INVESTIGATED';
    return true;
  });

  // Prepare chart data
  const statusData = metrics?.ticketsByStatus
    ? Object.entries(metrics.ticketsByStatus).map(([name, value]) => ({
        name: name.replace(/_/g, ' '),
        value,
      }))
    : [
        { name: 'READY', value: 2 },
        { name: 'WAITING INFO', value: 1 },
        { name: 'INVESTIGATED', value: 3 },
      ];

  const missingInfoData = metrics?.missingInfoFrequency
    ? Object.entries(metrics.missingInfoFrequency).map(([name, count]) => ({
        name: name.replace(/([A-Z])/g, ' $1').trim(),
        count,
      }))
    : [
        { name: 'Logs', count: 4 },
        { name: 'Request Payload', count: 3 },
        { name: 'API Details', count: 2 },
        { name: 'Environment', count: 1 },
      ];

  const serviceData = metrics?.incidentsByService
    ? Object.entries(metrics.incidentsByService).map(([service, count]) => ({
        service,
        count,
      }))
    : [
        { service: 'WFM', count: 3 },
        { service: 'PEDS', count: 2 },
        { service: 'CIRCUIT-SVC', count: 2 },
        { service: 'GATEWAY', count: 1 },
      ];

  return (
    <div className="space-y-6 pb-12">
      {/* Top Stat KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Ingested Tickets"
          value={summary?.totalTickets || issues.length}
          subtitle="Real-time webhooks & ingest"
          icon={Inbox}
          color="blue"
        />
        <StatCard
          title="Ready for Investigation"
          value={summary?.readyTickets || issues.filter((i) => i.status === 'READY').length}
          subtitle="Complete diagnostic payload"
          icon={CheckCircle2}
          color="emerald"
          badge="Verified"
        />
        <StatCard
          title="Waiting for Information"
          value={summary?.waitingForInfoTickets || issues.filter((i) => i.status === 'WAITING_FOR_INFORMATION').length}
          subtitle="Reporter notified via email"
          icon={AlertTriangle}
          color="amber"
          badge="Action Req"
        />
        <StatCard
          title="RCA Completed"
          value={summary?.rcaCompleted || issues.filter((i) => i.investigationStatus === 'COMPLETED').length}
          subtitle="Deep root cause diagnosed"
          icon={FileCheck}
          color="purple"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <StatCard
          title="Average Ticket Readiness"
          value={`${summary?.averageReadinessScore || 85}%`}
          subtitle="Weighted diagnostic completeness"
          icon={Gauge}
          color="teal"
        />
        <StatCard
          title="Estimated Time Saved"
          value={`${summary?.estimatedHoursSaved || 14.5} hrs`}
          subtitle="* Simulated / estimated comparison vs manual operations"
          icon={Clock}
          color="emerald"
          badge="Est. Metric"
        />
      </div>

      {/* Analytics Visual Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chart 1: Status Breakdown */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Tickets by Lifecycle State</h3>
            <Layers className="w-4 h-4 text-slate-500" />
          </div>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  innerRadius={45}
                  outerRadius={70}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap justify-center gap-2 mt-2">
            {statusData.map((entry, idx) => (
              <span key={idx} className="flex items-center text-[11px] text-slate-400">
                <span className="w-2 h-2 rounded-full mr-1" style={{ backgroundColor: COLORS[idx % COLORS.length] }}></span>
                {entry.name} ({entry.value})
              </span>
            ))}
          </div>
        </div>

        {/* Chart 2: Missing Information Frequency */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Missing Diagnostics Frequency</h3>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={missingInfoData} layout="vertical" margin={{ left: 10, right: 20, top: 10, bottom: 0 }}>
                <XAxis type="number" stroke="#64748b" fontSize={10} />
                <YAxis dataKey="name" type="category" stroke="#94a3b8" fontSize={10} width={90} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#f59e0b" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 3: Incidents by Affected Service */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Incidents by Service</h3>
            <TrendingUp className="w-4 h-4 text-teal-400" />
          </div>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={serviceData} margin={{ left: 0, right: 10, top: 10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="service" stroke="#94a3b8" fontSize={10} />
                <YAxis stroke="#64748b" fontSize={10} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#14b8a6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Main Ticket Operations Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        {/* Table Filters & Search */}
        <div className="p-4 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-850">
          <div className="flex items-center space-x-2">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
              <input
                type="text"
                placeholder="Search ticket key, summary, service..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9 pr-4 py-1.5 rounded-lg bg-slate-950 border border-slate-700/80 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-teal-500 w-64"
              />
            </div>

            <div className="flex bg-slate-950 rounded-lg p-0.5 border border-slate-700">
              <button
                onClick={() => setStatusFilter('ALL')}
                className={`px-3 py-1 text-xs font-semibold rounded-md transition ${
                  statusFilter === 'ALL' ? 'bg-slate-800 text-teal-400 shadow-sm' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                All ({issues.length})
              </button>
              <button
                onClick={() => setStatusFilter('READY')}
                className={`px-3 py-1 text-xs font-semibold rounded-md transition ${
                  statusFilter === 'READY' ? 'bg-slate-800 text-teal-400 shadow-sm' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Ready
              </button>
              <button
                onClick={() => setStatusFilter('WAITING')}
                className={`px-3 py-1 text-xs font-semibold rounded-md transition ${
                  statusFilter === 'WAITING' ? 'bg-slate-800 text-teal-400 shadow-sm' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Waiting Info
              </button>
              <button
                onClick={() => setStatusFilter('INVESTIGATED')}
                className={`px-3 py-1 text-xs font-semibold rounded-md transition ${
                  statusFilter === 'INVESTIGATED' ? 'bg-slate-800 text-teal-400 shadow-sm' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Investigated
              </button>
            </div>
          </div>

          <div className="text-xs text-slate-400 flex items-center space-x-1">
            <span>Showing</span>
            <span className="font-bold text-white">{filteredIssues.length}</span>
            <span>tickets</span>
          </div>
        </div>

        {/* Table Content */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider text-[11px] border-b border-slate-800">
              <tr>
                <th className="py-3.5 px-4 font-semibold">Jira Key</th>
                <th className="py-3.5 px-4 font-semibold">Summary</th>
                <th className="py-3.5 px-4 font-semibold">Reporter</th>
                <th className="py-3.5 px-4 font-semibold">Readiness</th>
                <th className="py-3.5 px-4 font-semibold">Status</th>
                <th className="py-3.5 px-4 font-semibold">Affected Service</th>
                <th className="py-3.5 px-4 font-semibold">Probable Root Cause</th>
                <th className="py-3.5 px-4 font-semibold">AI Confidence</th>
                <th className="py-3.5 px-4 font-semibold text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filteredIssues.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-slate-500">
                    No tickets found matching current filters. Click "Simulate Jira Issue" or "Load Demo Data" above.
                  </td>
                </tr>
              ) : (
                filteredIssues.map((issue) => {
                  const isReady = issue.status === 'READY';
                  const isWaiting = issue.status === 'WAITING_FOR_INFORMATION';
                  const isInvestigated = issue.status === 'INVESTIGATED' || issue.investigationStatus === 'COMPLETED';

                  return (
                    <tr
                      key={issue.id || issue.jiraKey}
                      onClick={() => onSelectIssue(issue.jiraKey)}
                      className="hover:bg-slate-850/80 cursor-pointer transition group"
                    >
                      <td className="py-3.5 px-4 font-mono font-bold text-teal-400">
                        {issue.jiraKey}
                      </td>
                      <td className="py-3.5 px-4 font-medium text-white max-w-xs truncate">
                        {issue.summary}
                      </td>
                      <td className="py-3.5 px-4 text-slate-400 truncate max-w-[120px]">
                        {issue.reporter || 'engineer@jira.com'}
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="flex items-center space-x-2">
                          <span className={`font-mono font-bold ${
                            (issue.readinessScore || 0) >= 80 ? 'text-emerald-400' :
                            (issue.readinessScore || 0) >= 60 ? 'text-amber-400' : 'text-rose-400'
                          }`}>
                            {issue.readinessScore != null ? `${issue.readinessScore}%` : 'N/A'}
                          </span>
                          <div className="w-12 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                            <div
                              className={`h-full rounded-full ${
                                (issue.readinessScore || 0) >= 80 ? 'bg-emerald-500' :
                                (issue.readinessScore || 0) >= 60 ? 'bg-amber-500' : 'bg-rose-500'
                              }`}
                              style={{ width: `${issue.readinessScore || 0}%` }}
                            ></div>
                          </div>
                        </div>
                      </td>
                      <td className="py-3.5 px-4">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                          isInvestigated ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20' :
                          isReady ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                          isWaiting ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                          'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                        }`}>
                          {issue.status.replace(/_/g, ' ')}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 font-semibold text-slate-300">
                        {issue.affectedService ? (
                          <span className="bg-slate-800 px-2 py-0.5 rounded text-[11px] font-mono border border-slate-700">
                            {issue.affectedService}
                          </span>
                        ) : (
                          <span className="text-slate-600">—</span>
                        )}
                      </td>
                      <td className="py-3.5 px-4 text-slate-400 max-w-xs truncate">
                        {issue.probableRootCause || <span className="text-slate-600 italic">Pending investigation</span>}
                      </td>
                      <td className="py-3.5 px-4">
                        {issue.aiConfidence ? (
                          <span className="font-mono text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                            {issue.aiConfidence}%
                          </span>
                        ) : (
                          <span className="text-slate-600">—</span>
                        )}
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectIssue(issue.jiraKey);
                          }}
                          className="inline-flex items-center space-x-1 text-slate-400 group-hover:text-teal-400 transition"
                        >
                          <span>Inspect</span>
                          <ChevronRight className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

import React from 'react';
import { Bell, Menu, Moon, RefreshCw, Search, Sun, Sparkles, PlayCircle } from 'lucide-react';
import { AppView, BackendHealth, NvidiaStatus } from '../types';
import { Button } from '../components/ui/primitives';
import { useTheme } from '../theme/ThemeProvider';
import { cn } from '../lib/cn';

const TITLES: Record<AppView, { title: string; crumb: string }> = {
  overview: { title: 'Incident Operations', crumb: 'Overview' },
  issues: { title: 'Jira Issues', crumb: 'Jira Issues' },
  logs: { title: 'Log Investigations', crumb: 'Log Investigations' },
  repos: { title: 'Repository Explorer', crumb: 'Repository Explorer' },
  knowledge: { title: 'Knowledge Base', crumb: 'Similar Incidents' },
  notifications: { title: 'Notifications', crumb: 'Notifications' },
  settings: { title: 'Settings & Integration Health', crumb: 'Settings' },
  'api-flow': { title: 'API Flow Visualization', crumb: 'API Flow' },
};

interface TopBarProps {
  currentView: AppView;
  issueKey?: string | null;
  search: string;
  onSearch: (value: string) => void;
  onOpenMobile: () => void;
  onOpenNotifications: () => void;
  health: BackendHealth | null;
  aiStatus: NvidiaStatus | null;
  backendReachable: boolean;
  onSyncJira?: () => void;
  onLoadDemoData?: () => void;
  onOpenSimulate?: () => void;
  loading?: boolean;
}

export const TopBar: React.FC<TopBarProps> = ({
  currentView,
  issueKey,
  search,
  onSearch,
  onOpenMobile,
  onOpenNotifications,
  health,
  aiStatus,
  backendReachable,
  onSyncJira,
  onLoadDemoData,
  onOpenSimulate,
  loading,
}) => {
  const { theme, toggleTheme } = useTheme();
  const page = TITLES[currentView];

  return (
    <header className="sticky top-0 z-30 border-b border-line bg-surface/95 backdrop-blur">
      <div className="flex flex-col gap-3 px-4 py-3 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-center gap-3">
          <button
            type="button"
            className="rounded-md p-2 text-muted hover:bg-surface-2 md:hidden"
            onClick={onOpenMobile}
            aria-label="Open navigation"
          >
            <Menu className="h-4 w-4" />
          </button>
          <div>
            <div className="text-[11px] text-muted">
              JiraPilot AI / {page.crumb}
              {issueKey ? ` / ${issueKey}` : ''}
            </div>
            <h2 className="text-sm font-semibold text-ink">{issueKey || page.title}</h2>
          </div>
        </div>

        <div className="flex flex-1 flex-col gap-2 lg:max-w-4xl lg:flex-row lg:items-center lg:justify-end">
          <label className="relative min-w-0 flex-1 max-w-xs">
            <span className="sr-only">Search issues</span>
            <Search className="pointer-events-none absolute left-2.5 top-2.5 h-4 w-4 text-muted" />
            <input
              value={search}
              onChange={(e) => onSearch(e.target.value)}
              placeholder="Search issue key, summary..."
              className="h-9 w-full rounded-md border border-line bg-canvas pl-8 pr-3 text-xs text-ink placeholder:text-muted focus:border-accent focus:outline-none"
            />
          </label>

          <div className="flex flex-wrap items-center gap-2">
            {/* Sync Jira (KAN) Action Button */}
            {onSyncJira && (
              <Button
                variant="primary"
                size="sm"
                onClick={onSyncJira}
                disabled={loading}
                title="Fetch and synchronize live tickets from Atlassian Jira Cloud (project KAN)"
                className="bg-indigo-600 hover:bg-indigo-500 text-white shadow-sm font-semibold active:scale-95 transition"
              >
                <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
                <span>Sync Jira (KAN)</span>
              </Button>
            )}

            {/* Load Demo Data Button */}
            {onLoadDemoData && (
              <Button
                variant="secondary"
                size="sm"
                onClick={onLoadDemoData}
                disabled={loading}
                title="Load synthetic hackathon scenario tickets (NOVA-101 to NOVA-107)"
                className="hidden sm:inline-flex items-center gap-1.5 active:scale-95 transition"
              >
                <Sparkles className="h-3.5 w-3.5 text-amber-500" />
                <span>Demo Data</span>
              </Button>
            )}

            {/* Simulate Issue Button */}
            {onOpenSimulate && (
              <Button
                variant="secondary"
                size="sm"
                onClick={onOpenSimulate}
                title="Simulate incoming Jira issue"
                className="hidden md:inline-flex items-center gap-1.5 active:scale-95 transition"
              >
                <PlayCircle className="h-3.5 w-3.5 text-teal" />
                <span>Simulate</span>
              </Button>
            )}

            {/* Status Pills */}
            <StatusPill
              label={health?.demoMode ? 'Demo Jira' : backendReachable ? 'Live Jira mode' : 'Jira unknown'}
              ok={backendReachable}
              warn={Boolean(health?.demoMode)}
            />
            <StatusPill
              label={aiStatus?.configured ? `AI · ${aiStatus.model}` : 'AI · fallback'}
              ok={Boolean(aiStatus?.configured)}
              warn={!aiStatus?.configured}
            />

            <Button variant="ghost" size="sm" onClick={onOpenNotifications} aria-label="Open notifications">
              <Bell className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={toggleTheme} aria-label="Toggle theme">
              {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};

const StatusPill: React.FC<{ label: string; ok?: boolean; warn?: boolean }> = ({ label, ok, warn }) => (
  <span
    className={cn(
      'hidden items-center gap-1.5 rounded-full border px-2 py-1 text-[11px] font-medium lg:inline-flex',
      warn ? 'border-amber/30 bg-amber-soft text-amber' : ok ? 'border-teal/30 bg-teal-soft text-teal' : 'border-line bg-surface-2 text-muted'
    )}
    title={label}
  >
    {ok && !warn ? <span className="h-1.5 w-1.5 rounded-full bg-teal" /> : warn ? <RefreshCw className="h-3 w-3" /> : <span className="h-1.5 w-1.5 rounded-full bg-muted" />}
    <span className="max-w-[9rem] truncate">{label}</span>
  </span>
);

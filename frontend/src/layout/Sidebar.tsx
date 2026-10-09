import React from 'react';
import {
  Activity,
  Bell,
  BookOpen,
  GitBranch,
  LayoutDashboard,
  PanelLeft,
  Settings,
  Ticket,
  FileSearch,
} from 'lucide-react';
import { AppView } from '../types';
import { cn } from '../lib/cn';

interface SidebarProps {
  currentView: AppView;
  onNavigate: (view: AppView) => void;
  collapsed: boolean;
  onToggle: () => void;
  mobileOpen: boolean;
  onCloseMobile: () => void;
  demoMode?: boolean | null;
  notificationCount: number;
}

const NAV = [
  { id: 'overview' as const, label: 'Overview', icon: LayoutDashboard },
  { id: 'issues' as const, label: 'Jira Issues', icon: Ticket },
  { id: 'logs' as const, label: 'Log Investigations', icon: FileSearch },
  { id: 'repos' as const, label: 'Repository Explorer', icon: GitBranch },
  { id: 'knowledge' as const, label: 'Knowledge Base', icon: BookOpen },
  { id: 'notifications' as const, label: 'Notifications', icon: Bell },
  { id: 'settings' as const, label: 'Settings', icon: Settings },
];

export const Sidebar: React.FC<SidebarProps> = ({
  currentView,
  onNavigate,
  collapsed,
  onToggle,
  mobileOpen,
  onCloseMobile,
  demoMode,
  notificationCount,
}) => {
  const content = (
    <div className="flex h-full flex-col">
      <div className={cn('flex items-center gap-2.5 border-b border-line px-3 py-4', collapsed && 'justify-center px-2')}>
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent text-white">
          <Activity className="h-4 w-4" />
        </div>
        {!collapsed && (
          <div className="min-w-0">
            <div className="truncate text-sm font-semibold text-ink">JiraPilot AI</div>
            <div className="text-[11px] text-muted">Incident operations</div>
          </div>
        )}
      </div>

      <nav className="flex-1 space-y-1 p-2" aria-label="Primary">
        {NAV.map((item) => {
          const active = currentView === item.id;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => {
                onNavigate(item.id);
                onCloseMobile();
              }}
              className={cn(
                'flex w-full items-center gap-2.5 rounded-md px-2.5 py-2 text-sm transition-colors',
                active ? 'bg-accent-soft text-accent' : 'text-muted hover:bg-surface-2 hover:text-ink',
                collapsed && 'justify-center px-2'
              )}
              title={item.label}
            >
              <item.icon className="h-4 w-4 shrink-0" />
              {!collapsed && (
                <span className="flex-1 truncate text-left">{item.label}</span>
              )}
              {!collapsed && item.id === 'notifications' && notificationCount > 0 && (
                <span className="rounded-full bg-amber-soft px-1.5 text-[10px] font-semibold text-amber">
                  {notificationCount}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      <div className="border-t border-line p-3">
        {!collapsed && demoMode != null && (
          <div className="mb-3 rounded-md border border-line bg-surface-2 px-2.5 py-2 text-[11px] text-muted">
            {demoMode ? 'Demo mode is active. Synthetic Jira client in use.' : 'Live Jira mode is enabled by backend configuration.'}
          </div>
        )}
        <button
          type="button"
          onClick={onToggle}
          className="flex w-full items-center justify-center gap-2 rounded-md px-2 py-2 text-xs text-muted hover:bg-surface-2 hover:text-ink"
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <PanelLeft className="h-4 w-4" />
          {!collapsed && <span>Collapse</span>}
        </button>
      </div>
    </div>
  );

  return (
    <>
      <aside
        className={cn(
          'hidden h-screen shrink-0 border-r border-line bg-surface transition-[width] duration-200 md:block',
          collapsed ? 'w-[72px]' : 'w-60'
        )}
      >
        {content}
      </aside>
      {mobileOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <button type="button" className="absolute inset-0 bg-ink/40" aria-label="Close navigation" onClick={onCloseMobile} />
          <aside className="relative h-full w-64 bg-surface shadow-panel">{content}</aside>
        </div>
      )}
    </>
  );
};

import React, { useState } from 'react';
import { AppView, BackendHealth, NvidiaStatus } from '../types';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';

interface AppShellProps {
  currentView: AppView;
  onNavigate: (view: AppView) => void;
  issueKey?: string | null;
  search: string;
  onSearch: (value: string) => void;
  onOpenNotifications: () => void;
  health: BackendHealth | null;
  aiStatus: NvidiaStatus | null;
  backendReachable: boolean;
  notificationCount: number;
  onSyncJira?: () => void;
  onLoadDemoData?: () => void;
  onOpenSimulate?: () => void;
  loading?: boolean;
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({
  currentView,
  onNavigate,
  issueKey,
  search,
  onSearch,
  onOpenNotifications,
  health,
  aiStatus,
  backendReachable,
  notificationCount,
  onSyncJira,
  onLoadDemoData,
  onOpenSimulate,
  loading,
  children,
}) => {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-canvas text-ink">
      <Sidebar
        currentView={currentView}
        onNavigate={onNavigate}
        collapsed={collapsed}
        onToggle={() => setCollapsed((v) => !v)}
        mobileOpen={mobileOpen}
        onCloseMobile={() => setMobileOpen(false)}
        demoMode={health?.demoMode}
        notificationCount={notificationCount}
      />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar
          currentView={currentView}
          issueKey={issueKey}
          search={search}
          onSearch={onSearch}
          onOpenMobile={() => setMobileOpen(true)}
          onOpenNotifications={onOpenNotifications}
          health={health}
          aiStatus={aiStatus}
          backendReachable={backendReachable}
          onSyncJira={onSyncJira}
          onLoadDemoData={onLoadDemoData}
          onOpenSimulate={onOpenSimulate}
          loading={loading}
        />
        <main className="mx-auto w-full max-w-[1400px] flex-1 px-4 py-6 sm:px-6">{children}</main>
      </div>
    </div>
  );
};

import React, { useEffect, useState } from 'react';
import { BackendHealth, NvidiaStatus, PolicySettings } from '../types';
import { api } from '../api/client';
import { Button, Card, PageHeader, StatusBadge } from '../components/ui/primitives';
import { PolicyPanel } from '../components/PolicyPanel';
import { useToast } from '../components/ui/Toast';

interface SettingsPageProps {
  health: BackendHealth | null;
  aiStatus: NvidiaStatus | null;
  backendReachable: boolean;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({ health, aiStatus, backendReachable }) => {
  const { push } = useToast();
  const [policy, setPolicy] = useState<PolicySettings | null>(null);
  const [recipient, setRecipient] = useState('reporter@example.com');
  const [sending, setSending] = useState(false);

  useEffect(() => {
    api.getPolicy().then(setPolicy).catch(() => push({ kind: 'error', title: 'Unable to load policy settings' }));
  }, [push]);

  return (
    <div className="space-y-6">
      <PageHeader title="Settings & Integration Health" description="Policy controls and live service status. Credentials stay on the backend." />

      <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
        <Card className="p-4">
          <div className="text-xs uppercase tracking-wide text-muted">Backend</div>
          <div className="mt-2 flex items-center justify-between">
            <span className="text-sm text-ink">{health?.service || 'JiraPilot orchestrator'}</span>
            <StatusBadge tone={backendReachable ? 'success' : 'danger'}>{backendReachable ? health?.status || 'UP' : 'Down'}</StatusBadge>
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-xs uppercase tracking-wide text-muted">Jira</div>
          <div className="mt-2 flex items-center justify-between">
            <span className="text-sm text-ink">{health?.demoMode ? 'Demo client' : 'Live mode configured'}</span>
            <StatusBadge tone="warning">{health?.demoMode ? 'Demo' : backendReachable ? 'Configured' : 'Unknown'}</StatusBadge>
          </div>
          <p className="mt-2 text-[11px] text-muted">This reflects backend DEMO_MODE, not a live Jira ping.</p>
        </Card>
        <Card className="p-4">
          <div className="text-xs uppercase tracking-wide text-muted">AI provider</div>
          <div className="mt-2 flex items-center justify-between">
            <span className="text-sm text-ink">{aiStatus?.configured ? aiStatus.model : 'Deterministic fallback'}</span>
            <StatusBadge tone={aiStatus?.configured ? 'success' : 'warning'}>{aiStatus?.activeMode || 'unknown'}</StatusBadge>
          </div>
        </Card>
      </div>

      <Card className="p-4">
        <h3 className="mb-2 text-sm font-semibold text-ink">Test email delivery</h3>
        <p className="mb-3 text-xs text-muted">Uses the existing notification endpoint. Recipients must pass backend allowlist checks.</p>
        <div className="flex flex-col gap-2 sm:flex-row">
          <input
            value={recipient}
            onChange={(e) => setRecipient(e.target.value)}
            className="h-9 flex-1 rounded-md border border-line bg-canvas px-3 text-sm text-ink"
            aria-label="Test email recipient"
          />
          <Button
            variant="primary"
            disabled={sending || !recipient.trim()}
            onClick={async () => {
              setSending(true);
              try {
                await api.sendTestEmail(recipient.trim());
                push({ kind: 'success', title: 'Test email request accepted' });
              } catch {
                push({ kind: 'error', title: 'Test email failed' });
              } finally {
                setSending(false);
              }
            }}
          >
            {sending ? 'Sending…' : 'Send test email'}
          </Button>
        </div>
      </Card>

      {policy && (
        <PolicyPanel
          policy={policy}
          onChange={setPolicy}
          onSave={async () => {
            const updated = await api.updatePolicy(policy);
            setPolicy(updated);
            push({ kind: 'success', title: 'Policy saved' });
          }}
        />
      )}
    </div>
  );
};

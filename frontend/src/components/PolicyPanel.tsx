import React, { useState } from 'react';
import { PolicySettings } from '../types';
import { Button, Card } from './ui/primitives';

interface PolicyPanelProps {
  policy: PolicySettings;
  onChange: (policy: PolicySettings) => void;
  onSave: () => Promise<void>;
}

export const PolicyPanel: React.FC<PolicyPanelProps> = ({ policy, onChange, onSave }) => {
  const [saving, setSaving] = useState(false);

  const numberField = (label: string, key: keyof PolicySettings) => (
    <label className="text-xs text-muted">
      {label}
      <input
        type="number"
        value={Number(policy[key] ?? 0)}
        onChange={(e) => onChange({ ...policy, [key]: parseInt(e.target.value, 10) || 0 })}
        className="mt-1 h-8 w-full rounded-md border border-line bg-canvas px-2 text-sm text-ink"
      />
    </label>
  );

  return (
    <form
      className="space-y-4"
      onSubmit={async (e) => {
        e.preventDefault();
        setSaving(true);
        try {
          await onSave();
        } finally {
          setSaving(false);
        }
      }}
    >
      <Card className="p-4">
        <h3 className="mb-3 text-sm font-semibold text-ink">Workflow automation</h3>
        <div className="space-y-3">
          {[
            ['autoInvestigateEnabled', 'Automatic investigation on ready', 'Triggers RCA when readiness passes the threshold'],
            ['autoCommentEnabled', 'Automated Jira comments', 'Posts missing-info lists and investigation reports'],
            ['autoEmailEnabled', 'Automated reporter emails', 'Notifies the reporter when diagnostics are missing'],
          ].map(([key, title, hint]) => (
            <label key={key} className="flex items-center justify-between gap-4 border-b border-line pb-3 last:border-0 last:pb-0">
              <span>
                <span className="block text-sm text-ink">{title}</span>
                <span className="text-xs text-muted">{hint}</span>
              </span>
              <input
                type="checkbox"
                checked={Boolean(policy[key as keyof PolicySettings])}
                onChange={(e) => onChange({ ...policy, [key]: e.target.checked })}
              />
            </label>
          ))}
        </div>
      </Card>

      <Card className="p-4">
        <h3 className="mb-3 text-sm font-semibold text-ink">Readiness weights</h3>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {numberField('Logs', 'weightLogs')}
          {numberField('API details', 'weightApiDetails')}
          {numberField('Request payload', 'weightRequestPayload')}
          {numberField('Description', 'weightDescription')}
          {numberField('Environment', 'weightEnvironment')}
          {numberField('Error message', 'weightErrorMessage')}
        </div>
      </Card>

      <Card className="p-4">
        <h3 className="mb-3 text-sm font-semibold text-ink">Thresholds</h3>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          {numberField('Readiness threshold', 'readinessThreshold')}
          {numberField('AI confidence min', 'confidenceThreshold')}
          {numberField('Similarity threshold', 'similarityThreshold')}
        </div>
        <div className="mt-4 flex justify-end">
          <Button type="submit" variant="primary" disabled={saving}>
            {saving ? 'Saving…' : 'Save policy'}
          </Button>
        </div>
      </Card>
    </form>
  );
};

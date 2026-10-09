import React, { useState } from 'react';
import { Bell } from 'lucide-react';
import { MockEmail } from '../types';
import { Card, EmptyState, PageHeader, StatusBadge } from '../components/ui/primitives';
import { notificationTone } from '../lib/status';
import { formatDateTime, labelStatus } from '../lib/format';

interface NotificationsPageProps {
  emails: MockEmail[];
  onSelectIssue: (key: string) => void;
}

export const NotificationsPage: React.FC<NotificationsPageProps> = ({ emails, onSelectIssue }) => {
  const [activeId, setActiveId] = useState<number | null>(emails[0]?.id ?? null);
  const active = emails.find((email) => email.id === activeId) || emails[0];

  return (
    <div>
      <PageHeader title="Notifications" description="Email delivery history from the orchestrator. Status values come from the backend log." />
      {emails.length === 0 ? (
        <Card>
          <EmptyState
            icon={Bell}
            title="No notifications recorded yet"
            description="Reporter emails appear here after validation or investigation workflows dispatch them."
          />
        </Card>
      ) : (
        <Card className="grid min-h-[28rem] grid-cols-1 md:grid-cols-3">
          <div className="border-b border-line md:border-b-0 md:border-r">
            {emails.map((email) => (
              <button
                key={email.id}
                type="button"
                onClick={() => setActiveId(email.id)}
                className={`block w-full border-b border-line px-4 py-3 text-left ${active?.id === email.id ? 'bg-surface-2' : 'hover:bg-surface-2'}`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono text-xs font-semibold text-accent">{email.jiraKey}</span>
                  <StatusBadge tone={notificationTone(email.status)}>{labelStatus(email.status)}</StatusBadge>
                </div>
                <div className="mt-1 truncate text-xs text-ink">{email.subject}</div>
                <div className="text-[11px] text-muted">{formatDateTime(email.sentAt)}</div>
              </button>
            ))}
          </div>
          <div className="p-5 md:col-span-2">
            {active && (
              <>
                <div className="mb-3 flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-ink">{active.subject}</h3>
                  <button type="button" className="text-xs text-accent" onClick={() => onSelectIssue(active.jiraKey)}>
                    Open issue
                  </button>
                </div>
                <p className="text-xs text-muted">To {active.recipient}</p>
                <pre className="mt-4 whitespace-pre-wrap rounded-lg border border-line bg-canvas p-4 text-xs text-ink">{active.content}</pre>
              </>
            )}
          </div>
        </Card>
      )}
    </div>
  );
};

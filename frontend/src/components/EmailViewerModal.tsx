import React, { useEffect, useState } from 'react';
import { Mail } from 'lucide-react';
import { MockEmail } from '../types';
import { api } from '../api/client';
import { Dialog, EmptyState, StatusBadge } from './ui/primitives';
import { notificationTone } from '../lib/status';
import { formatDateTime, labelStatus } from '../lib/format';

interface EmailViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedKey?: string;
}

export const EmailViewerModal: React.FC<EmailViewerModalProps> = ({ isOpen, onClose }) => {
  const [emails, setEmails] = useState<MockEmail[]>([]);
  const [activeEmail, setActiveEmail] = useState<MockEmail | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    api.getAllEmails().then((data) => {
      setEmails(data);
      setActiveEmail(data[0] || null);
    }).catch(() => setEmails([]));
  }, [isOpen]);

  return (
    <Dialog open={isOpen} onClose={onClose} title="Notification inbox" description="Backend email delivery log" icon={Mail} wide>
      <div className="grid min-h-[24rem] grid-cols-1 md:grid-cols-3">
        <div className="border-b border-line md:border-b-0 md:border-r">
          {emails.length === 0 ? (
            <EmptyState title="No notification emails recorded yet." description="Emails appear after validation or investigation workflows dispatch them." />
          ) : (
            emails.map((email) => (
              <button
                key={email.id}
                type="button"
                onClick={() => setActiveEmail(email)}
                className={`block w-full border-b border-line px-4 py-3 text-left ${activeEmail?.id === email.id ? 'bg-surface-2' : 'hover:bg-surface-2'}`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-semibold text-accent">{email.jiraKey}</span>
                  <StatusBadge tone={notificationTone(email.status)}>{labelStatus(email.status)}</StatusBadge>
                </div>
                <div className="mt-1 truncate text-xs text-ink">{email.subject}</div>
                <div className="text-[11px] text-muted">{formatDateTime(email.sentAt)}</div>
              </button>
            ))
          )}
        </div>
        <div className="p-5 md:col-span-2">
          {activeEmail ? (
            <>
              <h3 className="text-sm font-semibold text-ink">{activeEmail.subject}</h3>
              <p className="mt-1 text-xs text-muted">To {activeEmail.recipient}</p>
              <pre className="mt-4 whitespace-pre-wrap rounded-lg border border-line bg-canvas p-4 text-xs">{activeEmail.content}</pre>
            </>
          ) : (
            <EmptyState title="Select a notification" description="Choose an email from the list to inspect delivery content." />
          )}
        </div>
      </div>
    </Dialog>
  );
};

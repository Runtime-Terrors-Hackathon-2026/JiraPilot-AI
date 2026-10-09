import React, { useState, useEffect } from 'react';
import { MockEmail } from '../types';
import { api } from '../api/client';
import { X, Mail, Clock, User, CheckCircle2, RefreshCw } from 'lucide-react';

interface EmailViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedKey?: string;
}

export const EmailViewerModal: React.FC<EmailViewerModalProps> = ({ isOpen, onClose, selectedKey }) => {
  const [emails, setEmails] = useState<MockEmail[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeEmail, setActiveEmail] = useState<MockEmail | null>(null);

  const fetchEmails = async () => {
    setLoading(true);
    try {
      const data = await api.getAllEmails();
      setEmails(data);
      if (data.length > 0 && !activeEmail) {
        setActiveEmail(data[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchEmails();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-4xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-850">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-teal-500/10 text-teal-400 border border-teal-500/20">
              <Mail className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Mock Email Notification Viewer</h2>
              <p className="text-xs text-slate-400">Live inspection of automated reporter emails dispatched by JiraPilot AI</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={fetchEmails}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
              title="Refresh Emails"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="grid grid-cols-1 md:grid-cols-3 flex-1 overflow-hidden">
          {/* Email List */}
          <div className="border-r border-slate-800 overflow-y-auto max-h-[60vh] bg-slate-900/50">
            {emails.length === 0 ? (
              <div className="p-6 text-center text-xs text-slate-500">
                No notification emails recorded yet.
              </div>
            ) : (
              emails.map((email) => (
                <div
                  key={email.id}
                  onClick={() => setActiveEmail(email)}
                  className={`p-4 border-b border-slate-800 cursor-pointer transition ${
                    activeEmail?.id === email.id ? 'bg-slate-800/80 border-l-2 border-l-teal-500' : 'hover:bg-slate-850'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono text-xs font-bold text-teal-400">{email.jiraKey}</span>
                    <span className="text-[10px] text-slate-500">{new Date(email.sentAt).toLocaleTimeString()}</span>
                  </div>
                  <div className="text-xs font-medium text-slate-200 truncate">{email.subject}</div>
                  <div className="text-[11px] text-slate-400 truncate mt-1">To: {email.recipient}</div>
                </div>
              ))
            )}
          </div>

          {/* Email Preview */}
          <div className="md:col-span-2 p-6 overflow-y-auto max-h-[60vh] bg-slate-950 flex flex-col justify-between">
            {activeEmail ? (
              <div>
                <div className="border-b border-slate-800 pb-4 mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-bold text-white">{activeEmail.subject}</span>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-teal-500/10 text-teal-400 border border-teal-500/20 flex items-center space-x-1">
                      <CheckCircle2 className="w-3 h-3 mr-1" />
                      <span>{activeEmail.status}</span>
                    </span>
                  </div>
                  <div className="space-y-1 text-xs text-slate-400">
                    <div><span className="text-slate-500">From:</span> jirapilot-notifications@example.com</div>
                    <div><span className="text-slate-500">To:</span> {activeEmail.recipient}</div>
                    <div><span className="text-slate-500">Jira Ticket:</span> <span className="text-teal-400 font-mono font-bold">{activeEmail.jiraKey}</span></div>
                  </div>
                </div>

                <div className="p-4 bg-slate-900 rounded-xl border border-slate-800 text-xs text-slate-300 whitespace-pre-wrap leading-relaxed font-mono">
                  {activeEmail.content}
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-slate-500 text-xs">
                Select an email from the left sidebar to preview content.
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-850 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

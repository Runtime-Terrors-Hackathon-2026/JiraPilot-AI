import React, { useMemo, useState } from 'react';
import { FileText, RefreshCw, Send, Terminal, Upload } from 'lucide-react';
import { IssueAttachment } from '../types';
import { api } from '../api/client';
import { Button, Card, CloneCommand, Dialog, EmptyState, StatusBadge } from './ui/primitives';
import { useToast } from './ui/Toast';
import { attachmentTone } from '../lib/status';
import { formatBytes, labelStatus } from '../lib/format';

interface Props {
  issueKey: string;
  attachments?: IssueAttachment[];
  onRefresh: () => void;
}

function parseAnalysis(att?: IssueAttachment) {
  if (!att?.analysisJson) return null;
  try {
    return JSON.parse(att.analysisJson);
  } catch {
    return null;
  }
}

export const LogInvestigationCard: React.FC<Props> = ({ issueKey, attachments = [], onRefresh }) => {
  const { push } = useToast();
  const [selectedAttId, setSelectedAttId] = useState<number | null>(attachments[0]?.id || null);
  const [uploading, setUploading] = useState(false);
  const [pastedLog, setPastedLog] = useState('');
  const [showPasteModal, setShowPasteModal] = useState(false);
  const [commentPreview, setCommentPreview] = useState<string | null>(null);
  const [emailPreview, setEmailPreview] = useState<{ html: string; text: string; subject: string } | null>(null);
  const [postingComment, setPostingComment] = useState(false);
  const [sendingEmail, setSendingEmail] = useState(false);

  const activeAtt = attachments.find((a) => a.id === selectedAttId) || attachments[0];
  const parsed = useMemo(() => parseAnalysis(activeAtt), [activeAtt]);
  const endpoints = parsed?.endpoints || [];
  const evidence = (parsed?.evidence || []).slice(0, 40);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await api.uploadAttachmentFile(issueKey, file);
      push({ kind: 'success', title: `Analyzed ${file.name}` });
      onRefresh();
    } catch (err: any) {
      push({ kind: 'error', title: 'Upload failed', message: err.message });
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card className="overflow-hidden">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line px-5 py-4">
        <div>
          <h3 className="text-sm font-semibold text-ink">Attachments and logs</h3>
          <p className="text-xs text-muted">Redaction, endpoint extraction and repository matching for {issueKey}</p>
        </div>
        <div className="flex gap-2">
          <label className="inline-flex h-8 cursor-pointer items-center gap-1.5 rounded-md bg-accent px-2.5 text-xs font-medium text-white">
            <Upload className="h-3.5 w-3.5" />
            Upload log
            <input type="file" className="hidden" accept=".log,.txt,.json,.jsonl,.gz" onChange={handleFileUpload} disabled={uploading} />
          </label>
          <Button size="sm" onClick={() => setShowPasteModal(true)}>
            <Terminal className="h-3.5 w-3.5" />
            Paste logs
          </Button>
        </div>
      </div>

      {attachments.length === 0 ? (
        <EmptyState
          icon={FileText}
          title="No log attachments have been analyzed yet."
          description="Add a synthetic log attachment to begin an investigation."
          action={
            <Button
              onClick={() => {
                setPastedLog(`2026-10-09 08:14:22.102 WARN c.n.inventory.service.ResourceAllocationService - [corrId=CORR-DEMO-1001] Resource DEMO-RESOURCE-1001 already reserved.\norg.springframework.dao.DataIntegrityViolationException: Pre-existing allocation detected for resource ID: DEMO-RESOURCE-1001\nHTTP 409 Conflict returned`);
                setShowPasteModal(true);
              }}
            >
              Load sample telemetry
            </Button>
          }
        />
      ) : (
        <>
          <div className="flex gap-2 overflow-x-auto border-b border-line px-5 py-2">
            {attachments.map((att) => (
              <button
                key={att.id}
                type="button"
                onClick={() => setSelectedAttId(att.id)}
                className={`flex items-center gap-2 rounded-md px-2.5 py-1.5 text-xs ${activeAtt?.id === att.id ? 'bg-accent-soft text-accent' : 'text-muted hover:bg-surface-2'}`}
              >
                {att.filename}
                <StatusBadge tone={attachmentTone(att.status)}>{labelStatus(att.status)}</StatusBadge>
              </button>
            ))}
          </div>
          {activeAtt && (
            <div className="grid grid-cols-1 gap-4 p-5 lg:grid-cols-3">
              <div className="space-y-4 lg:col-span-2">
                <div className="grid grid-cols-2 gap-3 rounded-lg border border-line p-3 sm:grid-cols-4">
                  <Meta label="Service" value={activeAtt.primaryService} />
                  <Meta label="Endpoint" value={activeAtt.primaryEndpoint} />
                  <Meta label="HTTP" value={activeAtt.primaryStatus ? `HTTP ${activeAtt.primaryStatus}` : undefined} />
                  <Meta label="Correlation ID" value={activeAtt.correlationId} />
                </div>
                <div className="rounded-lg border border-line p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <h4 className="text-xs font-semibold uppercase tracking-wide text-muted">Evidence-backed hypothesis</h4>
                    <StatusBadge tone="warning">
                      {activeAtt.confidenceCategory || 'MEDIUM'} ({Math.round((activeAtt.confidenceScore || 0) * 100)}%)
                    </StatusBadge>
                  </div>
                  <p className="text-sm text-ink">{activeAtt.probableRootCause || 'Inconclusive — insufficient diagnostic telemetry.'}</p>
                  <p className="mt-2 text-xs text-muted">{activeAtt.analysisSummary}</p>
                  <p className="mt-2 text-[11px] text-muted">This is a hypothesis from the analysis engine, not a confirmed root cause.</p>
                </div>
                {endpoints.length > 0 && (
                  <div className="rounded-lg border border-line p-4">
                    <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">Extracted API endpoints</h4>
                    <ul className="space-y-1 font-mono text-xs">
                      {endpoints.map((ep: any, i: number) => (
                        <li key={i}>{typeof ep === 'string' ? ep : `${ep.method || ''} ${ep.endpoint || JSON.stringify(ep)}`}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {evidence.length > 0 && (
                  <div className="overflow-hidden rounded-lg bg-log">
                    <div className="border-b border-white/10 px-3 py-2 text-xs text-log-ink">Evidence with line references</div>
                    <div className="max-h-64 overflow-auto p-3 font-mono text-[11px] text-log-ink">
                      {evidence.map((row: any, i: number) => (
                        <div key={i} className="grid grid-cols-[3rem_1fr] gap-2">
                          <span className="text-right text-muted">{row.line || row.lineNumber || i + 1}</span>
                          <span>{row.message || row.text || JSON.stringify(row)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                <div>
                  <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">Approved clone command</h4>
                  <p className="mb-2 text-xs text-ink">{activeAtt.recommendedRepo || 'No repository match yet'}</p>
                  <CloneCommand command={activeAtt.cloneCommand} onCopied={() => push({ kind: 'success', title: 'Clone command copied' })} />
                </div>
              </div>
              <div className="space-y-3">
                <Button className="w-full" onClick={async () => {
                  try {
                    const res = await api.getCommentPreview(activeAtt.id);
                    setCommentPreview(res.commentPreview);
                  } catch (err: any) {
                    push({ kind: 'error', title: 'Comment preview failed', message: err.message });
                  }
                }}>Preview Jira comment</Button>
                <Button className="w-full" onClick={async () => {
                  try {
                    setEmailPreview(await api.getEmailPreview(activeAtt.id));
                  } catch (err: any) {
                    push({ kind: 'error', title: 'Email preview failed', message: err.message });
                  }
                }}>
                  <Send className="h-3.5 w-3.5" />
                  Preview email
                </Button>
                <Button className="w-full" onClick={async () => {
                  try {
                    await api.retryAttachment(activeAtt.id);
                    push({ kind: 'success', title: 'Re-analysis completed' });
                    onRefresh();
                  } catch (err: any) {
                    push({ kind: 'error', title: 'Retry failed', message: err.message });
                  }
                }}>
                  <RefreshCw className="h-3.5 w-3.5" />
                  Retry analysis
                </Button>
                <div className="rounded-lg border border-line p-3 text-xs text-muted">
                  <Row label="Size" value={formatBytes(activeAtt.sizeBytes)} />
                  <Row label="MIME" value={activeAtt.mimeType || 'text/plain'} />
                  <Row label="SHA-256" value={activeAtt.sha256Hash || '—'} />
                  <Row label="Jira comment" value={activeAtt.jiraCommentPosted ? 'Posted' : 'Draft'} />
                  <Row label="Email" value={activeAtt.emailSent ? 'Sent' : 'Not sent'} />
                  {activeAtt.quarantined && <Row label="Quarantine" value={activeAtt.quarantineReason || 'Needs review'} />}
                </div>
              </div>
            </div>
          )}
        </>
      )}

      <Dialog open={showPasteModal} onClose={() => setShowPasteModal(false)} title="Paste application telemetry" description="Logs are processed by the existing attachment API.">
        <div className="space-y-3 p-5">
          <textarea className="h-64 w-full rounded-lg border border-line bg-log p-3 font-mono text-xs text-log-ink" value={pastedLog} onChange={(e) => setPastedLog(e.target.value)} />
          <div className="flex justify-end gap-2">
            <Button onClick={() => setShowPasteModal(false)}>Cancel</Button>
            <Button
              variant="primary"
              disabled={uploading || !pastedLog.trim()}
              onClick={async () => {
                setUploading(true);
                try {
                  await api.uploadAttachmentText(issueKey, pastedLog, 'pasted_telemetry.log');
                  setShowPasteModal(false);
                  setPastedLog('');
                  push({ kind: 'success', title: 'Pasted telemetry analyzed' });
                  onRefresh();
                } catch (err: any) {
                  push({ kind: 'error', title: 'Analysis failed', message: err.message });
                } finally {
                  setUploading(false);
                }
              }}
            >
              {uploading ? 'Analyzing…' : 'Analyze telemetry'}
            </Button>
          </div>
        </div>
      </Dialog>

      <Dialog open={Boolean(commentPreview)} onClose={() => setCommentPreview(null)} title="Jira comment preview" description={`Standardized investigation report for ${issueKey}`} wide>
        <div className="space-y-3 p-5">
          <pre className="max-h-96 overflow-auto whitespace-pre-wrap rounded-lg border border-line bg-canvas p-4 text-xs">{commentPreview}</pre>
          <div className="flex justify-between">
            <Button onClick={() => commentPreview && navigator.clipboard.writeText(commentPreview)}>Copy markdown</Button>
            <div className="flex gap-2">
              <Button onClick={() => setCommentPreview(null)}>Close</Button>
              {activeAtt && (
                <Button
                  variant="primary"
                  disabled={postingComment}
                  onClick={async () => {
                    setPostingComment(true);
                    try {
                      const res = await api.postCommentToJira(activeAtt.id);
                      push({ kind: 'success', title: res.message || 'Comment posted' });
                      setCommentPreview(null);
                      onRefresh();
                    } catch (err: any) {
                      push({ kind: 'error', title: 'Post failed', message: err.message });
                    } finally {
                      setPostingComment(false);
                    }
                  }}
                >
                  {postingComment ? 'Posting…' : 'Post comment to Jira'}
                </Button>
              )}
            </div>
          </div>
        </div>
      </Dialog>

      <Dialog open={Boolean(emailPreview)} onClose={() => setEmailPreview(null)} title="Email notification preview" description={emailPreview?.subject} wide>
        <div className="space-y-3 p-5">
          {emailPreview && (
            <div className="max-h-80 overflow-auto rounded-lg border border-line bg-white p-4 text-slate-900" dangerouslySetInnerHTML={{ __html: emailPreview.html }} />
          )}
          <div className="flex justify-end gap-2">
            <Button onClick={() => setEmailPreview(null)}>Close</Button>
            {activeAtt && (
              <Button
                variant="primary"
                disabled={sendingEmail}
                onClick={async () => {
                  setSendingEmail(true);
                  try {
                    await api.sendEmail(activeAtt.id);
                    push({ kind: 'success', title: 'Email dispatch accepted by backend' });
                    setEmailPreview(null);
                    onRefresh();
                  } catch (err: any) {
                    push({ kind: 'error', title: 'Email send failed', message: err.message });
                  } finally {
                    setSendingEmail(false);
                  }
                }}
              >
                {sendingEmail ? 'Sending…' : 'Send notification'}
              </Button>
            )}
          </div>
        </div>
      </Dialog>
    </Card>
  );
};

const Meta: React.FC<{ label: string; value?: string | number | null }> = ({ label, value }) => (
  <div>
    <div className="text-[11px] uppercase tracking-wide text-muted">{label}</div>
    <div className="truncate text-sm font-medium text-ink">{value || '—'}</div>
  </div>
);

const Row: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="flex justify-between gap-2 py-1">
    <span>{label}</span>
    <span className="truncate font-mono text-ink">{value}</span>
  </div>
);

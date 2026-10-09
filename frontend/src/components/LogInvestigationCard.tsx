import React, { useState } from 'react';
import {
  FileText, Upload, RefreshCw, Send, MessageSquare, Copy, Check,
  AlertTriangle, ShieldCheck, Terminal, ExternalLink, Cpu, Info, CheckCircle2
} from 'lucide-react';
import { IssueAttachment } from '../types';
import { api } from '../api/client';

interface Props {
  issueKey: string;
  attachments?: IssueAttachment[];
  onRefresh: () => void;
}

export const LogInvestigationCard: React.FC<Props> = ({ issueKey, attachments = [], onRefresh }) => {
  const [selectedAttId, setSelectedAttId] = useState<number | null>(attachments[0]?.id || null);
  const [uploading, setUploading] = useState(false);
  const [copiedCmd, setCopiedCmd] = useState<string | null>(null);
  const [pastedLog, setPastedLog] = useState('');
  const [showPasteModal, setShowPasteModal] = useState(false);
  const [commentPreview, setCommentPreview] = useState<string | null>(null);
  const [emailPreview, setEmailPreview] = useState<{ html: string; text: string; subject: string } | null>(null);
  const [postingComment, setPostingComment] = useState(false);
  const [sendingEmail, setSendingEmail] = useState(false);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const activeAtt = attachments.find(a => a.id === selectedAttId) || attachments[0];

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await api.uploadAttachmentFile(issueKey, file);
      setActionSuccess(`Successfully uploaded and analyzed ${file.name}`);
      onRefresh();
    } catch (err: any) {
      alert(err.message || 'Failed to process file');
    } finally {
      setUploading(false);
    }
  };

  const handlePasteSubmit = async () => {
    if (!pastedLog.trim()) return;
    setUploading(true);
    try {
      await api.uploadAttachmentText(issueKey, pastedLog, 'pasted_telemetry.log');
      setShowPasteModal(false);
      setPastedLog('');
      setActionSuccess('Successfully analyzed pasted telemetry log.');
      onRefresh();
    } catch (err: any) {
      alert(err.message || 'Failed to analyze text');
    } finally {
      setUploading(false);
    }
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCmd(label);
    setTimeout(() => setCopiedCmd(null), 2500);
  };

  const openCommentPreview = async (attId: number) => {
    try {
      const res = await api.getCommentPreview(attId);
      setCommentPreview(res.commentPreview);
    } catch (err: any) {
      alert('Failed to load comment preview: ' + err.message);
    }
  };

  const handlePostComment = async (attId: number) => {
    setPostingComment(true);
    try {
      const res = await api.postCommentToJira(attId);
      setActionSuccess(res.message);
      setCommentPreview(null);
      onRefresh();
    } catch (err: any) {
      alert('Error posting to Jira: ' + err.message);
    } finally {
      setPostingComment(false);
    }
  };

  const openEmailPreview = async (attId: number) => {
    try {
      const res = await api.getEmailPreview(attId);
      setEmailPreview(res);
    } catch (err: any) {
      alert('Failed to load email preview: ' + err.message);
    }
  };

  const handleSendEmail = async (attId: number) => {
    setSendingEmail(true);
    try {
      await api.sendEmail(attId);
      setActionSuccess('Investigation email notification dispatched (or simulated in mock viewer).');
      setEmailPreview(null);
      onRefresh();
    } catch (err: any) {
      alert('Error sending email: ' + err.message);
    } finally {
      setSendingEmail(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl mb-8">
      {/* Header */}
      <div className="bg-slate-800/80 px-6 py-4 border-b border-slate-700/60 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500/10 text-blue-400 rounded-lg border border-blue-500/20">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-100 flex items-center gap-2">
              Log Intelligence & Repository Discovery
              <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30">
                Northstar Digital Systems
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Deterministic parsing, evidence correlation, and codebase matching for issue {issueKey}
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          <label className="cursor-pointer px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors shadow">
            <Upload className="w-3.5 h-3.5" />
            <span>Upload Log (.log, .json, .gz)</span>
            <input
              type="file"
              className="hidden"
              accept=".log,.txt,.json,.jsonl,.gz"
              onChange={handleFileUpload}
              disabled={uploading}
            />
          </label>
          <button
            onClick={() => setShowPasteModal(true)}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors"
          >
            <Terminal className="w-3.5 h-3.5 text-slate-400" />
            <span>Paste Logs</span>
          </button>
        </div>
      </div>

      {actionSuccess && (
        <div className="bg-emerald-500/10 border-b border-emerald-500/20 px-6 py-2.5 flex items-center justify-between text-xs text-emerald-400">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>{actionSuccess}</span>
          </div>
          <button onClick={() => setActionSuccess(null)} className="text-emerald-500 hover:text-emerald-300">✕</button>
        </div>
      )}

      {/* Main Content Area */}
      {attachments.length === 0 ? (
        <div className="p-12 text-center">
          <FileText className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h4 className="text-slate-300 font-medium mb-1">No Log Attachments Analyzed Yet</h4>
          <p className="text-xs text-slate-400 max-w-md mx-auto mb-5">
            Attach a synthetic diagnostic log file (.log, .txt, .json, or .log.gz) to trigger automated secret redaction, API discovery, and codebase matching.
          </p>
          <div className="flex justify-center gap-3">
            <label className="cursor-pointer px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-medium flex items-center gap-2 transition-colors">
              <Upload className="w-4 h-4" />
              Upload Diagnostic Log
              <input type="file" className="hidden" accept=".log,.txt,.json,.jsonl,.gz" onChange={handleFileUpload} />
            </label>
            <button
              onClick={() => {
                setPastedLog(`2026-10-09 08:14:22.102 WARN c.n.inventory.service.ResourceAllocationService - [corrId=CORR-DEMO-1001] Resource DEMO-RESOURCE-1001 already reserved.\norg.springframework.dao.DataIntegrityViolationException: Pre-existing allocation detected for resource ID: DEMO-RESOURCE-1001\n\tat com.northstar.inventory.repository.JpaResourceRepository.save(JpaResourceRepository.java:94)\nHTTP 409 Conflict returned`);
                setShowPasteModal(true);
              }}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-medium border border-slate-700"
            >
              Load Sample Telemetry
            </button>
          </div>
        </div>
      ) : (
        <div>
          {/* Attachment Selector Tabs */}
          <div className="bg-slate-950/40 px-6 py-2 border-b border-slate-800 flex items-center gap-2 overflow-x-auto">
            {attachments.map(att => (
              <button
                key={att.id}
                onClick={() => setSelectedAttId(att.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-2 transition-all ${
                  activeAtt?.id === att.id
                    ? 'bg-blue-600/20 text-blue-300 border border-blue-500/30'
                    : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                }`}
              >
                <FileText className="w-3.5 h-3.5" />
                <span className="truncate max-w-[140px]">{att.filename}</span>
                <span className={`px-1.5 py-0.2 rounded text-[10px] font-semibold ${
                  att.status === 'COMPLETED' ? 'bg-emerald-500/20 text-emerald-400' :
                  att.status === 'NEEDS_REVIEW' ? 'bg-amber-500/20 text-amber-400' :
                  att.status === 'FAILED' ? 'bg-rose-500/20 text-rose-400' : 'bg-blue-500/20 text-blue-400'
                }`}>
                  {att.status}
                </span>
              </button>
            ))}
          </div>

          {activeAtt && (
            <div className="p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column: Diagnostics & Root Cause */}
              <div className="lg:col-span-2 space-y-6">
                {/* Status Bar */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-950/50 p-4 rounded-xl border border-slate-800/80">
                  <div>
                    <span className="text-[11px] text-slate-400 uppercase tracking-wider block">Detected Service</span>
                    <span className="text-sm font-semibold text-slate-200">{activeAtt.primaryService || 'Unknown'}</span>
                  </div>
                  <div>
                    <span className="text-[11px] text-slate-400 uppercase tracking-wider block">Observed API</span>
                    <span className="text-sm font-semibold text-blue-400 truncate block">{activeAtt.primaryEndpoint || 'Unknown'}</span>
                  </div>
                  <div>
                    <span className="text-[11px] text-slate-400 uppercase tracking-wider block">HTTP Status</span>
                    <span className="text-sm font-semibold text-rose-400">{activeAtt.primaryStatus ? `HTTP ${activeAtt.primaryStatus}` : 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-[11px] text-slate-400 uppercase tracking-wider block">Correlation ID</span>
                    <span className="text-sm font-mono text-amber-300 truncate block">{activeAtt.correlationId || 'Not found'}</span>
                  </div>
                </div>

                {/* Root Cause & Confidence */}
                <div className="bg-slate-950/40 p-5 rounded-xl border border-slate-800">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                      <ShieldCheck className="w-4 h-4 text-emerald-400" />
                      Probable Root Cause Hypothesis
                    </span>
                    <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-medium">
                      Confidence: {activeAtt.confidenceCategory || 'MEDIUM'} ({Math.round((activeAtt.confidenceScore || 0.7) * 100)}%)
                    </span>
                  </div>
                  <p className="text-sm text-slate-200 font-medium leading-relaxed mb-3">
                    {activeAtt.probableRootCause || 'Inconclusive - insufficient diagnostic telemetry.'}
                  </p>
                  <p className="text-xs text-slate-400">
                    {activeAtt.analysisSummary}
                  </p>
                </div>

                {/* Codebase Matcher & Copyable Clone Commands */}
                {activeAtt.recommendedRepo && (
                  <div className="bg-gradient-to-r from-blue-950/30 to-indigo-950/20 p-5 rounded-xl border border-blue-500/30 shadow-lg">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <Terminal className="w-4 h-4 text-blue-400" />
                        <h4 className="text-sm font-semibold text-slate-100">Recommended Codebase for Debugging</h4>
                      </div>
                      <span className="text-[11px] text-blue-400 font-mono bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20">
                        {activeAtt.recommendedRepo}
                      </span>
                    </div>

                    <div className="space-y-2 mb-3">
                      {/* Command 1: git clone */}
                      <div className="flex items-center justify-between bg-slate-950 p-2.5 rounded-lg border border-slate-800 font-mono text-xs text-blue-300">
                        <span className="truncate mr-2">{activeAtt.cloneCommand || `git clone https://github.com/northstar-labs/${activeAtt.recommendedRepo}.git`}</span>
                        <button
                          onClick={() => copyToClipboard(activeAtt.cloneCommand || `git clone https://github.com/northstar-labs/${activeAtt.recommendedRepo}.git`, 'clone')}
                          className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded flex items-center gap-1 text-[11px] shrink-0"
                        >
                          {copiedCmd === 'clone' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                          {copiedCmd === 'clone' ? 'Copied' : 'Copy'}
                        </button>
                      </div>

                      {/* Command 2: git clone --branch main */}
                      <div className="flex items-center justify-between bg-slate-950 p-2.5 rounded-lg border border-slate-800 font-mono text-xs text-indigo-300">
                        <span className="truncate mr-2">{`git clone --branch main https://github.com/northstar-labs/${activeAtt.recommendedRepo}.git`}</span>
                        <button
                          onClick={() => copyToClipboard(`git clone --branch main https://github.com/northstar-labs/${activeAtt.recommendedRepo}.git`, 'branch')}
                          className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded flex items-center gap-1 text-[11px] shrink-0"
                        >
                          {copiedCmd === 'branch' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                          {copiedCmd === 'branch' ? 'Copied' : 'Copy'}
                        </button>
                      </div>
                    </div>

                    <p className="text-[11px] text-slate-400 flex items-center gap-1">
                      <Info className="w-3.5 h-3.5 text-blue-400" />
                      Approved repository match based on verified endpoint contract and stack-trace namespace.
                    </p>
                  </div>
                )}
              </div>

              {/* Right Column: Actions, Jira Comment & EmailJS */}
              <div className="space-y-4">
                <div className="bg-slate-950/40 p-4 rounded-xl border border-slate-800 space-y-3">
                  <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Automated Actions</h4>

                  {/* Jira Comment Button */}
                  <button
                    onClick={() => openCommentPreview(activeAtt.id)}
                    className="w-full px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-medium flex items-center justify-between transition-colors"
                  >
                    <span className="flex items-center gap-2">
                      <MessageSquare className="w-4 h-4 text-blue-400" />
                      Preview Jira RCA Comment
                    </span>
                    <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
                  </button>

                  {/* EmailJS Button */}
                  <button
                    onClick={() => openEmailPreview(activeAtt.id)}
                    className="w-full px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-medium flex items-center justify-between transition-colors"
                  >
                    <span className="flex items-center gap-2">
                      <Send className="w-4 h-4 text-indigo-400" />
                      EmailJS Notification Preview
                    </span>
                    <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
                  </button>

                  {/* Retry Analysis */}
                  <button
                    onClick={async () => {
                      await api.retryAttachment(activeAtt.id);
                      setActionSuccess('Re-analysis completed successfully.');
                      onRefresh();
                    }}
                    className="w-full px-3 py-2 bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-800 rounded-lg text-xs font-medium flex items-center justify-center gap-2 transition-colors"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    Retry Analysis
                  </button>
                </div>

                {/* Metadata card */}
                <div className="bg-slate-950/40 p-4 rounded-xl border border-slate-800 text-xs space-y-2 text-slate-400">
                  <div className="flex justify-between">
                    <span>File Size:</span>
                    <span className="text-slate-300 font-mono">{activeAtt.sizeBytes ? `${(activeAtt.sizeBytes / 1024).toFixed(1)} KB` : 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>MIME Type:</span>
                    <span className="text-slate-300 font-mono">{activeAtt.mimeType || 'text/plain'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>SHA-256 Hash:</span>
                    <span className="text-slate-300 font-mono text-[10px] truncate max-w-[140px]">{activeAtt.sha256Hash || 'idempotent'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Jira Comment Posted:</span>
                    <span className={activeAtt.jiraCommentPosted ? 'text-emerald-400 font-medium' : 'text-slate-400'}>
                      {activeAtt.jiraCommentPosted ? 'Yes' : 'Pending Manual Post'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Email Dispatched:</span>
                    <span className={activeAtt.emailSent ? 'text-emerald-400 font-medium' : 'text-slate-400'}>
                      {activeAtt.emailSent ? 'Yes' : 'Pending'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Paste Modal */}
      {showPasteModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-2xl w-full p-6 shadow-2xl">
            <h3 className="text-base font-semibold text-slate-100 mb-2">Paste Raw Application Telemetry</h3>
            <p className="text-xs text-slate-400 mb-4">
              Paste stack traces, plain-text logs, or JSON logs for instant deterministic parsing and codebase recommendation.
            </p>
            <textarea
              className="w-full h-64 bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs font-mono text-slate-200 focus:outline-none focus:border-blue-500 mb-4"
              placeholder="Paste logs here..."
              value={pastedLog}
              onChange={e => setPastedLog(e.target.value)}
            />
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowPasteModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handlePasteSubmit}
                disabled={uploading || !pastedLog.trim()}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-medium disabled:opacity-50"
              >
                {uploading ? 'Analyzing...' : 'Analyze Telemetry'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Jira Comment Preview Modal */}
      {commentPreview && activeAtt && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-3xl w-full p-6 shadow-2xl">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-blue-400" />
                Jira Comment Preview — Standardized Template
              </h3>
              <button onClick={() => setCommentPreview(null)} className="text-slate-400 hover:text-slate-200">✕</button>
            </div>
            <p className="text-xs text-slate-400 mb-4">
              Review the formatted investigation report before publishing to Jira issue <strong>{issueKey}</strong>.
            </p>
            <pre className="bg-slate-950 border border-slate-800 rounded-lg p-4 text-xs font-mono text-slate-300 max-h-96 overflow-y-auto whitespace-pre-wrap mb-4">
              {commentPreview}
            </pre>
            <div className="flex justify-between items-center">
              <button
                onClick={() => copyToClipboard(commentPreview, 'preview')}
                className="px-3 py-1.5 bg-slate-800 text-slate-300 rounded text-xs flex items-center gap-1.5"
              >
                {copiedCmd === 'preview' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                Copy Markdown
              </button>
              <div className="flex gap-2">
                <button
                  onClick={() => setCommentPreview(null)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-lg text-xs"
                >
                  Close
                </button>
                <button
                  onClick={() => handlePostComment(activeAtt.id)}
                  disabled={postingComment}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-medium disabled:opacity-50"
                >
                  {postingComment ? 'Posting...' : 'Post Comment to Jira'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* EmailJS Preview Modal */}
      {emailPreview && activeAtt && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-2xl w-full p-6 shadow-2xl">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                <Send className="w-5 h-5 text-indigo-400" />
                EmailJS Notification Preview
              </h3>
              <button onClick={() => setEmailPreview(null)} className="text-slate-400 hover:text-slate-200">✕</button>
            </div>
            <p className="text-xs text-slate-400 mb-2">
              Subject: <strong>{emailPreview.subject}</strong>
            </p>
            <div className="bg-white rounded-lg p-4 max-h-80 overflow-y-auto mb-4 border border-slate-700">
              <div dangerouslySetInnerHTML={{ __html: emailPreview.html }} />
            </div>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setEmailPreview(null)}
                className="px-4 py-2 bg-slate-800 text-slate-300 rounded-lg text-xs"
              >
                Close
              </button>
              <button
                onClick={() => handleSendEmail(activeAtt.id)}
                disabled={sendingEmail}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-medium disabled:opacity-50"
              >
                {sendingEmail ? 'Sending...' : 'Send Notification'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

import {
  JiraIssue,
  DashboardSummary,
  DashboardMetrics,
  PolicySettings,
  MockEmail,
  ValidationResult,
  InvestigationResult,
  BackendHealth,
  NvidiaStatus
} from '../types';

const getApiBase = (): string => {
  const envUrl = ((import.meta as any)?.env?.VITE_API_BASE_URL as string | undefined)?.trim();
  if (!envUrl) return '/api';
  const trimmed = envUrl.replace(/\/+$/, '');
  return trimmed.endsWith('/api') ? trimmed : `${trimmed}/api`;
};

const API_BASE = getApiBase();

export const api = {
  // Issues
  async getIssues(): Promise<JiraIssue[]> {
    const res = await fetch(`${API_BASE}/issues`);
    if (!res.ok) throw new Error('Failed to fetch issues');
    return res.json();
  },

  async getIssue(key: string): Promise<JiraIssue> {
    const res = await fetch(`${API_BASE}/issues/${key}`);
    if (!res.ok) throw new Error(`Failed to fetch issue ${key}`);
    return res.json();
  },

  async createOrUpdateIssue(data: Partial<JiraIssue>): Promise<JiraIssue> {
    const res = await fetch(`${API_BASE}/issues`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create/update issue');
    return res.json();
  },

  async revalidateIssue(key: string): Promise<ValidationResult> {
    const res = await fetch(`${API_BASE}/issues/${key}/validate`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to validate issue');
    return res.json();
  },

  async investigateIssue(key: string): Promise<InvestigationResult> {
    const res = await fetch(`${API_BASE}/issues/${key}/investigate`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to investigate issue');
    return res.json();
  },

  async postComment(key: string, comment: string): Promise<boolean> {
    const res = await fetch(`${API_BASE}/issues/${key}/comment`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ comment }),
    });
    if (!res.ok) throw new Error('Failed to post comment');
    return res.json();
  },

  async syncJiraCloud(projectKey = 'KAN'): Promise<JiraIssue[]> {
    const res = await fetch(`${API_BASE}/issues/jira/sync?projectKey=${projectKey}`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to sync from Jira Cloud');
    return res.json();
  },

  // Dashboard
  async getSummary(): Promise<DashboardSummary> {
    const res = await fetch(`${API_BASE}/dashboard/summary`);
    if (!res.ok) throw new Error('Failed to fetch summary');
    return res.json();
  },

  async getMetrics(): Promise<DashboardMetrics> {
    const res = await fetch(`${API_BASE}/dashboard/metrics`);
    if (!res.ok) throw new Error('Failed to fetch metrics');
    return res.json();
  },

  // Demo
  async loadDemoData(): Promise<{ status: string; loadedCount: number }> {
    const res = await fetch(`${API_BASE}/demo/load-data`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to load demo data');
    return res.json();
  },

  async simulateIssue(data: Partial<JiraIssue>): Promise<JiraIssue> {
    const res = await fetch(`${API_BASE}/demo/simulate-issue`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to simulate issue');
    return res.json();
  },

  // Policy
  async getPolicy(): Promise<PolicySettings> {
    const res = await fetch(`${API_BASE}/policies`);
    if (!res.ok) throw new Error('Failed to fetch policies');
    return res.json();
  },

  async updatePolicy(policy: PolicySettings): Promise<PolicySettings> {
    const res = await fetch(`${API_BASE}/policies`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(policy),
    });
    if (!res.ok) throw new Error('Failed to update policies');
    return res.json();
  },

  // Emails
  async getAllEmails(): Promise<MockEmail[]> {
    const res = await fetch(`${API_BASE}/notifications/emails`);
    if (!res.ok) throw new Error('Failed to fetch notifications');
    return res.json();
  },

  // Knowledge
  async getKnowledgeBase(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/knowledge`);
    if (!res.ok) throw new Error('Failed to fetch knowledge');
    return res.json();
  },

  // Attachments & Log Intelligence
  async getAttachments(key: string): Promise<any[]> {
    const res = await fetch(`${API_BASE}/issues/${key}/attachments`);
    if (!res.ok) throw new Error('Failed to fetch attachments');
    return res.json();
  },

  async uploadAttachmentFile(key: string, file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/issues/${key}/attachments/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || 'Failed to upload attachment');
    }
    return res.json();
  },

  async uploadAttachmentText(key: string, logText: string, filename = 'pasted_telemetry.log'): Promise<any> {
    const res = await fetch(`${API_BASE}/issues/${key}/attachments/upload`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ logText, filename }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || 'Failed to process log telemetry');
    }
    return res.json();
  },

  async retryAttachment(id: number): Promise<any> {
    const res = await fetch(`${API_BASE}/attachments/${id}/retry`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to retry attachment analysis');
    return res.json();
  },

  async getCommentPreview(id: number): Promise<{ commentPreview: string }> {
    const res = await fetch(`${API_BASE}/attachments/${id}/comment-preview`);
    if (!res.ok) throw new Error('Failed to generate comment preview');
    return res.json();
  },

  async postCommentToJira(id: number): Promise<{ success: boolean; message: string }> {
    const res = await fetch(`${API_BASE}/attachments/${id}/post-comment`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to post comment to Jira');
    return res.json();
  },

  async getEmailPreview(id: number): Promise<{ html: string; text: string; subject: string }> {
    const res = await fetch(`${API_BASE}/attachments/${id}/email-preview`);
    if (!res.ok) throw new Error('Failed to generate email preview');
    return res.json();
  },

  async sendEmail(id: number): Promise<any> {
    const res = await fetch(`${API_BASE}/attachments/${id}/send-email`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to dispatch investigation email');
    return res.json();
  },

  async getHealth(): Promise<BackendHealth> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Backend health check failed');
    return res.json();
  },

  async getNvidiaStatus(): Promise<NvidiaStatus> {
    try {
      const res = await fetch('http://localhost:8000/api/v1/nvidia/status');
      if (res.ok) return res.json();
    } catch {}
    return {
      provider: 'nvidia',
      enabled: false,
      configured: false,
      activeMode: 'deterministic_fallback',
      model: 'unconfigured',
      baseUrl: '',
      timeoutSeconds: 0,
    };
  },

  async sendTestEmail(recipient: string): Promise<any> {
    const res = await fetch(`${API_BASE}/notifications/test-email`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ recipient }),
    });
    if (!res.ok) throw new Error('Failed to send test email');
    return res.json();
  },

  // AI Code Investigation
  async runCodeInvestigation(key: string, repoId?: string, serviceName?: string): Promise<any> {
    const params = new URLSearchParams();
    if (repoId) params.append('repositoryId', repoId);
    if (serviceName) params.append('serviceName', serviceName);
    const qs = params.toString() ? `?${params.toString()}` : '';
    const res = await fetch(`${API_BASE}/issues/${key}/code-investigation/run${qs}`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to run code investigation');
    return res.json();
  },

  async getCodeInvestigation(key: string): Promise<any> {
    const res = await fetch(`${API_BASE}/issues/${key}/code-investigation`);
    if (!res.ok) throw new Error('Failed to fetch code investigation');
    return res.json();
  },

  async generateDiff(key: string, payload: { investigationId?: string; repositoryId?: string; filePath?: string; targetMethod?: string }): Promise<any> {
    const res = await fetch(`${API_BASE}/issues/${key}/code-investigation/generate-diff`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to generate code diff');
    return res.json();
  },

  async runRecommendedTests(key: string, command: string, testClass: string): Promise<any> {
    const res = await fetch(`${API_BASE}/issues/${key}/code-investigation/run-tests`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command, testClass }),
    });
    if (!res.ok) throw new Error('Failed to run recommended tests');
    return res.json();
  },

  async getRepositoryFile(repoId: string, path: string): Promise<any> {
    const res = await fetch(`${API_BASE}/issues/repository/${repoId}/file?path=${encodeURIComponent(path)}`);
    if (!res.ok) throw new Error('Failed to fetch repository file');
    return res.json();
  },
};

import {
  JiraIssue,
  DashboardSummary,
  DashboardMetrics,
  PolicySettings,
  MockEmail,
  ValidationResult,
  InvestigationResult
} from '../types';

const API_BASE = '/api';

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
};

import { IssueAttachment, IssueStatus, JiraIssue } from '../types';

export type Tone = 'neutral' | 'accent' | 'success' | 'warning' | 'danger' | 'info';

export function issueTone(status?: IssueStatus | string): Tone {
  switch (status) {
    case 'READY':
      return 'success';
    case 'WAITING_FOR_INFORMATION':
      return 'warning';
    case 'INVESTIGATED':
    case 'RESOLVED':
      return 'info';
    case 'INVESTIGATING':
      return 'accent';
    case 'FAILED':
      return 'danger';
    default:
      return 'neutral';
  }
}

export function investigationTone(status?: string): Tone {
  switch (status) {
    case 'COMPLETED':
      return 'success';
    case 'RUNNING':
      return 'accent';
    case 'FAILED':
      return 'danger';
    default:
      return 'neutral';
  }
}

export function attachmentTone(status?: string): Tone {
  switch (status) {
    case 'COMPLETED':
      return 'success';
    case 'NEEDS_REVIEW':
    case 'VALIDATING':
    case 'ANALYZING':
      return 'warning';
    case 'FAILED':
      return 'danger';
    default:
      return 'info';
  }
}

export function notificationTone(status?: string): Tone {
  const normalized = (status || '').toUpperCase();
  if (normalized === 'FAILED') return 'danger';
  if (normalized === 'SENT') return 'success';
  if (normalized === 'SIMULATED') return 'info';
  return 'warning';
}

export function readinessTone(score?: number | null): Tone {
  if (score == null) return 'neutral';
  if (score >= 80) return 'success';
  if (score >= 60) return 'warning';
  return 'danger';
}

export function nextAction(issue: JiraIssue): string {
  if (issue.status === 'WAITING_FOR_INFORMATION') return 'Request reporter details';
  if (issue.investigationStatus === 'FAILED') return 'Retry investigation';
  if (issue.status === 'READY' && issue.investigationStatus !== 'COMPLETED') return 'Start investigation';
  if (issue.investigationStatus === 'RUNNING') return 'Review in-progress analysis';
  if (issue.status === 'INVESTIGATED' || issue.investigationStatus === 'COMPLETED') return 'Review findings';
  const failedAttachment = (issue.attachments || []).some((a) => a.status === 'FAILED');
  if (failedAttachment) return 'Retry log analysis';
  return 'Validate ticket';
}

export function latestAttachment(issue: JiraIssue): IssueAttachment | undefined {
  const list = issue.attachments || [];
  return list[list.length - 1];
}

export const REQUIRED_FIELDS = [
  { key: 'description', label: 'Description' },
  { key: 'apiDetails', label: 'API endpoint' },
];

export const RECOMMENDED_FIELDS = [
  { key: 'logs', label: 'Server logs' },
  { key: 'requestPayload', label: 'Request payload' },
  { key: 'errorMessage', label: 'Error message' },
  { key: 'environment', label: 'Environment' },
];

export const OPTIONAL_FIELDS = [
  { key: 'expectedBehavior', label: 'Expected behavior' },
  { key: 'actualBehavior', label: 'Actual behavior' },
  { key: 'replicationSteps', label: 'Replication steps' },
];

export function fieldAvailable(issue: JiraIssue, key: string): boolean {
  const fromValidation = issue.validation?.availableInformation?.includes(key);
  const value = (issue as unknown as Record<string, unknown>)[key];
  return Boolean(fromValidation || (typeof value === 'string' && value.trim()));
}

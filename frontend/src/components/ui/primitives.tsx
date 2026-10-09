import React from 'react';
import { LucideIcon } from 'lucide-react';
import { cn } from '../../lib/cn';
import { Tone } from '../../lib/status';

export const Button: React.FC<
  React.ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
    size?: 'sm' | 'md';
  }
> = ({ className, variant = 'secondary', size = 'md', ...props }) => (
  <button
    className={cn(
      'inline-flex items-center justify-center gap-1.5 rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/60 disabled:pointer-events-none disabled:opacity-50',
      size === 'sm' ? 'h-8 px-2.5 text-xs' : 'h-9 px-3 text-sm',
      variant === 'primary' && 'bg-accent text-white hover:opacity-90',
      variant === 'secondary' && 'border border-line bg-surface text-ink hover:bg-surface-2',
      variant === 'ghost' && 'text-muted hover:bg-surface-2 hover:text-ink',
      variant === 'danger' && 'bg-danger text-white hover:opacity-90',
      className
    )}
    {...props}
  />
);

export const Card: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, ...props }) => (
  <div className={cn('rounded-xl border border-line bg-surface shadow-panel', className)} {...props} />
);

export const StatusBadge: React.FC<{ tone?: Tone; children: React.ReactNode; className?: string }> = ({
  tone = 'neutral',
  children,
  className,
}) => (
  <span
    className={cn(
      'inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide',
      tone === 'success' && 'border-teal/25 bg-teal-soft text-teal',
      tone === 'warning' && 'border-amber/25 bg-amber-soft text-amber',
      tone === 'danger' && 'border-danger/25 bg-danger-soft text-danger',
      tone === 'accent' && 'border-accent/25 bg-accent-soft text-accent',
      tone === 'info' && 'border-accent/20 bg-accent-soft text-accent',
      tone === 'neutral' && 'border-line bg-surface-2 text-muted',
      className
    )}
  >
    {children}
  </span>
);

export const PageHeader: React.FC<{
  title: string;
  description?: string;
  actions?: React.ReactNode;
}> = ({ title, description, actions }) => (
  <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
    <div>
      <h1 className="text-xl font-semibold tracking-tight text-ink">{title}</h1>
      {description && <p className="mt-1 max-w-3xl text-sm text-muted">{description}</p>}
    </div>
    {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
  </div>
);

export const MetricCard: React.FC<{
  title: string;
  value: string | number;
  hint?: string;
  icon: LucideIcon;
  tone?: Tone;
  onClick?: () => void;
}> = ({ title, value, hint, icon: Icon, tone = 'accent', onClick }) => {
  const inner = (
    <>
      <div className="flex items-start justify-between gap-3">
        <span className="text-xs font-medium uppercase tracking-wider text-muted">{title}</span>
        <span
          className={cn(
            'rounded-md border p-1.5',
            tone === 'success' && 'border-teal/20 bg-teal-soft text-teal',
            tone === 'warning' && 'border-amber/20 bg-amber-soft text-amber',
            tone === 'danger' && 'border-danger/20 bg-danger-soft text-danger',
            (tone === 'accent' || tone === 'info') && 'border-accent/20 bg-accent-soft text-accent',
            tone === 'neutral' && 'border-line bg-surface-2 text-muted'
          )}
        >
          <Icon className="h-4 w-4" />
        </span>
      </div>
      <div className="mt-3 text-2xl font-semibold tracking-tight text-ink">{value}</div>
      {hint && <p className="mt-1 text-xs text-muted">{hint}</p>}
    </>
  );

  if (onClick) {
    return (
      <button type="button" onClick={onClick} className="rounded-xl border border-line bg-surface p-4 text-left shadow-panel transition-colors hover:border-accent/30">
        {inner}
      </button>
    );
  }
  return <Card className="p-4">{inner}</Card>;
};

export const EmptyState: React.FC<{
  icon?: LucideIcon;
  title: string;
  description: string;
  action?: React.ReactNode;
}> = ({ icon: Icon, title, description, action }) => (
  <div className="flex flex-col items-center px-6 py-12 text-center">
    {Icon && <Icon className="mb-3 h-8 w-8 text-muted" />}
    <h3 className="text-sm font-semibold text-ink">{title}</h3>
    <p className="mt-1 max-w-md text-sm text-muted">{description}</p>
    {action && <div className="mt-4">{action}</div>}
  </div>
);

export const ErrorState: React.FC<{
  title?: string;
  message: string;
  onRetry?: () => void;
}> = ({ title = 'Unable to load this view', message, onRetry }) => (
  <div className="flex items-start justify-between gap-3 rounded-xl border border-danger/30 bg-danger-soft px-4 py-3">
    <div>
      <div className="text-sm font-medium text-danger">{title}</div>
      <p className="mt-0.5 text-xs text-muted">{message}</p>
    </div>
    {onRetry && (
      <Button size="sm" onClick={onRetry}>
        Retry
      </Button>
    )}
  </div>
);

export const Skeleton: React.FC<{ className?: string }> = ({ className }) => (
  <div className={cn('animate-pulse rounded-md bg-surface-2', className)} />
);

export const ReadinessIndicator: React.FC<{ score?: number | null }> = ({ score }) => {
  const value = score ?? 0;
  const tone = value >= 80 ? 'bg-teal' : value >= 60 ? 'bg-amber' : 'bg-danger';
  return (
    <div className="flex items-center gap-2">
      <span className="font-mono text-xs font-semibold text-ink">{score == null ? '—' : `${score}%`}</span>
      <div className="h-1.5 w-14 overflow-hidden rounded-full bg-surface-2">
        <div className={cn('h-full rounded-full', tone)} style={{ width: `${Math.min(value, 100)}%` }} />
      </div>
    </div>
  );
};

export const Dialog: React.FC<{
  open: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  icon?: LucideIcon;
  children: React.ReactNode;
  wide?: boolean;
}> = ({ open, onClose, title, description, icon: Icon, children, wide }) => {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-[70] flex items-center justify-center p-4">
      <button type="button" className="absolute inset-0 bg-ink/40" aria-label="Close dialog" onClick={onClose} />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
        className={cn(
          'relative z-10 flex max-h-[90vh] w-full flex-col overflow-hidden rounded-xl border border-line bg-surface shadow-panel',
          wide ? 'max-w-3xl' : 'max-w-2xl'
        )}
      >
        <div className="flex items-start justify-between border-b border-line px-5 py-4">
          <div className="flex items-start gap-3">
            {Icon && (
              <span className="rounded-md border border-accent/20 bg-accent-soft p-2 text-accent">
                <Icon className="h-4 w-4" />
              </span>
            )}
            <div>
              <h2 id="dialog-title" className="text-sm font-semibold text-ink">
                {title}
              </h2>
              {description && <p className="mt-0.5 text-xs text-muted">{description}</p>}
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose} aria-label="Close">
            Close
          </Button>
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto">{children}</div>
      </div>
    </div>
  );
};

export const CloneCommand: React.FC<{ command?: string | null; onCopied?: () => void }> = ({ command, onCopied }) => {
  const [copied, setCopied] = React.useState(false);
  if (!command) {
    return <p className="text-xs text-muted">No approved clone command is available for this match.</p>;
  }
  return (
    <div className="flex items-center justify-between gap-2 rounded-lg border border-line bg-log px-3 py-2 font-mono text-xs text-log-ink">
      <code className="truncate">{command}</code>
      <Button
        size="sm"
        onClick={async () => {
          await navigator.clipboard.writeText(command);
          setCopied(true);
          onCopied?.();
          window.setTimeout(() => setCopied(false), 2000);
        }}
      >
        {copied ? 'Copied' : 'Copy'}
      </Button>
    </div>
  );
};

export const AnalysisProgress: React.FC<{
  active: boolean;
  label: string;
  stages: string[];
  message: string;
}> = ({ active, label, stages, message }) => {
  if (!active) return null;
  return (
    <Card className="p-4">
      <div className="flex items-center gap-3">
        <span className="relative flex h-2.5 w-2.5">
          <span className="absolute inline-flex h-full w-full animate-pulse-soft rounded-full bg-accent opacity-60 motion-reduce:animate-none" />
          <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-accent" />
        </span>
        <div>
          <div className="text-sm font-medium text-ink">{label}</div>
          <p className="text-xs text-muted">{message}</p>
        </div>
      </div>
      <ol className="mt-4 space-y-2">
        {stages.map((stage, index) => (
          <li key={stage} className="flex items-center gap-2 text-xs text-muted">
            <span className={cn('h-1.5 w-1.5 rounded-full', index === 0 ? 'bg-accent' : 'bg-line')} />
            {stage}
          </li>
        ))}
      </ol>
      <p className="mt-3 text-[11px] text-muted">
        Progress is indeterminate until the analysis engine returns a result. Stages describe the workflow, not live job percentages.
      </p>
    </Card>
  );
};

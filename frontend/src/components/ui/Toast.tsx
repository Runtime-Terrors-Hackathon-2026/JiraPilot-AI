import React, { createContext, useCallback, useContext, useMemo, useState } from 'react';
import { AlertCircle, CheckCircle2, Info, X } from 'lucide-react';
import { cn } from '../../lib/cn';

export type ToastKind = 'success' | 'error' | 'info';

interface ToastItem {
  id: string;
  kind: ToastKind;
  title: string;
  message?: string;
}

interface ToastContextValue {
  push: (toast: Omit<ToastItem, 'id'>) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const push = useCallback((toast: Omit<ToastItem, 'id'>) => {
    const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    setToasts((current) => [...current, { ...toast, id }]);
    window.setTimeout(() => {
      setToasts((current) => current.filter((item) => item.id !== id));
    }, 4200);
  }, []);

  const value = useMemo(() => ({ push }), [push]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed bottom-4 right-4 z-[80] flex w-[min(100%-2rem,22rem)] flex-col gap-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            role="status"
            className={cn(
              'rounded-lg border bg-surface px-3 py-2.5 shadow-panel animate-fade-in',
              toast.kind === 'success' && 'border-teal/30',
              toast.kind === 'error' && 'border-danger/40',
              toast.kind === 'info' && 'border-line'
            )}
          >
            <div className="flex items-start gap-2">
              {toast.kind === 'success' ? (
                <CheckCircle2 className="mt-0.5 h-4 w-4 text-teal" />
              ) : toast.kind === 'error' ? (
                <AlertCircle className="mt-0.5 h-4 w-4 text-danger" />
              ) : (
                <Info className="mt-0.5 h-4 w-4 text-accent" />
              )}
              <div className="min-w-0 flex-1">
                <div className="text-sm font-medium text-ink">{toast.title}</div>
                {toast.message && <p className="mt-0.5 text-xs text-muted">{toast.message}</p>}
              </div>
              <button
                type="button"
                className="rounded p-1 text-muted hover:bg-surface-2 hover:text-ink"
                onClick={() => setToasts((current) => current.filter((item) => item.id !== toast.id))}
                aria-label="Dismiss notification"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
}

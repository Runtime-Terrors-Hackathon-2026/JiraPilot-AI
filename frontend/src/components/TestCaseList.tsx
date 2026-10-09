import React, { useState } from 'react';
import { TestCase } from '../types';
import { Button, Card, EmptyState, StatusBadge } from './ui/primitives';

interface TestCaseListProps {
  testCases?: TestCase[];
}

export const TestCaseList: React.FC<TestCaseListProps> = ({ testCases }) => {
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const cases = testCases || [];

  return (
    <Card className="p-5">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-ink">Suggested tests and debugging actions</h3>
        <span className="text-xs text-muted">{cases.length} generated</span>
      </div>
      {cases.length === 0 ? (
        <EmptyState title="No generated tests yet" description="Investigation results will include unit, integration and API cases when the engine returns them." />
      ) : (
        <div className="space-y-3">
          {cases.map((tc) => (
            <div key={tc.id} className="rounded-lg border border-line p-3">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-xs font-semibold text-accent">{tc.id}</span>
                <span className="text-xs font-medium text-ink">{tc.title}</span>
                <StatusBadge>{tc.type}</StatusBadge>
              </div>
              <p className="mt-1 text-xs text-muted">{tc.description}</p>
              <p className="mt-1 text-xs text-teal">Expected: {tc.expectedResult}</p>
              {tc.testCodeSnippet && (
                <div className="relative mt-2">
                  <pre className="overflow-x-auto rounded-md bg-log p-3 font-mono text-[11px] text-log-ink">{tc.testCodeSnippet}</pre>
                  <Button
                    size="sm"
                    className="absolute right-2 top-2"
                    onClick={async () => {
                      await navigator.clipboard.writeText(tc.testCodeSnippet || '');
                      setCopiedId(tc.id);
                      window.setTimeout(() => setCopiedId(null), 2000);
                    }}
                  >
                    {copiedId === tc.id ? 'Copied' : 'Copy'}
                  </Button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};

import React, { useState } from 'react';
import { Terminal } from 'lucide-react';
import { Button, Card, EmptyState } from './ui/primitives';

interface CurlViewerProps {
  curlCommand?: string;
  postmanJson?: string;
}

export const CurlViewer: React.FC<CurlViewerProps> = ({ curlCommand, postmanJson }) => {
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState<'curl' | 'postman'>('curl');
  const content = activeTab === 'curl' ? curlCommand : postmanJson;

  return (
    <Card className="p-5">
      <div className="mb-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2">
          <Terminal className="h-4 w-4 text-accent" />
          <h3 className="text-sm font-semibold text-ink">Suggested tests and reproduction</h3>
        </div>
        <div className="flex rounded-md border border-line p-0.5">
          <button type="button" onClick={() => setActiveTab('curl')} className={`rounded px-2 py-1 text-xs ${activeTab === 'curl' ? 'bg-accent-soft text-accent' : 'text-muted'}`}>cURL</button>
          <button type="button" onClick={() => setActiveTab('postman')} className={`rounded px-2 py-1 text-xs ${activeTab === 'postman' ? 'bg-accent-soft text-accent' : 'text-muted'}`}>Postman</button>
        </div>
      </div>
      {!content ? (
        <EmptyState title="No reproduction payload yet" description="Run an investigation to generate a cURL or Postman body from the analysis engine." />
      ) : (
        <div className="relative">
          <pre className="overflow-x-auto rounded-lg bg-log p-4 font-mono text-xs text-log-ink">{content}</pre>
          <Button
            size="sm"
            className="absolute right-2 top-2"
            onClick={async () => {
              await navigator.clipboard.writeText(content);
              setCopied(true);
              window.setTimeout(() => setCopied(false), 2000);
            }}
          >
            {copied ? 'Copied' : 'Copy'}
          </Button>
        </div>
      )}
    </Card>
  );
};

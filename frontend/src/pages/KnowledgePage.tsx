import React, { useEffect, useState } from 'react';
import { BookOpen, Search } from 'lucide-react';
import { api } from '../api/client';
import { Card, EmptyState, ErrorState, PageHeader, Skeleton } from '../components/ui/primitives';

export const KnowledgePage: React.FC = () => {
  const [records, setRecords] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchKnowledge = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getKnowledgeBase();
      setRecords(data);
    } catch {
      setError('Unable to load the incident knowledge base.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKnowledge();
  }, []);

  const filtered = records.filter(
    (r) =>
      r.jiraKey?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.summary?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.affectedService?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.rootCause?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-4">
      <PageHeader
        title="Knowledge Base / Similar Incidents"
        description="Historical patterns used for similarity correlation. Records come from the backend knowledge API."
      />
      <label className="relative block max-w-md">
        <span className="sr-only">Search knowledge base</span>
        <Search className="pointer-events-none absolute left-2.5 top-2.5 h-4 w-4 text-muted" />
        <input
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search incidents, services, root causes"
          className="h-9 w-full rounded-md border border-line bg-surface pl-8 pr-3 text-sm text-ink"
        />
      </label>
      {error && <ErrorState message={error} onRetry={fetchKnowledge} />}
      {loading && (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          <Skeleton className="h-40" />
          <Skeleton className="h-40" />
        </div>
      )}
      {!loading && filtered.length === 0 ? (
        <Card>
          <EmptyState
            icon={BookOpen}
            title="No similar incidents match this search."
            description="Load demo data or complete an investigation so resolved incidents can be remembered."
          />
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          {filtered.map((item, idx) => (
            <Card key={item.jiraKey || idx} className="p-4">
              <div className="mb-2 flex items-center gap-2">
                <span className="font-mono text-xs font-semibold text-accent">{item.jiraKey}</span>
                <span className="text-xs text-muted">{item.affectedService}</span>
              </div>
              <h3 className="text-sm font-semibold text-ink">{item.summary}</h3>
              <p className="mt-3 text-xs text-muted">Observed pattern</p>
              <p className="text-xs text-ink">{item.rootCause}</p>
              <p className="mt-3 text-xs text-muted">Recorded resolution</p>
              <p className="text-xs text-teal">{item.resolution}</p>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

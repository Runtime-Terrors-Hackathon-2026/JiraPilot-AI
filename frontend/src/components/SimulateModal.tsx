import React, { useState } from 'react';
import { PlayCircle } from 'lucide-react';
import { JiraIssue } from '../types';
import { api } from '../api/client';
import { Button, Dialog } from './ui/primitives';
import { useToast } from './ui/Toast';

interface SimulateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (issue: JiraIssue) => void;
}

export const SimulateModal: React.FC<SimulateModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const { push } = useToast();
  const [key, setKey] = useState('HACK-1001');
  const [summary, setSummary] = useState('Circuit creation API failing');
  const [description, setDescription] = useState('Circuit creation fails intermittently during provisioning in SANDBOX environment.');
  const [reporter, setReporter] = useState('developer@example.com');
  const [environment, setEnvironment] = useState('SANDBOX');
  const [apiDetails, setApiDetails] = useState('POST /api/circuit/provision');
  const [logs, setLogs] = useState('2026-10-08 10:31:42 ERROR [PEDS] Duplicate NFID detected: TEST-NFID-1001 correlationId=CORR-1001\n2026-10-08 10:31:43 ERROR [WFM] Downstream request failed status=500 endpoint=/api/circuit/provision correlationId=CORR-1001');
  const [requestPayload, setRequestPayload] = useState('{\n  "circuitId": "TEST-CKT-1001",\n  "customerId": "TEST-CUST-8821",\n  "nfid": "TEST-NFID-1001"\n}');
  const [errorMessage, setErrorMessage] = useState('HTTP 500 Internal Server Error: Duplicate NFID detected');
  const [expectedBehavior, setExpectedBehavior] = useState('HTTP 201 Created and active circuit record created');
  const [actualBehavior, setActualBehavior] = useState('HTTP 500 with SQL unique constraint error');
  const [loading, setLoading] = useState(false);

  const loadPreset = (presetType: 'complete' | 'incomplete' | 'timeout') => {
    if (presetType === 'complete') {
      setKey('HACK-1001');
      setSummary('Circuit creation API failing');
      setDescription('Circuit creation fails intermittently during provisioning in SANDBOX environment.');
      setReporter('alice.engineer@example.com');
      setEnvironment('SANDBOX');
      setApiDetails('POST /api/circuit/provision');
      setLogs('2026-10-08 10:31:42 ERROR [PEDS] Duplicate NFID detected: TEST-NFID-1001 correlationId=CORR-1001\n2026-10-08 10:31:43 ERROR [WFM] Downstream request failed status=500 endpoint=/api/circuit/provision correlationId=CORR-1001');
      setRequestPayload('{\n  "circuitId": "TEST-CKT-1001",\n  "customerId": "TEST-CUST-8821",\n  "nfid": "TEST-NFID-1001"\n}');
      setErrorMessage('HTTP 500 Duplicate NFID');
      setExpectedBehavior('HTTP 201 Created');
      setActualBehavior('HTTP 500 Server Error');
    } else if (presetType === 'incomplete') {
      setKey('HACK-1002');
      setSummary('API is failing. Please check.');
      setDescription('API is failing. Please check why circuits are not being created.');
      setReporter('bob.developer@example.com');
      setEnvironment('DEV');
      setApiDetails('');
      setLogs('');
      setRequestPayload('');
      setErrorMessage('');
      setExpectedBehavior('');
      setActualBehavior('');
    } else {
      setKey('HACK-1003');
      setSummary('Work Order dispatch timeout when calling Inventory Service');
      setDescription('High latency and 504 Gateway Timeout during peak dispatch requests.');
      setReporter('carol.lead@example.com');
      setEnvironment('PROD-US-EAST');
      setApiDetails('POST /api/work-order/dispatch');
      setLogs('2026-10-08 11:15:25 ERROR [WFM] DownstreamTimeoutException: Read timed out connecting to Inventory Service correlationId=CORR-5542');
      setRequestPayload('{\n  "workOrderId": "WO-9942",\n  "serviceType": "FIBER"\n}');
      setErrorMessage('HTTP 504 Gateway Timeout');
      setExpectedBehavior('HTTP 200 OK within 500ms SLA');
      setActualBehavior('HTTP 504 Timeout');
    }
  };

  const field = (label: string, value: string, onChange: (v: string) => void, extra?: string) => (
    <label className="block text-xs font-medium text-ink">
      {label}
      {extra === 'textarea' ? (
        <textarea value={value} onChange={(e) => onChange(e.target.value)} rows={3} className="mt-1 w-full rounded-md border border-line bg-canvas px-3 py-2 font-mono text-xs text-ink" />
      ) : (
        <input value={value} onChange={(e) => onChange(e.target.value)} className="mt-1 h-9 w-full rounded-md border border-line bg-canvas px-3 text-sm text-ink" />
      )}
    </label>
  );

  return (
    <Dialog open={isOpen} onClose={onClose} title="Simulate Jira issue" description="Ingest a synthetic ticket through the real validation pipeline" icon={PlayCircle} wide>
      <form
        className="space-y-4 p-5"
        onSubmit={async (e) => {
          e.preventDefault();
          setLoading(true);
          try {
            const issue = await api.simulateIssue({
              key, summary, description, reporter, environment, apiDetails, logs, requestPayload, errorMessage, expectedBehavior, actualBehavior,
            });
            onSuccess(issue);
            onClose();
          } catch {
            push({ kind: 'error', title: 'Simulation failed', message: 'The backend rejected the simulate-issue request.' });
          } finally {
            setLoading(false);
          }
        }}
      >
        <div className="flex flex-wrap gap-2">
          <Button type="button" size="sm" onClick={() => loadPreset('complete')}>Complete ticket</Button>
          <Button type="button" size="sm" onClick={() => loadPreset('incomplete')}>Needs information</Button>
          <Button type="button" size="sm" onClick={() => loadPreset('timeout')}>Downstream timeout</Button>
        </div>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
          {field('Jira key', key, setKey)}
          <div className="md:col-span-2">{field('Summary', summary, setSummary)}</div>
        </div>
        {field('Description', description, setDescription, 'textarea')}
        <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
          {field('Reporter', reporter, setReporter)}
          {field('Environment', environment, setEnvironment)}
          {field('API endpoint', apiDetails, setApiDetails)}
        </div>
        {field('Logs', logs, setLogs, 'textarea')}
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          {field('Request payload', requestPayload, setRequestPayload, 'textarea')}
          <div className="space-y-3">
            {field('Expected behavior', expectedBehavior, setExpectedBehavior)}
            {field('Actual behavior', actualBehavior, setActualBehavior)}
            {field('Error message', errorMessage, setErrorMessage)}
          </div>
        </div>
        <div className="flex justify-end gap-2">
          <Button type="button" onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="primary" disabled={loading}>{loading ? 'Ingesting…' : 'Ingest and validate'}</Button>
        </div>
      </form>
    </Dialog>
  );
};

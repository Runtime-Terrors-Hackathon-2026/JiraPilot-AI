import React, { useEffect, useState } from 'react';
import { Sliders } from 'lucide-react';
import { PolicySettings } from '../types';
import { api } from '../api/client';
import { Dialog } from './ui/primitives';
import { PolicyPanel } from './PolicyPanel';
import { useToast } from './ui/Toast';

interface PolicyModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PolicyModal: React.FC<PolicyModalProps> = ({ isOpen, onClose }) => {
  const { push } = useToast();
  const [policy, setPolicy] = useState<PolicySettings | null>(null);

  useEffect(() => {
    if (isOpen) {
      api.getPolicy().then(setPolicy).catch(() => push({ kind: 'error', title: 'Unable to load policy' }));
    }
  }, [isOpen, push]);

  return (
    <Dialog open={isOpen} onClose={onClose} title="Triage policy" description="Weighted readiness scoring and automation thresholds" icon={Sliders}>
      <div className="p-5">
        {policy && (
          <PolicyPanel
            policy={policy}
            onChange={setPolicy}
            onSave={async () => {
              const updated = await api.updatePolicy(policy);
              setPolicy(updated);
              push({ kind: 'success', title: 'Policy saved' });
            }}
          />
        )}
      </div>
    </Dialog>
  );
};

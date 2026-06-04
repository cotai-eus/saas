import { Badge } from '../../../shared/components/ui';
import type { CampaignStatus } from '../../../shared/api/types';

const STATUS_CONFIG: Record<CampaignStatus, { label: string; variant: 'success' | 'info' | 'warning' | 'default' | 'danger' }> = {
  active: { label: 'Ativa', variant: 'success' },
  scheduled: { label: 'Agendada', variant: 'info' },
  paused: { label: 'Pausada', variant: 'warning' },
  done: { label: 'Concluída', variant: 'default' },
  draft: { label: 'Rascunho', variant: 'default' },
  error: { label: 'Falha', variant: 'danger' },
};

interface CampaignStatusBadgeProps {
  status: CampaignStatus;
}

export function CampaignStatusBadge({ status }: CampaignStatusBadgeProps) {
  const config = STATUS_CONFIG[status];
  return <Badge variant={config.variant}>{config.label}</Badge>;
}

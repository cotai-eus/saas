import { useParams, useNavigate } from 'react-router-dom';
import { useCampaign } from '../features/campaigns/hooks/useCampaigns';
import { CampaignStatusBadge } from '../features/campaigns/components/CampaignStatusBadge';
import { Button } from '../shared/components/ui';
import { formatDateTime } from '../shared/utils/date';
import { formatNumber } from '../shared/utils/number';

export default function CampaignDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const campaign = useCampaign(id!);

  if (!campaign) {
    return (
      <div className="flex flex-col items-center justify-center py-[var(--space-10)] gap-[var(--space-4)]">
        <p className="text-[var(--color-text-muted)]">Campanha não encontrada</p>
        <Button onClick={() => navigate('/campaigns')}>Voltar</Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-[var(--space-6)]">
      <div className="flex items-center justify-between">
        <div>
          <button
            onClick={() => navigate('/campaigns')}
            className="text-[var(--font-size-sm)] text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] bg-transparent border-none mb-[var(--space-1)]"
          >
            ← Voltar
          </button>
          <div className="flex items-center gap-[var(--space-3)]">
            <h1 className="text-[var(--font-size-xl)] font-bold text-[var(--color-text-primary)]">
              {campaign.name}
            </h1>
            <CampaignStatusBadge status={campaign.status} />
          </div>
        </div>
        <Button variant="secondary">Editar</Button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-[var(--space-4)]">
        <div className="rounded-[var(--radius-md)] bg-[var(--color-bg-base)] border border-[var(--color-border)] p-[var(--space-4)]">
          <p className="text-[var(--font-size-xs)] text-[var(--color-text-muted)] mb-[var(--space-1)]">Total de contatos</p>
          <p className="text-[var(--font-size-lg)] font-semibold">{formatNumber(campaign.recipient_count)}</p>
        </div>
        <div className="rounded-[var(--radius-md)] bg-[var(--color-bg-base)] border border-[var(--color-border)] p-[var(--space-4)]">
          <p className="text-[var(--font-size-xs)] text-[var(--color-text-muted)] mb-[var(--space-1)]">Enviadas</p>
          <p className="text-[var(--font-size-lg)] font-semibold">{formatNumber(campaign.sent_count)}</p>
        </div>
        <div className="rounded-[var(--radius-md)] bg-[var(--color-bg-base)] border border-[var(--color-border)] p-[var(--space-4)]">
          <p className="text-[var(--font-size-xs)] text-[var(--color-text-muted)] mb-[var(--space-1)]">Entregues</p>
          <p className="text-[var(--font-size-lg)] font-semibold">{formatNumber(campaign.delivered_count)}</p>
        </div>
        <div className="rounded-[var(--radius-md)] bg-[var(--color-bg-base)] border border-[var(--color-border)] p-[var(--space-4)]">
          <p className="text-[var(--font-size-xs)] text-[var(--color-text-muted)] mb-[var(--space-1)]">Entrega</p>
          <p className="text-[var(--font-size-lg)] font-semibold">
            {campaign.sent_count > 0
              ? `${Math.round((campaign.delivered_count / campaign.sent_count) * 100)}%`
              : '—'}
          </p>
        </div>
      </div>

      <div className="rounded-[var(--radius-md)] bg-[var(--color-bg-base)] border border-[var(--color-border)] p-[var(--space-4)]">
        <h3 className="text-[var(--font-size-base)] font-semibold mb-[var(--space-3)]">Detalhes</h3>
        <dl className="grid grid-cols-1 md:grid-cols-2 gap-[var(--space-3)]">
          <div>
            <dt className="text-[var(--font-size-xs)] text-[var(--color-text-muted)]">Canal</dt>
            <dd className="text-[var(--font-size-sm)] text-[var(--color-text-primary)]">{campaign.channel_name || campaign.channel_id}</dd>
          </div>
          <div>
            <dt className="text-[var(--font-size-xs)] text-[var(--color-text-muted)]">Criada em</dt>
            <dd className="text-[var(--font-size-sm)] text-[var(--color-text-primary)]">{formatDateTime(campaign.created_at)}</dd>
          </div>
          {campaign.scheduled_at && (
            <div>
              <dt className="text-[var(--font-size-xs)] text-[var(--color-text-muted)]">Agendada para</dt>
              <dd className="text-[var(--font-size-sm)] text-[var(--color-text-primary)]">{formatDateTime(campaign.scheduled_at)}</dd>
            </div>
          )}
        </dl>
      </div>
    </div>
  );
}

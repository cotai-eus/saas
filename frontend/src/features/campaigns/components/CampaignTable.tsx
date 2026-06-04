import { Link } from 'react-router-dom';
import { CampaignStatusBadge } from './CampaignStatusBadge';
import { formatDate } from '../../../shared/utils/date';
import { formatNumber } from '../../../shared/utils/number';
import type { Campaign } from '../../../shared/api/types';

interface CampaignTableProps {
  campaigns: Campaign[];
}

export function CampaignTable({ campaigns }: CampaignTableProps) {
  if (campaigns.length === 0) {
    return (
      <div className="text-center py-[var(--space-10)] text-[var(--color-text-muted)]">
        Nenhuma campanha encontrada
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b border-[var(--color-border)]">
            <th scope="col" className="text-left py-[var(--space-3)] px-[var(--space-3)] text-[var(--font-size-xs)] font-semibold uppercase tracking-wider text-[var(--color-text-muted)]">Nome</th>
            <th scope="col" className="text-left py-[var(--space-3)] px-[var(--space-3)] text-[var(--font-size-xs)] font-semibold uppercase tracking-wider text-[var(--color-text-muted)]">Status</th>
            <th scope="col" className="text-right py-[var(--space-3)] px-[var(--space-3)] text-[var(--font-size-xs)] font-semibold uppercase tracking-wider text-[var(--color-text-muted)]">Contatos</th>
            <th scope="col" className="text-right py-[var(--space-3)] px-[var(--space-3)] text-[var(--font-size-xs)] font-semibold uppercase tracking-wider text-[var(--color-text-muted)]">Enviadas</th>
            <th scope="col" className="text-right py-[var(--space-3)] px-[var(--space-3)] text-[var(--font-size-xs)] font-semibold uppercase tracking-wider text-[var(--color-text-muted)]">Entrega</th>
            <th scope="col" className="text-right py-[var(--space-3)] px-[var(--space-3)] text-[var(--font-size-xs)] font-semibold uppercase tracking-wider text-[var(--color-text-muted)]">Data</th>
          </tr>
        </thead>
        <tbody>
          {campaigns.map((campaign) => (
            <tr key={campaign.id} className="border-b border-[var(--color-border)] hover:bg-[var(--color-bg-subtle)] transition-colors">
              <td className="py-[var(--space-3)] px-[var(--space-3)]">
                <Link
                  to={`/campaigns/${campaign.id}`}
                  className="text-[var(--font-size-base)] font-medium text-[var(--color-text-primary)] no-underline hover:text-[var(--color-brand-dark)]"
                >
                  {campaign.name}
                </Link>
              </td>
              <td className="py-[var(--space-3)] px-[var(--space-3)]">
                <CampaignStatusBadge status={campaign.status} />
              </td>
              <td className="py-[var(--space-3)] px-[var(--space-3)] text-right text-[var(--font-size-base)] text-[var(--color-text-secondary)]">
                {formatNumber(campaign.recipient_count)}
              </td>
              <td className="py-[var(--space-3)] px-[var(--space-3)] text-right text-[var(--font-size-base)] text-[var(--color-text-secondary)]">
                {formatNumber(campaign.sent_count)}
              </td>
              <td className="py-[var(--space-3)] px-[var(--space-3)] text-right text-[var(--font-size-base)] text-[var(--color-text-secondary)]">
                {campaign.sent_count > 0
                  ? `${Math.round((campaign.delivered_count / campaign.sent_count) * 100)}%`
                  : '—'}
              </td>
              <td className="py-[var(--space-3)] px-[var(--space-3)] text-right text-[var(--font-size-base)] text-[var(--color-text-secondary)]">
                {formatDate(campaign.created_at)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

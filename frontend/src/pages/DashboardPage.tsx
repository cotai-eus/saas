import { useAuth } from '../shared/hooks';
import { useChannels } from '../features/channels/hooks/useChannels';
import { useCampaigns } from '../features/campaigns/hooks/useCampaigns';
import { useContacts } from '../features/contacts/hooks/useContacts';
import { StatCard } from '../shared/components/ui';
import { SendsLineChart } from '../features/reports/components/SendsLineChart';
import { formatNumber, formatCompact } from '../shared/utils/number';
import { CampaignTable } from '../features/campaigns/components/CampaignTable';

export default function DashboardPage() {
  const { user } = useAuth();
  const { data: channels } = useChannels();
  const { campaigns, isLoading: campaignsLoading } = useCampaigns();
  const { data: contacts } = useContacts();

  const totalSent = campaigns.reduce((s, c) => s + c.sent_count, 0);
  const totalDelivered = campaigns.reduce((s, c) => s + c.delivered_count, 0);
  const deliveryRate = totalSent > 0 ? Math.round((totalDelivered / totalSent) * 100) : 0;

  return (
    <div className="flex flex-col gap-[var(--space-6)]">
      <h2 className="text-[var(--font-size-xl)] font-bold text-[var(--color-text-primary)]">
        Bom dia, {user?.email?.split('@')[0] || 'Usuário'} 👋
      </h2>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-[var(--space-4)]">
        <StatCard label="Campanhas" value={formatNumber(campaigns.length)} loading={campaignsLoading} />
        <StatCard label="Mensagens enviadas" value={formatCompact(totalSent)} loading={campaignsLoading} />
        <StatCard label="Taxa de entrega" value={`${deliveryRate}%`} change={deliveryRate > 70 ? 5 : -2} loading={campaignsLoading} />
        <StatCard label="Contatos" value={formatCompact(contacts?.length || 0)} loading={!contacts} />
        <StatCard label="Canais" value={formatNumber(channels?.length || 0)} loading={!channels} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-[var(--space-4)]">
        <div className="lg:col-span-2">
          <SendsLineChart />
        </div>
        <div className="rounded-[var(--radius-md)] bg-[var(--color-bg-base)] border border-[var(--color-border)] p-[var(--space-4)]">
          <h3 className="text-[var(--font-size-base)] font-semibold text-[var(--color-text-primary)] mb-[var(--space-3)]">
            Status dos canais
          </h3>
          <div className="flex flex-col gap-[var(--space-2)]">
            {channels?.length === 0 && (
              <p className="text-[var(--font-size-sm)] text-[var(--color-text-muted)]">Nenhum canal conectado</p>
            )}
            {channels?.map((ch) => (
              <div key={ch.id} className="flex items-center justify-between py-[var(--space-2)] border-b border-[var(--color-border)] last:border-0">
                <span className="text-[var(--font-size-sm)] font-medium text-[var(--color-text-primary)]">{ch.name}</span>
                <span className={`text-[var(--font-size-xs)] font-medium px-[var(--space-2)] py-[1px] rounded-full ${
                  ch.status === 'connected'
                    ? 'bg-[var(--color-success-bg)] text-[var(--color-success)]'
                    : 'bg-[var(--color-danger-bg)] text-[var(--color-danger)]'
                }`}>
                  {ch.status === 'connected' ? 'Conectado' : 'Desconectado'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="rounded-[var(--radius-md)] bg-[var(--color-bg-base)] border border-[var(--color-border)]">
        <div className="px-[var(--space-4)] py-[var(--space-3)] border-b border-[var(--color-border)]">
          <h3 className="text-[var(--font-size-base)] font-semibold text-[var(--color-text-primary)]">
            Campanhas recentes
          </h3>
        </div>
        <CampaignTable campaigns={campaigns.slice(0, 5)} />
      </div>
    </div>
  );
}

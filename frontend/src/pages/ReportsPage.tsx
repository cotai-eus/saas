import { SendsLineChart } from '../features/reports/components/SendsLineChart';
import { ChannelMixPieChart } from '../features/reports/components/ChannelMixPieChart';
import { EmptyState } from '../shared/components/ui';

export default function ReportsPage() {
  const hasData = true;

  if (!hasData) {
    return (
      <EmptyState
        title="Sem dados ainda"
        description="Envie sua primeira campanha para ver métricas."
      />
    );
  }

  return (
    <div className="flex flex-col gap-[var(--space-6)]">
      <div className="flex items-center justify-between">
        <h2 className="text-[var(--font-size-xl)] font-bold text-[var(--color-text-primary)]">
          Relatórios
        </h2>
        <div className="flex gap-[var(--space-2)]">
          {['7d', '30d', '90d'].map((period) => (
            <button
              key={period}
              className="px-[var(--space-3)] py-[var(--space-1)] rounded-[var(--radius-md)] text-[var(--font-size-sm)] font-medium bg-[var(--color-brand)] text-white border-none"
            >
              {period === '7d' ? '7 dias' : period === '30d' ? '30 dias' : '90 dias'}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-[var(--space-4)]">
        <SendsLineChart />
        <ChannelMixPieChart />
      </div>
    </div>
  );
}

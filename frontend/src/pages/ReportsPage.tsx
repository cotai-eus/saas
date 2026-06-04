import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { SendsLineChart } from '../features/reports/components/SendsLineChart';
import { ChannelMixPieChart } from '../features/reports/components/ChannelMixPieChart';
import { EmptyState, Spinner } from '../shared/components/ui';
import { apiClient } from '../shared/api/client';
import { ENDPOINTS } from '../shared/api/endpoints';
import { cn } from '../shared/utils/cn';

type Period = '7d' | '30d' | '90d';

const periods: { key: Period; label: string }[] = [
  { key: '7d', label: '7 dias' },
  { key: '30d', label: '30 dias' },
  { key: '90d', label: '90 dias' },
];

export default function ReportsPage() {
  const [period, setPeriod] = useState<Period>('30d');

  const { data: messages, isLoading } = useQuery({
    queryKey: ['messages', period],
    queryFn: () => apiClient.get<unknown[]>(ENDPOINTS.messages),
    retry: false,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-[var(--space-20)]">
        <Spinner size="md" />
      </div>
    );
  }

  if (!messages || messages.length === 0) {
    return (
      <EmptyState
        title="Sem dados ainda"
        description="Envie sua primeira campanha para ver métricas."
      />
    );
  }

  return (
    <div className="flex flex-col gap-[var(--space-6)] animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-[var(--font-size-xl)] font-bold text-[var(--color-text-primary)]">
            Relatórios
          </h2>
          <p className="text-[var(--font-size-sm)] text-[var(--color-text-secondary)] mt-[var(--space-1)]">
            Acompanhe o desempenho das suas campanhas
          </p>
        </div>
        <div className="flex gap-[var(--space-1)] bg-[var(--color-bg-subtle)] rounded-[var(--radius-md)] p-[var(--space-1)]">
          {periods.map((p) => (
            <button
              key={p.key}
              onClick={() => setPeriod(p.key)}
              className={cn(
                'px-[var(--space-3)] py-[var(--space-1)] rounded-[var(--radius-sm)] text-[var(--font-size-sm)] font-medium border-none transition-colors',
                period === p.key
                  ? 'bg-[var(--color-bg-base)] text-[var(--color-text-primary)] shadow-[var(--shadow-sm)]'
                  : 'bg-transparent text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]',
              )}
            >
              {p.label}
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
